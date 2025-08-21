# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Utilities for connecting InvenioRDM to DAMAP, tailored to the environment of TU Wien."""

from flask_principal import AnonymousIdentity


def tuw_id_generator(identity) -> dict[str, str]:
    """
    Generates user identities mapped to namespace names specific to the TUW environment.

    Parameters:
        identity: The user identity.

    Returns:
        dict: Namespaces with the user identifiers.
    """
    identifiers = {}
    if identity and not isinstance(identity, AnonymousIdentity):
        u = identity.user

        if u.email.endswith("tuwien.ac.at"):
            tiss_id = u.user_profile.get("tiss_id")

            if tiss_id:
                identifiers["tiss_id"] = str(tiss_id)

    return identifiers
