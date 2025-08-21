# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2025 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Curations-related celery tasks."""

from datetime import UTC, date, datetime, timedelta
from typing import List, Optional

from celery import shared_task
from celery.schedules import crontab
from flask import current_app
from invenio_access.permissions import system_identity
from invenio_base.urls import invenio_url_for
from invenio_notifications.tasks import broadcast_notification
from invenio_pidstore.models import PIDDoesNotExistError
from invenio_rdm_records.proxies import current_rdm_records_service as records_service
from invenio_requests.customizations.event_types import CommentEventType
from invenio_requests.proxies import current_events_service as events_service
from invenio_requests.proxies import current_requests_service as requests_service

from ..proxies import current_config_tuw


def auto_generate_curation_request_remarks(request):
    """Auto-generate remarks on the curation request based on simple rules."""
    record = request.topic.resolve()
    remarks = []

    # check if the description has been edited
    deposit_form_defaults = current_app.config.get("APP_RDM_DEPOSIT_FORM_DEFAULTS", {})
    default_description = deposit_form_defaults.get("description", None)
    if callable(default_description):
        default_description = default_description()

    description = record.metadata["description"] or ""
    if description == default_description:
        remarks.append("The description is still the default template, please edit.")
    elif "to be edited" in description.lower():
        remarks.append(
            "The description looks like it's meant to still be edited, please check."
        )

    # check if a license has been applied
    if not record.metadata.get("rights", []):
        remarks.append(
            "Not assigning a license strongly restricts the legal reusability (all rights are reserved). Is this intentional?"
        )

    return remarks


def _get_last_request_action_timestamp(request):
    """Get the timestamp of the last log event on the request, or its creation time."""
    # check if the request has been sitting around for a while
    events = events_service.search(
        identity=system_identity,
        request_id=request["id"],
    )
    log_events = [e for e in events if e["type"] == "L"]
    if not log_events:
        # curation requests without any log events are in "submitted" state,
        # and we need to look at the creation/update time
        timestamp = datetime.fromisoformat(request["created"])
    else:
        # otherwise, we look at the last log event
        timestamp = datetime.fromisoformat(log_events[-1]["created"])

    return timestamp


@shared_task(ignore_result=True)
def send_acceptance_reminder_to_uploader(recid: str):
    """Send a reminder notification about the accepted review to the uploader."""
    from ..notifications import UserNotificationBuilder

    draft = records_service.read_draft(identity=system_identity, id_=recid)._obj
    if (owner := draft.parent.access.owned_by) is None:
        return

    # NOTE: this requires the UI app, which is the base for the celery app
    deposit_form_url = invenio_url_for(
        "invenio_app_rdm_records.deposit_edit",
        pid_value=draft.pid.pid_value,
    )

    notification = UserNotificationBuilder.build(
        receiver=owner.dump(),
        subject="ℹ️ Reminder: Your record is ready for publication!",
        draft=draft,
        deposit_form_url=deposit_form_url,
        template_name="acceptance-reminder.jinja",
    )
    broadcast_notification(notification.dumps())


@shared_task(ignore_result=True)
def send_open_requests_reminder_to_reviewers(request_ids: List[str]):
    """Send a reminder notification about open curation requests to the reviewers."""
    from ..notifications import GroupNotificationBuilder

    requests = []
    for reqid in request_ids:
        # we assume that only a single request has the same UUID
        request, *_ = list(requests_service.search(system_identity, q=f"uuid:{reqid}"))

        # NOTE: the reported "self_html" URL is currently broken
        # (points to "/requests/..." rather than "/me/requests/...")
        request_url = invenio_url_for(
            "invenio_app_rdm_requests.user_dashboard_request_view",
            request_pid_value=request["id"],
        )

        requests.append({"request": dict(request), "request_url": request_url})

    notification = GroupNotificationBuilder.build(
        receiver={"group": current_app.config["CURATIONS_MODERATION_ROLE"]},
        subject="⚠️ Reminder: There are some open curation requests",
        requests=requests,
        template_name="review-reminder.jinja",
    )
    broadcast_notification(notification.dumps())


