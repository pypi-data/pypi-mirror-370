# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 TU Wien.
#
# Invenio-Theme-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for the utility functions."""

from invenio_access.permissions import system_identity
from invenio_accounts.proxies import current_datastore
from invenio_db import db
from invenio_rdm_records.proxies import current_rdm_records_service as rec_service
from invenio_rdm_records.resources.serializers import UIJSONSerializer

from invenio_theme_tuw.utils import (
    fetch_user_infos,
    get_admin_mail_addresses,
    records_serializer,
    resolve_record,
    resolve_user_owner,
    toggle_user_trust,
)


def test_fetch_user_infos(user):
    """Test fetching of user infos."""
    user_infos = fetch_user_infos()
    assert isinstance(user_infos, list)
    assert len(user_infos) == 1

    assert user_infos[0]["user"] == user.user


def test_get_admin_mail_addresses(app):
    """Test fetching the configured admin email addresses."""
    emails = {
        "max": "maximilian.moser@tuwien.ac.at",
        "sotiris": "sotirios.tsepelakis@tuwien.ac.at",
    }
    app.config.pop("APP_RDM_ADMIN_EMAIL_RECIPIENT", None)
    app.config["MAIL_ADMIN"] = emails["max"]

    # if the config item is a string, we still expect a list
    email = get_admin_mail_addresses(app)
    assert isinstance(email, list)
    assert len(email) == 1
    assert email[0] == emails["max"]

    # the value should be taken from MAIL_ADMIN as a fallback...
    app.config["MAIL_ADMIN"] = [emails["max"], emails["sotiris"]]
    email = get_admin_mail_addresses(app)
    assert isinstance(email, list)
    assert len(email) == 2
    assert (email[0], email[1]) == (emails["max"], emails["sotiris"])

    # ... but if configured, we look at APP_RDM_ADMIN_EMAIL_RECIPIENT
    app.config["MAIL_ADMIN"] = "richard.unused.data@tuwien.ac.at"
    app.config["APP_RDM_ADMIN_EMAIL_RECIPIENT"] = [emails["max"], emails["sotiris"]]
    email = get_admin_mail_addresses(app)
    assert isinstance(email, list)
    assert len(email) == 2
    assert (email[0], email[1]) == (emails["max"], emails["sotiris"])


def test_toggle_user_trust(user, vocabularies, trusted_user_role):
    """Test if toggling the "trusted-user" role for users works."""
    user = user.user
    role = current_datastore.find_role("trusted-user")
    assert not user.has_role(role)

    # toggling the role should add the role to the user
    toggle_user_trust(user.id)
    assert user.has_role(role)

    # toggling again should remove the role again
    toggle_user_trust(user.id)
    assert not user.has_role(role)


def test_resolve_record(app, vocabularies, files_loc, minimal_record):
    """Test if resolving records works."""
    record = rec_service.create(system_identity, minimal_record)
    res_rec = resolve_record(record.id)

    # by default, the record service dereferences the relations fields
    # (e.g. referenced resource type, etc.)
    record._obj.relations.clean()
    assert record._obj == res_rec


def test_resolve_user_owner(app, user, vocabularies, files_loc, minimal_record):
    """Test fetching the record's owner (user)."""
    record = rec_service.create(system_identity, minimal_record)._obj
    record.parent.access.owned_by = user.user
    record.parent.commit()
    record.commit()
    db.session.commit()
    assert record.parent.access.owned_by.resolve() is not None

    # if the record has a user as owner, we expect it to be resolved
    owner = resolve_user_owner(record)
    assert owner is user.user


def test_resolve_user_owner_no_owner(app, vocabularies, files_loc, minimal_record):
    """Test fetching the record's owner (user) when it has no owner."""
    record = rec_service.create(system_identity, minimal_record)._obj
    owner = record.parent.access.owned_by.resolve()
    assert owner is not None
    assert isinstance(owner, dict)
    assert owner["id"] == "system"
    assert owner["is_ghost"]

    # if the record has no owner, we expect None as return value
    owner = resolve_user_owner(record)
    assert owner is None


def test_record_serializer(app, vocabularies, files_loc, minimal_record):
    """Test serialization of a list of records."""
    records = []
    serialized_records = []
    for _ in range(5):
        record = rec_service.create(system_identity, minimal_record)
        records.append(record)
        serialized_records.append(UIJSONSerializer().dump_obj(record.to_dict()))

    assert records_serializer(records) == serialized_records


def test_record_serializer_empty():
    """Test serialization of empty list of records."""
    assert records_serializer([]) == []
    assert records_serializer() == []
