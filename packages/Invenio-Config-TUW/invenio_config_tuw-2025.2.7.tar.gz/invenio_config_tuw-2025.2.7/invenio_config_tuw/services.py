# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.


"""Overrides for core services."""

from collections import namedtuple
from datetime import datetime

import dictdiffer
from flask import current_app
from invenio_curations.services.components import (
    CurationComponent as BaseCurationComponent,
)
from invenio_drafts_resources.services.records.components import ServiceComponent
from invenio_pidstore.models import PIDStatus
from invenio_rdm_records.records.api import get_files_quota
from invenio_rdm_records.services.components import DefaultRecordsComponents
from invenio_records_resources.services.uow import TaskOp
from invenio_requests.resolvers.registry import ResolverRegistry

from .proxies import current_config_tuw
from .tasks import send_metadata_edit_notification, send_publication_notification


class ParentAccessSettingsComponent(ServiceComponent):
    """Service component that allows access requests per default."""

    def create(self, identity, record, **kwargs):
        """Set the parent access settings to allow access requests."""
        settings = record.parent.access.settings
        settings.allow_guest_requests = True
        settings.allow_user_requests = True
        settings.secret_link_expiration = 30


class PublicationNotificationComponent(ServiceComponent):
    """Component for notifying users about the publication of their record."""

    def publish(self, identity, draft=None, record=None, **kwargs):
        """Register a task to send off the notification email."""
        # the first time the record gets published, the PID's status
        # gets set to "R" but that won't have been transferred to the
        # record's data until the `record.commit()` from the unit of work
        has_been_published = (
            draft.pid.status == draft["pid"]["status"] == PIDStatus.REGISTERED
        )

        if not has_been_published:
            self.uow.register(
                TaskOp(send_publication_notification, record.pid.pid_value)
            )


class CurationComponent(BaseCurationComponent):
    """Curation component that only activates if curations are enabled."""

    def publish(self, identity, draft=None, record=None, **kwargs):
        """Check if record curation request has been accepted."""
        if current_config_tuw.curations_enabled:
            return super().publish(identity, draft=draft, record=record, **kwargs)

    def delete_draft(self, identity, draft=None, record=None, force=False):
        """Delete a draft."""
        if current_config_tuw.curations_enabled:
            return super().delete_draft(
                identity, draft=draft, record=record, force=force
            )

    def update_draft(self, identity, data=None, record=None, errors=None):
        """Update draft handler."""
        if current_config_tuw.curations_enabled:
            value = super().update_draft(
                identity, data=data, record=record, errors=errors
            )

            # suppress the "missing field: rdm-curation" error as that is more
            # confusing than helpful
            errors = errors or []
            curation_field_errors = [
                e for e in errors if e.get("field") == "custom_fields.rdm-curation"
            ]
            for e in curation_field_errors:
                errors.remove(e)

            return value


class PublicationDateComponent(ServiceComponent):
    """Component for populating the "publication_date" metadata field."""

    def new_version(self, identity, draft=None, record=None):
        """Set "publication_date" for new record versions."""
        draft.metadata.setdefault(
            "publication_date", datetime.now().strftime("%Y-%m-%d")
        )


class MetadataEditNotificationComponent(ServiceComponent):
    """Component for notifying the record owner about metadata edits."""

    def publish(self, identity, draft=None, record=None):
        """Send a notification to the record owner about edits they haven't made."""
        if not record or not (owner := record.parent.access.owned_by):
            return

        owner_id = str(owner.owner_id)
        has_revisions = record and list(record.revisions)
        is_system_or_owner = identity and str(identity.id) in ["system", owner_id]
        if not has_revisions or is_system_or_owner:
            # skip if there are no revisions, or if the owner published the edit, or
            # if the system is the publisher (mostly happens in scripts)
            return

        # compare the latest revision with the `draft` - this seems to list more
        # details (e.g. access settings) than comparisons with the `record`
        *_, latest_rev = record.revisions
        diffs = list(
            dictdiffer.diff(latest_rev, draft, dot_notation=False, expand=True)
        )
        if not latest_rev or not diffs:
            return

        Diff = namedtuple("Diff", ["field", "change"])
        additions, changes, removals = [], [], []
        for diff in diffs:
            type_, field_path, change = diff
            field_path = field_path.copy()

            # if certain fields didn't have values in the draft, their fields may not
            # have been present at all in its dict form - in this case, the change will
            # include the field's name (similar for removals, but other way):
            #
            # ('add', ['metadata'], [('version', '1')])
            # ('add', ['metadata'], [('languages', [{'id': 'eng'}])])
            # ('remove', ['metadata'], [('dates', [{'date': '2025', 'type': {'id': 'accepted'}}])])
            if type_ in ["add", "remove"] and len(change) == 1:
                field_name, change_ = change[0]
                if isinstance(field_name, str):
                    field_path.append(field_name)
                    change = change_

            difference = Diff(field_path, change)
            if type_ == "add":
                additions.append(difference)
            elif type_ == "remove":
                removals.append(difference)
            elif type_ == "change":
                changes.append(difference)
            else:
                current_app.logger.warn(
                    f"(calculating record diff) unknown diff type: {diff}"
                )

        # note: we use the "resolver registry" from Invenio-Requests here because it
        # operates on "raw" objects rather than service result items (which we don't
        # have available here) like the one from Invenio-Notifications does
        self.uow.register(
            TaskOp(
                send_metadata_edit_notification,
                record.pid.pid_value,
                ResolverRegistry.reference_identity(identity),
                additions,
                removals,
                changes,
            )
        )


class RecordQuotaServiceComponent(ServiceComponent):
    """Service component to set the record's bucket quota.

    This is effectively the same as the following PR:
    https://github.com/inveniosoftware/invenio-rdm-records/pull/2037

    It can be removed once that PR is merged.
    """

    def create(self, identity, data=None, record=None, errors=None):
        """Assigns files.enabled and sets the bucket's quota size & max file size."""
        quota = get_files_quota(record)
        if quota_size := quota.get("quota_size"):
            record.files.bucket.quota_size = quota_size

        if max_file_size := quota.get("max_file_size"):
            record.files.bucket.max_file_size = max_file_size


TUWRecordsComponents = [
    *DefaultRecordsComponents,
    ParentAccessSettingsComponent,
    RecordQuotaServiceComponent,
    PublicationDateComponent,
    PublicationNotificationComponent,
    MetadataEditNotificationComponent,
    CurationComponent,
]
