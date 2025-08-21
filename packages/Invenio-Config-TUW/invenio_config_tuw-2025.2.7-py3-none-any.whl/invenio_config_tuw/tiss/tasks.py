# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2025 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""TISS-related celery tasks running in the background."""

import copy
from collections import defaultdict
from difflib import SequenceMatcher
from typing import Dict, List, Optional

import requests
from celery import shared_task
from celery.schedules import crontab
from flask import current_app
from invenio_access.permissions import system_identity
from invenio_db import db
from invenio_records_resources.services.uow import UnitOfWork
from invenio_vocabularies.contrib.names import NamesService
from invenio_vocabularies.contrib.names.api import Name

from . import Employee, fetch_tiss_data


def get_tuw_ror_aliases() -> List[str]:
    """Fetch the aliases of TU Wien known to ROR."""
    try:
        response = requests.get("https://api.ror.org/organizations/04d836q62")
        if response.ok:
            tuw_ror = response.json()

            # aliases, acronyms, and translated names are now part of the "names" field
            tuw_ror_names = [n["value"] for n in tuw_ror["names"]]
            return tuw_ror_names

    except Exception as e:
        current_app.logger.warn(
            f"Error while fetching TU Wien information from ROR: {e}"
        )

    return [
        "TU Wien",
        "TUW",
        "Technische Universität Wien",
        "Vienna University of Technology",
    ]


def _find_name_entry_for_orcid(orcid: str, names: List[Name]) -> Optional[Name]:
    """Find the name entry with the given ORCID."""
    if not orcid:
        return None

    for name in names:
        if {"scheme": "orcid", "identifier": orcid} in name.get("identifiers", []):
            return name

    return None


def _update_name_data(
    name: dict, employee: Employee, tuw_aliases: Optional[List[str]] = None
) -> dict:
    """Update the given name entry data with the information from the employee."""
    tuw_aliases = tuw_aliases or ["TU Wien"]
    name = copy.deepcopy(name)
    name["given_name"] = employee.first_name
    name["family_name"] = employee.last_name
    if "name" in name:
        name["name"] = f"{employee.last_name}, {employee.first_name}"

    # normalize & deduplicate affilations, and make sure that TU Wien is one of them
    # NOTE: sorting is done to remove indeterminism and prevent unnecessary updates
    affiliations = {
        aff["name"] for aff in name["affiliations"] if aff["name"] not in tuw_aliases
    }
    affiliations.add("TU Wien")
    name["affiliations"] = sorted(
        [{"name": aff} for aff in affiliations], key=lambda aff: aff["name"]
    )

    # similar to above, add the ORCID mentioned in TISS and deduplicate
    identifiers = {(id_["scheme"], id_["identifier"]) for id_ in name["identifiers"]}
    if employee.orcid:
        identifiers.add(("orcid", employee.orcid))

    name["identifiers"] = sorted(
        [{"scheme": scheme, "identifier": id_} for scheme, id_ in identifiers],
        key=lambda id_: f'{id_["scheme"]}:{id_["identifier"]}',
    )

    return name


def _calc_name_distance(
    employee: Optional[Employee], name_voc: Optional[Name]
) -> float:
    """Calculate the distance between the employee name and the vocabulary entry."""
    if employee is None or name_voc is None:
        return 0

    fn, ln = name_voc.get("given_name", ""), name_voc.get("family_name", "")
    fn_dist = SequenceMatcher(a=fn, b=employee.first_name).ratio()
    ln_dist = SequenceMatcher(a=ln, b=employee.last_name).ratio()
    return fn_dist + ln_dist


def _massage_new_name_data(old_name_record: Name, new_name_data: dict) -> dict:
    """Update the old name record's data with new information.

    Also removes some fields that are known to not play nice with serialization,
    that we want to avoid getting into the `json` database column.
    Note: It's very unlikely that all these fields are present.
    """
    name_data = {**old_name_record}
    name_data.update(new_name_data)
    name_data.pop("$schema", None)
    name_data.pop("id", None)
    name_data.pop("pid", None)
    name_data.pop("created", None)
    name_data.pop("updated", None)
    name_data.pop("links", None)
    name_data.pop("revision_id", None)
    return name_data


