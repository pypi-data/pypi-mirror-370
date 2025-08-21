# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Customizations for the user model at TU Wien.

This includes the curation consent for record metadata as extension for the user's
preferences, and a custom registration form which requires the terms of use to be
accepted.
"""

from .preferences import CurationPreferencesForm, CurationPreferencesProxy
from .registration import tuw_registration_form
from .schemas import TUWUserPreferencesSchema, TUWUserProfileSchema, TUWUserSchema
from .utils import (
    check_user_email_for_tuwien,
    current_user_as_creator,
    get_user_by_username,
)
from .views import user_settings_blueprint

__all__ = (
    "CurationPreferencesForm",
    "CurationPreferencesProxy",
    "TUWUserPreferencesSchema",
    "TUWUserProfileSchema",
    "TUWUserSchema",
    "check_user_email_for_tuwien",
    "current_user_as_creator",
    "get_user_by_username",
    "tuw_registration_form",
    "user_settings_blueprint",
)
