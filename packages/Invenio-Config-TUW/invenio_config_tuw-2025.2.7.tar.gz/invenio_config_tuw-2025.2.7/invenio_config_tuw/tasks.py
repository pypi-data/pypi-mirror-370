# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2025 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Celery tasks running in the background."""

from difflib import HtmlDiff

from celery import shared_task
from celery.schedules import crontab
from flask import current_app
from invenio_access.permissions import system_identity
from invenio_base.urls import invenio_url_for
from invenio_db import db
from invenio_files_rest.models import FileInstance
from invenio_notifications.registry import (
    EntityResolverRegistry as NotificationsResolverRegistry,
)
from invenio_notifications.tasks import broadcast_notification
from invenio_rdm_records.proxies import current_rdm_records_service as records_service

from .notifications import UserNotificationBuilder


@shared_task(ignore_result=True)
def send_publication_notification(recid: str):
    """Send the record uploader an email about the publication of their record."""
    record = records_service.read(identity=system_identity, id_=recid)._obj
    record.relations.clean()
    if (owner := record.parent.access.owner) is None:
        current_app.logger.warn(
            f"Record '{recid}' has no owner to notify about its publication!"
        )
        return

    # build the message
    datacite_test_mode = current_app.config["DATACITE_TEST_MODE"]
    if "identifier" in record.get("pids", {}).get("doi", {}):
        doi = record["pids"]["doi"]["identifier"]

        if datacite_test_mode:
            base_url = "https://handle.test.datacite.org"
            pid_type = "DOI-like handle"
        else:
            base_url = "https://doi.org"
            pid_type = "DOI"

        pid_url = f"{base_url}/{doi}"

    else:
        pid_type = "URL"
        pid_url = invenio_url_for(
            "invenio_app_rdm_records.record_detail",
            pid_value=record.pid.pid_value,
        )

    # send the notification
    notification = UserNotificationBuilder.build(
        receiver=owner.dump(),
        subject=f'Your record "{record.metadata['title']}" was published',
        record=record,
        record_pid={"type": pid_type, "url": pid_url},
        template_name="record-publication.jinja",
    )
    broadcast_notification(notification.dumps())


@shared_task(ignore_reuslt=True)
def send_metadata_edit_notification(
    recid: str,
    publisher: dict,
    additions: list,
    removals: list,
    changes: list,
):
    """Send an email to the record's owner about a published edit."""
    record = records_service.read(identity=system_identity, id_=recid)._obj
    record.relations.clean()
    if (owner := record.parent.access.owner) is None:
        current_app.logger.warn(
            f"Record '{recid}' has no owner to notify about the published edit!"
        )
        return

    description_diff_table = None
    for change in changes:
        field_path, (old, new) = change
        if field_path[0] == "metadata" and field_path[1] == "description":
            diff = HtmlDiff(tabsize=4, wrapcolumn=100)
            old, new = old.splitlines(keepends=True), new.splitlines(keepends=True)
            description_diff_table = diff.make_table(old, new)

    # parse the most interesting changes for the user out of the dictionary diffs
    md_field_names = {"rights": "licenses"}
    updated_metadata_fields = set()
    updated_access_settings = False
    for change in [*additions, *removals, *changes]:
        field_path, *_ = change
        section, field_name = (
            (field_path[0], field_path[1])
            if len(field_path) > 1
            else (None, field_path[0])
        )
        if section == "metadata":
            field_name = md_field_names.get(field_name) or field_name
            updated_metadata_fields.add(field_name.replace("_", " ").capitalize())
        elif section == "access":
            updated_access_settings = True

    # note: in contrast to the "resolver registry" from Invenio-Requests, the one from
    # Invenio-Notifications resolves expanded service result item dictionaries that
    # can be passed on to notifications
    notification = UserNotificationBuilder.build(
        receiver=owner.dump(),
        subject=f'Edits for your record "{record.metadata['title']}" were published',
        recid=record.pid.pid_value,
        record=record,
        publisher=NotificationsResolverRegistry.resolve_entity(publisher),
        updated_access_settings=updated_access_settings,
        updated_metadata_fields=sorted(updated_metadata_fields),
        description_diff_table=description_diff_table,
        template_name="metadata-edit.jinja",
    )
    broadcast_notification(notification.dumps())


@shared_task
def remove_dead_files():
    """Remove dead file instances (that don't have a URI) from the database.

    These files seem to be leftovers from failed uploads that don't get cleaned up
    properly.
    """
    dead_file_instances = FileInstance.query.filter(FileInstance.uri.is_(None)).all()
    for fi in dead_file_instances:
        db.session.delete(fi)
        for o in fi.objects:
            db.session.delete(o)

    db.session.commit()


CELERY_BEAT_SCHEDULE = {
    "clean-dead-files": {
        "task": "invenio_config_tuw.tasks.remove_dead_files",
        "schedule": crontab(minute=1, hour=2),
    },
}
