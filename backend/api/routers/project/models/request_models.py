import typing
from datetime import datetime

import pydantic
from pydantic import BaseModel

from backend.api.routers.project.swagger_examples import request_examples


class Coordinate(BaseModel):
    latitude: float
    longitude: float

    def __init__(self, latitude: float, longitude: float, **kwargs):
        super().__init__(latitude=latitude, longitude=longitude)


class Geometry(pydantic.BaseModel):
    type: str  # @TODO add literal if possible for finite array of types
    coordinates: list[list[list[Coordinate]]]

    def __init__(self, *args, **kwargs):
        kwargs["coordinates"][0][0] = [
            Coordinate(*data) for data in kwargs["coordinates"][0][0]
        ]
        super().__init__(**kwargs)


class GeoJson(pydantic.BaseModel):
    type: str  # @TODO add literal if possible for finite array of types
    geometry: Geometry
    model_config = {
        "json_schema_extra": {"examples": [request_examples.geojson_data]}
    }

    def model_flatten(self) -> dict:
        return {
            "type": self.type,
            "geometry": {
                "type": self.geometry.type,
                "coordinates": [
                    coord.model_dump()
                    for coord in self.geometry.coordinates[0][0]
                ],
            },
        }


class ProjectRequest(pydantic.BaseModel):
    name: str = pydantic.Field(
        ...,
        max_length=32,
        description="Name: string with a maximum length of 32 characters.",
    )
    description: typing.Optional[str] = pydantic.Field(
        None,
        description="An optional description of the name.",
    )

    @pydantic.field_validator("name")
    def validate_name(cls, value):
        if not value.strip():  # Ensure the name is not only whitespace
            raise ValueError(
                "Name cannot be empty or consist only of whitespace."
            )
        return value


class DateRangeModel(BaseModel):
    start_date: datetime
    end_date: datetime

    @pydantic.field_validator("*")
    def validate_date_range(cls, values):
        start_date = values.get("start_date")
        end_date = values.get("end_date")
        now = datetime.now()
        if end_date > now:
            raise ValueError(
                "end_date must be less than or equal to the current datetime"
            )
        if start_date > end_date:
            raise ValueError(
                "start_date must be less than or equal to end_date"
            )
        return values


if __name__ == "__main__":
    #     # coord = Coordinate(*[-52.8430645648562, -5.63351005831322])
    #     # data1 = {
    #     #     "type": "MultiPolygon",
    #     #     "coordinates": [
    #     #         [
    #     #             [
    #     #                 [-52.8430645648562, -5.63351005831322],
    #     #                 [-52.8289481608136, -5.674529420529012],
    #     #                 [-52.8114438198008, -5.6661010219506664],
    #     #                 [-52.797327415758296, -5.654301057317909],
    #     #             ]
    #     #         ]
    #     #     ],
    #     # }
    #     # geo = Geometry(**data1)
    # tst = GeoJson.model_validate(geojson_data)
    pass
