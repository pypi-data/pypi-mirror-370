# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 TU Wien.
#
# Invenio-Theme-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test specific functions."""

import html
import json

import pytest
from flask import render_template_string
from flask_login import current_user
from invenio_access.permissions import system_identity
from invenio_accounts.proxies import current_datastore
from invenio_communities.proxies import current_communities
from invenio_db import db
from invenio_rdm_records.proxies import current_rdm_records_service as rec_service
from invenio_rdm_records.proxies import (
    current_record_communities_service as rec_com_service,
)
from invenio_records_permissions.generators import AuthenticatedUser
from invenio_requests.proxies import current_requests_service

from invenio_theme_tuw.views import (
    guarded_communities_create,
    guarded_deposit_create,
    guarded_deposit_edit,
)


@pytest.fixture()
def admin_user(user, admin_role):
    """Give the created user the admin role."""
    if not (had_admin_role := user.user.has_role(admin_role)):
        current_datastore.add_role_to_user(user.user, admin_role)

    yield user

    if not had_admin_role:
        current_datastore.remove_role_from_user(user.user, admin_role)


def test_tuw_create_schemaorg_metadata(
    app, vocabularies, minimal_record, files_loc, search_indices
):
    """Test Schema.org metadata creation."""
    record = rec_service.create(system_identity, minimal_record)
    template = r"{{ tuw_create_schemaorg_metadata(record) }}"
    with app.test_request_context():
        result = render_template_string(template, record=record.to_dict())
        parsed = json.loads(html.unescape(result))
        assert result and parsed
        assert "TU Wien" in result
        assert parsed["publisher"]["name"] == "TU Wien"
        for key in [
            "@context",
            "@type",
            "identifier",
            "name",
            "creator",
            "author",
            "publisher",
            "datePublished",
            "dateModified",
            "url",
        ]:
            assert key in parsed


#
# Contact uploader form
#


def test_contact_uploader_form(
    app, client, user, vocabularies, files_loc, minimal_record
):
    """Test rendering of the "contact uploader" form."""
    assert "invenio-theme-tuw" in app.extensions
    record = rec_service.create(system_identity, minimal_record)._obj
    record.parent.access.owned_by = user.user
    record.parent.commit()
    record.commit()
    db.session.commit()

    # test a simple GET for the contact form
    response = client.get(f"/tuw/contact-uploader/{record.pid.pid_value}")
    assert response.status_code == 200
    assert 'method="POST"' in response.text
    assert record.metadata["title"] in response.text
    assert user.user.user_profile["full_name"] in response.text


def test_contact_uploader_form_post_without_captcha(
    app, client, user, vocabularies, files_loc, minimal_record
):
    """Test using the "contact uploader" form."""
    assert "invenio-theme-tuw" in app.extensions
    app.config["CAPTCHA_ENABLE"] = False
    record = rec_service.create(system_identity, minimal_record)._obj
    record.parent.access.owned_by = user.user
    record.parent.commit()
    record.commit()
    db.session.commit()

    # test submitting the contact form with captcha disabled
    response = client.post(
        f"/tuw/contact-uploader/{record.pid.pid_value}",
        data={"name": "Max Moser", "email": "max@tuwien.ac.at", "message": "Hi there!"},
    )
    assert response.status_code == 200
    assert "Inquiry submitted" in response.text
    assert user.user.user_profile["full_name"] in response.text


def test_contact_uploader_form_post_wrong_captcha(
    app, client, user, vocabularies, files_loc, minimal_record
):
    """Test the "contact uploader" form's captcha."""
    assert "invenio-theme-tuw" in app.extensions
    app.config["CAPTCHA_ENABLE"] = True
    record = rec_service.create(system_identity, minimal_record)._obj
    record.parent.access.owned_by = user.user
    record.parent.commit()
    record.commit()
    db.session.commit()

    # test submitting the contact form with an invalid captcha
    response = client.post(
        f"/tuw/contact-uploader/{record.pid.pid_value}",
        data={
            "name": "Max Moser",
            "email": "max@tuwien.ac.at",
            "message": "Hi there!",
            "captcha": "!thiscan'tbethecorrectanswer#",
        },
    )
    assert response.status_code == 428
    assert "Captcha mismatch" in response.text


#
# Guarded create/edit pages
#


def test_deposit_create_allowed(app, user, vocabularies):
    """Test deposit guard. Allowing creation case."""
    # default behavior is to allow creation, no further action required
    response = guarded_deposit_create()
    assert "deposit-form" in response.data.decode()


def test_deposit_create_denied(app, user, reset_permissions):
    """Test deposit guard. Denying creation case."""
    # deny create permission
    rec_service.config.permission_policy_cls.can_create = []

    response, status_code = guarded_deposit_create()
    assert (
        "For your first upload, your account must be manually activated by our team"
        in response
    )
    assert status_code == 403


def test_deposit_edit_guard_allowed(app, user, vocabularies, files_loc, minimal_record):
    """Test deposit guard. Allowing edit case."""
    draft = rec_service.create(user.identity, minimal_record)

    # test if we can access the deposit page if we have permissions
    response = guarded_deposit_edit(pid_value=draft.id)
    assert response.status_code == 200
    assert isinstance(response.data.decode(), str)
    assert "deposit-form" in response.data.decode()


