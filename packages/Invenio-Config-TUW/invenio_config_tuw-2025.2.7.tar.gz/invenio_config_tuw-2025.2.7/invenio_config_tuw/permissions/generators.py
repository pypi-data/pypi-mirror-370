# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Permission generators to be used for the permission policies at TU Wien."""

from flask import current_app
from flask_login import current_user
from flask_principal import RoleNeed, UserNeed
from invenio_access.permissions import any_user
from invenio_curations.services.generators import (
    CurationModerators,
    IfCurationRequestExists,
)
from invenio_rdm_records.services.generators import ConditionalGenerator
from invenio_records_permissions.generators import Generator, IfConfig
from invenio_records_resources.services.files.generators import IfTransferType
from invenio_records_resources.services.files.transfer import (
    LOCAL_TRANSFER_TYPE,
    MULTIPART_TRANSFER_TYPE,
)


class IfPublished(ConditionalGenerator):
    """Conditional generator that checks if the record has been published before."""

    def _condition(self, record=None, **kwargs):
        """Check if the record has been published."""
        return record is not None and record.is_published


class DisableIf(Generator):
    """Denies ALL users including super users, if a condition is met."""

    def __init__(self, check=lambda: True):
        """Constructor."""
        super().__init__()
        self.check = check

    def excludes(self, **kwargs):
        """Preventing Needs."""
        if self.check():
            return [any_user]
        else:
            return []


class TrustedUsers(Generator):
    """Allows users with the "trusted-user" role."""

    def needs(self, record=None, **kwargs):
        """Enabling Needs."""
        return [RoleNeed("trusted-user")]


class RecordOwnersWithRole(Generator):
    """Allows record owners with a given role."""

    def __init__(self, role_name, exclude=True):
        """Constructor."""
        super().__init__()
        self.role_name = role_name
        self.exclude = exclude

    def needs(self, record=None, **kwargs):
        """Enabling Needs."""
        if record is None:
            if (
                bool(current_user)
                and not current_user.is_anonymous
                and current_user.has_role(self.role_name)
            ):
                return [UserNeed(current_user.id)]
            else:
                return []

        needs = []
        if owner := record.parent.access.owner:
            if owner.owner_id != "system":
                has_role = owner.resolve().has_role(self.role_name)
                if has_role:
                    needs.append(UserNeed(owner.owner_id))

        return needs

    def excludes(self, **kwargs):
        """Explicit excludes."""
        if not self.exclude:
            return super().excludes(**kwargs)

        elif (
            bool(current_user)
            and not current_user.is_anonymous
            and not current_user.has_role(self.role_name)
        ):
            return [UserNeed(current_user.id)]

        return []


def DisableIfReadOnly():
    """Disable permissions for everybody if the repository is set as read only."""
    return DisableIf(lambda: current_app.config.get("CONFIG_TUW_READ_ONLY_MODE", False))


def TrustedRecordOwners(exclude=False):
    """Allows record owners with the "trusted-user" role."""
    return RecordOwnersWithRole("trusted-user", exclude=exclude)


def IfCurationsEnabled(then_, else_):
    """Check if the curations module is enabled."""
    return IfConfig("CONFIG_TUW_CURATIONS_ENABLED", then_=then_, else_=else_)


def CurationModeratorsIfRequestExists(else_=None):
    """If curations are enabled and a request exists, allow moderators."""
    return IfCurationsEnabled(
        [IfCurationRequestExists(then_=[CurationModerators()], else_=[])],
        else_ or [],
    )


def IfLocalOrMultipart(then_, else_):
    """Wrapper for the ``IfTransferType`` generator for local and multipart files."""
    return IfTransferType(
        LOCAL_TRANSFER_TYPE,
        then_=then_,
        else_=IfTransferType(MULTIPART_TRANSFER_TYPE, then_=then_, else_=else_),
    )
