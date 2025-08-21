# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 - 2024 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Utility functions for authentication."""


from flask import current_app
from invenio_accounts.proxies import current_datastore
from invenio_db import db

from ..users.utils import get_user_by_username


def create_username_from_info(user_info):
    """Create a unique username from the specified user info."""
    email = user_info["email"]
    raw_username = username = email[: email.index("@")].replace(".", "-")
    num = 0

    if get_user_by_username(username) is not None:
        num += 1
        username = f"{raw_username}{num}"

    return username


def _get_or_create_role(role_name, description):
    """Fetch or create the specified role."""
    role = current_datastore.find_role(role_name)
    if not role:
        role_data = {
            "name": role_name,
            "description": description,
        }
        role = current_datastore.create_role(**role_data)
        db.session.commit()

    return role


def auto_trust_user(user):
    """Automatically trust newly registered users if that's configured."""
    auto_trust_enabled = current_app.config.get("CONFIG_TUW_AUTO_TRUST_USERS")
    trust_check = current_app.config.get("CONFIG_TUW_AUTO_TRUST_CONDITION", None)

    if user and auto_trust_enabled:
        # if the user was created successfully and auto-trust is enabled...
        trusted_user = _get_or_create_role(
            "trusted-user", "Users trusted with upload permissions"
        )

        # if no trust condition is specified, trust the user
        if trust_check is None or trust_check(user):
            # NOTE: the add_role_to_user function is idempotent
            current_datastore.add_role_to_user(user, trusted_user)
            db.session.commit()
