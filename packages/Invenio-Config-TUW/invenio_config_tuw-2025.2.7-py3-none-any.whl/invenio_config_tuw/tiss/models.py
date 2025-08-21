# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Data classes for representing information from TISS."""


from dataclasses import dataclass
from typing import List, Optional


@dataclass
class OrgUnit:
    """An organizational unit at TU Wien."""

    tiss_id: int
    code: str
    name_en: str
    name_de: str
    employees: List["Employee"]

    @classmethod
    def from_dict(cls, data: dict) -> "OrgUnit":
        """Parse the organizational unit from the given dictionary."""
        return cls(
            tiss_id=data["tiss_id"],
            code=data["code"],
            name_de=data.get("name_de", ""),
            name_en=data.get("name_en", ""),
            employees=[Employee.from_dict(emp) for emp in data.get("employees")],
        )

    def __hash__(self):
        """Use the TISS ID for hashing."""
        return hash(self.tiss_id)


@dataclass
class Employee:
    """An employee at TU Wien."""

    tiss_id: int
    orcid: Optional[str]
    first_name: str
    last_name: str
    pseudoperson: bool
    titles_pre: str
    titles_post: str

    @property
    def full_name(self):
        """Create the full name in the same style as InvenioRDM does."""
        return f"{self.last_name}, {self.first_name}"

    @classmethod
    def from_dict(cls, data: dict) -> "Employee":
        """Parse the employee from the given dictionary."""
        return cls(
            tiss_id=data["tiss_id"],
            orcid=data.get("orcid", None),
            first_name=data["first_name"],
            last_name=data["last_name"],
            pseudoperson=data.get("pseudoperson", False),
            titles_pre=data.get("preceding_titles", ""),
            titles_post=data.get("postpositioned_titles", ""),
        )

    def to_name_entry(self):
        """Massage the employee into the shape of a name entry."""
        ids = []
        if self.orcid:
            ids.append({"scheme": "orcid", "identifier": self.orcid})

        return {
            "id": self.orcid or str(self.tiss_id),
            "given_name": self.first_name,
            "family_name": self.last_name,
            "identifiers": ids,
            "affiliations": [{"id": "04d836q62", "name": "TU Wien"}],
        }

    def __hash__(self):
        """Use the TISS ID for hashing."""
        return hash(self.tiss_id)
