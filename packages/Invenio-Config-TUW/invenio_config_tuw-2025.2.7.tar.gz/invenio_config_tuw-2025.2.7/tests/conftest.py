# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 - 2021 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import os
import shutil

import pytest
from flask_security.utils import hash_password, login_user
from flask_webpackext.manifest import (
    JinjaManifest,
    JinjaManifestEntry,
    JinjaManifestLoader,
)
from invenio_access.permissions import system_identity
from invenio_accounts.testutils import login_user_via_session
from invenio_app.factory import create_app as create_invenio
from invenio_communities.cache.cache import IdentityCache
from invenio_files_rest.models import Location
from invenio_rdm_records.proxies import current_rdm_records_service as records_service
from invenio_records_resources.proxies import current_service_registry
from invenio_vocabularies.proxies import current_service as vocab_svc
from simplekv.memory import DictStore

from invenio_config_tuw.auth.settings import TUWSSOSettingsHelper


#
# Mock the webpack manifest to avoid having to compile the full assets.
#
class MockJinjaManifest(JinjaManifest):
    """Mock manifest."""

    def __getitem__(self, key):
        """Get a manifest entry."""
        return JinjaManifestEntry(key, [key])

    def __getattr__(self, name):
        """Get a manifest entry."""
        return JinjaManifestEntry(name, [name])


class MockManifestLoader(JinjaManifestLoader):
    """Manifest loader creating a mocked manifest."""

    def load(self, filepath):
        """Load the manifest."""
        return MockJinjaManifest()


class DictIdentityCache(IdentityCache):
    """Simple dictionary-based identity cache."""

    def __init__(self):
        """Constructor."""
        self._dict = {}

    def get(self, key):
        """Get the cached object."""
        return self._dict.get(key)

    def set(self, key, value):
        """Cache the object."""
        self._dict[key] = value

    def flush(self):
        """Flush the cache."""
        self._dict.clear()

    def delete(self, key):
        """Delete a key."""
        self._dict.pop(key, None)

    def append(self, key, value):
        """Append a new value to a value list."""
        self._dict[key] += value


@pytest.fixture(scope="module")
def create_app(instance_path):
    """Create test app."""
    return create_invenio


@pytest.fixture(scope="module")
def app_config(app_config):
    """Testing configuration."""
    helper = TUWSSOSettingsHelper(
        title="Keycloak",
        description="TUW-OIDC",
        base_url="http://localhost:8080",
        realm="test",
    )
    app_config["OAUTHCLIENT_REMOTE_APPS"] = {"keycloak": helper.remote_app}
    app_config["OAUTHCLIENT_KEYCLOAK_REALM_URL"] = helper.realm_url
    app_config["OAUTHCLIENT_KEYCLOAK_USER_INFO_URL"] = helper.user_info_url
    app_config["OAUTHCLIENT_KEYCLOAK_VERIFY_AUD"] = False
    app_config["OAUTHCLIENT_KEYCLOAK_VERIFY_EXP"] = False
    app_config["OAUTHCLIENT_KEYCLOAK_AUD"] = "tudata"
    app_config["KEYCLOAK_APP_CREDENTIALS"] = {
        "consumer_key": "key",
        "consumer_secret": "secret",
    }

    # set a dead simple in-memory session store, for the OIDC workflow
    app_config["ACCOUNTS_SESSION_STORE_FACTORY"] = lambda app: DictStore({})
    app_config["COMMUNITIES_IDENTITIES_CACHE_HANDLER"] = lambda app: DictIdentityCache()

    # some further testing config
    app_config["TESTING"] = True
    app_config["WTF_CSRF_ENABLED"] = False
    app_config["MAIL_SUPPRESS_SEND"] = True
    app_config["WEBPACKEXT_MANIFEST_LOADER"] = MockManifestLoader
    app_config["SERVER_NAME"] = "localhost"

    return app_config


@pytest.fixture()
def users(app, db):
    """Create example user."""
    with db.session.begin_nested():
        datastore = app.extensions["security"].datastore
        user1 = datastore.create_user(
            email="info@inveniosoftware.org",
            password=hash_password("password"),
            active=True,
        )
        user2 = datastore.create_user(
            email="ser-testalot@inveniosoftware.org",
            password=hash_password("beetlesmasher"),
            active=True,
        )

    db.session.commit()
    return [user1, user2]


