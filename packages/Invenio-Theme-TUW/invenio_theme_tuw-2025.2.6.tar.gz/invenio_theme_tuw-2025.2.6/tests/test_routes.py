# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 TU Wien.
#
# Invenio-Theme-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test routes."""

import re

import pytest


def test_frontpage(app):
    """Test the frontpage registered via our module."""
    app.config.update(
        {
            "THEME_SITENAME": "TUW Theme Testing",
        }
    )
    response = app.test_client().get("/")
    assert response.status_code == 200
    assert b"TUW Theme Testing" in response.data


def test_tuw_policies_route(app):
    """Test the policies page registered via our module."""
    resp = app.test_client().get("/tuw/policies")
    assert resp.status_code == 200
    assert b"Policies" in resp.data


def test_tuw_contact_route(app):
    """Test the contact page registered via our module."""
    resp = app.test_client().get("/tuw/contact")
    assert resp.status_code == 200
    assert b"Contact" in resp.data


@pytest.mark.parametrize(
    ["name", "status", "content"],
    [
        (
            "florian.woerister",
            200,
            ["Florian W&ouml;rister", "Ex Almost TU:RD Manager"],
        ),
        ("derek.molnar", 200, ["Derek Molnar", "He made Damap great again."]),
        ("maximilian.moser", 404, []),
    ],
)
def test_tuwstones(app, name, status, content):
    """Test Florian's tombstone page."""
    resp = app.test_client().get(f"/tuwstones/{name}")
    assert resp.status_code == status
    for snippet in content:
        assert snippet in resp.text


def test_about(app, client):
    """Test the `/about` redirect."""
    response = client.get("/about")
    assert response.status_code == 301
    assert response.headers["Location"].endswith("/tuw/about")

    response = client.get("/about", follow_redirects=True)
    assert response.status_code == 200
    re.findall(r"<h1>About [A-Za-z ]+</h1>", response.text)
