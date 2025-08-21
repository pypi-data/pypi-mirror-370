# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2025 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module containing some customizations and configuration for TU Wien."""

from datetime import datetime
from operator import attrgetter

import invenio_base.app
from importlib_metadata import entry_points as iter_entry_points
from invenio_app_rdm.config import (
    NOTIFICATIONS_BACKENDS,
    NOTIFICATIONS_BUILDERS,
    NOTIFICATIONS_ENTITY_RESOLVERS,
)
from invenio_curations.config import CURATIONS_NOTIFICATIONS_BUILDERS
from invenio_curations.services.facets import status as facets_status
from invenio_curations.services.facets import type as facets_type
from invenio_i18n import gettext as _
from invenio_oauthclient.views.client import auto_redirect_login
from invenio_rdm_records.checks import requests as checks_requests
from invenio_rdm_records.config import (
    RDM_PARENT_PERSISTENT_IDENTIFIERS,
    RDM_PERSISTENT_IDENTIFIERS,
)

from .auth import TUWSSOSettingsHelper
from .curations import (
    TUWCurationRequestReviewNotificationBuilder as TUWReviewNotifBuilder,
)
from .curations import (
    TUWCurationRequestUploaderResubmitNotificationBuilder as TUWUploaderResubmitNotifBuilder,
)
from .curations.tasks import auto_generate_curation_request_remarks
from .notifications import (
    GroupNotificationBuilder,
    SystemEntityResolver,
    TUWEmailNotificationBackend,
    UserNotificationBuilder,
)
from .permissions import (
    TUWCommunityPermissionPolicy,
    TUWRecordPermissionPolicy,
    TUWRequestsPermissionPolicy,
)
from .records import TUWRDMDraft
from .services import TUWRecordsComponents
from .users import (
    TUWUserPreferencesSchema,
    TUWUserProfileSchema,
    TUWUserSchema,
    tuw_registration_form,
)
from .users.utils import check_user_email_for_tuwien, current_user_as_creator
from .users.views import notification_settings

# Invenio-Config-TUW
# ==================

CONFIG_TUW_AUTO_TRUST_USERS = True
"""Whether or not to auto-assign the 'trusted-user' role to new users."""

CONFIG_TUW_AUTO_TRUST_CONDITION = check_user_email_for_tuwien
"""Function for checking if the user is eligible for auto-trust.

This must be a function that accepts a 'user' argument and returns a boolean value.
Alternatively, it can be set to None. This is the same as ``lambda u: True``.
"""

CONFIG_TUW_READ_ONLY_MODE = False
"""Disallow insert and update operations in the repository."""

CONFIG_TUW_DISABLE_ERROR_MAILS = False
"""Disable registration of the SMTP mail handler to suppress warnings."""

CONFIG_TUW_MINIFY_ENABLED = False
"""Enable or disable the Flask-Minify extension."""

CONFIG_TUW_CURATIONS_ENABLED = True
"""Enable the `Invenio-Curations` integration."""

CONFIG_TUW_SITE_IDENTIFIER = None
"""An identifier (e.g. acronym), e.g. to be added to email subjects as prefix."""

CONFIG_TUW_MAIL_XSENDER = None
"""Value to be set as value for the X-Sender header in notification emails.

If set to `None`, the first available option will be used:
* `CONFIG_TUW_SITE_IDENTIFIER`
* `SERVER_NAME`
* the first entry for `TRUSTED_HOSTS`
"""

CONFIG_TUW_AUTO_ACCEPT_CURATION_REQUESTS = False
"""Whether or not the system should auto-accept curation requests.

This can be either a boolean value to be returned for all requests, or it can be
a function that takes the request as argument and returns a boolean value.
Functions can be either supplied via reference, or via import string.
"""

CONFIG_TUW_AUTO_COMMENT_CURATION_REQUESTS = auto_generate_curation_request_remarks
"""A function to automatically generate remarks for record curation requests.

The function must take the request as argument and return a list of messages (strings)
to be used to create a system comment on the request.
Functions can be either supplied via reference, or via import string.
A value of ``None`` disables this feature.
"""

CONFIG_TUW_CONFIG_OVERRIDE_PREFIX = None
"""Prefix to check for when overriding configuration items.

If this value is set to any string, then configuration items whose keys start
with this prefix will be used to override the values for configuration items with
the same name (but without the prefix).

Example:
If the value is set to "CONTAINERIZED_", then the value of "CONTAINERIZED_SEARCH_HOSTS"
will override the value of "SEARCH_HOSTS".

A value of `None` (the default) will disable this feature.
"""

