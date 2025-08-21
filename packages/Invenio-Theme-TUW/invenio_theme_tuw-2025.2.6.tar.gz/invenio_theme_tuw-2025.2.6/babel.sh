#!/bin/bash
# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 TU Wien.
#
# Invenio-Theme-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

function usage() {
    echo "usage: ${0} <COMMAND> [args...]"
    echo
    echo "available commands: compile, extract, init, update"
}

if [[ $# -lt 1 ]]; then
    usage >&2
    exit 1
fi

command="${1}"
shift
case "${command}" in
    init)
        pybabel init \
            --input-file "invenio_theme_tuw/translations/messages.pot" \
            --output-dir "invenio_theme_tuw/translations/" \
            "${@}"
        ;;
    compile)
        pybabel compile \
            --directory "invenio_theme_tuw/translations/" \
            "${@}"
        ;;
    extract)
        pybabel extract \
            --copyright-holder "TU Wien" \
            --msgid-bugs-address "tudata@tuwien.ac.at" \
            --mapping-file "babel.ini" \
            --output-file "invenio_theme_tuw/translations/messages.pot" \
            --add-comments "NOTE" \
            invenio_theme_tuw \
            "${@}"
        ;;
    update)
        pybabel update \
            --input-file "invenio_theme_tuw/translations/messages.pot" \
            --output-dir "invenio_theme_tuw/translations/" \
            "${@}"
        ;;
    *)
        echo >&2 "error: unknown command: ${command}"
        echo >&2
        usage >&2
        exit 1
        ;;
esac
