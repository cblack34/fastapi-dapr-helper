"""
This module provides the subscribe decorator to be used in combination with a route generator
to create subscriptions to Dapr pubsub topics with FastAPI.
"""

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

    # TODO: Add example
    # TODO: update tests for invalid types of inputs.

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