def _update_existing_name_entry(
    name_entry: Name,
    employee: Employee,
    tuw_ror_aliases: List[str],
    names_service: NamesService,
    uow: UnitOfWork,
) -> bool:
    """Update the name entry with the new employee data."""
    name_voc_id = name_entry.pid.pid_value
    new_name = f"{employee.last_name}, {employee.first_name}"
    old_name = name_entry.get(
        "name",
        f"{name_entry.get('family_name')}, {name_entry.get('given_name')}",
    )

    # if we found a match via ORCID, we update it according to the TISS data
    name = names_service.read(identity=system_identity, id_=name_voc_id)
    new_name_data = _update_name_data(name.data, employee, tuw_ror_aliases)

    # only update the entry if it actually differs somehow; pop fields
    # that aren't expected by the JSON/marshmallow schemas
    if name.data != new_name_data:
        names_service.update(
            identity=system_identity,
            id_=name_voc_id,
            data=_massage_new_name_data(name._record, new_name_data),
            uow=uow,
        )
        current_app.logger.info(
            f"TISS sync: updated name '{name_voc_id}' from "
            f"'{old_name}' to '{new_name}'"
        )
        return True

    return False


def _collect_employees_per_orcid(
    employees: List[Employee],
) -> Dict[str, List[Employee]]:
    """Collect employees by ORCID.

    This is useful in case several employees have the same ORCID listed on their
    TISS profile.
    We've had such cases in the past, e.g. when secretaries perform work for researchers
    and put in their ORCID to simplify some workflows.
    """
    orcid_employees = defaultdict(list)
    for employee in employees:
        if not employee.pseudoperson and employee.orcid:
            orcid_employees[employee.orcid].append(employee)

    return orcid_employees


def _get_employee_for_name_entry(
    matching_name_entry: Name, employees: List[Employee]
) -> Optional[Employee]:
    """Get the employee that matches the given name entry best."""
    employee = None
    if len(employees) == 1:
        (employee,) = employees
    elif len(employees) > 1:
        # if we several TISS profiles with the same ORCID, we use the one
        # with the closest match in name in our names vocabulary
        employee = sorted(
            employees,
            key=lambda e: _calc_name_distance(employee, matching_name_entry),
        )[-1]

    return employee


@shared_task(ignore_result=True)
def sync_names_from_tiss(employees: Optional[List[Employee]] = None) -> dict:
    """Look up TU Wien employees via TISS and update the names vocabulary."""
    results = {"created": 0, "updated": 0, "failed": 0}
    tuw_ror_aliases = get_tuw_ror_aliases()
    svc = current_app.extensions["invenio-vocabularies"].names_service

    all_names = [
        svc.record_cls.get_record(model.id)
        for model in svc.record_cls.model_cls.query.all()
        if not model.is_deleted and model.data
    ]
    if not employees:
        _, employees = fetch_tiss_data()

    with UnitOfWork(db.session) as uow:
        for orcid, employees in _collect_employees_per_orcid(employees).items():
            matching_name_entry = _find_name_entry_for_orcid(orcid, all_names)
            employee = _get_employee_for_name_entry(matching_name_entry, employees)
            if employee is None:
                continue

            try:
                if matching_name_entry and _update_existing_name_entry(
                    matching_name_entry, employee, tuw_ror_aliases, svc, uow
                ):
                    results["updated"] += 1

                elif not matching_name_entry:
                    # if we couldn't find a match via ORCID, that's a new entry
                    svc.create(
                        identity=system_identity, data=employee.to_name_entry(), uow=uow
                    )
                    results["created"] += 1

            except Exception as e:
                results["failed"] += 1
                current_app.logger.warn(
                    f"TISS sync: failed for '{employee}', with error: {e}"
                )

        uow.commit()

    return results


CELERY_BEAT_SCHEDULE = {
    "tiss-name-sync": {
        "task": "invenio_config_tuw.tiss.tasks.sync_names_from_tiss",
        "schedule": crontab(minute=0, hour=3, day_of_week="sat"),
    },
}