CONFIG_TUW_STORAGE_LOCATION_FOR_IP = {}
"""Configuration for setting the storage location for new records based on IP address.

The configuration option is expected to be a dictionary where the keys are IP addresses
(no subnet masks are supported), and the values are either ``Location`` objects or their
names.
If there is no match for the request's IP address, or the lookup result is ``None``,
then the default location will be used.

This setting is intended to store files from certain automated uploads (e.g. shared
setups in computer labs) in an alternative location with a simplified backup setup.
"""


# Invenio-Mail
# ============
# See https://invenio-mail.readthedocs.io/en/latest/configuration.html

MAIL_SERVER = "localhost"
"""Domain ip where mail server is running."""

SECURITY_EMAIL_SENDER = "no-reply@tuwien.ac.at"
"""Email address used as sender of account registration emails."""

MAIL_SUPPRESS_SEND = True
"""Disable email sending by default."""

SECURITY_SEND_REGISTER_EMAIL = True
"""Enable sending emails after user registration."""

SECURITY_EMAIL_SUBJECT_REGISTER = _("Welcome to TU Wien Research Data!")
"""Email subject for account registration emails."""

SECURITY_EMAIL_HTML = True
"""Send the HTML version of the email."""

# disable sending of emails related to local login
SECURITY_SEND_PASSWORD_CHANGE_EMAIL = False
SECURITY_SEND_PASSWORD_RESET_EMAIL = False
SECURITY_SEND_PASSWORD_RESET_NOTICE_EMAIL = False


# Invenio-Previewer
# =================

PREVIEWER_MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

PREVIEWER_MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


# Authentication
# ==============

SECURITY_CHANGEABLE = False
"""Allow password change by users."""

SECURITY_RECOVERABLE = False
"""Allow password recovery by users."""

SECURITY_REGISTERABLE = False
""""Allow users to register."""

SECURITY_CONFIRMABLE = False
"""Allow user to confirm their email address."""

ACCOUNTS = True
"""Tells if the templates should use the accounts module."""

ACCOUNTS_LOCAL_LOGIN_ENABLED = False
"""Disable local login (rely only on OAuth)."""

USERPROFILES_READ_ONLY = True
"""Prevent users from updating their profiles."""


# Invenio-OAuthClient
# ===================

ACCOUNTS_LOGIN_VIEW_FUNCTION = auto_redirect_login

OAUTHCLIENT_SIGNUP_FORM = tuw_registration_form

OAUTHCLIENT_AUTO_REDIRECT_TO_EXTERNAL_LOGIN = True

helper = TUWSSOSettingsHelper(
    title="TU Wien SSO",
    description="TU Wien Single Sign-On",
    base_url="https://s194.dl.hpc.tuwien.ac.at",
    realm="tu-data-test",
)

OAUTHCLIENT_KEYCLOAK_REALM_URL = helper.realm_url
OAUTHCLIENT_KEYCLOAK_USER_INFO_URL = helper.user_info_url
OAUTHCLIENT_KEYCLOAK_AUD = "tu-data-test"
OAUTHCLIENT_KEYCLOAK_VERIFY_AUD = True
OAUTHCLIENT_KEYCLOAK_USER_INFO_FROM_ENDPOINT = True
OAUTHCLIENT_REMOTE_APPS = {
    "keycloak": helper.remote_app,
}


# Invenio-App-RDM
# ================

APP_RDM_DEPOSIT_FORM_DEFAULTS = {
    "publication_date": lambda: datetime.now().strftime("%Y-%m-%d"),
    "creators": current_user_as_creator,
    "rights": [
        {
            "id": "cc-by-4.0",
            "title": "Creative Commons Attribution 4.0 International",
            "description": (
                "The Creative Commons Attribution license allows "
                "re-distribution and re-use of a licensed work "
                "on the condition that the creator is "
                "appropriately credited."
            ),
            "link": "https://creativecommons.org/licenses/by/4.0/legalcode",
        }
    ],
    "publisher": "TU Wien",
    "resource_type": {
        "id": "dataset",
    },
    "description": "<h2>A primer on your dataset's description (to be edited)</h2><p>The influence of proper documentation on the reusability for research data should not be underestimated!<br>In order to help others understand how to interpret and reuse your data, we provide you with a few questions to help you structure your dataset's description (though please don't feel obligated to stick to them):</p><h3>Context and methodology</h3><ul><li>What is the research domain or project in which this dataset was created?</li><li>Which purpose does this dataset serve?</li><li>How was this dataset created?</li></ul><h3>Technical details</h3><ul><li>What is the structure of this dataset? Do the folders and files follow a certain naming convention?</li><li>Is any specific software required to open and work with this dataset?</li><li>Are there any additional resources available regarding the dataset, e.g. documentation, source code, etc.?</li></ul><h3>Further details</h3><ul><li>Is there anything else that other people may need to know when they want to reuse the dataset?</li></ul>",  # noqa
}

