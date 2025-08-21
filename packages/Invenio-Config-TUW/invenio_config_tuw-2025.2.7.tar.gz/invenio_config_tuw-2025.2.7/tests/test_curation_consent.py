# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for the per-user curation consent flag."""

import pytest
from invenio_accounts.proxies import current_datastore


def test_curation_setting(users):
    """Test setting the curation consent flag for users."""
    user = users[0]
    preferences = user.preferences or {}
    assert "curation_consent" not in preferences

    # try setting it to valid values
    user.preferences = {**preferences, "curation_consent": False}
    assert user.preferences.get("curation_consent") is False
    user.preferences = {**preferences, "curation_consent": True}
    assert user.preferences.get("curation_consent") is True

    # setting it to an invalid value shouldn't work
    with pytest.raises(ValueError):
        user.preferences = {**user.preferences, "curation_consent": object()}


def test_curation_preferences_form(client_with_login):
    """Test the curation settings for a user."""
    assert "curation_consent" not in (client_with_login._user.preferences or {})
    response = client_with_login.get("/account/settings/curation/")
    assert response.status_code == 200

    # give consent for curation
    response = client_with_login.post(
        "/account/settings/curation/",
        data={"preferences-curation-consent": "on", "submit": "preferences-curation-"},
    )
    user = current_datastore.get_user(client_with_login._user.email)
    assert response.status_code == 200
    assert user.preferences.get("curation_consent") is True

    # withdraw consent for curation
    # (omitting the checkbox value will evaluate it to `False`)
    response = client_with_login.post(
        "/account/settings/curation/",
        data={"submit": "preferences-curation-"},
    )
    user = current_datastore.get_user(client_with_login._user.email)
    assert response.status_code == 200
    assert user.preferences.get("curation_consent") is False
