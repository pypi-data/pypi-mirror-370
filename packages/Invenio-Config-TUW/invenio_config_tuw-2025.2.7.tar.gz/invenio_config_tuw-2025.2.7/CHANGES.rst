..
    Copyright (C) 2020-2025 TU Wien.

    Invenio Config TUW is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.

Changes
=======


Version 2025.2.7 (released 2025-08-20)

- chase permission changes related to the multipart-upload


Version 2025.2.6 (released 2025-08-14)

- set ``self.app`` in the extension to avoid needing to call ``flask.current_app``
- register ``task_failure`` celery signal handler that stores failure information to valkey for a day


Version 2025.2.5 (released 2025-08-13)

- fix errors in the curation-related reminder notifications
- use the new `invenio_url_for()` function instead of legacy mechanisms


Version 2025.2.4 (released 2025-08-12)

- remove curation consent from registration form and set its default value to `True`


Version 2025.2.3 (released 2025-08-11)

- fix import paths in curation-related reminder tasks


Version 2025.2.2 (released 2025-08-07)

- set `DEBUG_TB_ENABLED=False` by default
- refactor the TISS names sync
- allow a list of employees to be passed into `sync_names_from_tiss()` instead of querying TISS
- update `get_tuw_ror_aliases()` to work with the new ROR v2 schema


Version 2025.2.1 (released 2025-08-04)

- v13: set new config options for file size and quota limits


Version 2025.2.0 (released 2025-08-01)

- fix some SonarQube complaints
- v13: configure new feature flags
- v13: chase changes for flask 3
- v13: chase record ownership change in v13
- v13: implement wrapper for removed `IfFileIsLocal` permission generator
- v13: chase "shared with me" dashboard search parameter rework
- v13: replace `APP_ALLOWED_HOSTS` config with `TRUSTED_HOSTS`
- v13: bump minimum requirements


Version 2025.1.14 (released 2025-05-09)

- Add service component for making sure that the user quota is honored for new drafts


Version 2025.1.13 (released 2025-04-15)

- Add possibility to set alternative storage location for new records based on IP address


Version 2025.1.12 (released 2025-03-20)

- Send notification about started reviews to other reviewers
- Allow user/group notifications to render a different template
- Send notifications to record owners about edits published by somebody else
- Fix incorrect usage of `lstrip()` and `rstrip()`
- Add tests for curation-related workflows and notifications
- Align notification templates with those from Invenio-Theme-TUW
- A few minor changes for SonarQube


Version 2025.1.11 (released 2025-03-11)

- Omit the default value for "version" on the deposit form
- Automatically set the publication date for new versions of records


Version 2025.1.10 (released 2025-02-28)

- Re-enable `rdm-curation` requests


Version 2025.1.9 (released 2025-02-13)

- Allow secondary email address to be removed again
- Add "id" to the fake entity created by `SystemEntityProxy._resolve()`


Version 2025.1.8 (released 2025-02-13)

- Explicitly set calculated value for `THEME_SITEURL` in the config


Version 2025.1.7 (released 2025-02-11)

- Override `BROKER_URL` more aggressively


Version 2025.1.6 (released 2025-02-11)

- Remove accidentally added MXID field from notification settings template
- Move the configuration magic (assembly & overrides) to extension loading
- Ensure that the `Invenio-Config-TUW` extension is loaded first
- Rename the registered `invenio_config.module` entrypoint


Version 2025.1.5 (released 2025-02-10)

- Add background task for cleaning up "dead" files periodically
- Assemble some config items from their parts on application startup


Version 2025.1.4 (released 2025-02-08)

- Rename task `send_publication_notification_email` and make it use notifications
- Enable overriding config items with values from prefixed variants
- Add possibility to set a secondary email address for user notifications


Version 2025.1.3 (released 2025-02-06)

- Update translation infrastructure
- Fix config class override not being reflected in Jinja templates


Version 2025.1.2 (released 2025-02-05)

- Rework the Flask config class override as a `finalize_app` handler
- Temporarily unset `SERVER_NAME` during requests, to avoid forcing it for `url_for()`


Version 2025.1.1 (released 2025-02-04)

- Override `Flask.create_url_adapter()` to match v3.1 regarding `SERVER_NAME`


Version 2025.1.0 (released 2025-01-31)

- Add `Invenio-Curations` as a dependency
- Update configuration and permissions to work with it
- Implement customized notification infrastructure
- Set `X-Sender` email header value to identify sender service
- Add background tasks for reminding reviewers and uploaders


Version 2025.0.0 (released 2025-01-13)

