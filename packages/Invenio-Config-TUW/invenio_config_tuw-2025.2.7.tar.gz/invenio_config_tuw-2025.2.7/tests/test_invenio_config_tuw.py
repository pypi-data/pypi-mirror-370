# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 - 2021 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

from flask import Flask

from invenio_config_tuw import InvenioConfigTUW


def test_version():
    """Test version import."""
    from invenio_config_tuw import __version__

    assert __version__


def test_init():
    """Test extension initialization."""
    app = Flask("testapp")
    app.config["SERVER_NAME"] = "localhost"
    InvenioConfigTUW(app)
    assert "invenio-config-tuw" in app.extensions

    app = Flask("testapp")
    app.config["SERVER_NAME"] = "localhost"
    ext = InvenioConfigTUW()
    assert "invenio-config-tuw" not in app.extensions
    ext.init_app(app)
    assert "invenio-config-tuw" in app.extensions
