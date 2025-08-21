# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2025 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Custom registration form, covering the new fields from the extended user profile."""

from flask import current_app
from markupsafe import Markup
from werkzeug.local import LocalProxy
from wtforms import BooleanField, Form, FormField, HiddenField, validators

_security = LocalProxy(lambda: current_app.extensions["security"])


def tuw_registration_form(*args, **kwargs):
    """Create the registration form for TU Wien.

    This registration form will only hold values but not display any input fields,
    because we get all our information from the TUW SSO/Keycloak.
    The form's structure should reflect that of the ``User`` model.

    Note: Invenio-OAuthClient 2.0 tweaked the workings of the registration a bit;
    now the precedence mask is applied to values from the user's input in the form,
    the result of which is then fed back to the form (for validation, I assume),
    which in turn is fetched again and used to populate the user account.
    This means that we have to actually hold information in the forms and can't
    just set every field to ``None``.
    Also, it means that all custom fields for the ``user_profile`` and ``preferences``
    have to appear in the form.
    """
    # the url must contain the special characters rather than encoded values:
    # `Markup` escapes them
    terms_of_use_url = "https://www.tuwien.at/index.php?eID=dms&s=4&path=Directives and Regulations of the Rectorate/Research_Data_Terms_of_Use.pdf"  # noqa
    message = Markup(
        f"Accept the <a href='{terms_of_use_url}' target='_blank'>Terms and Conditions</a> (<strong>required</strong>)"  # noqa
    )

    class UserProfileForm(Form):
        """Form for the user profile."""

        full_name = HiddenField()
        given_name = HiddenField()
        family_name = HiddenField()
        affiliations = HiddenField()
        tiss_id = HiddenField()

    class UserPreferenceForm(Form):
        """Form for the user preferences."""

        visibility = HiddenField(default="public")
        email_visibility = HiddenField(default="restricted")

    class UserRegistrationForm(_security.confirm_register_form):
        """Form for the basic user information."""

        email = HiddenField()
        username = HiddenField()
        user_profile = FormField(UserProfileForm, separator=".")
        preferences = FormField(UserPreferenceForm, separator=".")
        password = None
        recaptcha = None
        profile = None  # disable the default 'profile' form from invenio
        submit = None  # defined in the template
        terms_of_use = BooleanField(message, validators=[validators.DataRequired()])

        def _get_tiss_id(self):
            """Parse the TISS ID value into a number."""
            try:
                return int(self.user_profile.tiss_id.data)
            except Exception:
                return None

        def to_dict(self):
            """Turn the form into a dictionary."""
            return {
                "email": self.email.data,
                "username": self.username.data,
                "password": None,
                "user_profile": {
                    "full_name": self.user_profile.full_name.data,
                    "given_name": self.user_profile.given_name.data,
                    "family_name": self.user_profile.family_name.data,
                    "affiliations": self.user_profile.affiliations.data,
                    "tiss_id": self._get_tiss_id(),
                },
                "preferences": {
                    "visibility": self.preferences.visibility.data,
                    "email_visibility": self.preferences.email_visibility.data,
                    "curation_consent": True,
                },
            }

    return UserRegistrationForm(*args, **kwargs)