@shared_task(ignore_result=True)
def remind_uploaders_about_accepted_reviews(
    remind_after_days: Optional[List[int]] = None,
) -> List[str]:
    """Find curation reviews that were accepted a while ago and remind the uploaders.

    ``remind_after_days`` specifies after how many days of inactivity reminders
    should be sent out to reviewers.
    Default: ``[1, 3, 5, 7, 10, 14, 30]``
    """
    if remind_after_days is None:
        remind_after_days = [1, 3, 5, 7, 10, 14, 30]

    # first, we get a list of all requests that have been updated in the last year
    #
    # note: the date query is intended to set a soft limit on the number of results
    #       to avoid unbounded degradation over time
    #       also, we don't expect any requests that haven't been updated in over a year
    #       to still be relevant for notifications
    #
    # note: querying for "L"-type "accepted" events won't work, as the information
    #       about the action is stored in the payload which is disabled for indexing
    #       as of InvenioRDM v12
    start_date = (date.today() - timedelta(days=365)).isoformat()
    today = date.today().isoformat()
    accepted_curation_requests = requests_service.search(
        identity=system_identity,
        q=(
            "type:rdm-curation AND "
            "status:accepted AND "
            f"updated:[{start_date} TO {today}]"
        ),
    )

    records_reminded = []
    now = datetime.now(tz=UTC)
    for request in accepted_curation_requests:
        if isinstance(request, dict):
            # we don't want dictionaries, we want request API classes
            # BEWARE: other than for resolving the topic, this is useless!
            request = requests_service.record_cls(request)

        try:
            # quick sanity check: don't notify about weird zombie requests
            record = request.topic.resolve()
            if record.is_published:
                continue
        except PIDDoesNotExistError:
            pass

        # check if we're hitting one of the reminder dates
        timestamp = _get_last_request_action_timestamp(request)
        if abs((now - timestamp).days) in remind_after_days:
            send_acceptance_reminder_to_uploader.delay(record.pid.pid_value)
            records_reminded.append(record.pid.pid_value)

    return records_reminded


@shared_task(ignore_result=True)
def remind_reviewers_about_open_reviews(
    remind_after_days: Optional[List[int]] = None,
) -> List[str]:
    """Remind a user about having an accepted review for an unpublished record.

    ``remind_after_days`` specifies after how many days of inactivity reminders
    should be sent out to reviewers.
    Default: ``[1, 3, 5, 7, 10, 14, 30]``
    """
    if remind_after_days is None:
        remind_after_days = [1, 3, 5, 7, 10, 14, 30]

    # note: we don't expect a lot of results for this query at any time,
    #       as the number of open requests should be low at any point
    open_curation_requests = requests_service.search(
        identity=system_identity,
        q="type:rdm-curation AND (status:submitted OR status:resubmitted)",
    )

    now = datetime.now(tz=UTC)
    stale_request_ids = []
    for request in open_curation_requests:
        if isinstance(request, dict):
            # we don't want dictionaries, we want request API classes
            # BEWARE: other than for resolving the topic, this is useless!
            request = requests_service.record_cls(request)

        try:
            # quick sanity check: don't notify about weird zombie requests
            record = request.topic.resolve()
            if record and record.is_published:
                continue
        except PIDDoesNotExistError:
            pass

        # check if we're hitting one of the reminder dates
        timestamp = _get_last_request_action_timestamp(request)
        if abs((now - timestamp).days) in remind_after_days:
            stale_request_ids.append(request["id"])

    if stale_request_ids:
        send_open_requests_reminder_to_reviewers.delay(stale_request_ids)

    return stale_request_ids


@shared_task(ignore_result=True)
def auto_review_curation_request(request_id: str):
    """Have the system automatically accept a submission request."""
    request = requests_service.read(id_=request_id, identity=system_identity)._obj
    if request.status not in ["submitted", "resubmitted"]:
        return

    # if configured, let the system automatically start a review and accept
    auto_accept = current_config_tuw.auto_accept_record_curation_request(request)
    if auto_accept:
        requests_service.execute_action(
            identity=system_identity,
            id_=request_id,
            action="review",
        )

    # auto-generate a mini review about the record
    remarks = current_config_tuw.generate_record_curation_request_remarks(request)
    if remarks:
        events_service.create(
            identity=system_identity,
            request_id=request_id,
            event_type=CommentEventType,
            data={
                "payload": {
                    "content": "\n".join([f"<p>{remark}</p>" for remark in remarks]),
                    "format": "html",
                }
            },
        )

    if auto_accept:
        requests_service.execute_action(
            identity=system_identity,
            id_=request_id,
            action="accept",
            data={
                "payload": {
                    "content": "<p>Automatically accepted by the system</p>",
                    "format": "html",
                }
            },
        )


CELERY_BEAT_SCHEDULE = {
    "reviewers-open-requests-reminder": {
        "task": "invenio_config_tuw.curations.tasks.remind_reviewers_about_open_reviews",
        "schedule": crontab(minute=30, hour=8),
    },
    "uploaders-acceptance-reminder": {
        "task": "invenio_config_tuw.curations.tasks.remind_uploaders_about_accepted_reviews",
        "schedule": crontab(minute=30, hour=8),
    },
}
