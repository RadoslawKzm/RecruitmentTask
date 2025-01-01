from datetime import datetime
from typing import Optional, Protocol


class Coordinate(Protocol):
    coordinate_id: int
    latitude: float
    longitude: float

    def model_dump(self):
        pass


class Geometry(Protocol):
    geometry_id: int
    type: str
    coordinates: list[Coordinate]

    def model_dump(self):
        pass


class Geojson(Protocol):
    geojson_id: int
    type: str
    geometry: Geometry

    def model_dump(self):
        pass


class Project(Protocol):
    project_id: int
    name: str
    start_date: datetime
    end_date: datetime
    description: Optional[str]
    geojson: Geojson

    def model_dump(self):
        pass
