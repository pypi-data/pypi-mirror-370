# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Entity resolvers & proxies that are needed for TU Wien workflows."""

from invenio_access.permissions import system_identity
from invenio_records_resources.references.entity_resolvers import (
    EntityProxy,
    EntityResolver,
)


class SystemEntityProxy(EntityProxy):
    """Entity proxy for the fake "system" entity."""

    def get_needs(self):
        """Get the needs of the ``system_identity``."""
        return system_identity.needs

    def _resolve(self):
        """Create a user-like representation of the system.

        Since this will mostly be used in Jinja templates, it being a dictionary
        and not an actual object is fine.
        """
        return {
            "id": "system",
            "username": "system",
            "user_profile": {"full_name": "System"},
        }

    def pick_resolved_fields(self, identity, resolved_dict):
        """Select which fields to return when resolving the reference."""
        return resolved_dict


class SystemEntityResolver(EntityResolver):
    """Entity resolver for the system identity."""

    type_key = "users"

    def _reference_entity(self, entity):
        """Create a reference dictionary for the system."""
        return {"user": "system"}

    def _get_entity_proxy(self, ref_dict):
        """Get an entity proxy for the fake "system" entity."""
        return SystemEntityProxy(None, ref_dict)

    def matches_entity(self, entity):
        """Since the system is not an actual entity, it can never match anything."""
        return False

    def matches_reference_dict(self, ref_dict):
        """Only matches the dictionary ``{"user": "system"}``."""
        return ref_dict == {"user": "system"}
