# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Utility functions for authentication."""


from invenio_oauthclient.contrib.keycloak import KeycloakSettingsHelper


class TUWSSOSettingsHelper(KeycloakSettingsHelper):
    """KeycloakSettingsHelper, adjusted for the needs of TU Data."""

    def __init__(
        self, title, description, base_url, realm, app_key=None, icon=None, **kwargs
    ):
        """Constructor."""
        signup_options = kwargs.get("signup_options", None) or {}
        signup_options.setdefault("send_register_msg", True)
        signup_options.setdefault("auto_confirm", True)
        kwargs["signup_options"] = signup_options
        kwargs.setdefault(
            "precedence_mask",
            {
                "email": True,
                "username": True,
                "user_profile": {
                    "full_name": True,
                    "given_name": True,
                    "family_name": True,
                    "affiliations": True,
                    "tiss_id": True,
                },
            },
        )

        super().__init__(
            title, description, base_url, realm, app_key=None, icon=None, **kwargs
        )

    def get_handlers(self):
        """Return a dict with the auth handlers."""
        return {
            "authorized_handler": "invenio_config_tuw.auth:authorized_signup_handler",
            "disconnect_handler": (
                "invenio_oauthclient.contrib.keycloak.handlers:disconnect_handler"
            ),
            "signup_handler": {
                "info": "invenio_config_tuw.auth:info_handler",
                "setup": "invenio_oauthclient.contrib.keycloak.handlers:setup_handler",
                "view": "invenio_oauthclient.handlers.ui:signup_handler",
            },
        }
