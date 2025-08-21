# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Utilities for integrating InvenioRDM with TISS."""

from .models import Employee, OrgUnit
from .utils import fetch_tiss_data

__all__ = (
    "Employee",
    "OrgUnit",
    "fetch_tiss_data",
)
