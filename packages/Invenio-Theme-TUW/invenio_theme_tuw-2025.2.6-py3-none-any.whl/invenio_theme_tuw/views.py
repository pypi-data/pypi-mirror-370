# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2025 TU Wien.
#
# Invenio-Theme-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""TU Wien theme for Invenio (RDM)."""

import re
from copy import deepcopy
from datetime import datetime

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from invenio_accounts.proxies import current_datastore
from invenio_app_rdm.config import _get_package_version
from invenio_app_rdm.records_ui.views.deposits import deposit_create, deposit_edit
from invenio_communities.proxies import current_communities
from invenio_communities.views.communities import (
    PRIVATE_PERMISSIONS,
    communities_new,
    render_community_theme_template,
)
from invenio_communities.views.decorators import pass_community
from invenio_mail.tasks import send_email
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_rdm_records.proxies import (
    current_community_records_service as com_rec_service,
)
from invenio_rdm_records.proxies import current_rdm_records_service as rec_service
from invenio_rdm_records.resources.serializers import (
    SchemaorgJSONLDSerializer,
    UIJSONSerializer,
)
from sqlalchemy.exc import NoResultFound

from .community_stats import (
    create_events_query,
    display_discrete_counts,
    map_folium,
    process_query,
)
from .search import FrontpageRecordsSearch
from .utils import (
    fetch_user_infos,
    get_admin_mail_addresses,
    records_serializer,
    resolve_record,
    resolve_user_owner,
    toggle_user_trust,
)


def _ui_serialize(rec):
    """Wrapper for the ``UIJSONSerializer`` handling various stages of records."""
    if isinstance(rec, (rec_service.draft_cls, rec_service.record_cls)):
        rec = rec_service.result_item(rec_service, g.identity, rec)

    return UIJSONSerializer().dump_obj(rec if isinstance(rec, dict) else rec.to_dict())


@login_required
def guarded_deposit_create(*args, **kwargs):
    """Guard the creation page for records, based on permissions."""
    if not rec_service.check_permission(g.identity, "create"):
        return (
            render_template("invenio_theme_tuw/guards/deposit.html", user=current_user),
            403,
        )

    return deposit_create(*args, **kwargs)


@login_required
def guarded_deposit_edit(*args, **kwargs):
    """Guard the edit page for records, based on permissions."""
    # NOTE: this extra loading of the draft introduces an extra DB query, but i think
    #       it should not make too much of a difference for us
    try:
        draft = rec_service.draft_cls.pid.resolve(
            kwargs["pid_value"], registered_only=False
        )
    except (PIDDoesNotExistError, NoResultFound):
        return render_template(current_app.config["THEME_404_TEMPLATE"]), 404

    if not rec_service.check_permission(g.identity, "update_draft", record=draft):
        if not rec_service.check_permission(g.identity, "preview", record=draft):
            return (
                render_template(
                    "invenio_theme_tuw/guards/deposit.html", user=current_user
                ),
                403,
            )
        else:
            # if the user has permission to preview the draft but not to edit it,
            # redirect them to the preview page
            return redirect(
                url_for(
                    "invenio_app_rdm_records.record_detail",
                    pid_value=draft.pid.pid_value,
                    preview=1,
                )
            )

    return deposit_edit(*args, **kwargs)


@login_required
def guarded_communities_create(*args, **kwargs):
    """Guard the communities creation page, based on permissions."""
    if not current_communities.service.check_permission(g.identity, "create"):
        return (
            render_template(
                "invenio_theme_tuw/guards/community.html", user=current_user
            ),
            403,
        )

    return communities_new(*args, **kwargs)


def tuw_index():
    """Custom landing page showing the latest 5 records."""
    try:
        records = FrontpageRecordsSearch()[:5].sort("-created").execute()
    except Exception as e:
        current_app.logger.error(e)
        records = []

    return render_template(
        "invenio_theme_tuw/overrides/frontpage.html",
        records=records_serializer(records),
    )


