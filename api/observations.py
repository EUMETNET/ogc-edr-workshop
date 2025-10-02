from __future__ import annotations

import logging
from typing import Annotated

from covjson_pydantic.coverage import CoverageCollection
from covjson_pydantic.parameter import Parameter
from edr_pydantic.parameter import EdrBaseModel
from fastapi import APIRouter
from fastapi import Path
from fastapi import Query
from geojson_pydantic import FeatureCollection
from starlette.responses import JSONResponse


router = APIRouter(prefix="/collections/daily")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class CoverageJsonResponse(JSONResponse):
    media_type = "application/prs.coverage+json"


class GeoJsonResponse(JSONResponse):
    media_type = "application/geo+json"


class EDRFeatureCollection(EdrBaseModel, FeatureCollection):
    parameters: dict[str, Parameter]


@router.get(
    "/locations",
    tags=["Collection data queries"],
    name="List of locations",
    description="List the locations available for the collection",
    response_model=EDRFeatureCollection,
    response_model_exclude_none=True,
    response_class=GeoJsonResponse,
)
async def get_locations(
    bbox: Annotated[str | None, Query(example="5.0,52.0,6.0,52.1")] = None,
    # TODO: now that we have a larger time span consider to implement datetime.
    # datetime: Annotated[str | None, Query(example="2024-02-22T00:00:00Z/2024-02-27T00:00:00Z")] = None,
    parameter_name: Annotated[
        str | None,
        Query(
            alias="parameter-name",
            description="Comma separated list of parameter names. "
            "Return only locations that have one of these parameter.",
            example="FG, DDVEC",
        ),
    ] = None,
) -> EDRFeatureCollection:
    pass


@router.get(
    "/locations/{location_id}",
    tags=["Collection data queries"],
    name="Query endpoint for Location queries of collection " "daily defined by a location id.",
    description="Return data for the location defined by location_id",
    response_model=CoverageCollection,
    response_model_exclude_none=True,
    response_class=CoverageJsonResponse,
)
async def get_data_location_id(
    location_id: Annotated[str, Path(example="0-20000-0-06260")],
    parameter_name: Annotated[
        str | None,
        Query(alias="parameter-name", description="Comma separated list of parameter names.", example="FG, DDVEC"),
    ] = None,
    datetime: Annotated[str | None, Query(example="2024-02-22T00:00:00Z/2024-02-27T00:00:00Z")] = None,
) -> CoverageCollection:
    pass


@router.get(
    "/area",
    tags=["Collection data queries"],
    name="Query endpoint for area queries of collection " "daily defined by a polygon.",
    description="Return data for the area defined by the polygon",
    response_model=CoverageCollection,
    response_model_exclude_none=True,
    response_class=CoverageJsonResponse,
)
async def get_data_area(
    coords: Annotated[str, Query(example="POLYGON((5.0 52.0, 6.0 52.0,6.0 52.1,5.0 52.1, 5.0 52.0))")],
    parameter_name: Annotated[
        str | None,
        Query(alias="parameter-name", description="Comma separated list of parameter names.", example="FG, DDVEC"),
    ] = None,
    datetime: Annotated[str | None, Query(example="2024-02-22T00:00:00Z/2024-02-27T00:00:00Z")] = None,
) -> CoverageCollection:
    pass