def test_deposit_edit_guard_preview_redirect(
    app, user, vocabularies, files_loc, minimal_record, reset_permissions
):
    """Test deposit guard. Denying edit case."""
    rec_service.config.permission_policy_cls.can_update_draft = []
    draft = rec_service.create(user.identity, minimal_record)

    # let's check if the guarded deposit edit page redirects us to the preview page
    # response status code: 3xx
    response = guarded_deposit_edit(pid_value=draft.id)
    assert not isinstance(response, str)
    assert 300 <= response.status_code < 400
    assert "preview=1" in response.location.split("?", 1)[1]
    assert draft.id in response.location


def test_deposit_edit_guard_deny(
    app, user, vocabularies, files_loc, minimal_record, reset_permissions
):
    """Test deposit guard. Denying edit case."""
    rec_service.config.permission_policy_cls.can_update_draft = []
    rec_service.config.permission_policy_cls.can_preview = []
    draft = rec_service.create(user.identity, minimal_record)

    # let's check if the guarded deposit edit page returns a 403 response
    response = guarded_deposit_edit(pid_value=draft.id)
    assert not isinstance(response, str)
    assert len(response) == 2
    assert response[1] == 403


def test_community_create_guard_allowed(
    app, user, vocabularies, files_loc, minimal_record
):
    """Test if the deposit guard page lets allowed users through."""
    permissions = current_communities.service.config.permission_policy_cls
    old_can_create = permissions.can_create
    permissions.can_create = [AuthenticatedUser()]

    response = guarded_communities_create()
    assert isinstance(response, str)
    assert "data-form-config" in response

    permissions.can_create = old_can_create


def test_community_create_guard_denied(
    app, user, vocabularies, files_loc, minimal_record
):
    """Test if the deposit guard page lets blocks unauthorized users."""
    permissions = current_communities.service.config.permission_policy_cls
    old_can_create = permissions.can_create
    permissions.can_create = []

    # let's check if the guarded deposit edit page returns a 403 response
    response = guarded_communities_create()
    assert not isinstance(response, str)
    assert len(response) == 2
    assert response[1] == 403

    permissions.can_create = old_can_create


#
# Admin stuff
#


def test_admin_user_list(app, client_with_login, admin_user, admin_role):
    """Test the user list for admins."""
    client = client_with_login
    response = client.get("/tuw/admin/users")
    assert response.status_code == 200
    assert str(admin_user.user.id) in response.text
    assert admin_user.user.user_profile["full_name"] in response.text
    assert admin_user.user.email in response.text


def test_admin_user_list_toggle_trust(
    app, client_with_login, admin_user, admin_role, trusted_user_role
):
    """Test the user list for admins."""
    client = client_with_login
    had_trusted_user_role = admin_user.user.has_role(trusted_user_role)

    response = client.post("/tuw/admin/users", data={"user_id": admin_user.user.id})
    assert response.status_code == 200

    assert admin_user.user.has_role(trusted_user_role) != had_trusted_user_role


def test_admin_welcome_text(app, client_with_login, admin_user, admin_role):
    """Test the user list for admins."""
    client = client_with_login
    response = client.get(f"/tuw/admin/users/welcome?uid={admin_user.user.id}")
    assert response.status_code == 200
    assert f"Dear {admin_user.user.user_profile['full_name']}" in response.text


#
# Community Statistics
#


def test_community_kpi_dashboard(
    app, client_with_login, files_loc, minimal_record, vocabularies, search_indices
):
    """General test for the per-community KPI dashboard."""
    svc = current_communities.service

    # create a new community with a record
    slug = "xcom"
    com = svc.create(
        system_identity,
        {
            "slug": slug,
            "metadata": {"title": slug},
            "access": {
                "visibility": "public",
            },
        },
    )
    draft = rec_service.create(system_identity, minimal_record)._obj
    record = rec_service.publish(system_identity, draft.pid.pid_value)._obj
    _requests, _errors = rec_com_service.add(
        system_identity, record.pid.pid_value, {"communities": [{"id": slug}]}
    )
    record.index.refresh()

    # note: in v13, inclusion requests get accepted automatically by the system,
    #       depending on the `com.access.review_policy` and the identity
    #       (the system is always allowed to publish directly into the community)
    if _requests[0]["request"]["status"] != "accepted":
        req_id = _requests[0]["request_id"]
        current_requests_service.execute_action(system_identity, req_id, "accept")

    record.index.refresh()
    response = client_with_login.get(f"/communities/{slug}/statistics")
    assert response.status_code == 403

    # invite the user & accept the invite
    current_communities.service.members.invite(
        system_identity,
        com.id,
        {"members": [{"type": "user", "id": str(current_user.id)}], "role": "reader"},
    )
    current_requests_service.record_cls.index.refresh()
    invite, *_ = current_requests_service.search(
        system_identity,
        {
            "type": "community-invitation",
            "topic": {"community": com.id},
            "receiver": {"user": str(current_user.id)},
        },
    )
    current_communities.service.members.accept_invite(system_identity, invite["id"])

    # check that the "reader" role is not enough
    response = client_with_login.get(f"/communities/{slug}/statistics")
    assert response.status_code == 403

    # update role & check if that worked
    current_communities.service.members.update(
        system_identity,
        com.id,
        {"role": "owner", "members": [{"type": "user", "id": str(current_user.id)}]},
    )
    response = client_with_login.get(f"/communities/{slug}/statistics")
    assert response.status_code == 200
