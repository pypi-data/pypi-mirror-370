# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio-Config-TUW hacks and overrides to be applied on application startup.

This module provides a blueprint whose sole purpose is to execute some code exactly
once during application startup (via ``bp.record_once()``).
These functions will be executed after the Invenio modules' extensions have been
initialized, and thus we can rely on them being already available.
"""


from .misc import (
    customize_curation_request_type,
    override_search_drafts_options,
    register_menu_entries,
    register_smtp_error_handler,
)

__all__ = (
    "customize_curation_request_type",
    "override_search_drafts_options",
    "register_menu_entries",
    "register_smtp_error_handler",
)
