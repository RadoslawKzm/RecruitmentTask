import typing
from datetime import datetime

import pydantic

from backend.api.routers.project.swagger_examples.response_examples import (
    get_project_example,
)


class Coordinate(pydantic.BaseModel):
    latitude: float
    longitude: float

    model_config = {"from_attributes": True}


class Geometry(pydantic.BaseModel):
    type: str  # @TODO add literal if possible for finite array of types
    coordinates: list[Coordinate]

    model_config = {"from_attributes": True}


class GeoJson(pydantic.BaseModel):
    type: str  # @TODO add literal if possible for finite array of types
    geometry: Geometry

    model_config = {"from_attributes": True}


class ProjectResponse(pydantic.BaseModel):
    project_id: int = pydantic.Field(..., description="Project ID")
    name: str = pydantic.Field(
        ...,
        max_length=32,
        description="Name: string with a maximum length of 32 characters.",
    )
    description: typing.Optional[str] = pydantic.Field(
        None,
        description="An optional description of the name.",
    )
    date_range: typing.Tuple[datetime, datetime] = pydantic.Field(
        ...,
        description="Date range: tuple of two datetime values (start, end).",
    )
    geojson: GeoJson

    # model_config = {"from_attributes": True}
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {"examples": [get_project_example]},
    }


# example_return = {
#     "project_id": 1,
#     "name": "test_name_return",
#     "description": "test_description_return",
#     "date_range": (datetime(2023, 1, 1), datetime(2023, 12, 31)),
#     "geojson": {
#         "type": "Feature",
#         "geometry": {
#             "type": "MultiPolygon",
#             "coordinates": [
#                 {
#                     "latitude": -52.8430645648562,
#                     "longitude": -5.63351005831322,
#                 },
#                 {
#                     "latitude": -52.8289481608136,
#                     "longitude": -5.674529420529012,
#                 },
#                 {
#                     "latitude": -52.8114438198008,
#                     "longitude": -5.6661010219506664,
#                 },
#                 {
#                     "latitude": -52.797327415758296,
#                     "longitude": -5.654301057317909,
#                 },
#             ],
#         },
#     },
# }