RDM_RECORDS_SERVICE_COMPONENTS = TUWRecordsComponents
"""Override for the default record service components."""

RDM_CITATION_STYLES = [
    ("apa", _("APA")),
    ("bibtex", _("BibTeX")),
    ("ieee", _("IEEE")),
]

RDM_PERMISSION_POLICY = TUWRecordPermissionPolicy

OAISERVER_METADATA_FORMATS = {
    "oai_dc": {
        "serializer": "invenio_rdm_records.oai:dublincore_etree",
        "schema": "http://www.openarchives.org/OAI/2.0/oai_dc.xsd",
        "namespace": "http://www.openarchives.org/OAI/2.0/oai_dc/",
    },
    "datacite": {
        "serializer": "invenio_rdm_records.oai:datacite_etree",
        "schema": "http://schema.datacite.org/meta/nonexistant/nonexistant.xsd",
        "namespace": "http://datacite.org/schema/nonexistant",
    },
    "oai_datacite": {
        "serializer": "invenio_rdm_records.oai:oai_datacite_etree",
        "schema": "http://schema.datacite.org/oai/oai-1.1/oai.xsd",
        "namespace": "http://schema.datacite.org/oai/oai-1.1/",
    },
}

RDM_ARCHIVE_DOWNLOAD_ENABLED = False

RDM_DRAFT_CLS = TUWRDMDraft


# Invenio-Requests
# ================

REQUESTS_PERMISSION_POLICY = TUWRequestsPermissionPolicy

REQUESTS_FACETS = {
    "type": {
        "facet": facets_type,
        "ui": {
            "field": "type",
        },
    },
    "status": {
        "facet": facets_status,
        "ui": {
            "field": "status",
        },
    },
}


# Invenio-Communities
# ================

COMMUNITIES_ALLOW_RESTRICTED = True

COMMUNITIES_PERMISSION_POLICY = TUWCommunityPermissionPolicy


# Limitations
# ===========

RATELIMIT_ENABLED = True

RATELIMIT_AUTHENTICATED_USER = "30000 per hour;3000 per minute"

RATELIMIT_GUEST_USER = "6000 per hour;600 per minute"

# Default file size limits for deposits: 75 GB
max_file_size = 75 * (1024**3)

# ... per file
RDM_FILES_DEFAULT_MAX_FILE_SIZE = FILES_REST_DEFAULT_MAX_FILE_SIZE = max_file_size
RDM_MEDIA_FILES_DEFAULT_MAX_FILE_SIZE = max_file_size

# ... for the entire bucket
RDM_FILES_DEFAULT_QUOTA_SIZE = FILES_REST_DEFAULT_QUOTA_SIZE = max_file_size
RDM_MEDIA_FILES_DEFAULT_QUOTA_SIZE = max_file_size

# ... and on the deposit form UI
APP_RDM_DEPOSIT_FORM_QUOTA = {
    "maxFiles": 100,
    "maxStorage": max_file_size,
}

# show the display in powers of 2 (KiB, MiB, GiB, ...) rather than 10 (KB, MB, GB, ...)
APP_RDM_DISPLAY_DECIMAL_FILE_SIZES = False

# for multipart form uploads, we'll use a max. content length of 100 MB
# (e.g. community logo upload, but not record/draft file deposits)
MAX_CONTENT_LENGTH = 100 * (1024**2)


# Invenio-Curations
# =================

NOTIFICATIONS_BUILDERS = {
    **NOTIFICATIONS_BUILDERS,
    **CURATIONS_NOTIFICATIONS_BUILDERS,
    TUWReviewNotifBuilder.type: TUWReviewNotifBuilder,
    TUWUploaderResubmitNotifBuilder.type: TUWUploaderResubmitNotifBuilder,
    UserNotificationBuilder.type: UserNotificationBuilder,
    GroupNotificationBuilder.type: GroupNotificationBuilder,
}

