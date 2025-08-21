# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2025 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio-Config-TUW hacks and overrides to be applied on application startup.

This module provides a blueprint whose sole purpose is to execute some code exactly
once during application startup (via ``bp.record_once()``).
These functions will be executed after the Invenio modules' extensions have been
initialized, and thus we can rely on them being already available.
"""

from logging import ERROR
from logging.handlers import SMTPHandler

from invenio_administration.permissions import administration_permission
from invenio_rdm_records.services.search_params import SharedOrMyDraftsParam
from invenio_requests.proxies import current_request_type_registry
from invenio_search.engine import dsl

from ..curations import TUWCurationRequest
from ..logs import DetailedFormatter


class TUWSharedOrMyDraftsParm(SharedOrMyDraftsParam):
    """Variant of the "shared_with_me" interpreter that gives more results to admins."""

    def _generate_shared_with_me_query(self, identity):
        """Generate the "shared_with_me" query.

        For admins, this matches all records that aren't theirs.
        For normal users, this typically involves records with access grants.
        """
        if administration_permission.allows(identity):
            return dsl.Q(
                "query_string", query=f"NOT parent.access.owned_by.user:{identity.id}"
            )

        return super()._generate_shared_with_me_query(identity)


def register_smtp_error_handler(app):
    """Register email error handler to the application."""
    handler_name = "invenio-config-tuw-smtp-error-handler"

    # check reasons to skip handler registration
    error_mail_disabled = app.config.get("CONFIG_TUW_DISABLE_ERROR_MAILS", False)
    if app.debug or app.testing or error_mail_disabled:
        # email error handling should occur only in production mode, if not disabled
        return

    elif any(handler.name == handler_name for handler in app.logger.handlers):
        # we don't want to register duplicate handlers
        return

    elif "invenio-mail" not in app.extensions:
        app.logger.warning(
            (
                "The Invenio-Mail extension is not loaded! "
                "Skipping registration of SMTP error handler."
            )
        )
        return

    # check if mail server and admin email(s) are present in the config
    # if not raise a warning
    if app.config.get("MAIL_SERVER") and app.config.get("MAIL_ADMIN"):
        # configure auth
        username = app.config.get("MAIL_USERNAME")
        password = app.config.get("MAIL_PASSWORD")
        auth = (username, password) if username and password else None

        # configure TLS
        secure = None
        if app.config.get("MAIL_USE_TLS"):
            secure = ()

        # initialize SMTP Handler
        mail_handler = SMTPHandler(
            mailhost=(app.config["MAIL_SERVER"], app.config.get("MAIL_PORT", 25)),
            fromaddr=app.config["SECURITY_EMAIL_SENDER"],
            toaddrs=app.config["MAIL_ADMIN"],
            subject=app.config["THEME_SITENAME"] + " - Failure",
            credentials=auth,
            secure=secure,
        )
        mail_handler.name = handler_name
        mail_handler.setLevel(ERROR)
        mail_handler.setFormatter(DetailedFormatter())

        # attach to the application
        app.logger.addHandler(mail_handler)

    else:
        app.logger.warning(
            "Mail configuration missing: SMTP error handler not registered!"
        )


def override_search_drafts_options(app):
    """Override the "search drafts" options to show all accessible drafts."""
    # doing this via config is (currently) not possible, as the `search_drafts`
    # property can't be overridden with a config item (unlike `search`, above it)
    # cf. https://github.com/inveniosoftware/invenio-rdm-records/blob/maint-10.x/invenio_rdm_records/services/config.py#L327-L332
    try:
        service = app.extensions["invenio-rdm-records"].records_service
        service.config.search_drafts.params_interpreters_cls.remove(
            SharedOrMyDraftsParam
        )
        service.config.search_drafts.params_interpreters_cls.append(
            TUWSharedOrMyDraftsParm
        )
    except ValueError:
        pass


def register_menu_entries(app):
    """Register the curation setting endpoint in Flask-Menu."""
    menu = app.extensions["menu"].root()
    menu.submenu("settings.curation").register(
        "invenio_config_tuw_settings.curation_settings_view",
        '<i class="file icon"></i> Curation',
        order=1,
    )


def customize_curation_request_type(app):
    """Override the rdm-curations request type with our own version."""
    current_request_type_registry.register_type(TUWCurationRequest(), force=True)