@login_required
@pass_community(serialize=True)
def community_statistics(pid_value, community, community_ui):
    """Show monthly usage statistics for all records in a community."""
    records = com_rec_service.search(g.identity, pid_value)
    records_by_recid = {r["id"]: r for r in records}

    permissions = community.has_permissions_to(PRIVATE_PERMISSIONS)
    if not permissions["can_search_requests"]:
        abort(403)
    elif not records:
        abort(404)

    # Get the query args
    stats_type = request.args.get("type", "both")
    recid = request.args.get("recid")
    month = request.args.get("month")

    # Validate the query args
    if not recid or recid not in records_by_recid:
        recid, *_ = records_by_recid

    try:
        month = re.sub(r"(\d{1,5}-\d{1,2})-\d{1,2}", r"\1", month, count=1)
        month = datetime.strptime(month, "%Y-%m")
    except (TypeError, ValueError):
        month = None
    if not month:
        month = datetime.today()
    month = month.strftime("%Y-%m")

    if stats_type not in ["view", "download", "both"]:
        stats_type = "both"

    record_stats = process_query(create_events_query(stats_type, recid, month))
    if record_stats:
        countries, counts = zip(*record_stats.items(), strict=False)
    else:
        countries, counts = [], []

    # Note: the map's root needs to be rendered before its components can be rendered
    fmap = map_folium(countries, counts, height=600, attributionControl=False)
    map_root = fmap.get_root()
    map_root.render()

    dataframe = display_discrete_counts(record_stats)

    record = records_by_recid[recid]
    return render_community_theme_template(
        "invenio_communities/details/statistics/index.html",
        theme=community_ui.get("theme", {}),
        community=community,
        community_ui=community_ui,
        stats_type=stats_type,
        month=month,
        stats=record_stats,
        record=record,
        record_ui=_ui_serialize(record),
        records=records,
        map_html=map_root.html.render(),
        map_header=map_root.header.render(),
        map_script=map_root.script.render(),
        table_html=dataframe.to_html(),
        permissions=permissions,
    )


