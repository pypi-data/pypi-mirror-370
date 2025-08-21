# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Functions for fetching information from TISS."""

from typing import Optional, Set, Tuple

import requests

from .models import Employee, OrgUnit


def _get_org_unit_dict(code: str) -> dict:
    """Fetch the data about the org unit from TISS."""
    response = requests.get(
        f"https://tiss.tuwien.ac.at/api/orgunit/v23/code/{code}?persons=true"
    )
    # NOTE: some org units don't seem to have an OID
    #       (e.g. "E366t1 - Institutsbibliothek"),
    #       it seems to be safer to go through the 'code'
    assert response.status_code == 200

    org_unit = response.json()
    return org_unit


def _fetch_tiss_data(
    org_unit: dict,
    org_units: Optional[Set[OrgUnit]] = None,
    employees: Optional[Set[Employee]] = None,
) -> Tuple[Set[OrgUnit], Set[Employee]]:
    """Fetch and parse the info about org units and employees from TISS."""
    org_units = org_units if org_units is not None else set()
    employees = employees if employees is not None else set()

    unit = OrgUnit.from_dict(org_unit)
    org_units.add(unit)
    employees.update(set(unit.employees))

    child_units = org_unit.get("children", org_unit.get("child_orgs_refs", []))
    for child_unit in child_units:
        child_unit_dict = _get_org_unit_dict(child_unit["code"])
        _fetch_tiss_data(child_unit_dict, org_units, employees)

    return org_units, employees


def fetch_tiss_data() -> Tuple[Set[OrgUnit], Set[Employee]]:
    """Fetch and parse the info about all org units and their employees from TISS."""
    return _fetch_tiss_data(_get_org_unit_dict("E000"))