CURATIONS_MODERATION_ROLE = "reviewer"

CURATIONS_ALLOW_PUBLISHING_EDITS = True

CURATIONS_PERMISSIONS_VIA_GRANTS = False

NOTIFICATIONS_ENTITY_RESOLVERS = [
    SystemEntityResolver("users"),
    *NOTIFICATIONS_ENTITY_RESOLVERS,
]


# Misc. Configuration
# ===================

# Make sure Flask-DebugToolbar is disabled by default and needs to be enabled explicitly
DEBUG_TB_ENABLED = False

# Default locale (language)
BABEL_DEFAULT_LOCALE = "en"

# Default time zone
BABEL_DEFAULT_TIMEZONE = "Europe/Vienna"

# Recaptcha public key (change to enable).
RECAPTCHA_PUBLIC_KEY = None

# Recaptcha private key (change to enable).
RECAPTCHA_PRIVATE_KEY = None

# Preferred URL scheme to use
PREFERRED_URL_SCHEME = "https"

# Extended schema for user preferences
ACCOUNTS_USER_PREFERENCES_SCHEMA = TUWUserPreferencesSchema()

# Extended schema for user preferences
ACCOUNTS_USER_PROFILE_SCHEMA = TUWUserProfileSchema()

# Extended schema for users in the users service
USERS_RESOURCES_SERVICE_SCHEMA = TUWUserSchema

NOTIFICATIONS_BACKENDS = {
    **NOTIFICATIONS_BACKENDS,
    TUWEmailNotificationBackend.id: TUWEmailNotificationBackend(),
}

NOTIFICATIONS_SETTINGS_VIEW_FUNCTION = notification_settings


def sorted_app_loader(app, entry_points=None, modules=None):
    """Application extension loader that operates in lexicographic order.

    This is useful for us, to ensure that our `Invenio-Config-TUW` extension
    is loaded before any of the others.
    This enables us to hook into the startup process after the configuration
    loader is done (and, especially, has finished interpreting environment
    variables that we use heavily for configuration), but before any other
    Invenio extensions have been loaded (and potentially started caching values).
    """

    def init_func(ext):
        ext(app)

    for entry_point in entry_points or []:
        unique_eps = set(iter_entry_points(group=entry_point))
        for ep in sorted(unique_eps, key=attrgetter("name")):
            try:
                init_func(ep.load())
            except Exception:
                app.logger.error(f"Failed to initialize entry point: {ep}")
                raise
    if modules:
        for m in modules:
            try:
                init_func(m)
            except Exception:
                app.logger.error(f"Failed to initialize module: {m}")
                raise


# override the app loader with our sorted variant
invenio_base.app.app_loader = sorted_app_loader


# InvenioRDM v13: new configuration and feature flags
# ---------------------------------------------------

# enable FAIR signposting level 1
APP_RDM_RECORD_LANDING_PAGE_FAIR_SIGNPOSTING_LEVEL_1_ENABLED = True

# enable audit logs
AUDIT_LOGS_ENABLED = True

# enable the new Uppy uploader (overridden in Theme-TUW to hide the "browse folders")
APP_RDM_DEPOSIT_NG_FILES_UI_ENABLED = True

# show "browse" tab for collections in communities (if a community has any collections)
COMMUNITIES_SHOW_BROWSE_MENU_ENTRY = True

# enable the automatic request checks feature, and enable them for community requests
CHECKS_ENABLED = True
RDM_COMMUNITY_SUBMISSION_REQUEST_CLS = checks_requests.CommunitySubmission
RDM_COMMUNITY_INCLUSION_REQUEST_CLS = checks_requests.CommunityInclusion

# disable the new possibility to not mint a DOI, and pre-select the option to get a DOI
# NOTE: if DATACITE_ENABLED=False, the "doi" key is automatically removed from the
#       RDM_PERSISTENT_IDENTIFIERS config dictionary on initialization
RDM_PERSISTENT_IDENTIFIERS["doi"]["ui"]["default_selected"] = "no"  # yes/no/not_needed
RDM_PERSISTENT_IDENTIFIERS["doi"]["required"] = True
RDM_PARENT_PERSISTENT_IDENTIFIERS["doi"]["required"] = True
