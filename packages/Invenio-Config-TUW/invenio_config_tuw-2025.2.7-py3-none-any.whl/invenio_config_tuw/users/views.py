# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Custom view functions for TU Wien."""

from flask import Blueprint, current_app, flash, render_template, request
from flask_login import current_user, login_required
from invenio_app_rdm.theme.views import handle_notifications_form
from invenio_db import db
from invenio_i18n import lazy_gettext as _

from .preferences import CurationPreferencesForm, TUWNotificationsForm

user_settings_blueprint = Blueprint(
    "invenio_config_tuw_settings",
    __name__,
    url_prefix="/account/settings/curation",
    template_folder="templates",
)


@user_settings_blueprint.route("/", methods=["GET", "POST"])
@login_required
def curation_settings_view():
    """Page for the curation consent setting in user profiles."""
    preferences_curation_form = CurationPreferencesForm(
        formdata=None, obj=current_user, prefix="preferences-curation"
    )

    form_name = request.form.get("submit", None)
    form = preferences_curation_form if form_name else None

    if form:
        form.process(formdata=request.form)
        if form.validate_on_submit():
            form.populate_obj(current_user)
            db.session.add(current_user)
            current_app.extensions["security"].datastore.commit()
            flash(("Curation settings were updated."), category="success")

    return render_template(
        ["invenio_theme_tuw/settings/curation.html", "curation_settings.html"],
        preferences_curation_form=preferences_curation_form,
    )


def notification_settings():
    """View for notification settings."""
    preferences_notifications_form = TUWNotificationsForm(
        formdata=None, obj=current_user, prefix="preferences-notifications"
    )

    # Pick form
    form_name = request.form.get("submit", None)
    form = preferences_notifications_form if form_name else None

    # Process form
    if form:
        form.process(formdata=request.form)
        if form.validate_on_submit():
            handle_notifications_form(form)
            flash(_("Notification preferences were updated."), category="success")

    return render_template(
        [
            "invenio_theme_tuw/notifications_settings.html",
            "notifications_settings.html",
        ],
        notifications_form=preferences_notifications_form,
    )
