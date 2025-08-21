..
    Copyright (C) 2020-2025 TU Wien.

    Invenio-Config-TUW is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.

====================
 Invenio-Config-TUW
====================

Invenio package for tweaking InvenioRDM to the needs of TU Wien.

The following list is a quick overview of the most relevant customizations happening in this package:

* Configuration values
* Permission policies
* Mandatory submission reviews
* OIDC authentication handling
* E-Mail notification on errors
* Customized notification backends
* User profile extension
* Integration with other TU Wien services
* Custom background tasks


Details
=======

Configuration values
--------------------

The primary purpose of this Invenio package is to provide some baseline configuration for InvenioRDM to suit deployment at TU Wien.
These updated configurations include (but are not limited to) setting default values for record metadata and enabling access requests for restricted records per default.


Permission policies
-------------------

InvenioRDM is not just some sort of cheap storage platform where users can upload their data and update it at any time.
Instead, it is a platform intended to host digital objects that get `DOIs <https://www.doi.org/>`_ assigned.
Since the idea behind DOIs (and persistent identifiers in general) is to point at the same content over time, it does not allow users to change the files after publication.

This is one of the unique features that the system offers that may not be immediately obvious to users.
To make sure that users understand the implications of using the system, we require a brief communication between the users and operators.

In contrast to vanilla InvenioRDM, having an account is not enough to create uploads in our system.
Instead, the creation of records requires the ``trusted-user`` role, which typically has to be given out by administrators.

Also, communities can be quite confusing in the beginning.
Thus, we restrict the creation of new communities for non-administrators.


Mandatory submission reviews
----------------------------

Before any upload can be published, it needs to undergo a mandatory submission review.
This enhances the quality, reusability, and long-term preservation of uploaded content.

Previously, this was implemented via customized permission policies and required communication via external channels.
As of ``v2025.1.0``, the workflow is based on `Invenio-Curations <https://github.com/tu-graz-library/invenio-curations>`_.
This allows the entire workflow to be handled through the system, and allows the system to act as a ticketing system for reviews.


OIDC authentication handling
----------------------------

We do not want to handle certain aspects like password management of user management in our system.
Instead, we offload authentication to a separate service, with which InvenioRDM communicates via OIDC.
Sometimes we have slightly non-standard requirements, which are satisfied by the authentication handler logic in this package.


E-Mail notification on errors
-----------------------------

This package defines a custom log handler for error-level logs which sends out notifications as e-mail to a set of configured recipient addresses.


Customized notification backends
--------------------------------

To make setting automatic email handling rules simple, we set the ``X-Sender`` email header field to a configurable value.


User profile extension
----------------------

We forgot to secure the rights to curate metadata for uploads in our system in the first version of the terms of use.
So instead, we extended the user profiles to collect consent for curation individually per user.


Integration with other TU Wien services
---------------------------------------

One of the benefits of hosting InvenioRDM as an institutional repository is that it enables some conveniences by integrating with the local environment more.
For example, we integrate with `TISS <https://tiss.tuwien.ac.at/>`_ by periodically querying it for TU Wien employees and adding their names to the controlled vocabulary of known ``names``.


Custom background tasks
-----------------------

To make the continued operation of the system smoother, this package also provides some background tasks:

* Reminder notifications to reviewers about open submission reviews
* Reminder notifications to users about accepted submissions
* Periodic updates of the ``names`` vocabulary via TISS
