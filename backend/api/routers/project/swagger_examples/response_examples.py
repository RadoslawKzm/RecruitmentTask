from typing import Any, Dict, Optional, Union

from fastapi import status

about: Optional[Dict[Union[int, str], Dict[str, Any]]] = {
    "200": {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "normal": {
                        "summary": "About successful",
                        "value": {
                            "status_code": status.HTTP_200_OK,
                            "content": {"data": "version_v1"},
                        },
                    },
                }
            }
        },
    },
}

get_project_example = {
    "project_id": 10,
    "name": "Project 69",
    "description": "Simplicity is the ultimate sophistication",
    "date_range": ["1920-05-18T00:00:00", "2005-04-02T00:00:00"],
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
