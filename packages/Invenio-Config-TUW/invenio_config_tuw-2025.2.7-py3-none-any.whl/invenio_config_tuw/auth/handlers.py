# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2023 TU Wien.
#
# Invenio Config TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Custom handlers for the Keycloak integration."""


from flask import current_app, redirect, session
from flask_login import current_user
from flask_security.confirmable import requires_confirmation
from flask_security.utils import do_flash
from invenio_base.urls import invenio_url_for
from invenio_db import db
from invenio_i18n import gettext as _
from invenio_oauthclient.contrib.keycloak.helpers import get_user_info
from invenio_oauthclient.errors import (
    OAuthClientMustRedirectSignup,
    OAuthClientUnAuthorized,
    OAuthClientUserNotRegistered,
    OAuthClientUserRequiresConfirmation,
)
from invenio_oauthclient.handlers.authorized import get_session_next_url
from invenio_oauthclient.handlers.token import (
    response_token_setter,
    token_getter,
    token_session_key,
)
from invenio_oauthclient.handlers.ui import oauth_resp_remote_error_handler
from invenio_oauthclient.oauth import oauth_authenticate, oauth_get_user, oauth_register
from invenio_oauthclient.proxies import current_oauthclient
from invenio_oauthclient.signals import (
    account_info_received,
    account_setup_committed,
    account_setup_received,
)
from invenio_oauthclient.tasks import create_or_update_roles_task
from invenio_oauthclient.utils import create_csrf_disabled_registrationform, fill_form
from markupsafe import Markup

from .utils import auto_trust_user, create_username_from_info, get_user_by_username


def info_handler(remote, resp):
    """Retrieve remote account information for finding matching local users."""
    # NOTE: for lookup of local users, only the 'external_id' and 'user.email' are used
    #       => calculation of the 'user.user_profile.username'
    #          here should actually be safe
    from_token, from_endpoint = get_user_info(remote, resp)
    user_info = {**(from_token or {}), **(from_endpoint or {})}

    # get or synthesize the name entries for the user profile
    # note: we used to only get the "full_name"; it's unlikely that this would
    #       need to be synthesized
    given_name = user_info.get("given_name")
    family_name = user_info.get("family_name")
    full_name = user_info.get("name")
    if not full_name:
        full_name = f"{given_name} {family_name}"

    # get unique domains for reported affiliations
    # e.g. ["employee@tuwien.ac.at", student@tuwien.ac.at"] -> {"tuwien.ac.at"}
    affiliations = {
        aff.split("@")[1]
        for aff in user_info.get("affiliation") or []
        if len(aff.split("@")) == 2
    }

    # fill out the information required by 'invenio-accounts'.
    #
    # note: "external_id": `preferred_username` should also work,
    #       as it is seemingly not editable in Keycloak
    result = {
        "user": {
            "active": True,
            "email": user_info["email"],
            "username": user_info.get("preferred_username"),
            "user_profile": {
                "full_name": full_name,
                "given_name": given_name,
                "family_name": family_name,
                "affiliations": ", ".join(affiliations),
            },
        },
        "external_id": user_info["sub"],
        "external_method": remote.name,
    }

    # store the TISS ID for users with TUW affiliation, if available
    if (uid := user_info.get("saml_uid", None)) is not None:
        if "tuwien.ac.at" in affiliations:
            result["user"]["user_profile"]["tiss_id"] = int(uid)

    return result


@oauth_resp_remote_error_handler
def authorized_signup_handler(resp, remote, *args, **kwargs):
    """Handle sign-in/up functionality.

    :param remote: The remote application.
    :param resp: The response.
    :returns: Redirect response.
    """
    try:
        # change: we override the `authorized_handler()` implementation
        next_url = authorized_handler(resp, remote, *args, **kwargs)

        # Redirect to next
        if next_url:
            return redirect(next_url)

        return redirect(invenio_url_for("invenio_oauthclient_settings.index"))

    except OAuthClientUserRequiresConfirmation as exc:
        do_flash(
            Markup(
                _(
                    f"A confirmation email has already been sent to {exc.user.email}. Didn't receive it? Click <strong><a href=\"{invenio_url_for('security.send_confirmation')}\">here</a></strong> to resend it."
                )
            ),
            category="success",
        )
        return redirect("/")


