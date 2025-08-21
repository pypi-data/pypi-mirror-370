# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Local proxies for Invenio-Config-TUW objects."""

from flask import current_app
from werkzeug.local import LocalProxy

current_config_tuw = LocalProxy(lambda: current_app.extensions["invenio-config-tuw"])
