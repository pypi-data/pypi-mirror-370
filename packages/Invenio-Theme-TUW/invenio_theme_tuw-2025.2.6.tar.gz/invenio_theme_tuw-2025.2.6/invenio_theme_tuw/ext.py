# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 TU Wien.
#
# Invenio-Theme-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module containing the theme for TU Wien."""


from flask_session_captcha import FlaskSessionCaptcha

from . import config


class InvenioThemeTUW:
    """Invenio-Theme-TUW extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        self.init_captcha_extension(app)
        app.extensions["invenio-theme-tuw"] = self

    def init_captcha_extension(self, app):
        """Initialize the Flask-Session-Captcha extension."""
        self.captcha = FlaskSessionCaptcha()
        app.extensions["flask-session-captcha"] = self.captcha

        try:
            self.captcha.init_app(app)
        except RuntimeWarning as w:
            app.logger.warn(w)

    def init_config(self, app):
        """Initialize configuration."""
        # Use theme's base template if theme is installed
        for k in dir(config):
            app.config.setdefault(k, getattr(config, k))
