# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Miscellaneous tests that don't really belong anywhere else."""

from logging.handlers import SMTPHandler

from flask import g, request
from invenio_access.permissions import Identity, system_identity
from invenio_db import db
from invenio_rdm_records.proxies import current_rdm_records_service as service
from invenio_records_resources.services.uow import UnitOfWork

import invenio_config_tuw
from invenio_config_tuw.startup import register_smtp_error_handler
from invenio_config_tuw.tasks import (
    send_metadata_edit_notification,
    send_publication_notification,
)
from invenio_config_tuw.users.utils import current_user_as_creator


def test_send_publication_notification_email(example_record, mocker):
    """Test (not really) sending an email about the publication of a record."""
    record = example_record
    with mocker.patch("invenio_config_tuw.tasks.broadcast_notification"):
        send_publication_notification(record.pid.pid_value)

        # the `expected_args` will need to be updated whenever we change the messages
        recid = record.pid.pid_value
        title = record.metadata["title"]
        expected_args = {
            "type": "user-notification",
            "context": {
                "receiver": {"user": record.parent.access.owned_by.resolve().id},
                "subject": f'Your record "{title}" was published',
                "record": dict(record),
                "record_pid": {
                    "type": "URL",
                    "url": f"https://localhost/records/{recid}",
                },
                "template_name": "record-publication.jinja",
                "message": None,
                "plain_message": None,
                "html_message": None,
                "md_message": None,
            },
        }

        invenio_config_tuw.tasks.broadcast_notification.assert_called_once_with(
            expected_args
        )


def test_send_edit_notification_email(example_record, users, mocker):
    """Test if published record edits send a notification to the record owner."""
    recid = example_record.pid.pid_value
    old_check_permission = service.check_permission
    service.check_permission = (lambda *args, **kwargs: True).__get__(
        service, type(service)
    )

    def _update_draft(title, identity):
        """Update the draft with the given title."""
        draft = service.edit(identity, recid)
        new_data = draft.data.copy()
        new_data["metadata"]["title"] = title
        service.update_draft(identity, recid, new_data)

        uow = UnitOfWork()
        service.publish(identity, recid, uow=uow)
        uow.commit()
        return uow

    # the system identity *should not* trigger the notification
    uow = _update_draft("Different title", system_identity)
    assert not [
        op
        for op in uow._operations
        if getattr(op, "_celery_task", None) == send_metadata_edit_notification
    ]

    # the owner *should not* trigger the notification
    uow = _update_draft("Yet another title", Identity(users[0].id))
    assert not [
        op
        for op in uow._operations
        if getattr(op, "_celery_task", None) == send_metadata_edit_notification
    ]

    # another user *should* trigger the notification
    uow = _update_draft("Last new title", Identity(users[1].id))
    assert [
        op
        for op in uow._operations
        if getattr(op, "_celery_task", None) == send_metadata_edit_notification
    ]

    service.check_permission = old_check_permission


def test_record_metadata_current_user_as_creator(client_with_login):
    """Test the auto-generation of a "creator" entry for the current user."""
    user = client_with_login._user
    user.user_profile = {
        "tiss_id": 274424,
        "given_name": "Maximilian",
        "family_name": "Moser",
        "full_name": "Maximilian Moser",
        "affiliations": "tuwien.ac.at",
    }
    db.session.commit()

    expected_data = {
        "affiliations": [{"id": "04d836q62", "name": "TU Wien"}],
        "person_or_org": {
            "family_name": user.user_profile["family_name"],
            "given_name": user.user_profile["given_name"],
            "identifiers": [],
            "name": user.user_profile["full_name"],
            "type": "personal",
        },
        "role": "contactperson",
    }

    # `current_user` requires a little rain dance to work
    with client_with_login.application.test_request_context():
        g._login_user = user
        creator_data = current_user_as_creator()

    assert [expected_data] == creator_data


def test_register_smtp_error_handler(app):
    """Test the registration of the SMTP handler for error logs."""
    # the SMTP handler registration has a few configuration requirements
    old_debug, old_testing = app.debug, app.testing
    app.debug, app.testing = False, False
    app.config["MAIL_SERVER"] = "smtp.example.com"
    app.config["MAIL_ADMIN"] = "admin@example.com"

    # check if the log handler registration works
    old_num_handlers = len(app.logger.handlers)
    assert not any(isinstance(h, SMTPHandler) for h in app.logger.handlers)
    register_smtp_error_handler(app)
    new_num_handlers = len(app.logger.handlers)
    assert any(isinstance(h, SMTPHandler) for h in app.logger.handlers)
    assert new_num_handlers == old_num_handlers + 1

    # reset the previous debug/testing flags for the app
    app.debug, app.testing = old_debug, old_testing


def test_choose_files_location(app, files_locs, disabled_curations):
    """Test the selection of a storage location based on request context."""
    default_loc, alt_loc = files_locs
    assert default_loc.default
    assert not alt_loc.default

    with app.test_request_context():
        draft = service.create(system_identity, {})._obj
        assert draft.files.bucket.location is default_loc

    with app.test_request_context():
        app.config["CONFIG_TUW_STORAGE_LOCATION_FOR_IP"] = {
            request.remote_addr: alt_loc.name
        }
        draft = service.create(system_identity, {})._obj
        assert draft.files.bucket.location is alt_loc

    with app.test_request_context():
        app.config["CONFIG_TUW_STORAGE_LOCATION_FOR_IP"] = {
            request.remote_addr: alt_loc
        }
        draft = service.create(system_identity, {})._obj
        assert draft.files.bucket.location is alt_loc

    with app.test_request_context():
        app.config["CONFIG_TUW_STORAGE_LOCATION_FOR_IP"] = {request.remote_addr: None}
        draft = service.create(system_identity, {})._obj
        assert draft.files.bucket.location is default_loc