def authorized_handler(resp, remote, *args, **kwargs):
    """Handle user login after OAuth authorize step.

    :param resp: The response of the `authorized` endpoint.
    :param remote: The remote application.
    :returns: The URL to go next after login.
    """
    # Validate the response and set token in the user session. This must happen
    # first to make sure that the response payload is valid.
    # Returned token is None when anonymous user
    token = response_token_setter(remote, resp)

    # Set the remote in the user session to know how the user logged in.
    # Useful on log out, so that we can logout on remote too, when needed.
    session["OAUTHCLIENT_SESSION_REMOTE_NAME"] = remote.name

    # Remove any previously stored auto register session key
    session.pop(token_session_key(remote.name) + "_autoregister", None)

    handlers = current_oauthclient.signup_handlers[remote.name]

    # call user info endpoint
    account_info = handlers["info"](resp)
    assert "external_id" in account_info
    account_info_received.send(remote, response=resp, account_info=account_info)

    # call groups endpoint, when defined
    session["unmanaged_roles_ids"] = set()
    groups_handler = handlers.get("groups")
    if groups_handler:
        groups = groups_handler(resp)
        if groups:
            # preventively add/update Invenio roles based on the fetched user groups
            # (async), so that new groups are almost immediately searchable
            create_or_update_roles_task.delay(groups)
            # Set the unmanaged roles in the user session, used in other modules.
            # Unmanaged user roles are not stored in the DB for privacy reasons:
            # sys admins should not know the external groups of a user.
            session["unmanaged_roles_ids"] = {group["id"] for group in groups}

    # In the normal OAuth flow, the user is not yet authenticated. However, it the user
    # is already logged in, and goes to 'Linked accounts', clicks 'Connect' on another
    # remote app, `authorized` will be called with the new remote.
    is_normal_oauth_flow = not current_user.is_authenticated
    if is_normal_oauth_flow:
        # get the user from the DB using the current remote
        user = oauth_get_user(
            remote.consumer_key,
            account_info=account_info,
            access_token=token_getter(remote)[0],
        )

        if user is None:
            # User not found, this is the first login. Register the user.
            # The registration raises an exception when the account info is not enough
            # to register the user.
            form = create_csrf_disabled_registrationform(remote)
            form = fill_form(form, account_info["user"])

            try:
                user = _register_user(resp, remote, account_info, form)
            except OAuthClientUserNotRegistered:
                # save in the session info to display the extra signup form to the user
                session[token_session_key(remote.name) + "_autoregister"] = True
                session[token_session_key(remote.name) + "_account_info"] = account_info
                session[token_session_key(remote.name) + "_response"] = resp
                db.session.commit()
                # this will trigger a redirect to /signup (therefor
                # signup_handler/extra_signup_handler funcs) and will require the user
                # to fill in the registration form with the missing information
                raise OAuthClientMustRedirectSignup()

        # check if user requires confirmation
        # that happens when user was previously logged in but email was not yet
        # confirmed
        if requires_confirmation(user):
            raise OAuthClientUserRequiresConfirmation(user=user)

        if not oauth_authenticate(
            remote.consumer_key,
            user,
            require_existing_link=False,
            require_user_confirmation=False,
        ):
            raise OAuthClientUnAuthorized()

        # change: update user info after each login (including registration)
        if user is not None:
            user_info = account_info.get("user", {})
            new_email = user_info.get("email", user.email)
            new_profile = user_info.get("user_profile", {})

            if user.email != new_email:
                user.email = new_email

                # our usernames are based on the users' email addresses;
                # thus, we need to update the username if the email address changes
                user.username = create_username_from_info(user_info)

            # update the user's profile information if it has changed
            old_profile = user.user_profile or {}
            if new_profile and new_profile != old_profile:
                user.user_profile = {**old_profile, **new_profile}

        # Store token in the database instead of only the session
        token = response_token_setter(remote, resp)

    _complete_authorize(resp, remote, handlers, token)

    # Return the URL where to go next
    next_url = get_session_next_url(remote.name)
    if next_url:
        return next_url


def _complete_authorize(resp, remote, handlers, token):
    """Complete authorized flow.

    This happens after:
     - A normal authorized flow.
     - The extra signup registration, where the user needs to fill in the missing
       information during the first login.
    """
    is_first_login_with_this_remote = not token.remote_account.extra_data
    if is_first_login_with_this_remote:
        # call the `setup` handler to get complete the first login with this remote
        account_setup = handlers["setup"](token, resp)
        account_setup_received.send(
            remote, token=token, response=resp, account_setup=account_setup
        )
        db.session.commit()
        account_setup_committed.send(remote, token=token)
    else:
        db.session.commit()


def _register_user(resp, remote, account_info, form):
    """Try to register the user with info got from the remote app.

    :param resp: The response of the `authorized` endpoint.
    :param remote: The remote application.
    """
    # change: generate username
    username = account_info["user"]["username"]
    if not form.validate() or get_user_by_username(username) is not None:
        # if the 'preferred_username' wasn't valid or already taken,
        # try to auto-generate a valid and unique username
        account_info["user"]["username"] = create_username_from_info(
            account_info["user"]
        )
        form = fill_form(form, account_info["user"])

    remote_app = current_app.config["OAUTHCLIENT_REMOTE_APPS"][remote.name]
    precedence_mask = remote_app.get("precedence_mask")
    signup_options = remote_app.get("signup_options")

    user = oauth_register(
        form,
        account_info["user"],
        precedence_mask=precedence_mask,
        signup_options=signup_options,
    )

    if user is None:
        # Registration failed: the account info is not enough to register the user.
        # Save info in the session, necessary for the user registration flow with form.
        raise OAuthClientUserNotRegistered()

    # auto-trust new users, if they meet the configured criteria
    # NOTE: this was moved here from ext.py (as a handler for the
    # flask_security.signals.user_registered signal), because that
    # didn't quite work with a containerized setup...
    auto_trust_user(user)

    return user
