# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2025 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio-Config-TUW hacks and overrides to be applied on application startup.

This module provides a blueprint whose sole purpose is to execute some code exactly
once during application startup (via ``bp.record_once()``).
These functions will be executed after the Invenio modules' extensions have been
initialized, and thus we can rely on them being already available.
"""

from functools import partial

from flask import current_app, request
from flask.config import Config
from werkzeug.local import LocalProxy

from ..auth.settings import TUWSSOSettingsHelper


class TUWConfig(Config):
    """Override for the Flask config that evaluates the SITE_{API,UI}_URL proxies."""

    @classmethod
    def from_flask_config(cls, config):
        """Create a clone of the given config."""
        if isinstance(config, TUWConfig):
            return config

        return cls(config.root_path, config)

    def __getitem__(self, key):
        """Return config[key], or str(config[key]) if key is 'SITE_{UI,API}_URL'."""
        value = super().__getitem__(key)

        # give special treatment to the URL configuration items:
        # enforce their evaluation as strings
        if key in ("SITE_UI_URL", "SITE_API_URL"):
            value = str(value)

        return value


def _get_config(app, key, prefixes=None, default=None):
    """Get the config item, preferably with the longest matching prefix."""
    prefixes = [p for p in (prefixes or []) if p is not None]
    for prefix in sorted(prefixes, key=len, reverse=True):
        prefixed_key = prefix + key
        if prefixed_key in app.config:
            return app.config[prefixed_key]

    if key in app.config:
        return app.config[key]
    else:
        return default


def _make_site_url(suffix):
    """Create a URL with the given suffix from contextual information.

    If available, use the request's Host URL as base for the URL.
    Otherwise, look at the configuration value for `THEME_SITEURL`.
    """
    url = None

    try:
        if request and request.host_url and request.host_url.startswith("http"):
            url = request.host_url

    except RuntimeError:
        # this will be hit if we're working outside of a request context
        pass

    # use THEME_SITEURL or relative URLs as fallback
    if url is None:
        url = current_app.config.get("THEME_SITEURL", "")

    # do a little dance to make sure there's no extra slashes
    return (url.removesuffix("/") + "/" + suffix.removeprefix("/")).removesuffix("/")


def assemble_db_uri_from_parts(app):
    """Assemble the DB connection string from its parts."""
    prefixes = ["SQLALCHEMY_"]
    db_uri = _get_config(app, "DATABASE_URI", prefixes)

    db_driver = _get_config(
        app, "DATABASE_DRIVER", prefixes, default="postgresql+psycopg2"
    )
    db_user = _get_config(app, "DATABASE_USER", prefixes)
    db_pw = _get_config(app, "DATABASE_PASSWORD", prefixes)
    db_host = _get_config(app, "DATABASE_HOST", prefixes, default="localhost")
    db_db = _get_config(app, "DATABASE_DB", prefixes, default=db_user)

    if all((v is not None for v in [db_driver, db_user, db_pw, db_host, db_db])):
        db_uri = f"{db_driver}://{db_user}:{db_pw}@{db_host}/{db_db}"

    if db_uri is not None:
        app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    else:
        app.logger.warn("Warning: No DB conection string set")


def assemble_broker_uri_from_parts(app):
    """Assemble the broker URI from its parts."""
    rabbitmq_user = _get_config(app, "RABBITMQ_USER")
    rabbitmq_password = _get_config(app, "RABBITMQ_PASSWORD")
    broker_url = _get_config(app, "BROKER_URL")
    broker_host = _get_config(app, "BROKER_HOST", default="localhost")
    broker_protocol = _get_config(app, "BROKER_PROTOCOL", default="amqp")
    broker_user = _get_config(app, "BROKER_USER", default=rabbitmq_user)
    broker_password = _get_config(app, "BROKER_PASSWORD", default=rabbitmq_password)

    if None not in [broker_protocol, broker_user, broker_password, broker_host]:
        broker_url = (
            f"{broker_protocol}://{broker_user}:{broker_password}@{broker_host}/"
        )
    elif broker_url is None:
        broker_url = "amqp://guest:guest@localhost:5672/"

    # celery doesn't like having BROKER_HOST *and* the other values set
    app.config.pop("BROKER_HOST", None)
    app.config["BROKER_URL"] = broker_url
    app.config["CELERY_BROKER_URL"] = broker_url


def assemble_cache_uri_from_parts(app):
    """Assemble the various cache URIs from their parts."""
    redis_user = _get_config(app, "CACHE_REDIS_USER")
    redis_password = _get_config(app, "CACHE_REDIS_PASSWORD")
    redis_host = _get_config(app, "CACHE_REDIS_HOST", default="localhost")
    redis_port = _get_config(app, "CACHE_REDIS_PORT", default="6379")
    redis_protocol = _get_config(app, "CACHE_REDIS_PROTOCOL", default="redis")
    redis_db = _get_config(app, "CACHE_REDIS_DB", default="0")

    # set the redis database names that should be used for various parts
    account_sessions_db = _get_config(app, "ACCOUNTS_SESSION_REDIS_DB", default="1")
    celery_results_db = _get_config(app, "CELERY_RESULT_BACKEND_DB", default="2")
    ratelimit_storage_db = _get_config(app, "RATELIMIT_STORAGE_DB", default="3")
    communities_identities_db = _get_config(
        app, "COMMUNITIES_IDENTITIES_STORAGE_DB", default="4"
    )

    if redis_user is None and redis_password is not None:
        # the default user in redis is named 'default'
        redis_user = "default"

    def _make_redis_url(db):
        """Create redis URL from the given DB name."""
        if redis_password is not None:
            return f"{redis_protocol}://{redis_user}:{redis_password}@{redis_host}:{redis_port}/{db}"
        else:
            return f"{redis_protocol}://{redis_host}:{redis_port}/{db}"

    cache_redis_url = _make_redis_url(redis_db)
    accounts_session_redis_url = _make_redis_url(account_sessions_db)
    celery_results_backend_url = _make_redis_url(celery_results_db)
    ratelimit_storage_url = _make_redis_url(ratelimit_storage_db)
    communities_identities_cache_url = _make_redis_url(communities_identities_db)

    app.config["CACHE_TYPE"] = "redis"
    app.config["CACHE_REDIS_URL"] = cache_redis_url
    app.config["IIIF_CACHE_REDIS_URL"] = cache_redis_url
    app.config["ACCOUNTS_SESSION_REDIS_URL"] = accounts_session_redis_url
    app.config["CELERY_RESULT_BACKEND"] = celery_results_backend_url
    app.config["RATELIMIT_STORAGE_URL"] = ratelimit_storage_url
    app.config["RATELIMIT_STORAGE_URI"] = ratelimit_storage_url
    app.config["COMMUNITIES_IDENTITIES_CACHE_REDIS_URL"] = (
        communities_identities_cache_url
    )


def assemble_site_urls_from_parts(app):
    """Create `LocalProxy` objects for the `SITE_{API,UI}_URL` items."""
    server_name = _get_config(app, "SERVER_NAME")
    preferred_scheme = _get_config(app, "PREFERRED_URL_SCHEME", "https")
    theme_siteurl = _get_config(app, "THEME_SITEURL")
    trusted_hosts = _get_config(app, "TRUSTED_HOSTS")

    # note: the preferred way is setting the `SERVER_NAME` configuration
    if server_name:
        theme_siteurl = theme_siteurl or f"{preferred_scheme}://{server_name}"

    elif theme_siteurl:
        server_name = (
            theme_siteurl.removeprefix("http://").removeprefix("https://").split("/")[0]
        )
        app.logger.info(
            f"No SERVER_NAME set, calculated value '{server_name}' from THEME_SITEURL: '{theme_siteurl}'"
        )

    else:
        raise RuntimeError(
            "Neither SERVER_NAME or THEME_SITEURL are configured. Aborting."
        )

    # having the TRUSTED_HOSTS specified as space-separated values makes it
    # easier to use in nginx
    if isinstance(trusted_hosts, str):
        trusted_hosts = trusted_hosts.split()

    # note: 'invenio-cli run' likes to populate INVENIO_SITE_{UI,API}_URL...
    app.config["SITE_UI_URL"] = LocalProxy(partial(_make_site_url, ""))
    app.config["SITE_API_URL"] = LocalProxy(partial(_make_site_url, "/api"))
    app.config["THEME_SITEURL"] = theme_siteurl
    app.config["OAISERVER_ID_PREFIX"] = server_name
    app.config["TRUSTED_HOSTS"] = trusted_hosts


def assemble_keycloak_config_from_parts(app):
    """Assemble the Keycloak remote app from its parts."""
    consumer_key = app.config.get("OAUTHCLIENT_KEYCLOAK_CONSUMER_KEY")
    consumer_secret = app.config.get("OAUTHCLIENT_KEYCLOAK_CONSUMER_SECRET")

    if consumer_key is not None and consumer_secret is not None:
        app_credentials = {
            "consumer_key": consumer_key,
            "consumer_secret": consumer_secret,
        }
        app.config["OAUTHCLIENT_KEYCLOAK_APP_CREDENTIALS"] = app_credentials
        app.config["KEYCLOAK_APP_CREDENTIALS"] = app_credentials

    base_url = app.config.get("OAUTHCLIENT_KEYCLOAK_BASE_URL")
    realm = app.config.get("OAUTHCLIENT_KEYCLOAK_REALM")
    app_title = app.config.get("OAUTHCLIENT_KEYCLOAK_APP_TITLE")
    app_description = app.config.get("OAUTHCLIENT_KEYCLOAK_APP_DESCRIPTION")

    if base_url is not None and realm is not None:
        helper = TUWSSOSettingsHelper(
            title=app_title or "TU Wien SSO",
            description=app_description or "TU Wien Single Sign-On",
            base_url=base_url,
            realm=realm,
        )
        remote_app = helper.remote_app

        if app_title is not None:
            remote_app["title"] = app_title

        # ensure that this remote app is listed as "keycloak" in the app config
        remote_apps = {
            **(app.config.get("OAUTHCLIENT_REMOTE_APPS") or {}),
            "keycloak": remote_app,
        }
        app.config["OAUTHCLIENT_KEYCLOAK_REALM_URL"] = helper.realm_url
        app.config["OAUTHCLIENT_KEYCLOAK_USER_INFO_URL"] = helper.user_info_url
        app.config["OAUTHCLIENT_REMOTE_APPS"] = remote_apps


def populate_unset_salt_values(app):
    """Populate the salt values if they're not set yet."""
    secret_key = app.config.get("SECRET_KEY", None)
    app.config.setdefault("CSRF_SECRET_SALT", secret_key)
    app.config.setdefault("SECURITY_RESET_SALT", secret_key)
    app.config.setdefault("SECURITY_LOGIN_SALT", secret_key)
    app.config.setdefault("SECURITY_PASSWORD_SALT", secret_key)
    app.config.setdefault("SECURITY_CONFIRM_SALT", secret_key)
    app.config.setdefault("SECURITY_CHANGE_SALT", secret_key)
    app.config.setdefault("SECURITY_REMEMBER_SALT", secret_key)


