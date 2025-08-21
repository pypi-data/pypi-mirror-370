# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Customizations for the ``rdm-curation`` requests from ``Invenio-Curations``."""

from invenio_curations.notifications.builders import (
    CurationRequestActionNotificationBuilder,
    CurationRequestReviewNotificationBuilder,
)
from invenio_curations.notifications.generators import GroupMembersRecipient
from invenio_curations.requests.curation import (
    CurationCreateAndSubmitAction,
    CurationRequest,
    CurationResubmitAction,
    CurationSubmitAction,
)
from invenio_notifications.services.uow import NotificationOp
from invenio_requests.notifications.filters import UserRecipientFilter
from invenio_users_resources.notifications.filters import UserPreferencesRecipientFilter
from invenio_users_resources.notifications.generators import UserRecipient

from ..notifications import TUWTaskOp
from .tasks import auto_review_curation_request

# Notification builders
# ---------------------
# They are used to generate notifications, and will primarily be used by the request
# actions (see below).
# Each notification builder has information about the target audience (recipients &
# recipient filters), and means to extract relevant information from the notification
# context.
# The generated notifications will be handled by the registered notification backend.


class TUWCurationRequestUploaderResubmitNotificationBuilder(
    CurationRequestActionNotificationBuilder
):
    """Notification builder for the request creator on resubmit."""

    type = f"{CurationRequestActionNotificationBuilder.type}.resubmit-creator"
    recipients = [UserRecipient("request.created_by")]
    recipient_filters = [UserPreferencesRecipientFilter()]


class TUWCurationRequestReviewNotificationBuilder(
    CurationRequestReviewNotificationBuilder
):
    """Notification builder for review action."""

    recipients = [
        UserRecipient("request.created_by"),
        GroupMembersRecipient("request.receiver"),
    ]
    recipient_filters = [
        UserPreferencesRecipientFilter(),
        UserRecipientFilter("executing_user"),
    ]


# Request actions
# ---------------
# Requests are effectively state machines, which have states and transitions.
# The transitions are modeled via the "request actions", and they perform some
# code operation on activation.
# These operations typically also include the generation of notifications via
# notification builders (see above).


class TUWCurationResubmitAction(CurationResubmitAction):
    """Notify both uploader and reviewer on resubmit, and auto-review."""

    def execute(self, identity, uow):
        """Notify uploader when the record gets resubmitted for review."""
        uow.register(
            NotificationOp(
                TUWCurationRequestUploaderResubmitNotificationBuilder.build(
                    identity=identity, request=self.request
                )
            )
        )
        uow.register(
            TUWTaskOp(auto_review_curation_request, str(self.request.id), countdown=15)
        )
        return super().execute(identity, uow)


class TUWCurationSubmitAction(CurationSubmitAction):
    """Submit action with a hook for automatic reviews.

    Note: It looks like this isn't really being used, in favor of "create & submit".
    """

    def execute(self, identity, uow):
        """Register auto-review task and perform the submit action."""
        uow.register(
            TUWTaskOp(auto_review_curation_request, str(self.request.id), countdown=15)
        )

        return super().execute(identity, uow)


class TUWCurationCreateAndSubmitAction(CurationCreateAndSubmitAction):
    """'Create & submit' action with a hook for automatic reviews."""

    def execute(self, identity, uow):
        """Register auto-review task and perform the 'create & submit' action."""
        uow.register(
            TUWTaskOp(auto_review_curation_request, str(self.request.id), countdown=15)
        )

        return super().execute(identity, uow)


# Request type
# ------------
# As mentioned above, requests are basically state machines.
# The individual pieces (e.g. request actions) are registered in the request type.


class TUWCurationRequest(CurationRequest):
    """Customized curation request class with modified resubmit action."""

    available_actions = {
        **CurationRequest.available_actions,
        "create": TUWCurationCreateAndSubmitAction,
        "submit": TUWCurationSubmitAction,
        "resubmit": TUWCurationResubmitAction,
    }
