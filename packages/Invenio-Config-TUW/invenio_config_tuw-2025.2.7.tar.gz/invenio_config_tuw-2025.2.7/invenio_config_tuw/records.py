# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Overrides for the default records & drafts classes."""


from flask import request
from invenio_rdm_records.records.api import RDMDraft, RDMFileDraft, get_files_quota
from invenio_records_resources.records.systemfields.files import FilesField

from .proxies import current_config_tuw


def choose_files_location(record=None):
    """Choose the bucket's default location based on the request's IP address.

    This will be executed as part of the ``post_create()`` hook of the ``FilesField``,
    which runs after a draft has been created (i.e. before any opportunity to upload
    files).
    """
    bucket_args = get_files_quota(record)

    location = None
    if request:
        location = current_config_tuw.default_location_for_ip(request.remote_addr)

    if location is not None:
        bucket_args["location"] = location.name

    return bucket_args


class TUWRDMDraft(RDMDraft):
    """Override for the default draft class, for storing files in another location."""

    # The values here are copied from the super class, except for the bucket args
    files = FilesField(
        store=False,
        dump=False,
        file_cls=RDMFileDraft,
        # Don't delete, we'll manage in the service
        delete=False,
        bucket_args=choose_files_location,
    )
