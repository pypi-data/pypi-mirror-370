# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Permission customizations for use at TU Wien."""

from .policies import (
    TUWCommunityPermissionPolicy,
    TUWRecordPermissionPolicy,
    TUWRequestsPermissionPolicy,
)

__all__ = (
    "TUWCommunityPermissionPolicy",
    "TUWRecordPermissionPolicy",
    "TUWRequestsPermissionPolicy",
)
