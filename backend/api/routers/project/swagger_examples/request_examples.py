import typing
from datetime import datetime

project_id: dict[str, dict[str, str]] = {
    "example name 1": {"value": "1337"},
    "example name 2": {"value": "2137"},
}

name: dict[str, dict[str, str]] = {
    "example name 1": {"value": "Project 69"},
    "example name 2": {"value": "Data 1337"},
    "example name 3": {"value": "LandOf2137"},
}

description: dict[str, dict[str, str]] = {
    "example description 1": {
        "value": "Simplicity is the ultimate sophistication"
    },
    "example description 2": {
        "value": "It's easy to complicate, but hard to simplify"
    },
    "example description 3": {"value": "Keep it stupid simple"},
    "example description 4": {"value": "You ain't gonna need it"},
    "example description 5": {
        "value": "Do not repeat yourself, except while taking with you spouse"
    },
    "example description 6": {
        "value": "Better ask for forgiveness than for permission. "
        "Oh shi..., my kid stole a bike"
    },
}


date_range: dict[str, dict[str, tuple[datetime, datetime]]] = {
    "date1": {"value": (datetime(1920, 5, 18), datetime(2005, 4, 2))},
    "date2": {"value": (datetime(1930, 8, 5), datetime(2012, 8, 25))},
    "date3": {"value": (datetime(1962, 2, 22), datetime(2006, 4, 9))},
    "date4": {"value": (datetime(1922, 12, 28), datetime(2018, 11, 12))},
}

geojson_data: dict[str, str | dict[str, str | list[list[list[list[int]]]]]] = {
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

geojson_data2: dict[
    str, str | dict[str, str | list[list[list[list[int]]]]]
] = {
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
                    [-52.788292917171, -5.651491506446291],
                    [-52.7803877309072, -5.640815088854069],
                    [-52.7555428597923, -5.641377010471558],
                    [-52.738603174941204, -5.63800547260297],
                    [-52.729568676354, -5.631262338119598],
                    [-52.719404865443295, -5.626204935899693],
                    [-52.709241054532704, -5.616089999567166],
                    [-52.6708444355369, -5.569446637469866],
                    [-52.6787496218007, -5.558206718303779],
                    [-52.687784120388, -5.534602190108217],
                    [-52.7098057106944, -5.5390983634896],
                    [-52.7244867708986, -5.546404572245265],
                    [-52.7600601090859, -5.5722565836830285],
                    [-52.7843403240391, -5.584058210883924],
                    [-52.8074912266689, -5.589115978388449],
                    [-52.823301599196604, -5.618337778382639],
                    [-52.8385473155626, -5.620585548523252],
                    [-52.8430645648562, -5.63351005831322],
                ]
            ]
        ],
    },
}


geojson_request_example: dict[str, dict[str, str | dict | typing.Any]] = {
    "normal": {
        "summary": "A normal example",
        "description": "A **normal** item works correctly.",
        "value": geojson_data,
    },
    "normal 2": {
        "summary": "A normal example 2",
        "description": "A **normal** item works correctly.",
        "value": geojson_data,
    },
    # If you want invalid example uncomment and add invalid data
    # "invalid": {
    #     "summary": "Invalid data is rejected with an error",
    #     "value": geojson_data,
    # },
}
