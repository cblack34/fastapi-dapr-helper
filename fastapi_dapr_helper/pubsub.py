from typing import Optional, Dict, Any

from fastapi import FastAPI, APIRouter


def subscribe(
    app: [FastAPI, APIRouter],
    path: str,
    pubsub: str,
    topic: str,
    tags: Optional[str] = None,
    metadata: Optional[Dict[str, str]] = None,
    dead_letter_topic: Optional[str] = None,
    openapi_extra: Optional[Dict[str, Any]] = None,
    *args,
    **kwargs,
):
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
