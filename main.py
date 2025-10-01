# For developing:    uvicorn main:app --reload
from __future__ import annotations

import logging

import uvicorn
from brotli_asgi import BrotliMiddleware
from edr_pydantic.capabilities import ConformanceModel
from edr_pydantic.capabilities import Contact
from edr_pydantic.capabilities import LandingPageModel
from edr_pydantic.capabilities import Provider
from edr_pydantic.collections import Collection
from edr_pydantic.collections import Collections
from edr_pydantic.link import Link
from fastapi import FastAPI
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse

from api import collection
from api import observations
from api.util import create_url_from_request


def setup_logging():
    logger = logging.getLogger()
    syslog = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s ; edr-api ; %(process)s ; %(levelname)s ; %(name)s ; %(message)s")

    syslog.setFormatter(formatter)
    logger.addHandler(syslog)


setup_logging()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = FastAPI(
    title="EDR workshop",
    contact={
        "email": "rodeoproject@fmi.fi",
        "name": "RODEO",
    },
    description="Climate EDR API",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1, "tryItOutEnabled": True},
    version="v1",
)
app.add_middleware(BrotliMiddleware)


# According to OGC EDR spec, we can not return 422 (Fast API default for request validation errors),
# so we return these as 400, making sure we keep the standard FastAPI format.
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder({"detail": exc.errors()}),
    )


@app.get("/health", include_in_schema=False)
async def health_endpoint():
    return "ok"


@app.get(
    "/",
    tags=["Capabilities"],
    name="landing page of this API",
    description="The landing page provides links to the API definition,"
    + " the Conformance statements and the metadata about the feature data in this dataset.",
    response_model=LandingPageModel,
    response_model_exclude_none=True,
)
async def landing_page(request: Request) -> LandingPageModel:
    url = str(request.url)

    return LandingPageModel(
        title="EDR tutorial",
        description="A simple example EDR implementation",
        keywords=["Weather", "Temperature", "Wind", "Humidity", "Pressure", "Clouds", "Radiation"],
        provider=Provider(name="RODEO", url="https://rodeo-project.eu/"),
        contact=Contact(email="rodeoproject@fmi.fi"),
        links=[
            Link(href=url, rel="self", title="Landing Page in JSON"),
            Link(href=url + "docs", rel="service-desc", title="API description in HTML"),
            Link(href=url + "openapi.json", rel="service-desc", title="API description in JSON"),
            Link(href=url + "conformance", rel="data", title="Conformance Declaration in JSON"),
            Link(href=url + "collections", rel="data", title="Collections metadata in JSON"),
        ],
    )


@app.get(
    "/conformance",
    tags=["Capabilities"],
    response_model=ConformanceModel,
    response_model_exclude_none=True,
)
async def get_conformance(request: Request) -> ConformanceModel:
    return ConformanceModel(
        conformsTo=[
            "http://www.opengis.net/spec/ogcapi-edr-1/1.1/conf/core",
            "http://www.opengis.net/spec/ogcapi-common-1/1.0/conf/core",
            "http://www.opengis.net/spec/ogcapi-common-2/1.0/conf/collections",
            "http://www.opengis.net/spec/ogcapi-edr-1/1.1/conf/oas30",
            # "http://www.opengis.net/spec/ogcapi-edr-1/1.1/conf/html",
            "http://www.opengis.net/spec/ogcapi-edr-1/1.1/conf/edr-geojson",
            "http://www.opengis.net/spec/ogcapi-edr-1/1.1/conf/covjson",
        ]
    )


@app.get(
    "/collections",
    tags=["Capabilities"],
    name="List the available collections from the service",
    response_model=Collections,
    response_model_exclude_none=True,
)
async def get_collections(request: Request) -> Collections:
    base_url = create_url_from_request(request)
    return Collections(
        links=[
            Link(href=base_url, rel="self"),
        ],
        collections=[collection.get_collection_metadata(base_url, is_self=False)],
    )


@app.get(
    "/collections/daily-in-situ-meteorological-observations-validated",
    tags=["Collection metadata"],
    response_model=Collection,
    response_model_exclude_none=True,
)
async def get_collection_metadata(request: Request) -> Collection:
    base_url = create_url_from_request(request)
    return collection.get_collection_metadata(base_url, is_self=True)


# Include other routes
app.include_router(observations.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