@pytest.fixture()
def roles(app, db):
    """Create required roles."""
    with db.session.begin_nested():
        datastore = app.extensions["security"].datastore
        role = datastore.create_role(
            id=app.config["CURATIONS_MODERATION_ROLE"],
            name=app.config["CURATIONS_MODERATION_ROLE"],
            description="Publication request reviewers",
        )

    db.session.commit()
    return [role]


@pytest.fixture()
def client_with_login(client, users):
    """A test client for the app with a logged-in user."""
    user = users[0]
    login_user(user)
    login_user_via_session(client, email=user.email)
    client._user = user
    return client


@pytest.fixture()
def files_locs(db):
    """Creates app location for testing."""
    loc_path = "testing_data_location"
    if os.path.exists(loc_path):
        shutil.rmtree(loc_path)

    os.makedirs(loc_path)
    loc1 = Location(name="local", uri=loc_path, default=True)
    loc2 = Location(name="alt", uri=loc_path, default=False)
    db.session.add(loc1)
    db.session.add(loc2)
    db.session.commit()
    yield [loc1, loc2]

    os.rmdir(loc_path)


@pytest.fixture()
def resource_types(db):
    """Creates the required resource type vocabulary for the tests."""
    vocab_svc.create_type(system_identity, "resourcetypes", "rsrct")
    vocab_svc.create(
        system_identity,
        {
            "id": "dataset",
            "icon": "table",
            "props": {
                "csl": "dataset",
                "datacite_general": "Dataset",
                "datacite_type": "",
                "openaire_resourceType": "21",
                "openaire_type": "dataset",
                "eurepo": "info:eu-repo/semantics/other",
                "schema.org": "https://schema.org/Dataset",
                "subtype": "",
                "type": "dataset",
                "marc21_type": "dataset",
                "marc21_subtype": "",
            },
            "title": {"en": "Dataset"},
            "tags": ["depositable", "linkable"],
            "type": "resourcetypes",
        },
    )


@pytest.fixture()
def affiliations(db):
    """Creates the required affiliations vocabulary for the tests."""
    vocab_svc.create_type(system_identity, "affiliations", "aff")

    service = current_service_registry.get("affiliations")
    service.create(
        system_identity,
        {
            "acronym": "TUW",
            "id": "04d836q62",
            "identifiers": [{"identifier": "04d836q62", "scheme": "ror"}],
            "name": "TU Wien",
            "title": {"de": "Technische Universit\xe4t Wien", "en": "TU Wien"},
        },
    )


@pytest.fixture()
def example_record(app, db, files_locs, users, resource_types):
    """Example record."""
    # avoid curations for the creation of the example record
    curations_enabled = app.config["CONFIG_TUW_CURATIONS_ENABLED"]
    app.config["CONFIG_TUW_CURATIONS_ENABLED"] = False

    data = {
        "access": {
            "record": "public",
            "files": "public",
        },
        "files": {
            "enabled": False,
        },
        "metadata": {
            "creators": [
                {
                    "person_or_org": {
                        "family_name": "Darksouls",
                        "given_name": "John",
                        "type": "personal",
                    }
                },
            ],
            "description": app.config["APP_RDM_DEPOSIT_FORM_DEFAULTS"]["description"],
            "publication_date": "2024-12-31",
            "publisher": "TU Wien",
            "resource_type": {"id": "dataset"},
            "title": "Exciting dataset",
        },
    }

    # create and publish the record
    draft = records_service.create(system_identity, data)
    record = records_service.publish(system_identity, draft.id)._obj

    # make the first user the owner of the record
    record.parent.access.owned_by = users[0]
    record.parent.commit()
    record.commit()
    db.session.commit()

    app.config["CONFIG_TUW_CURATIONS_ENABLED"] = curations_enabled
    return record


@pytest.fixture()
def disabled_curations(app):
    """Disable the curations workflow for individual tests."""
    curations_enabled = app.config["CONFIG_TUW_CURATIONS_ENABLED"]
    app.config["CONFIG_TUW_CURATIONS_ENABLED"] = False
    yield

    # restore the curations config
    app.config["CONFIG_TUW_CURATIONS_ENABLED"] = curations_enabled
