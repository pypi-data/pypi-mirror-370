# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2025 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Various schemas to use in InvenioRDM."""

from invenio_app_rdm.users.schemas import NotificationsUserSchema as UserSchema
from invenio_app_rdm.users.schemas import (
    UserPreferencesNotificationsSchema as UserPreferencesSchema,
)
from invenio_users_resources.services.schemas import (
    NotificationPreferences,
    UserProfileSchema,
)
from marshmallow import fields, pre_load


# profile
class TUWUserProfileSchema(UserProfileSchema):
    """User profile schema with TU Wien extensions."""

    given_name = fields.String()
    family_name = fields.String()
    tiss_id = fields.Integer()


# preferences
class TUWNotificationPreferencesSchema(NotificationPreferences):
    """Schema for notification preferences."""

    secondary_email = fields.Email()

    @pre_load
    def remove_empty_secondary_mail(self, data, **kwargs):
        """Turn empty string for secondary emails into `None`."""
        if not data.get("secondary_email"):
            data.pop("secondary_email", None)

        return data


class TUWUserPreferencesSchema(UserPreferencesSchema):
    """User preferences schema with TU Wien extensions."""

    curation_consent = fields.Boolean(default=True)
    notifications = fields.Nested(TUWNotificationPreferencesSchema)


# complete user schema
class TUWUserSchema(UserSchema):
    """User schema with TU Wien extensions."""

    preferences = fields.Nested(TUWUserPreferencesSchema)
