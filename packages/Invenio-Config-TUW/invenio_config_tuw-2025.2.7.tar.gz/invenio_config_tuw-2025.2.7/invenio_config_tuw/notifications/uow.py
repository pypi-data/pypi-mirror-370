# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Custom ``TaskOp`` implementation."""


from invenio_records_resources.services.uow import TaskOp


class TUWTaskOp(TaskOp):
    """A celery task operation.

    Providing options for celery has been implemented via
    ``TaskOp.for_async_apply()`` in Invenio-Records-Resources v6.
    Once we get that version, we can remove this class here.
    """

    def __init__(self, celery_task, *args, countdown=None, **kwargs):
        """Initialize the task operation."""
        self._celery_task = celery_task
        self._args = args
        self._kwargs = kwargs
        self._cd = countdown

    def on_post_commit(self, uow):
        """Run the post task operation."""
        self._celery_task.apply_async(
            args=self._args, kwargs=self._kwargs, countdown=self._cd
        )
