# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Overrides for notification builders from ``Invenio-Notifications``."""

from invenio_curations.notifications.generators import GroupMembersRecipient
from invenio_notifications.models import Notification
from invenio_notifications.services.builders import NotificationBuilder
from invenio_notifications.services.generators import EntityResolve, UserEmailBackend
from invenio_users_resources.notifications.generators import UserRecipient


class UserNotificationBuilder(NotificationBuilder):
    """Basic notification builder for users."""

    type = "user-notification"
    context = [EntityResolve(key="receiver")]
    recipients = [UserRecipient(key="receiver")]
    recipient_backends = [UserEmailBackend()]

    @classmethod
    def build(
        cls,
        receiver,
        subject,
        message=None,
        html_message=None,
        plain_message=None,
        md_message=None,
        template_name=None,
        **kwargs,
    ):
        """Build notification with context."""
        return Notification(
            type=cls.type,
            context={
                "receiver": receiver,
                "subject": subject,
                "message": message,
                "html_message": html_message,
                "plain_message": plain_message,
                "md_message": md_message,
                "template_name": template_name,
                **kwargs,
            },
        )


class GroupNotificationBuilder(UserNotificationBuilder):
    """Basic notification builder for groups."""

    type = "group-notification"
    recipients = [GroupMembersRecipient(key="receiver")]
