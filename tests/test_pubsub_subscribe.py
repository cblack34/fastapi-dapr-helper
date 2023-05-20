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


def test_subscribe_with_optional_args():
    app = FastAPI()
    test_route = "/test_route"
    test_pubsub = "test_pubsub"
    test_topic = "test_topic"
    test_tags = ["tag1", "tag2"]
    test_metadata = {"meta1": "data1"}
    test_dead_letter_topic = "dead_letter"
    test_openapi_extra = {"extra1": "data1"}

    @subscribe(
        app=app,
        path=test_route,
        pubsub=test_pubsub,
        topic=test_topic,
        tags=test_tags,
        metadata=test_metadata,
        dead_letter_topic=test_dead_letter_topic,
        openapi_extra=test_openapi_extra,
    )
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
        "metadata": test_metadata,
        "deadLetterTopic": test_dead_letter_topic,
    }
    assert route.openapi_extra["extra1"] == "data1"


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
    with pytest.raises(TypeError) as e_info:

        @subscribe(
            app="wrong_type",
            path="/test_route",
            pubsub="test_pubsub",
            topic="test_topic",
        )
        async def test_endpoint():
            return {"message": "test"}

    assert str(e_info.value) == 'Expected FastAPI or APIRouter instance for "app"'

    # Passing incorrect type for 'path' argument
    with pytest.raises(TypeError) as e_info:

        @subscribe(app=app, path=1234, pubsub="test_pubsub", topic="test_topic")
        async def test_endpoint():
            return {"message": "test"}

    assert str(e_info.value) == 'Expected string for "path"'

    # Passing incorrect type for 'pubsub' argument
    with pytest.raises(TypeError) as e_info:

        @subscribe(app=app, path="/test_route", pubsub=1234, topic="test_topic")
        async def test_endpoint():
            return {"message": "test"}

    assert str(e_info.value) == 'Expected string for "pubsub"'

    # Passing incorrect type for 'topic' argument
    with pytest.raises(TypeError) as e_info:

        @subscribe(app=app, path="/test_route", pubsub="test_pubsub", topic=1234)
        async def test_endpoint():
            return {"message": "test"}

    assert str(e_info.value) == 'Expected string for "topic"'

    # Passing incorrect type for 'tags' argument
    with pytest.raises(TypeError) as e_info:

        @subscribe(
            app=app,
            path="/test_route",
            pubsub="test_pubsub",
            topic="test_topic",
            tags="not_a_list",
        )
        async def test_endpoint():
            return {"message": "test"}

    assert str(e_info.value) == 'Expected list for "tags"'

    # Passing incorrect type for 'dead_letter_topic' argument
    with pytest.raises(TypeError) as e_info:

        @subscribe(
            app=app,
            path="/test_route",
            pubsub="test_pubsub",
            topic="test_topic",
            dead_letter_topic=1234,
        )
        async def test_endpoint():
            return {"message": "test"}

    assert str(e_info.value) == 'Expected string for "dead_letter_topic"'
