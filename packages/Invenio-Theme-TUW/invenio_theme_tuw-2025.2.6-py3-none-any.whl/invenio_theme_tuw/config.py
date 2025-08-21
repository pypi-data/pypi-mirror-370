# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2025 TU Wien.
#
# Invenio-Theme-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""TU Wien theme for Invenio (RDM)."""


def default_forecast():
    """It's Always Sunny in Vienna."""
    return "sunny"


THEME_TUW_MATOMO_ENABLED = False
"""Controls whether or not to include the JS snippet for Matomo in the base template."""

THEME_TUW_MATOMO_URL = "https://s191.dl.hpc.tuwien.ac.at/"
"""The URL under which Matomo is reachable."""

THEME_TUW_MATOMO_SITE_ID = "1"
"""An identifier for the site, to be used by Matomo."""

THEME_TUW_HEADER_WARNING = None
"""The (HTML-formatted) message to display in the header.

A value of ``None`` (which is the default) causes the message box to not be displayed.
"""

THEME_TUW_CONTACT_EMAIL = "tudata@tuwien.ac.at"
"""The e-mail address provided as contact."""

APP_THEME = ["semantic-ui"]
"""The application theme to use."""

THEME_TUW_COMMUNITY_PERMISSION_ERROR_PARAGRAPH = None
"""Paragraph to show on the communities permission guard page."""

THEME_TUW_DEPOSIT_PERMISSION_ERROR_PARAGRAPH = None
"""Paragraph to show on the deposit permission guard page."""

THEME_TUW_CRDM_URL = "https://www.tuwien.at/en/research/rti-support/research-data"
"""The URL pointing to more information about (Center of) RDM at TU Wien."""

THEME_TUW_FAQ_URL = "https://www.tuwien.at/en/research/rti-support/research-data/info-and-guidelines/preserving-and-publishing/tuw-data-repository-faq"  # noqa
"""The URL to the FAQ page to be displayed."""

THEME_TUW_FILE_FORMATS_URL = "https://www.tuwien.at/en/research/rti-support/research-data/rdm-infos-tips/preserving-and-publishing/file-formats"  # noqa
"""The URL to the recommended files format page to be displayed."""

THEME_TUW_UPLOAD_GUIDE_URL = "https://www.tuwien.at/fileadmin/Assets/forschung/Zentrum_Forschungsdatenmanagement/pdf-Sammlung/Upload-Guide_TUWRD.pdf"  # noqa
"""The URL for our upload guide."""

THEME_TUW_CONTACT_UPLOADER_ENABLED = True
"""Feature flag for enabling/disabling the "contact uploader" feature."""

THEME_TUW_CONTACT_UPLOADER_RATE_LIMIT = "5/day"
"""Rate limit for "contact uploader" attempts, via ``Flask-Limiter``."""

THEME_TUW_CONTACT_UPLOADER_SEND_CONFIRMATION = False
"""Whether or not to send a confirmation mail to the inquirer in "contact uploader".

This flag replaced ``THEME_TUW_CONTACT_UPLOADER_ADD_EMAIL_TO_CC``, since we're
now adding the uploader's secondary email address to CC.
Adding both the specified inquirer's email address and the uploader's secondary email
address might leak private information.
"""

THEME_TUW_FORECAST = default_forecast
"""Function for checking the upcoming weather."""

THEME_TUW_TEST_INSTANCE_URL = None
"""The URL for a test/sandbox instance to advertise (if not set to ``None``)."""

THEME_TUW_FAIRSHARING_URL = "https://fairsharing.org/FAIRsharing.88d503"
"""The URL for the repository's entry in FAIRsharing."""

THEME_TUW_RE3DATA_URL = "https://www.re3data.org/repository/r3d100013557"
"""The URL for the repository's entry in re3data."""

THEME_TUW_OPENAIRE_URL = (
    "https://explore.openaire.eu/search/dataprovider?pid=r3d100013557"
)
"""The URL for a search for the repository's datasets in OpenAIRE."""

THEME_TUW_INVENIORDM_URL = "https://inveniosoftware.org/products/rdm/"
"""The URL for the InvenioRDM project website."""


# Invenio-Theme
# =============
# See https://invenio-theme.readthedocs.io/en/latest/configuration.html

# The official repository name:
# Displayed in browser tab and in some text
THEME_SITENAME = "TU Wien Research Data"

# Templates
BASE_TEMPLATE = "invenio_theme_tuw/overrides/page.html"
THEME_FRONTPAGE_TEMPLATE = "invenio_theme_tuw/overrides/frontpage.html"
THEME_HEADER_TEMPLATE = "invenio_theme_tuw/overrides/header.html"
THEME_FOOTER_TEMPLATE = "invenio_theme_tuw/overrides/footer.html"
THEME_JAVASCRIPT_TEMPLATE = "invenio_theme_tuw/overrides/javascript.html"
THEME_ERROR_TEMPLATE = "invenio_theme_tuw/overrides/page_error.html"

# Header logo
THEME_LOGO = "images/tu-wien-logo-hd.png"
INSTANCE_THEME_FILE = "less/invenio_theme_tuw/theme.less"

# Override the Invenio-OAuthClient login form
OAUTHCLIENT_SIGNUP_TEMPLATE = "invenio_theme_tuw/overrides/signup.html"
OAUTHCLIENT_LOGIN_USER_TEMPLATE = "invenio_theme_tuw/overrides/login_user.html"


# Flask-WebpackExt
# ================
# See https://flask-webpackext.readthedocs.io/en/latest/configuration.html

WEBPACKEXT_PROJECT = "invenio_assets.webpack:rspack_project"

APP_RDM_DETAIL_SIDE_BAR_TEMPLATES = [
    "invenio_app_rdm/records/details/side_bar/manage_menu.html",
    "invenio_theme_tuw/overrides/metrics.html",
    "invenio_theme_tuw/details/uploaders.html",
    "invenio_app_rdm/records/details/side_bar/versions.html",
    "invenio_app_rdm/records/details/side_bar/external_resources.html",
    "invenio_app_rdm/records/details/side_bar/communities.html",
    "invenio_app_rdm/records/details/side_bar/keywords_subjects.html",
    "invenio_app_rdm/records/details/side_bar/details.html",
    "invenio_app_rdm/records/details/side_bar/locations.html",
    "invenio_app_rdm/records/details/side_bar/licenses.html",
    "invenio_app_rdm/records/details/side_bar/citations.html",
    "invenio_app_rdm/records/details/side_bar/export.html",
    "invenio_app_rdm/records/details/side_bar/technical_metadata.html",
]

# Flask-Session-Captcha
# =====================
# see https://github.com/Tethik/flask-session-captcha

CAPTCHA_ENABLE = True
CAPTCHA_LENGTH = 8
CAPTCHA_WIDTH = 200
CAPTCHA_HEIGHT = 60

# Flask-Session-Captcha is based on Flask-Session, but we use Flask-KVSession-Invenio
# so this is here to silence the warning about sessions
SESSION_TYPE = "redis"
