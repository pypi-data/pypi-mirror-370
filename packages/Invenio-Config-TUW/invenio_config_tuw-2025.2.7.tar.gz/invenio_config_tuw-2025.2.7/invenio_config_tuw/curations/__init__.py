# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Utilities dedicated to the curation workflow based on ``Invenio-Curations``."""

from .requests import (
    TUWCurationRequest,
    TUWCurationRequestReviewNotificationBuilder,
    TUWCurationRequestUploaderResubmitNotificationBuilder,
)

__all__ = (
    "TUWCurationRequest",
    "TUWCurationRequestReviewNotificationBuilder",
    "TUWCurationRequestUploaderResubmitNotificationBuilder",
)
