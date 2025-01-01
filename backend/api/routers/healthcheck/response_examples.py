from typing import Any, Dict, Optional, Union

from fastapi import status

health: Optional[Dict[Union[int, str], Dict[str, Any]]] = {
    "200": {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "ok_1": {
                        "summary": "Health check OK - Groot",
                        "value": {
                            "status_code": status.HTTP_200_OK,
                            "content": {"data": "I am Groot"},
                        },
                    },
                    "ok_2": {
                        "summary": "Health check OK - Mandalorian",
                        "value": {
                            "status_code": status.HTTP_200_OK,
                            "content": {"data": "This is the way"},
                        },
                    },
                    "ok_3": {
                        "summary": "Health check OK - Vader",
                        "value": {
                            "status_code": status.HTTP_200_OK,
                            "content": {"data": "Luke, I am your father"},
                        },
                    },
                    "ok_4": {
                        "summary": "Health check OK - GoT",
                        "value": {
                            "status_code": status.HTTP_200_OK,
                            "content": {"data": "Hodor..."},
                        },
                    },
                }
            }
        },
    },
}
