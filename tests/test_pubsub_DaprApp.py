from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_dapr_helper.pubsub import subscribe, DaprFastAPI


def mock_endpoint():
    return {"message": "test"}


def test_daprfastapi_initialization():
    dapr = DaprFastAPI()
    assert isinstance(dapr, DaprFastAPI)
    assert dapr._subscriptions == []
    assert not dapr.remove_dapr_data


def test_daprfastapi_with_remove_data_option():
    dapr = DaprFastAPI(remove_dapr_data=True)
    assert dapr.remove_dapr_data


def test_extract_route_info():
    app = FastAPI()
    dapr = DaprFastAPI()

    @subscribe(app=app, path="/test", pubsub="test_pubsub", topic="test_topic")
    def test_endpoint():
        return {"message": "test"}

    assert not dapr._subscriptions  # The route info list should be empty initially

    route_info = dapr._extract_route_info(app)
    assert (
        len(route_info) == 1
    )  # After extracting, there should be one item in the list

    # Check the contents of the extracted route info
    info = route_info[0]
    assert info["pubsubname"] == "test_pubsub"
    assert info["topic"] == "test_topic"
    assert info["route"] == "/test"
    assert info["metadata"] == {}

    # If remove_dapr_data option is enabled, dapr information should be removed from the route
    dapr = DaprFastAPI(remove_dapr_data=True)
    dapr._extract_route_info(app)
    for route in app.routes:
        if hasattr(route, "openapi_extra") and "dapr" in route.openapi_extra:
            assert False  # Fails the test if there is any route with 'dapr' in openapi_extra


def test_generate_subscribe_route():
    app = FastAPI()
    dapr = DaprFastAPI()

    @subscribe(app=app, path="/test", pubsub="test_pubsub", topic="test_topic")
    def mock_endpoint():
        return {"message": "test"}

    dapr.generate_subscribe_route(app)

    # Check that the /dapr/subscribe route has been added
    routes = [route.path for route in app.routes]
    assert "/dapr/subscribe" in routes

    # Test the /dapr/subscribe route
    client = TestClient(app)
    response = client.get("/dapr/subscribe")
    assert response.status_code == 200
    assert len(response.json()) == 1
    subscription_info = response.json()[0]
    assert subscription_info["pubsubname"] == "test_pubsub"
    assert subscription_info["topic"] == "test_topic"
    assert subscription_info["route"] == "/test"
    assert subscription_info["metadata"] == {}
