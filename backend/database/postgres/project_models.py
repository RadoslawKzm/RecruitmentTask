from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class Project(SQLModel, table=True):
    project_id: int | None = Field(default=None, primary_key=True, index=True)
    name: str = Field(max_length=32, nullable=False, index=True)
    start_date: datetime = Field(nullable=False)
    end_date: datetime = Field(nullable=False)
    description: Optional[str] = Field(nullable=True, default=None)

    # --- Relationships below ---#
    geojson: "GeoJson" = Relationship(
        back_populates="project",
        cascade_delete=True,
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class GeoJson(SQLModel, table=True):
    geojson_id: int | None = Field(default=None, primary_key=True, index=True)
    type: str = Field(nullable=False)

    # --- Relationships below ---#
    project_id: int = Field(
        foreign_key="project.project_id",
        ondelete="CASCADE",
        index=True,
    )
    project: Project = Relationship(
        back_populates="geojson",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    geometry: "Geometry" = Relationship(
        back_populates="geojson",
        cascade_delete=True,
        sa_relationship_kwargs={
            "lazy": "selectin",
            "cascade": "all, delete-orphan",
        },
    )


class Geometry(SQLModel, table=True):
    geometry_id: int | None = Field(default=None, primary_key=True, index=True)
    type: str = Field(nullable=False)

    # --- Relationships below ---#
    geojson_id: int = Field(
        foreign_key="geojson.geojson_id",
        ondelete="CASCADE",
        index=True,
    )  # Foreign key to GeoJson table
    geojson: GeoJson = Relationship(
        back_populates="geometry",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    coordinates: list["Coordinate"] = Relationship(
        back_populates="geometry",
        cascade_delete=True,
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class Coordinate(SQLModel, table=True):
    coord_id: int | None = Field(default=None, primary_key=True, index=True)
    latitude: float = Field(nullable=False)
    longitude: float = Field(nullable=False)

    # --- Relationships below ---#
    geometry_id: int = Field(
        foreign_key="geometry.geometry_id",
        ondelete="CASCADE",
        index=True,
    )  # Foreign key to GeoJson table
    geometry: Geometry = Relationship(
        back_populates="coordinates",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
