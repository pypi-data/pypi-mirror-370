# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 TU Wien.
#
# Invenio-Theme-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""JS/CSS Webpack bundles for TU Wien theme."""

from invenio_assets.webpack import WebpackThemeBundle

# the definition of our own bundle of frontend assets, which will be collected and
# built by `pywebpack`/`flask_webpackext`/`invenio_assets`.
#
# rough explanation of the arguments:
# * import_name: similar to above
# * folder:      similar to the `project_folder` above
# * default:     default theme to use if `APP_THEME` isn't set
# * themes:      dictionary with available themes and their definitions
theme = WebpackThemeBundle(
    import_name=__name__,
    folder="theme/assets",
    default="semantic-ui",
    themes={
        "semantic-ui": {
            "entry": {
                # JS
                "invenio-theme-tuw-clipboard": "./js/invenio_theme_tuw/clipboard/index.js",
                "invenio-theme-tuw-mobilemenu": "./js/invenio_theme_tuw/mobilemenu/index.js",
                "invenio-theme-tuw-snowfall": "./js/invenio_theme_tuw/snowfall/index.js",
                "invenio-theme-tuw-tracking": "./js/invenio_theme_tuw/tracking/index.js",
                # LESS
                "invenio-theme-tuw-login": "./less/invenio_theme_tuw/login.less",
                "invenio-theme-tuw-tuwstones": "./less/invenio_theme_tuw/tuwstone.less",
                "invenio-theme-tuw-task-failures": "./less/invenio_theme_tuw/task_failures.less",
                "invenio-theme-tuw-user-infos": "./less/invenio_theme_tuw/user_infos.less",
                "invenio-theme-tuw-users-welcome": "./less/invenio_theme_tuw/users_welcome.less",
            },
            "dependencies": {
                "jquery": "^3.2.1",
                "jquery-snowfall": "^1.7",
            },
            "aliases": {
                # the 'themes/tuw' alias registers our theme (*.{override,variables})
                # as 'tuw' theme for semantic-ui
                "themes/tuw": "less/invenio_theme_tuw/theme",
                # aliases in case you would like to reference js/less files from
                # somewhere else (e.g. other modules)
                "@less/invenio_theme_tuw": "less/invenio_theme_tuw",
                "@js/invenio_theme_tuw": "js/invenio_theme_tuw",
            },
        },
    },
)
