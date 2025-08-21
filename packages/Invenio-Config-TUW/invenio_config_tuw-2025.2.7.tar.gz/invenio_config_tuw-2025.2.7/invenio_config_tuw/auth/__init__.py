# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 - 2021 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module containing some customizations and configuration for TU Wien."""

from .handlers import authorized_signup_handler, info_handler
from .settings import TUWSSOSettingsHelper

__all__ = (
    "authorized_signup_handler",
    "info_handler",
    "TUWSSOSettingsHelper",
)