def assemble_and_populate_config(app):
    """Assemble some config from their parts and populate some unset config."""
    assemble_db_uri_from_parts(app)
    assemble_broker_uri_from_parts(app)
    assemble_cache_uri_from_parts(app)
    assemble_site_urls_from_parts(app)
    assemble_keycloak_config_from_parts(app)
    populate_unset_salt_values(app)


def override_prefixed_config(app):
    """Override config items with their prefixed siblings' values.

    The prefix is determined via the config item "CONFIG_TUW_CONFIG_OVERRIDE_PREFIX".
    Configuration items with this prefix will override the values for

    If the prefix is set to `None` (the default), then this feature will be disabled.
    """
    prefix = app.config.get("CONFIG_TUW_CONFIG_OVERRIDE_PREFIX", None)
    if prefix is None:
        return

    prefix_len = len(prefix)
    pairs = [(k, v) for k, v in app.config.items() if k.startswith(prefix)]

    for key, value in pairs:
        key = key[prefix_len:]
        app.config[key] = value


def override_flask_config(app):
    """Replace the app's config with our own override.

    This evaluates the ``LocalProxy`` objects used for ``SITE_{API,UI}_URL`` by
    casting them into strings (which is their expected type).
    """
    app.config = TUWConfig.from_flask_config(app.config)

    # we need to override the "config" global, as that might still be the
    # old "normal" Flask config, and thus have different content
    app.add_template_global(app.config, "config")
