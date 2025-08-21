# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Permission policies to be used at TU Wien."""

from typing import Iterable, List

from invenio_administration.generators import Administration
from invenio_communities.generators import CommunityCurators
from invenio_communities.permissions import CommunityPermissionPolicy
from invenio_curations.services.generators import (
    IfCurationRequestAccepted,
    IfRequestTypes,
)
from invenio_rdm_records.requests.community_submission import CommunitySubmission
from invenio_rdm_records.services.generators import (
    AccessGrant,
    CommunityInclusionReviewers,
    IfDeleted,
    IfNewRecord,
    IfRecordDeleted,
    IfRestricted,
    RecordCommunitiesAction,
    RecordOwners,
    ResourceAccessToken,
    SecretLinks,
    SubmissionReviewer,
)
from invenio_rdm_records.services.permissions import (
    RDMRecordPermissionPolicy,
    RDMRequestsPermissionPolicy,
)
from invenio_records_permissions.generators import (
    AnyUser,
    AuthenticatedUser,
    Disable,
    IfConfig,
    SystemProcess,
)
from invenio_requests.services.generators import Creator, Receiver, Status
from invenio_users_resources.services.permissions import UserManager

from .generators import CurationModeratorsIfRequestExists as CurationReviewers
from .generators import (
    DisableIfReadOnly,
    IfCurationsEnabled,
    IfLocalOrMultipart,
    TrustedRecordOwners,
    TrustedUsers,
)


def d(i: Iterable) -> List:
    """Deduplicate the content of the iterable by calling ``list(set(i))``."""
    return list(set(i))


def IfMetadataOnlyAllowed(then_):
    """Don't allow unless metadata-only records are allowed."""
    return IfConfig("RDM_ALLOW_METADATA_ONLY_RECORDS", then_=then_, else_=[])


def IfRestrictedAllowed(then_):
    """Don't allow unless restricted records are allowed."""
    return IfConfig("RDM_ALLOW_RESTRICTED_RECORDS", then_=then_, else_=[])


edit_link = SecretLinks("edit")
view_link = SecretLinks("view")
preview_link = SecretLinks("preview")
secret_links = {
    "manage": [],  # "manage" permissions can't be shared with links
    "edit": [edit_link],
    "view": [edit_link, view_link],
    "preview": [edit_link, preview_link],
}

manage_grant = AccessGrant("manage")
edit_grant = AccessGrant("edit")
view_grant = AccessGrant("view")
preview_grant = AccessGrant("preview")
access_grants = {
    "manage": [manage_grant],
    "edit": [manage_grant, edit_grant],
    "view": [manage_grant, edit_grant, view_grant],
    "preview": [manage_grant, edit_grant, preview_grant],
}

shared_access = {
    "manage": secret_links["manage"] + access_grants["manage"],
    "edit": secret_links["edit"] + access_grants["edit"],
    "view": secret_links["view"] + access_grants["view"],
    "preview": secret_links["preview"] + access_grants["preview"],
}


