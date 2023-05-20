import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_dapr_helper.pubsub import subscribe


def test_subscribe():
    app = FastAPI()
    test_route = "/test_route"
    test_pubsub = "test_pubsub"
    test_topic = "test_topic"

    @subscribe(app=app, path=test_route, pubsub=test_pubsub, topic=test_topic)
    async def test_endpoint():
        return {"message": "test"}

    client = TestClient(app)

    response = client.post(test_route)

    assert response.status_code == 200
    assert response.json() == {"message": "test"}
    assert test_route in [route.path for route in app.routes]
    route = next(route for route in app.routes if route.path == test_route)
    assert route.methods == {"POST"}

    # assert if dapr configuration in openapi_extra is set correctly
    assert route.openapi_extra["dapr"] == {
        "pubsubname": test_pubsub,
        "topic": test_topic,
        "metadata": {},
    }


def test_subscribe_missing_args():
    app = FastAPI()

    with pytest.raises(TypeError):

        @subscribe(app)
        async def test_endpoint():
            return {"message": "test"}

    with pytest.raises(TypeError):

        @subscribe(app, "/test_route")
        async def test_endpoint():
            return {"message": "test"}

    with pytest.raises(TypeError):

        @subscribe(app, "/test_route", "test_pubsub")
        async def test_endpoint():
            return {"message": "test"}


def test_subscribe_incorrect_args():
    app = FastAPI()

    # Passing incorrect type for 'app' argument
    with pytest.raises(Exception):

        @subscribe(
            app="wrong_type",
            path="/test_route",
            pubsub="test_pubsub",
            topic="test_topic",
        )
        async def test_endpoint():
            return {"message": "test"}

    # Passing incorrect type for 'path' argument
    with pytest.raises(Exception):

        @subscribe(app=app, path=1234, pubsub="test_pubsub", topic="test_topic")
        async def test_endpoint():
            return {"message": "test"}

    # Passing incorrect type for 'pubsub' argument
    with pytest.raises(Exception):

        @subscribe(app=app, path="/test_route", pubsub=1234, topic="test_topic")
        async def test_endpoint():
            return {"message": "test"}

    # Passing incorrect type for 'topic' argument
    with pytest.raises(Exception):

        @subscribe(app=app, path="/test_route", pubsub="test_pubsub", topic=1234)
        async def test_endpoint():
            return {"message": "test"}
