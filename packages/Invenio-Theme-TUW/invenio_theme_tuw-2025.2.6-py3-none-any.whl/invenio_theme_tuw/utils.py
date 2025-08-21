# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 TU Wien.
#
# Invenio-Theme-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Utility functions for Invenio-Theme-TUW."""

from invenio_accounts.models import User
from invenio_accounts.proxies import current_datastore
from invenio_db import db
from invenio_rdm_records.proxies import current_rdm_records_service as rec_service
from invenio_rdm_records.resources.serializers import UIJSONSerializer
from sqlalchemy.exc import NoResultFound


def resolve_record(recid):
    """Resolve the record with the given recid into an API class object."""
    try:
        return rec_service.record_cls.pid.resolve(recid, registered_only=False)
    except NoResultFound:
        # if no record can be found for the ID, let's try if we can find a draft
        # (e.g. in the case of a draft preview)
        #
        # note: `invenio_pidstore.errors` contains further exceptions that could
        #       be raised during the PID resolution
        return rec_service.draft_cls.pid.resolve(recid, registered_only=False)


def resolve_user_owner(record):
    """Resolve the first user-type owner of the record.

    The record is expected to be an API-class object, and the result will be a User
    model object.
    If the owner is not of type "user", or if it is the "system", then ``None`` will
    be returned.
    """
    owner = record.parent.access.owner
    if not owner or owner.owner_type != "user" or owner.owner_id == "system":
        return None

    return owner.resolve()


def fetch_user_infos():
    """Fetch information about each user for our hacky user info list."""
    user_infos = []
    trusted_user_role = current_datastore.find_role("trusted-user")

    for user in db.session.query(User).order_by(User.id.desc()).all():
        # check if the user has given us consent for record curation
        curation_consent = (user.preferences or {}).get("curation_consent", True)

        # check if the user can upload datasets
        trusted = user.has_role(trusted_user_role)

        info = {
            "user": user,
            "tiss_id": (user.user_profile or {}).get("tiss_id", None),
            "curation_consent": curation_consent,
            "trusted": trusted,
        }

        user_infos.append(info)

    return user_infos


def toggle_user_trust(user_id):
    """Add the "trusted-user" role to the user or remove it."""
    trusted_user_role = current_datastore.find_role("trusted-user")
    user = current_datastore.find_user(id=user_id)

    if not user.has_role(trusted_user_role):
        current_datastore.add_role_to_user(user, trusted_user_role)
        verb = "Trusted"
    else:
        current_datastore.remove_role_from_user(user, trusted_user_role)
        verb = "Untrusted"

    db.session.commit()
    user_name = user.user_profile.get("full_name") if user.user_profile else "N/A"
    return f"{verb} user #{user_id} ({user_name or 'N/A'})"


def records_serializer(records=None):
    """Serialize list of records."""
    record_list = []
    for record in records or []:
        record_list.append(UIJSONSerializer().dump_obj(record.to_dict()))
    return record_list


def get_admin_mail_addresses(app):
    """Get the configured email addresses for administrators."""
    addresses = app.config.get(
        "APP_RDM_ADMIN_EMAIL_RECIPIENT", app.config.get("MAIL_ADMIN")
    )

    # the config variable is expected to be either a list or a string
    if addresses and isinstance(addresses, str):
        addresses = [addresses]

    return addresses
