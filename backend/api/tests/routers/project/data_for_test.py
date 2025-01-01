import datetime

from backend.core.core_models import ProjectCore

read_from_db_1 = ProjectCore(
    **{
        "project_id": 12,
        "name": "Project 69",
        "start_date": datetime.datetime(1920, 5, 18, 0, 0),
        "end_date": datetime.datetime(2005, 4, 2, 0, 0),
        "description": "Simplicity is the ultimate sophisticatio",
        "geojson": {
            "type": "Feature",
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [
                    {
                        "latitude": -52.8430645648562,
                        "longitude": -5.63351005831322,
                    },
                    {
                        "latitude": -52.8289481608136,
                        "longitude": -5.674529420529012,
                    },
                    {
                        "latitude": -52.8114438198008,
                        "longitude": -5.6661010219506664,
                    },
                    {
                        "latitude": -52.797327415758296,
                        "longitude": -5.654301057317909,
                    },
                ],
            },
        },
    }
)

edit_in_db_1: dict = {
    "type": "Feature",
    "geometry": {
        "type": "MultiPolygon",
        "coordinates": [
            [
                [
                    [-52.8430645648562, -5.63351005831322],
                    [-52.8289481608136, -5.674529420529012],
                    [-52.8114438198008, -5.6661010219506664],
                    [-52.797327415758296, -5.654301057317909],
                ]
            ]
        ],
    },
}


flattened_geojson: dict = {
    "type": "Feature",
    "geometry": {
        "type": "MultiPolygon",
        "coordinates": [
            {
                "latitude": -52.8430645648562,
                "longitude": -5.63351005831322,
            },
            {
                "latitude": -52.8289481608136,
                "longitude": -5.674529420529012,
            },
            {
                "latitude": -52.8114438198008,
                "longitude": -5.6661010219506664,
            },
            {
                "latitude": -52.797327415758296,
                "longitude": -5.654301057317909,
            },
        ],
    },
}