def create_blueprint(app):
    """Create a blueprint with routes and resources."""
    blueprint = Blueprint(
        "invenio_theme_tuw",
        __name__,
        template_folder="theme/templates",
        static_folder="theme/static",
    )

    @blueprint.app_template_filter("tuw_doi_identifier")
    def tuw_doi_identifier(identifiers):
        """Extract DOI from sequence of identifiers."""
        if identifiers is not None:
            for identifier in identifiers:
                if identifier.get("scheme") == "doi":
                    return identifier.get("identifier")

    @blueprint.app_template_global("tuw_create_schemaorg_metadata")
    def tuw_create_schemaorg_metadata(record):
        """Create schema.org metadata to include in a <script> tag."""
        try:
            # since v13, record will be a `ResultItem` rathter than a `Record`
            if hasattr(record, "_obj"):
                record = record._obj
            return SchemaorgJSONLDSerializer().serialize_object(record)
        except Exception as e:
            current_app.logger.error(e)
            return '{"@context": "http://schema.org"}'

    @blueprint.app_template_global("record_count")
    def record_count():
        try:
            return FrontpageRecordsSearch().count()
        except Exception:
            return "all"

    @blueprint.route("/tuw/contact-uploader/<recid>", methods=["GET", "POST"])
    def contact_uploader(recid):
        """Contact page for the contact's uploader."""
        if not current_app.config.get("THEME_TUW_CONTACT_UPLOADER_ENABLED", False):
            abort(404)

        captcha = current_app.extensions["invenio-theme-tuw"].captcha
        record = resolve_record(recid)
        form_values = request.form.to_dict()
        if current_user and not current_user.is_anonymous:
            form_values.setdefault("name", current_user.user_profile.get("full_name"))
            form_values.setdefault("email", current_user.email)

        if record is None:
            abort(404)

        owner = record.parent.access.owned_by
        if not owner:
            abort(404)

        owner = owner.resolve()

        submitted = False
        captcha_failed = False
        if request.method == "POST":
            # NOTE: the captcha is a simple spam prevention measure, and it also
            #       prevents the form from being accidentally resubmitted wia refresh
            if not current_app.config["CAPTCHA_ENABLE"] or captcha.validate():
                sitename = current_app.config["THEME_SITENAME"]
                sender_name = request.form["name"]
                sender_email = request.form["email"]
                inquiry = request.form["message"] or "<Empty Message>"
                msg_kwargs = {
                    "sender_name": sender_name,
                    "sender_email": sender_email,
                    "message": inquiry,
                    "uploader": owner,
                    "record": record,
                    "record_ui": _ui_serialize(record),
                }
                html_message = render_template(
                    "invenio_theme_tuw/mails/contact.html",
                    **msg_kwargs,
                )
                message = render_template(
                    "invenio_theme_tuw/mails/contact.txt",
                    **msg_kwargs,
                )

                secondary_email = owner.preferences.get("notifications", {}).get(
                    "secondary_email", None
                )
                record_title = record.metadata["title"]
                send_email(
                    {
                        "subject": f'{sitename}: Inquiry about your record "{record_title}" from {sender_name}',
                        "html": html_message,
                        "body": message,
                        "recipients": [owner.email],
                        "cc": [secondary_email] if secondary_email else [],
                        "bcc": get_admin_mail_addresses(current_app),
                        "reply_to": sender_email,
                    }
                )

                # if enabled, send confirmation email to the inquirer
                send_confirmation_email = current_app.config.get(
                    "THEME_TUW_CONTACT_UPLOADER_SEND_CONFIRMATION", False
                )
                if send_confirmation_email:
                    html_message = render_template(
                        "invenio_theme_tuw/mails/contact_confirm.html",
                        **msg_kwargs,
                    )
                    message = render_template(
                        "invenio_theme_tuw/mails/contact_confirm.txt",
                        **msg_kwargs,
                    )
                    send_email(
                        {
                            "subject": f"{sitename}: Your inquiry has been sent",
                            "html": html_message,
                            "body": message,
                            "recipients": [sender_email],
                        }
                    )

                submitted = True

            else:
                captcha_failed = True

        response = render_template(
            "invenio_theme_tuw/contact_uploader.html",
            uploader=owner,
            submitted=submitted,
            record=record,
            record_ui=_ui_serialize(record),
            captcha_failed=captcha_failed,
            form_values=form_values,
        )
        return response, 200 if not captcha_failed else 428

    @blueprint.route("/about")
    def tuw_about_redirect():
        """Redirect to our actual about page."""
        return redirect(url_for(".tuw_about"), code=301)

    @blueprint.route("/tuw/about")
    def tuw_about():
        """Page showing general information about TUWRD."""
        return render_template(
            "invenio_theme_tuw/about.html", package_version=_get_package_version()
        )

    @blueprint.route("/tuw/about/api")
    def tuw_about_api():
        """Page showing information about the TUWRD API."""
        return render_template("invenio_theme_tuw/about_api.html")

    @blueprint.route("/tuw/about/damap")
    def tuw_about_damap():
        """Page showing information about the TUWRD API."""
        return render_template("invenio_theme_tuw/about_damap.html")

    @blueprint.route("/tuw/about/vre")
    def tuw_about_vre():
        """Page showing information about the TUWRD API."""
        return render_template("invenio_theme_tuw/about_vre.html")

    @blueprint.route("/tuw/policies")
    def tuw_policies():
        """Page showing the available repository policies."""
        return render_template("invenio_theme_tuw/policies.html")

    @blueprint.route("/tuw/terms-of-use")
    def tuw_terms_of_use():
        """Page showing the repository's terms of use documents."""
        return render_template("invenio_theme_tuw/terms_of_use.html")

    @blueprint.route("/tuw/contact")
    def tuw_contact():
        """Contact page."""
        return render_template("invenio_theme_tuw/contact.html")

    @blueprint.route("/tuw/admin/users", methods=["GET", "POST"])
    def list_user_info():
        """Hacky endpoint for listing user information."""
        admin_role = current_datastore.find_role("admin")
        if current_user and current_user.has_role(admin_role):

            # handle trusting of user
            if request.method == "POST":
                if (user_id := request.form.get("user_id", None)) is not None:
                    try:
                        flash(toggle_user_trust(user_id))
                    except Exception as e:
                        flash(e)

            return render_template(
                "invenio_theme_tuw/users_infos.html",
                user_infos=fetch_user_infos(),
            )
        else:
            abort(403)

    @blueprint.route("/tuw/admin/users/welcome")
    def show_user_welcome_text():
        """Show the welcome text for new users, to be sent to them via email."""
        admin_role = current_datastore.find_role("admin")
        if current_user and current_user.has_role(admin_role):
            uid = request.args.get("uid", None)

            if user := current_datastore.get_user(uid):
                return render_template(
                    "invenio_theme_tuw/users_welcome.html",
                    user=user,
                )
            else:
                # if the user can't be found, redirect to the overview
                return redirect(url_for(".list_user_info"))

        else:
            abort(403)

    @blueprint.route("/tuw/admin/task-failures")
    def list_task_failures():
        from invenio_config_tuw.proxies import current_config_tuw

        return render_template(
            "invenio_theme_tuw/task_failures.html",
            failures=sorted(
                current_config_tuw.get_stored_task_failures(),
                key=lambda f: f.get("timestamp"),
                reverse=True,
            ),
        )

    @blueprint.route("/tuwstones/florian.woerister")
    def tuw_tombstone_florian():
        """Tombstone page for Florian Wörister."""
        return render_template("invenio_theme_tuw/tuwstones/florian_woerister.html")

    @blueprint.route("/tuwstones/derek.molnar")
    def tuw_tombstone_derek():
        """Tombstone page for Derek Molnar."""
        return render_template("invenio_theme_tuw/tuwstones/derek_molnar.html")

    # register filters for showing uploaders
    blueprint.add_app_template_filter(resolve_record)
    blueprint.add_app_template_filter(resolve_user_owner)

    # register the per-community KPI stats endpoint, with laxer CSP headers
    # to allow for the CDNs required by the Folium map
    talisman = app.extensions["invenio-app"].talisman
    default_secure_headers = app.config.get("APP_DEFAULT_SECURE_HEADERS", {})
    csp = deepcopy(default_secure_headers.get("content_security_policy", {}))
    csp.setdefault("script-src", []).extend(
        ["cdn.jsdelivr.net", "code.jquery.com", "cdnjs.cloudflare.com"]
    )

    wrapper = talisman(content_security_policy={})
    blueprint.add_url_rule(
        "/communities/<pid_value>/statistics", view_func=wrapper(community_statistics)
    )

    return blueprint
