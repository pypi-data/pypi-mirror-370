# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for the TISS integration."""

import json
import os
import re

import httpretty
import pytest
from invenio_access.permissions import system_identity
from invenio_records_resources.proxies import current_service_registry

from invenio_config_tuw.tiss.models import OrgUnit
from invenio_config_tuw.tiss.tasks import sync_names_from_tiss
from invenio_config_tuw.tiss.utils import _get_org_unit_dict, fetch_tiss_data


@pytest.fixture()
def names_vocabularies(app, db):
    """Some name vocabulary entries."""
    names_service = current_service_registry.get("names")

    # this vocabulary entry will be updated, since the name changed
    names_service.create(
        system_identity,
        {
            "id": "0000-0003-1337-0425",
            "name": "Science, Boss",
            "given_name": "Boss",
            "family_name": "Science",
            "identifiers": [
                {"identifier": "0000-0003-1337-0425", "scheme": "orcid"},
            ],
            "affiliations": [{"name": "TU Wien"}],
        },
    )

    # this vocabulary entry will stay the same
    names_service.create(
        system_identity,
        {
            "id": "0000-0003-4206-1330",
            "name": "Ericsson, Anders",
            "given_name": "Anders",
            "family_name": "Ericsson",
            "identifiers": [
                {"identifier": "0000-0003-4206-1330", "scheme": "orcid"},
            ],
            "affiliations": [{"name": "TU Wien"}],
        },
    )


def mock_tiss_org_units():
    """Mock the TISS API for organizational units."""
    pattern = re.compile(
        # the query string needs to be taken into account
        r"^https://tiss.tuwien.ac.at/api/orgunit/v23/code/([eE]\d+[0-9-]*)(\?.*)?$"
    )

    def org_unit_callback(request, uri, response_headers):
        """Mock the TISS reply with our example data."""
        ou_code = pattern.match(uri).group(1).lower()
        data_path = os.path.join(
            os.path.dirname(__file__), "data", "tiss", f"{ou_code}.json"
        )

        with open(data_path, "r") as ou_file:
            ou_data = json.load(ou_file)

        # if we don't want the employees listed, we simply strip them out
        persons = request.querystring.get("persons", [])
        if not persons or persons[0] != "true":
            ou_data.pop("manager", None)
            ou_data.pop("employees", None)
            for sub_ou in ou_data.get("child_org_refs", []):
                sub_ou.pop("manager", None)

        response_headers["Content-Type"] = "application/json"
        return [200, response_headers, json.dumps(ou_data)]

    httpretty.register_uri(
        httpretty.GET,
        pattern,
        body=org_unit_callback,
    )


def mock_ror_api():
    """Mock the response for TUW in the ROR API."""
    data_path = os.path.join(os.path.dirname(__file__), "data", "ror-tuw.json")
    with open(data_path, "r") as data_file:
        ror_response = json.load(data_file)

    httpretty.register_uri(
        httpretty.GET,
        "https://api.ror.org/organizations/04d836q62",
        body=json.dumps(ror_response),
        content_type="application/json",
    )


def test_fetching_real_tiss_data():
    """Check if the real TISS API data looks as expected."""
    # fmt: off
    expected_common_keys = {
        "card_uri", "code", "employees", "manager", "name_de",
        "name_en", "number", "oid", "tiss_id", "type",
    }
    expected_e000_keys = expected_common_keys.union(
        {"child_orgs_refs"}
    )
    expected_e05806_keys = expected_common_keys.union(
        {"addresses", "parent_org_ref", "websites"}
    )
    # fmt: on

    # E000 is the root node, and doesn't have employees itself
    e000_data = _get_org_unit_dict("E000")
    assert e000_data["tiss_id"] == 3000
    assert set(e000_data.keys()) == expected_e000_keys
    assert not e000_data["employees"]
    e000_ou = OrgUnit.from_dict(e000_data)
    assert not e000_ou.employees

    # E058-06 is the CRDM, and has a few employees
    crdm_data = _get_org_unit_dict("E058-06")
    assert crdm_data["tiss_id"] == 6513
    assert set(crdm_data.keys()) == expected_e05806_keys
    assert crdm_data["employees"]
    crdm_ou = OrgUnit.from_dict(crdm_data)
    assert crdm_ou.employees


@httpretty.activate
def test_fetching_tiss_data():
    """Test fetching the fake TISS data."""
    mock_tiss_org_units()
    org_units, employees = fetch_tiss_data()

    # according to our test data, we expect 3 OUs with 4 employees in total
    assert len(org_units) == 3
    assert len(employees) == 4


@httpretty.activate
def test_sync_names_from_tiss(names_vocabularies, affiliations):
    """Test the TISS names vocabulary synchronization task."""
    mock_tiss_org_units()
    mock_ror_api()

    # our test data has 3 employees with ORCID identifiers:
    # one will be updated due to a name change, one will stay the same
    # and another one will be created fresh because it didn't exist before
    results = sync_names_from_tiss()
    assert results["created"] == 1
    assert results["updated"] == 1
    assert results["failed"] == 0
