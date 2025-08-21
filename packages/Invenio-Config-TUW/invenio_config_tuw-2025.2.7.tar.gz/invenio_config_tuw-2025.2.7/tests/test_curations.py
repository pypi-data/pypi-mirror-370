# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests the rdm-curation utilities."""

import pytest
from flask import current_app
from invenio_access.permissions import system_identity
from invenio_curations.proxies import current_curations_service as curations_service
from invenio_rdm_records.proxies import current_rdm_records_service as records_service
from invenio_requests.proxies import current_requests_service as requests_service

from invenio_config_tuw.curations.tasks import (
    auto_generate_curation_request_remarks,
    auto_review_curation_request,
    remind_reviewers_about_open_reviews,
    remind_uploaders_about_accepted_reviews,
)


@pytest.fixture()
def example_draft(app, db, files_locs, users, resource_types):
    """Example draft."""
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

    # create the draft & make the first user the owner of the record
    draft = records_service.create(system_identity, data)._obj
    draft.parent.access.owned_by = users[0]
    draft.parent.commit()
    draft.commit()
    db.session.commit()

    return draft


def test_curation_auto_remarks(example_record, roles):
    """Test the automatic generation of remarks on rdm-curation requests."""
    request = curations_service.create(
        system_identity, {"topic": {"record": example_record.pid.pid_value}}
    )
    remarks = auto_generate_curation_request_remarks(request._obj)
    assert len(remarks) == 2
    assert [r for r in remarks if "description" in r]
    assert [r for r in remarks if "license" in r]

    # clean the rdm-curation request for other tests
    requests_service.delete(system_identity, request.id)


def test_auto_accept_curation_requests(example_record, roles):
    """Test the automatic acceptance of rdm-curation requests."""
    request = curations_service.create(
        system_identity, {"topic": {"record": example_record.pid.pid_value}}
    )

    # if not enabled, don't auto-accept requests
    current_app.config["CONFIG_TUW_AUTO_ACCEPT_CURATION_REQUESTS"] = False
    auto_review_curation_request(request.id)
    request = requests_service.read(system_identity, request.id)._obj
    assert request.status == "submitted"

    # if enabled, don auto-accept requests
    current_app.config["CONFIG_TUW_AUTO_ACCEPT_CURATION_REQUESTS"] = True
    auto_review_curation_request(request.id)
    request = requests_service.read(system_identity, request.id)._obj
    assert request.status == "accepted"

    # clean the rdm-curation request for other tests
    requests_service.delete(system_identity, request.id)
    current_app.config["CONFIG_TUW_AUTO_ACCEPT_CURATION_REQUESTS"] = False


def test_remind_reviewers_about_open_requests(example_record, example_draft, roles):
    """Test the automatic reminder emails to reviewers about open curation requests."""
    # create request & force-sync search index
    request = curations_service.create(
        system_identity, {"topic": {"record": example_record.pid.pid_value}}
    )
    requests_service.indexer.index(request._obj, arguments={"refresh": "wait_for"})

    # we're dealing with published records here, so we don't expect any notifications
    assert request._obj.status == "submitted"
    assert len(remind_reviewers_about_open_reviews()) == 0
    assert len(remind_reviewers_about_open_reviews([1])) == 0
    assert len(remind_reviewers_about_open_reviews([0])) == 0

    # clean the rdm-curation request for other tests
    requests_service.delete(system_identity, request.id)

    # -------------------------------------
    # now we do the same thing with a draft
    # -------------------------------------

    request = curations_service.create(
        system_identity, {"topic": {"record": example_draft.pid.pid_value}}
    )
    requests_service.indexer.index(request._obj, arguments={"refresh": "wait_for"})

    assert request._obj.status == "submitted"
    assert len(remind_reviewers_about_open_reviews()) == 0
    assert len(remind_reviewers_about_open_reviews([1])) == 0
    assert len(remind_reviewers_about_open_reviews([0])) == 1

    # clean the rdm-curation request for other tests
    requests_service.delete(system_identity, request.id)


def test_remind_uploaders_about_accepted_requests(example_record, example_draft, roles):
    """Test the automatic reminder emails to users about accepted curation requests."""
    # create request & force-sync search index
    request = curations_service.create(
        system_identity, {"topic": {"record": example_record.pid.pid_value}}
    )
    if request._obj.status != "accepted":
        request = requests_service.execute_action(system_identity, request.id, "review")
        request = requests_service.execute_action(system_identity, request.id, "accept")
    requests_service.indexer.index(request._obj, arguments={"refresh": "wait_for"})

    # we're dealing with published records here, so we don't expect any notifications
    assert request._obj.status == "accepted"
    assert len(remind_uploaders_about_accepted_reviews()) == 0
    assert len(remind_uploaders_about_accepted_reviews([1])) == 0
    assert len(remind_uploaders_about_accepted_reviews([0])) == 0

    # clean the rdm-curation request for other tests
    requests_service.delete(system_identity, request.id)

    # -------------------------------------
    # now we do the same thing with a draft
    # -------------------------------------

    request = curations_service.create(
        system_identity, {"topic": {"record": example_draft.pid.pid_value}}
    )
    if request._obj.status != "accepted":
        request = requests_service.execute_action(system_identity, request.id, "review")
        request = requests_service.execute_action(system_identity, request.id, "accept")
    requests_service.indexer.index(request._obj, arguments={"refresh": "wait_for"})

    assert request._obj.status == "accepted"
    assert len(remind_uploaders_about_accepted_reviews()) == 0
    assert len(remind_uploaders_about_accepted_reviews([1])) == 0
    assert len(remind_uploaders_about_accepted_reviews([0])) == 1

    # clean the rdm-curation request for other tests
    requests_service.delete(system_identity, request.id)