class TUWRecordPermissionPolicy(RDMRecordPermissionPolicy):
    """Record permission policy of TU Wien."""

    # current state: invenio-rdm-records v11.0.0
    #
    # note: edit := create a draft from a record (i.e. putting it in edit mode),
    #               which does not imply the permission to save the edits
    # note: can_search_* is the permission for the search in general, the records
    #       (drafts) will be filtered as per can_read_* permissions
    #
    # note: most keys were taken from invenio-rdm-records and tweaked
    #       also, we disable write operations if the system is in read-only mode
    #
    # some explanations:
    # > can_access_draft: slightly less strict version of can_manage,
    #                     e.g. to not break user-records search
    # > can_curate:       people with curation rights (e.g. community curators)
    # > can_review:       slightly expanded from 'can_curate', can edit drafts
    #
    # high-level permissions: not used directly (only collections for reuse);
    #                         and get more permissive from top to bottom
    #
    # fmt: off
    can_manage             = d([TrustedRecordOwners(), RecordCommunitiesAction("curate"), SystemProcess()        ] + shared_access["manage"] )  # noqa
    can_access_draft       = d(can_manage       + [RecordOwners(), SubmissionReviewer(), CurationReviewers()     ] + shared_access["preview"])  # noqa
    can_curate             = d(can_manage       + [                                                              ] + shared_access["edit"]   )  # noqa
    can_review             = d(can_curate       + [SubmissionReviewer(), CurationReviewers()                     ]                           )  # noqa
    can_preview            = d(can_access_draft + [UserManager                                                   ]                           )  # noqa
    can_view               = d(can_access_draft + [RecordCommunitiesAction("view"), CommunityInclusionReviewers()] + shared_access["view"]   )  # noqa
    can_authenticated      = d(                   [AuthenticatedUser(), SystemProcess()                          ]                           )  # noqa
    can_all                = d(                   [AnyUser(), SystemProcess()                                    ]                           )  # noqa

    # records
    can_search                   = can_all                                                                                                      # noqa
    can_read                     = [IfRestricted("record", then_=can_view, else_=can_all)                            ]                          # noqa
    can_read_files               = [IfRestricted("files", then_=can_view, else_=can_all), ResourceAccessToken("read")]                          # noqa
    can_get_content_files        = [IfLocalOrMultipart(then_=can_read_files, else_=[SystemProcess()])                ]                          # noqa
    can_read_deleted             = [IfRecordDeleted([UserManager, SystemProcess()], else_=can_read)                  ]                          # noqa
    can_read_deleted_files       = can_read_deleted                                                                                             # noqa
    can_media_read_deleted_files = can_read_deleted_files                                                                                       # noqa
    can_create                   = [TrustedUsers(), DisableIfReadOnly(), SystemProcess()                             ]                          # noqa

    # drafts
    # > can_manage_files: allow enabling/disabling files
    # > can_manage_record_access: allow restricting access
    can_search_drafts           = can_authenticated                                                                                             # noqa
    can_read_draft              = can_preview                                                                                                   # noqa
    can_draft_read_files        = can_preview                                                            + [ResourceAccessToken("read")]        # noqa
    can_update_draft            = can_review                                                             + [DisableIfReadOnly()        ]        # noqa
    can_draft_create_files      = can_review                                                             + [DisableIfReadOnly()        ]        # noqa
    can_draft_set_content_files = [IfLocalOrMultipart(then_=can_review, else_=[SystemProcess()]),           DisableIfReadOnly()        ]        # noqa
    can_draft_get_content_files = [IfLocalOrMultipart(then_=can_draft_read_files, else_=[SystemProcess()]), DisableIfReadOnly()        ]        # noqa
    can_draft_commit_files      = [IfLocalOrMultipart(then_=can_review, else_=[SystemProcess()]),           DisableIfReadOnly()        ]        # noqa
    can_draft_update_files      = can_review                                                             + [DisableIfReadOnly()        ]        # noqa
    can_draft_delete_files      = can_review                                                             + [DisableIfReadOnly()        ]        # noqa
    can_manage_files            = [IfNewRecord(then_=can_create, else_=can_review),                         DisableIfReadOnly()        ]        # noqa
    can_manage_record_access    = [IfNewRecord(then_=can_create, else_=can_review),                         DisableIfReadOnly()        ]        # noqa

    # PIDs
    can_pid_create         = can_review + [DisableIfReadOnly()]                                                          # noqa
    can_pid_register       = can_review + [DisableIfReadOnly()]                                                          # noqa
    can_pid_update         = can_review + [DisableIfReadOnly()]                                                          # noqa
    can_pid_discard        = can_review + [DisableIfReadOnly()]                                                          # noqa
    can_pid_delete         = can_review + [DisableIfReadOnly()]                                                          # noqa

    # actions
    # > can_edit: RecordOwners is needed to not break the 'edit' button on the dashboard (UX)
    # > can_publish: if curations are enabled, similar as vanilla InvenioRDM (+ reviewers)
    #                otherwise, just the system and admins
    #                NOTE: metadata edits for published records don't require another review;
    #                      this is handled by the curation component
    can_edit               = [IfDeleted(then_=[Disable()], else_=can_curate + [RecordOwners(), DisableIfReadOnly()])]    # noqa
    can_delete_draft       = can_curate                                                       + [DisableIfReadOnly()]    # noqa
    can_new_version        = can_curate                                                       + [DisableIfReadOnly()]    # noqa
    can_lift_embargo       = can_manage                                                       + [DisableIfReadOnly()]    # noqa
    can_publish            = [IfCurationsEnabled(then_=can_review, else_=[SystemProcess()]),     DisableIfReadOnly()]    # noqa

    # record communities
    # can_add_community:    add a record to a community
    # can_remove_community: remove a community from a record
    # can_remove_record:    remove a record from a community
    can_add_community        = [RecordOwners(),                      SystemProcess(), DisableIfReadOnly()]               # noqa
    can_remove_community     = [RecordOwners(), CommunityCurators(), SystemProcess(), DisableIfReadOnly()]               # noqa
    can_remove_record        = [CommunityCurators(),                                  DisableIfReadOnly()]               # noqa
    can_bulk_add             = [SystemProcess(),                                      DisableIfReadOnly()]               # noqa

    #
    # media files (drafts)
    #
    can_draft_media_create_files      = can_review                                                                       # noqa
    can_draft_media_read_files        = can_review                                                                       # noqa
    can_draft_media_set_content_files = [IfLocalOrMultipart(then_=can_review, else_=[SystemProcess()])]                  # noqa
    can_draft_media_get_content_files = [IfLocalOrMultipart(then_=can_preview, else_=[SystemProcess()])]                 # noqa
    can_draft_media_commit_files      = [IfLocalOrMultipart(then_=can_review, else_=[SystemProcess()])]                  # noqa
    can_draft_media_update_files      = can_review                                                                       # noqa
    can_draft_media_delete_files      = can_review                                                                       # noqa

    #
    # media files (records)
    #
    can_media_read_files        = [IfRestricted("record", then_=can_view, else_=can_all), ResourceAccessToken("read")]   # noqa
    can_media_get_content_files = [IfLocalOrMultipart(then_=can_read, else_=[SystemProcess()])]                          # noqa
    can_media_create_files      = [Disable()]                                                                            # noqa
    can_media_set_content_files = [Disable()]                                                                            # noqa
    can_media_commit_files      = [Disable()]                                                                            # noqa
    can_media_update_files      = [Disable()]                                                                            # noqa
    can_media_delete_files      = [Disable()]                                                                            # noqa

    #
    # record deletion workflows
    #
    can_delete       = [Administration(), SystemProcess()]
    can_delete_files = [SystemProcess()]
    can_purge        = [SystemProcess()]

    #
    # quotas for records and users
    #
    can_manage_quota = [UserManager, SystemProcess()]

    # disabled (record management in InvenioRDM goes through drafts)
    can_update             = [Disable()]
    can_create_files       = [Disable()]
    can_set_content_files  = [Disable()]
    can_commit_files       = [Disable()]
    can_update_files       = [Disable()]
    can_query_stats        = [Disable()]

    # Used to hide at the moment the `parent.is_verified` field. It should be set to
    # correct permissions based on which the field will be exposed only to moderators
    can_moderate = [Disable()]
    # fmt: on


