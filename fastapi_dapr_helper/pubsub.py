"""
This module provides the subscribe decorator to be used in combination with a route generator
to create subscriptions to Dapr pubsub topics with FastAPI.
"""
import logging
from typing import Optional, Dict, Any, List, Union

from fastapi import FastAPI, APIRouter


def subscribe(
    app: Union[FastAPI, APIRouter],
    path: str,
    pubsub: str,
    topic: str,
    *args,
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, str]] = None,
    dead_letter_topic: Optional[str] = None,
    openapi_extra: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> callable:
    """
    A decorator used in combination with a route generator to create subscriptions to Dapr pubsub topics with FastAPI.

    Args:
        app (Union[FastAPI, APIRouter]): The FastAPI or APIRouter application.
        path (str): The endpoint path.
        pubsub (str): The pubsub name.
        topic (str): The topic name.
        tags (Optional[List[str]]): Optional tags for the endpoint.
        metadata (Optional[Dict[str, str]]): Optional metadata.
        dead_letter_topic (Optional[str]): Optional dead letter topic.
        openapi_extra (Optional[Dict[str, Any]]): Optional extra OpenAPI info.

    Returns:
        callable: The decorator.
    """
    if metadata is None:
        metadata = {}

    if openapi_extra is None:
        openapi_extra = {}

    if not isinstance(app, (FastAPI, APIRouter)):
        raise TypeError('Expected FastAPI or APIRouter instance for "app"')
    if not isinstance(path, str):
        raise TypeError('Expected string for "path"')
    if not isinstance(pubsub, str):
        raise TypeError('Expected string for "pubsub"')
    if not isinstance(topic, str):
        raise TypeError('Expected string for "topic"')
    if tags is not None and not isinstance(tags, list):
        raise TypeError('Expected list for "tags"')
    if dead_letter_topic is not None and not isinstance(dead_letter_topic, str):
        raise TypeError('Expected string for "dead_letter_topic"')

    def decorator(func):
        openapi_extra["dapr"] = {
            "pubsubname": pubsub,
            "topic": topic,
            "metadata": metadata,
            **(
                {"deadLetterTopic": dead_letter_topic}
                if dead_letter_topic is not None
                else {}
            ),
        }

        app.add_api_route(
            path=path,
            endpoint=func,
            methods=["POST"],
            tags=tags,
            openapi_extra=openapi_extra,
            *args,
            **kwargs,
        )

    return decorator


# pylint: disable=R0903
class DaprFastAPI:
    """
    Class to handle Dapr subscriptions and the FastAPI application.
    """

    def __init__(self, remove_dapr_data: bool = False):
        self.remove_dapr_data = remove_dapr_data
        self._subscriptions = []

    def _get_subscriptions(self):
        return self._subscriptions

    def _extract_subscriptions(self, app: FastAPI) -> List[Dict[str, Any]]:
        route_info = []

        for route in app.routes:
            if hasattr(route, "openapi_extra") is False:
                logging.info(f"Skipping route {route.path} as it has no openapi_extra")
                continue

            if route.openapi_extra is None:
                logging.info(f"Skipping route {route.path} as it has no openapi_extra")
                continue

            if "dapr" not in route.openapi_extra:
                logging.info(f"Skipping route {route.path} as it has no dapr info")
                continue

            logging.info(f"Extracting route {route.path} as it has dapr info")

            dapr_info = route.openapi_extra["dapr"]
            info = {
                "pubsubname": dapr_info["pubsubname"],
                "topic": dapr_info["topic"],
                "route": route.path,
                "metadata": dapr_info["metadata"],
            }

            route_info.append(info)

            if self.remove_dapr_data:
                del route.openapi_extra["dapr"]

        self._subscriptions.extend(route_info)

        return self._subscriptions

    def generate_subscribe_route(self, app: FastAPI):
        """
        Generates the /dapr/subscribe route in the FastAPI app.
        """
        self._extract_subscriptions(app)

        app.add_api_route(
            path="/dapr/subscribe",
            endpoint=self._get_subscriptions,
            methods=["GET"],
        )
