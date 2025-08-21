# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 TU Wien.
#
# Invenio-Theme-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

from flask import render_template_string

from invenio_theme_tuw.ext import InvenioThemeTUW


def test_version():
    """Test version import."""
    from invenio_theme_tuw import __version__

    assert __version__


def test_tuw_theme_bp_before_theme(app):
    """
    Test if invenio_theme_tuw is registered before invenio_theme.
    This is essential so that our custom templates are rendered when testing.
    """
    blueprints = list(app.blueprints.keys())
    assert blueprints.index("invenio_theme_tuw") < blueprints.index("invenio_app_rdm")


def test_render_template(app):
    """Test rendering of template."""
    template = r"""
    {% extends 'invenio_theme_tuw/overrides/page.html' %}
    {% block body %}{% endblock %}
    """
    with app.test_request_context():
        assert render_template_string(template)


def test_app_init(app):
    """Test if the initialization of the Invenio-Theme-TUW extension works."""
    InvenioThemeTUW(app)
    assert "invenio-theme-tuw" in app.extensions
    assert "flask-session-captcha" in app.extensions