class TUWRequestsPermissionPolicy(RDMRequestsPermissionPolicy):
    """Requests permission policy of TU Wien."""

    # disable write operations if the system is in read-only mode
    #
    # current state: invenio-rdm-records v11.0.0

    can_read = RDMRequestsPermissionPolicy.can_read + [
        Status(["review", "critiqued", "resubmitted"], [Creator(), Receiver()]),
    ]

    can_create_comment = can_read + [DisableIfReadOnly()]

    # fmt: off
    can_create                = RDMRequestsPermissionPolicy.can_create                + [DisableIfReadOnly()]  # noqa
    can_update                = RDMRequestsPermissionPolicy.can_update                + [DisableIfReadOnly()]  # noqa
    can_delete                = RDMRequestsPermissionPolicy.can_delete                + [DisableIfReadOnly()]  # noqa
    can_action_submit         = RDMRequestsPermissionPolicy.can_action_submit         + [DisableIfReadOnly()]  # noqa
    can_action_cancel         = RDMRequestsPermissionPolicy.can_action_cancel         + [DisableIfReadOnly()]  # noqa
    can_action_expire         = RDMRequestsPermissionPolicy.can_action_expire         + [DisableIfReadOnly()]  # noqa
    can_action_decline        = RDMRequestsPermissionPolicy.can_action_decline        + [DisableIfReadOnly()]  # noqa
    can_update_comment        = RDMRequestsPermissionPolicy.can_update_comment        + [DisableIfReadOnly()]  # noqa
    can_delete_comment        = RDMRequestsPermissionPolicy.can_delete_comment        + [DisableIfReadOnly()]  # noqa
    can_manage_access_options = RDMRequestsPermissionPolicy.can_manage_access_options + [DisableIfReadOnly()]  # noqa
    # fmt: on

    # "rdm-curation" requests have precedence over "community-submission" requests
    can_action_accept = [
        IfRequestTypes(
            request_types=[CommunitySubmission],
            then_=[
                IfCurationRequestAccepted(
                    then_=RDMRequestsPermissionPolicy.can_action_accept, else_=[]
                )
            ],
            else_=RDMRequestsPermissionPolicy.can_action_accept,
        ),
        DisableIfReadOnly(),
    ]

    # custom actions for curation request actions
    can_action_review = can_action_accept
    can_action_critique = can_action_accept
    can_action_resubmit = can_action_submit