- Refactor package structure
- Fix response status code check in ROR API call
- Refer to TUW by ROR ID in names synced from TISS
- Add tests


Version 2024.4 (released 2024-11-26, updated 2024-12-12)

- Pin `Flask-Menu`` dependency
- Add `Invenio-DAMAP` to the dependencies
- Implement TU Wien user identity generator for connection to DAMAP
- Cast TISS ID into string for the Invenio-DAMAP integration
- Send out notification emails when records get published
- Rework curation menu item registration and unpin `Flask-Menu`
- Fix TISS name vocabulary synchronization


Version 2024.3 (released 2024-10-01, updated 2024-11-13)

- Replace `setuptools` with `hatchling` as build tool
- Use `uv` over `pipx` for CI/CD
- General cleaning of built-up cruft
- Update wtforms import
- Update wtforms validator


Version 2024.2 (released 2024-06-24, updated 2024-10-01)

- v12 compat: Chase Invenio-OAuthClient refactoring
- v12 compat: Chase permission policy changes
- v12 compat: Chase record ownership changes
- v12 compat: Remove breadcrumbs
- Use configuration items instead of hacks for the community permission policy
- Flatten the user preference `curation.consent` to `curation_consent`
- Override search mappings
- Remove support for creating `community-submission` requests for drafts
- Allow {user,guest} access requests for new drafts by default
- Add install extras for search
- Add `Flask-Minify` as opt-in for minifying HTML responses (without the golang minifiers)
- Show all accessible drafts in the user's dashboard
- Give out permissions to access the draft's files with the preview permission
- Deduplicate some generators in the permission policy
- Remove references to the unused `trusted-publisher` role
- Use the `finalize_app` entrypoint for the SMTP handler rather than a hacky blueprint
- Update README
- Remove overridden search mappings for community members
- Update wording about curation consent on registration form


Version 2024.1 (released 2024-05-22, updated 2024-05-22)

- Store ``given_name`` and ``family_name`` in user profiles
- Use these values to more accurately synthesize default values for creators in metadata
- Store the TISS ID in the user profile for people with TU Wien affiliation


Version 2023.2 (released 2023-04-24, updated 2023-12-22)

- v11 compat: Update permission policies and disable archive download
- Set affiliation (hard-coded) to TU Wien in `user.profile`
- Set a default template for the `description` metadata field
- Add a null check for the current_user in the logging formatter
- Prevent the logging formatter from blowing up outside of a request context
- Add utilities and a celery task for updating the `names` vocabulary with information from TISS
- Enable sending of registration mails
- Allow edits to owners of published records even if they only have `trusted-user` role
- Fix a typo in the config generated by the `TUWSSOSettingsHelper`
- Fix function to fetch user by username
- Add record curation preferences to user settings


Version 2023.1 (released 2023-01-13)

- Update definition of the default creator for new uploads


Version 2022.3 (released 2022-10-28, updated 2022-11-30)

- v10 compat: Discard imports of removed Admin/SuperUser generators
- Rework the initialization procedure used for some custom overrides
- Migrate from setup.py to setup.cfg
- Move Flask config override from Invenio-Theme-TUW to Invenio-Config-TUW
- Update "Terms of Use" link in registration form


Version 2022.2 (released 2022-07-19, updated 2022-10-22)

- v9 compat: Chase changes in Invenio-{Accounts,OAuthClient} 2.x
- v9 compat: Update permission policies
- v9 compat: Hack in permission policy for communities
- Refactor permissions and config
- Remove leftover views.py
- Set deposit form file size limits
- Fix permissions
- Reverse contents of CHANGES.rst (recent changes are shown on top)
- Attach SMTP error handler to the application in production mode
- Add custom logging formatter
- Auto-confirm newly registered users' e-mail addresses if ``SECURITY_CONFIRMABLE`` is ``False``
- Set default user preferences (``visibility=public``, ``email_visibility=restricted``)
- Set default value for ``version`` metadata to ``1.0.0``
- Add config item to put the system into "read-only mode"


Version 2022.1 (released 2022-03-23, updated 2022-04-06)

- Update permissions for creating and editing drafts
- Use the OAI metadata implementation from Invenio-RDM-Records
- Change the default file size and bucket quota limits to 75GB


Version 2021.2 (released 2021-12-07, updated 2021-12-20)

- Make ready for InvenioRDM v7
- Add requests permission policy
- Enforce a rate limit for HTTP requests
- Change method of overriding the record permission policy
- Add datacite and oai_datacite metadataPrefixes to the OAI endpoint


Version 2021.1 (released 2021-07-15)

- Initial public release.
- Update the list of citation styles
