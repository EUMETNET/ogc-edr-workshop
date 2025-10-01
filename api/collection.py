from __future__ import annotations

import logging
from functools import cache

from edr_pydantic.collections import Collection
from edr_pydantic.data_queries import DataQueries
from edr_pydantic.data_queries import EDRQuery
from edr_pydantic.extent import Extent
from edr_pydantic.extent import Spatial
from edr_pydantic.extent import Temporal
from edr_pydantic.link import EDRQueryLink
from edr_pydantic.link import Link
from edr_pydantic.parameter import Parameter
from edr_pydantic.variables import Variables

from api.util import datetime_to_iso_string
from api.util import get_edr_parameter_from_variable
from data.data import get_stations
from data.data import get_temporal_extent
from data.data import get_temporal_interval
from data.data import get_variables


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@cache
def get_spatial_extent() -> tuple[float, float, float, float]:
    stations = get_stations()
    longs = list(map(lambda x: x.longitude, stations))
    lats = list(map(lambda x: x.latitude, stations))
    left = min(longs)
    right = max(longs)
    bottom = min(lats)
    top = max(lats)

    return left, bottom, right, top


def get_collection_metadata(base_url: str, is_self) -> Collection:
    start, end = get_temporal_extent()
    duration_str, duration_timedelta = get_temporal_interval()
    left, bottom, right, top = get_spatial_extent()

    repeats = int((end - start) / duration_timedelta + 1)
    temporal_values = [f"R{repeats}/{datetime_to_iso_string(start)}/{duration_str}"]

    parameters: dict[str, Parameter] = {}
    for var in sorted(get_variables(), key=lambda x: x.id):
        parameters[var.id] = get_edr_parameter_from_variable(var)

    collection = Collection(
        id="daily",
        title="EDR collection example",
        description="A simple example of an EDR collection.",
        links=[
            Link(href=base_url + "daily", rel="self" if is_self else "data"),
        ],
        extent=Extent(
            spatial=Spatial(
                bbox=[[left, bottom, right, top]],
                crs="EPSG:4326",
            ),
            temporal=Temporal(
                interval=[[start, end]],
                values=temporal_values,
                trs="datetime",
            ),
        ),
        data_queries=DataQueries(
            locations=EDRQuery(
                link=EDRQueryLink(
                    href=base_url + "daily/locations",
                    rel="data",
                    variables=Variables(query_type="locations", output_formats=["CoverageJSON"]),
                )
            ),
            area=EDRQuery(
                link=EDRQueryLink(
                    href=base_url + "daily/area",
                    rel="data",
                    variables=Variables(query_type="area", output_formats=["CoverageJSON"]),
                )
            ),
        ),
        crs=["WGS84"],
        output_formats=["CoverageJSON"],
        parameter_names=parameters,
    )
    return collection