class TUWCommunityPermissionPolicy(CommunityPermissionPolicy):
    """Communities permission policy of TU Wien."""

    # for now, we want to restrict the creation of communities to admins
    # and disable write operations if the system is in read-only mode
    #
    # current state: invenio-communities v14.0.0
    can_create = [SystemProcess(), DisableIfReadOnly()]

    # fmt: off
    can_update              = CommunityPermissionPolicy.can_update                                + [DisableIfReadOnly()]  # noqa
    can_delete              = CommunityPermissionPolicy.can_delete                                + [DisableIfReadOnly()]  # noqa
    can_purge               = CommunityPermissionPolicy.can_purge                                 + [DisableIfReadOnly()]  # noqa
    can_manage_access       = CommunityPermissionPolicy.can_manage_access                         + [DisableIfReadOnly()]  # noqa
    can_create_restricted   = [IfConfig("COMMUNITIES_ALLOW_RESTRICTED", then_=can_create, else_=[]), DisableIfReadOnly()]  # noqa
    can_rename              = CommunityPermissionPolicy.can_rename                                + [DisableIfReadOnly()]  # noqa
    can_submit_record       = CommunityPermissionPolicy.can_submit_record                         + [DisableIfReadOnly()]  # noqa
    can_include_directly    = CommunityPermissionPolicy.can_include_directly                      + [DisableIfReadOnly()]  # noqa
    can_members_add         = CommunityPermissionPolicy.can_members_add                           + [DisableIfReadOnly()]  # noqa
    can_members_invite      = CommunityPermissionPolicy.can_members_invite                        + [DisableIfReadOnly()]  # noqa
    can_members_manage      = CommunityPermissionPolicy.can_members_manage                        + [DisableIfReadOnly()]  # noqa
    can_members_bulk_update = CommunityPermissionPolicy.can_members_bulk_update                   + [DisableIfReadOnly()]  # noqa
    can_members_bulk_delete = CommunityPermissionPolicy.can_members_bulk_delete                   + [DisableIfReadOnly()]  # noqa
    can_members_update      = CommunityPermissionPolicy.can_members_update                        + [DisableIfReadOnly()]  # noqa
    can_members_delete      = CommunityPermissionPolicy.can_members_delete                        + [DisableIfReadOnly()]  # noqa
    can_invite_owners       = CommunityPermissionPolicy.can_invite_owners                         + [DisableIfReadOnly()]  # noqa
    can_featured_create     = CommunityPermissionPolicy.can_featured_create                       + [DisableIfReadOnly()]  # noqa
    can_featured_update     = CommunityPermissionPolicy.can_featured_update                       + [DisableIfReadOnly()]  # noqa
    can_featured_delete     = CommunityPermissionPolicy.can_featured_delete                       + [DisableIfReadOnly()]  # noqa
    can_set_theme           = CommunityPermissionPolicy.can_set_theme                             + [DisableIfReadOnly()]  # noqa
    can_delete_theme        = CommunityPermissionPolicy.can_delete_theme                          + [DisableIfReadOnly()]  # noqa
    can_manage_children     = CommunityPermissionPolicy.can_manage_children                       + [DisableIfReadOnly()]  # noqa
    can_manage_parent       = CommunityPermissionPolicy.can_manage_parent                         + [DisableIfReadOnly()]  # noqa

    # Used to hide at the moment the `is_verified` field. It should be set to
    # correct permissions based on which the field will be exposed only to moderators
    can_moderate = [Disable()]
    # fmt: on
