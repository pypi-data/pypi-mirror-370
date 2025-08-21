# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2025 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""User-related utility functions."""

from typing import Dict, Tuple

from flask_security import current_user
from invenio_accounts.models import User


def get_user_by_username(username):
    """Get the user identified by the username."""
    return User.query.filter(User.username == username).one_or_none()


def check_user_email_for_tuwien(user):
    """Check if the user's email belongs to TU Wien (but not as a student)."""
    domain = user.email.split("@")[-1]
    return domain.endswith("tuwien.ac.at") and "student" not in domain


def _names_from_user_profile(profile: Dict) -> Tuple[str, str, str]:
    """Get the ``given_name``, ``family_name`` and ``full_name`` of the user."""
    given_name, family_name = profile.get("given_name"), profile.get("family_name")
    full_name = profile.get("full_name")

    if given_name and family_name:
        full_name = full_name or f"{family_name}, {given_name}"

    elif full_name:
        if ", " in full_name:
            # in case there's a comma in the name, we assume it's "FAMILY, GIVEN"
            given_name, family_name = full_name.split(", ", 1)

        else:
            # otherwise, we assume it has the shape "GIVEN, FAMILY"
            name_parts = full_name.split()

            given_name = " ".join(name_parts[:-1])
            family_name = name_parts[-1]
            full_name = f"{family_name}, {given_name}"

    return (given_name, family_name, full_name)


def current_user_as_creator():
    """Use the currently logged-in user to populate a creator in the deposit form."""
    profile = current_user.user_profile or {}
    given_name, family_name, full_name = _names_from_user_profile(profile)

    # if we have no clue about the name, we skip the creator
    if not given_name and not family_name and not full_name:
        return []

    # TODO parse affiliation from user profile
    # TODO add identifiers (e.g. ORCID from TISS, if available)
    creator = {
        "affiliations": [{"id": "04d836q62", "name": "TU Wien"}],
        "person_or_org": {
            "family_name": family_name,
            "given_name": given_name,
            "identifiers": [],
            "name": full_name,
            "type": "personal",
        },
        "role": "contactperson",
    }

    return [creator]
