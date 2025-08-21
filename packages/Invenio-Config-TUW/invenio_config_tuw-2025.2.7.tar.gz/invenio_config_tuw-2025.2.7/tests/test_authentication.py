# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for the authentication workflow."""


import json
import os

import httpretty
import pytest
from flask_login.utils import _create_identifier
from flask_oauthlib.client import OAuthResponse
from invenio_accounts.proxies import current_datastore
from invenio_base.urls import invenio_url_for as url_for
from invenio_db import db
from invenio_oauthclient.views.client import serializer


def get_state(app):
    """Get state, like in the Invenio-OAuthClient tests."""
    return serializer.dumps(
        {
            "app": app,
            "sid": _create_identifier(),
            "next": None,
        }
    )


def mock_keycloak(app_config, realm_info_dict, token_response_dict, user_info):
    """Mock a running Keycloak instance."""
    keycloak_settings = app_config["OAUTHCLIENT_REMOTE_APPS"]["keycloak"]

    httpretty.register_uri(
        httpretty.POST,
        keycloak_settings["params"]["access_token_url"],
        body=json.dumps(token_response_dict),
        content_type="application/json",
    )
    httpretty.register_uri(
        httpretty.GET,
        app_config["OAUTHCLIENT_KEYCLOAK_USER_INFO_URL"],
        body=json.dumps(user_info.data),
        content_type="application/json",
    )
    httpretty.register_uri(
        httpretty.GET,
        app_config["OAUTHCLIENT_KEYCLOAK_REALM_URL"],
        body=json.dumps(realm_info_dict),
        content_type="application/json",
    )


@pytest.fixture
def token_response_dict():
    """Keycloak access token."""
    root = os.path.dirname(__file__)
    path = os.path.join(root, "data", "keycloak", "token_response.json")
    with open(path, "r") as data_file:
        return json.load(data_file)


@pytest.fixture
def user_info():
    """Keycloak user info."""
    root = os.path.dirname(__file__)
    path = os.path.join(root, "data", "keycloak", "user_info.json")
    with open(path, "r") as data_file:
        response = json.load(data_file)

    return OAuthResponse(
        resp=None,
        content=json.dumps(response),
        content_type="application/json",
    )


@pytest.fixture
def realm_info_dict():
    """Keycloak realm info."""
    root = os.path.dirname(__file__)
    path = os.path.join(root, "data", "keycloak", "realm_info.json")
    with open(path, "r") as data_file:
        return json.load(data_file)


@httpretty.activate
def test_authentication_workflow(app, realm_info_dict, token_response_dict, user_info):
    """Test the customized authentication workflow with Keycloak."""
    mock_keycloak(app.config, realm_info_dict, token_response_dict, user_info)

    # ---------------------------------------- #
    # part 1: initial login, with registration #
    # ---------------------------------------- #
    with app.test_client() as client:
        # initiate the login process (this is a required step)...
        resp = client.get(
            url_for("invenio_oauthclient.login", remote_app="keycloak"),
        )
        assert resp.status_code == 302

        # ... now, the user has authorized the login request and is redirected back...
        resp = client.get(
            url_for(
                "invenio_oauthclient.authorized",
                remote_app="keycloak",
                code="test",
                state=get_state("keycloak"),
            )
        )
        assert resp.status_code == 302
        assert resp.location == "/oauth/signup/keycloak/"
        registration_form = resp.location

        # to complete the auth process, the user has to fill out the registration form
        resp = client.get(registration_form)
        assert resp.status_code == 200
        assert 'name="terms_of_use"' in resp.text

        # note: the email & username don't matter here, they're taken from the tokens
        #       and the curation consent is always set to `True`, regardless of input
        form_data = {
            "email": "nonsense@example.com",
            "username": "nobody",
            "terms_of_use": True,
            "curation_consent": False,
        }
        resp = client.post(registration_form, data=form_data)
        assert resp.status_code == 302
        assert resp.location == "/"

        # after successful registration, the user should be available
        user = current_datastore.get_user(user_info.data["email"])
        assert user
        assert user.email == "maximilian.moser@tuwien.ac.at"
        assert user.username == "maximilian-moser"
        assert user.preferences["curation_consent"] is True
        assert user.user_profile["given_name"] == "Maximilian"
        assert user.user_profile["family_name"] == "Moser"
        assert user.user_profile["full_name"] == "Maximilian Moser"
        assert user.user_profile["affiliations"] == "tuwien.ac.at"
        assert user.user_profile["tiss_id"] == 274424

        # now let's log out again
        client.get(url_for("security.logout"))

    # --------------------------------------------------------------- #
    # part 2: somehow letting the IdP and local user data drift apart #
    # --------------------------------------------------------------- #
    # update the user's information
    user = current_datastore.get_user(user_info.data["email"])
    user.user_profile = {
        **user.user_profile,
        "given_name": "Max J.",
        "family_name": "Moser",
        "full_name": "Max J. Moser",
    }
    db.session.commit()

    # verify that the information actually changed
    user = current_datastore.get_user(user_info.data["email"])
    assert user.user_profile["given_name"] == "Max J."
    assert user.user_profile["family_name"] == "Moser"
    assert user.user_profile["full_name"] == "Max J. Moser"

    # -------------------------------------------------------------------- #
    # part 3: logging in again, having the user info updated automatically #
    # -------------------------------------------------------------------- #
    with app.test_client() as client:
        # initiate the login process (this is a required step)...
        resp = client.get(
            url_for("invenio_oauthclient.login", remote_app="keycloak"),
        )
        assert resp.status_code == 302

        # ... now, the user has authorized the login request and is redirected back...
        resp = client.get(
            url_for(
                "invenio_oauthclient.authorized",
                remote_app="keycloak",
                code="test",
                state=get_state("keycloak"),
            )
        )
        assert resp.status_code == 302
        assert resp.location == "https://localhost/account/settings/linkedaccounts/"

        # the user information should be updated according to the token
        user = current_datastore.get_user(user_info.data["email"])
        assert user.user_profile["given_name"] == "Maximilian"
        assert user.user_profile["family_name"] == "Moser"
        assert user.user_profile["full_name"] == "Maximilian Moser"
