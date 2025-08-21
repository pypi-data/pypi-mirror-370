# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 TU Wien.
#
# Invenio-Theme-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Setup functions to be executed on application startup."""

from flask import request
from flask_limiter import Limiter
from flask_menu import current_menu
from invenio_access.permissions import system_identity as sys_id
from invenio_administration.permissions import administration_permission
from invenio_app.limiter import useragent_and_ip_limit_key
from invenio_base.utils import obj_or_import_string
from invenio_i18n import lazy_gettext as _
from invenio_rdm_records.proxies import current_community_records_service as com_rec_svc

from .views import (
    guarded_communities_create,
    guarded_deposit_create,
    guarded_deposit_edit,
    tuw_index,
)


def _get_limiter(app):
    """Get the configured limiter, or initialize it if not available."""
    limiter = app.extensions["invenio-app"].limiter
    if limiter is None:
        limiter = Limiter(
            app,
            key_func=obj_or_import_string(
                app.config.get("RATELIMIT_KEY_FUNC"), default=useragent_and_ip_limit_key
            ),
        )

    return limiter


def override_bp_order(app):
    """Rearrange the order of registered blueprints.

    This ensures that jinja templates are loaded from Theme-TUW rather than other
    modules, which enables overriding of core templates (cf. `flask.render_template()`).
    This operation needs to be performed after all the blueprints have been registered.
    """
    bps = {}
    theme_tuw_bp = None
    for name, bp in app.blueprints.items():
        if name == "invenio_theme_tuw":
            theme_tuw_bp = bp
        else:
            bps[name] = bp

    app.blueprints = {"invenio_theme_tuw": theme_tuw_bp, **bps}


def override_view_functions(app):
    """Override the existing view functions with more access control."""
    app.view_functions["invenio_app_rdm.index"] = tuw_index

    # we have some additional role-based permissions (trusted-user) that decide
    # among other things if people can create records/drafts
    # this is not considered in the original view functions, which is why we
    # currently need to wrap them with our own guards
    app.view_functions["invenio_app_rdm_records.deposit_edit"] = guarded_deposit_edit
    app.view_functions["invenio_app_rdm_records.deposit_create"] = (
        guarded_deposit_create
    )
    app.view_functions["invenio_communities.communities_new"] = (
        guarded_communities_create
    )

    # limit the amount of contact requests that can be made per time period
    # (this needs to be done after the Flask-Limiter extension has been init.)
    if (limiter := _get_limiter(app)) is not None:
        limit_value = app.config.get("THEME_TUW_CONTACT_UPLOADER_RATE_LIMIT", "5/day")
        contact_uploader_view_func = app.view_functions[
            "invenio_theme_tuw.contact_uploader"
        ]
        app.view_functions["invenio_theme_tuw.contact_uploader"] = limiter.limit(
            limit_value, methods=["POST"]
        )(contact_uploader_view_func)


def register_menu_entries(app):
    """Register custom menu entries, for communities and the users administration."""
    current_menu.submenu("profile-admin.tuw_task_failures").register(
        endpoint="invenio_theme_tuw.list_task_failures",
        text=_(
            "%(icon)s Background task failures",
            icon='<i class="frown icon"></i>',
        ),
        order=2,
        visible_when=lambda: administration_permission.can(),
    )

    current_menu.submenu("profile-admin.user_infos").register(
        endpoint="invenio_theme_tuw.list_user_info",
        text=_(
            "%(icon)s TUW users administration",
            icon='<i class="users icon"></i>',
        ),
        order=3,
        visible_when=lambda: administration_permission.can(),
    )

    # note: the permissions kwarg already takes care of visibility settings
    current_menu.submenu("communities").submenu("statistics").register(
        endpoint="invenio_theme_tuw.community_statistics",
        text=_("Statistics"),
        order=70,
        expected_args=["pid_value"],
        visible_when=lambda: com_rec_svc.search(sys_id, request.community["id"]).total,
        **{"icon": "chart line", "permissions": "can_search_requests"},
    )
