# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for the upstream behavior, to check if our expectations still hold."""

from invenio_rdm_records.records.api import RDMDraft, get_files_quota

from invenio_config_tuw.records import TUWRDMDraft


def test_rdmdraft_file_property_override_expectations():
    """Test if our assumptions about upstream behavior for our overrides still hold."""

    assert RDMDraft.files._store is TUWRDMDraft.files._store
    assert RDMDraft.files._dump is TUWRDMDraft.files._dump
    assert RDMDraft.files._file_cls is TUWRDMDraft.files._file_cls
    assert RDMDraft.files._delete is TUWRDMDraft.files._delete
    assert RDMDraft.files._bucket_args is get_files_quota

    upstream_vals = vars(RDMDraft.files)
    upstream_vals.pop("_bucket_args")
    overridden_vals = vars(TUWRDMDraft.files)
    overridden_vals.pop("_bucket_args")
    assert upstream_vals == overridden_vals
