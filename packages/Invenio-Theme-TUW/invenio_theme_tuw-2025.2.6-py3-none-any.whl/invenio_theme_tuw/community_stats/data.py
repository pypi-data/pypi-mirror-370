# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 TU Wien.
#
# Invenio-Theme-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Utilities for processing usage events from ``Invenio-Stats`` entries."""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional, Set, Tuple

import pycountry
from invenio_search.engine import dsl
from invenio_search.proxies import current_search_client
from invenio_search.utils import prefix_index

type DataAccessType = Literal["download", "view", "both"]
type Query = str


@dataclass
class Event:
    """A subset of a logged usage event."""

    country: Optional[str] = field(default=None)
    session_id: Optional[str] = field(repr=False, default=None)
    timestamp: Optional[str] = field(repr=False, default=None)

    @classmethod
    def from_dict(cls, data: Dict):
        """Parse the ``Event`` from the dictionary."""
        return cls(data["country"], data["unique_session_id"], data["timestamp"])

    def append_dict(self, data: Dict[str, int]) -> None:
        """Increase the counter in ``data`` for this event's country."""
        if self.country is not None:
            if self.country not in data.keys():
                data[self.country] = 1
            else:
                data[self.country] += 1


def create_events_query(
    which: DataAccessType = "both", identifier: str = "", month: str = ""
) -> dsl.Search:
    """Create a search query for usage events for a specific record."""
    index = _build_search_domain(which)
    search = dsl.Search(using=current_search_client, index=prefix_index(index))
    search = search.filter("term", recid=identifier)
    if month:
        search = search.filter(
            "range", timestamp={"gte": month, "lte": month, "format": "yyyy-MM"}
        )
    return search


def process_query(query: dsl.Search, verbose: bool = False) -> Dict[str, int]:
    """Process the query results and return a list of country names and their counts.

    :param query: The parameterized search query to be executed.
    :return: A tuple containing a list of country names and a list of counts.
    """
    try:
        logged_events = query.execute().to_dict()["hits"]["hits"]
        country_counts, _ = _aggregate_country_event_counts(logged_events)
        counts: Dict[str, int] = _get_country_names_and_counts(
            country_counts, verbose=verbose
        )
    except Exception:
        # e.g. opensearchpy.exceptions.OpenSearchException
        counts: Dict[str, int] = {}

    return counts


def _get_country_names_and_counts(
    country_counts: Dict[str, int],
    verbose: bool = False,
) -> Dict[str, int]:
    """Convert the keys of a country counting dictionary from alpha-2 to alpha-3."""
    alpha3_counts: Dict[str, int] = {}

    for alpha2, count in country_counts.items():
        try:
            alpha3_name: str = pycountry.countries.get(alpha_2=alpha2).alpha_3
            alpha3_counts[alpha3_name] = count
        except LookupError as e:
            if verbose:
                print(f"LookupError for {alpha2}: {e}")
    return alpha3_counts


def _aggregate_country_event_counts(
    logged_events: List[Dict],
) -> Tuple[Dict[str, int], Set[str]]:
    """Parse the number of downloads per country from a list of logged usage events.

    Takes a list of logged events and returns:
    - a dictionary mapping country names to how many unique sessions included
      downloads from that country
    - a set of unique session IDs
    """
    session_to_countries: Dict[str, Set[str]] = defaultdict(set)
    all_session_ids: Set[str] = set()

    for log in logged_events:
        event = Event.from_dict(log["_source"])
        session_to_countries[event.session_id].add(event.country)
        all_session_ids.add(event.session_id)

    country_counts: Dict[str, int] = defaultdict(int)
    for countries in session_to_countries.values():
        for country in countries:
            country_counts[country] += 1

    return dict(country_counts), all_session_ids


def _build_search_domain(which: DataAccessType) -> str:
    match which:
        case "download" | "downloads":
            return "events-stats-file-download"
        case "view" | "views":
            return "events-stats-record-view"
        case "both":
            return "events-stats-*"
        case _:
            raise ValueError("Invalid argument for which")
