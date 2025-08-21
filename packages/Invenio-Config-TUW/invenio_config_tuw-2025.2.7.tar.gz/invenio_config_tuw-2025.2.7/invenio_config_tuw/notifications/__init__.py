# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""General customized notifications infrastructure."""

from .backends import TUWEmailNotificationBackend
from .builders import GroupNotificationBuilder, UserNotificationBuilder
from .entity_resolvers import SystemEntityProxy, SystemEntityResolver
from .uow import TUWTaskOp

__all__ = (
    "GroupNotificationBuilder",
    "SystemEntityProxy",
    "SystemEntityResolver",
    "TUWEmailNotificationBackend",
    "TUWTaskOp",
    "UserNotificationBuilder",
)
