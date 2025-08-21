# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 TU Wien.
#
# Invenio-Theme-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Utilities for generating various maps from data points."""

from pathlib import Path
from typing import Any

import folium
import geopandas as gpd
import pandas as pd

type CountryList = list[str]
type CountList = list[int]
type FoliumMapObject = folium.Map


def map_folium(
    countries: CountryList,
    counts: CountList,
    **kwargs: Any,
) -> FoliumMapObject:
    """Generate a Folium map with countries colored based on the counts.

    :param countries: List of country names (ISO 3166-1 alpha-3 ADM0_A3s).
    :param counts: List of counts corresponding to the countries.
    :return: Folium Map object.
    """
    # Get the world map data
    world = _fetch_and_combine_map_data(countries, counts)

    # Draw the map
    fmap = folium.Map(location=[0, 0], zoom_start=2, max_zoom=6, min_zoom=1, **kwargs)
    folium.Choropleth(
        geo_data=world,
        name="Choropleth",
        control=False,
        data=world,
        columns=["ADM0_A3", "count"],
        key_on="feature.properties.ADM0_A3",
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Counts per Country",
    ).add_to(fmap)
    tooltip_style = (
        "background-color: white; color: black; font-size: 12px; padding: 5px;"
    )
    folium.GeoJson(
        world,
        name="Country outlines",
        control=False,
        style_function=lambda feature: {  # noqa
            "fillColor": "transparent",  # Keep existing color
            "color": "black",  # Default border color
            "weight": 1,  # Border thickness
        },
        highlight_function=lambda feature: {  # noqa
            "fillColor": "yellow",  # Temporary highlight color on hover
            "color": "red",  # Border color on hover
            "weight": 3,  # Thicker border on hover
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["ADM0_A3", "count"],  # Show country name + access count
            aliases=["Country:", "Access Count:"],  # Label the fields
            localize=True,
            sticky=False,  # Tooltip stays when hovering
            labels=True,
            style=tooltip_style,
        ),
    ).add_to(fmap)
    return fmap


def _fetch_and_combine_map_data(
    countries: CountryList,
    counts: CountList,
) -> gpd.GeoDataFrame:
    # note: we're vendoring the ZIP file to reduce attack surface
    # it has been downloaded from nasciscdn.org on 2025-06-02:
    # https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip
    path = Path(__file__).parent / "data" / "ne_110m_admin_0_countries.zip"
    world: gpd.GeoDataFrame = gpd.read_file(path.absolute())
    data = pd.DataFrame({"country": countries, "count": counts})

    # Merge the world map data with the counts
    return world.merge(data, left_on="ADM0_A3", right_on="country", how="left")


def display_discrete_counts(counts: dict[str, int]) -> pd.DataFrame:
    """Display discrete counts in a DataFrame."""
    dataframe = pd.DataFrame(list(counts.items()), columns=["Country", "Count"])
    dataframe = dataframe.sort_values(by="Count", ascending=False)
    dataframe = dataframe.reset_index(drop=True)
    dataframe.index += 1  # Start index at 1 for display purposes
    return dataframe
