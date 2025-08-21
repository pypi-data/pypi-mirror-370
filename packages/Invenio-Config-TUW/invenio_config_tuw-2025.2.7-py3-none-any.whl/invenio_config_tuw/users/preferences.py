# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2025 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Form for curation-related user settings, inspired by the notifications settings."""

from flask_wtf import FlaskForm
from invenio_users_resources.forms import NotificationsForm
from wtforms import BooleanField, EmailField


class CurationPreferencesProxy:
    """Proxy class giving direct access to a user's curation preferences."""

    def __init__(self, user):
        """Constructor."""
        super().__setattr__("_user", user)

    def __getattr__(self, attr):
        """Get the attribute's value in the user's curation preferences."""
        if attr == "_user":
            return self._user

        return self._user.preferences.get(f"curation_{attr}")

    def __setattr__(self, attr, value):
        """Set the attribute's value in the user's curation preferences."""
        self._user.preferences = {
            **self._user.preferences,
            f"curation_{attr}": value,
        }

    def __hasattr__(self, attr):
        """Check if the user's curation preferences have the given attribute."""
        return f"curation_{attr}" in self._user.preferences


class CurationPreferencesForm(FlaskForm):
    """Form for editing a user's curation preferences."""

    proxy_cls = CurationPreferencesProxy

    # note: this field is disabled in the templates; we can't use `render_kw` because
    #       we're doing our own manual rendering in the templates for some reason...
    consent = BooleanField(
        "Consent to curation of my records",
        description=(
            "Allow the repository team to curate the metadata of my records, e.g. "
            "by fixing typos and adding new related works as they are reported."
        ),
    )

    def process(self, formdata=None, obj=None, data=None, extra_filters=None, **kwargs):
        """Build a proxy around the object."""
        if obj is not None:
            obj = self.proxy_cls(obj)

        return super().process(
            formdata=formdata, obj=obj, data=data, extra_filters=extra_filters, **kwargs
        )

    def populate_obj(self, user):
        """Populate the object."""
        user = self.proxy_cls(user)
        return super().populate_obj(user)


class TUWNotificationsForm(NotificationsForm):
    """Form for editing user notification preferences."""

    secondary_email = EmailField(
        label="Secondary email",
        description=(
            "Secondary email address for notifications. "
            "If set, this email address will be added in CC."
        ),
    )
