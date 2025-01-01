from datetime import datetime

import pydantic


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


class ProjectCore(pydantic.BaseModel):
    project_id: int
    name: str
    start_date: datetime
    end_date: datetime
    description: str
    geojson: GeoJson

    model_config = {"from_attributes": True}
