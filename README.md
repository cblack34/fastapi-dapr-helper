FastAPI Dapr Helper
===================

FastAPI Dapr Helper is a Python library that facilitates creating subscriptions to Dapr pubsub topics with FastAPI.

This library introduces a decorator named `subscribe` which, in conjunction with a route generator, allows you to easily setup Dapr pubsub topic subscriptions within your FastAPI application. The package also provides a `DaprFastAPI` class to manage the subscriptions and generate a subscription route in your FastAPI application.

## Installation

### pip

```bash
pip install fastapi-dapr-helper
```

### Poetry

```bash
poetry add fastapi-dapr-helper
```


## Subscribe Decorator

The `subscribe` decorator is designed to be used in combination with a route generator. It creates subscriptions to Dapr pubsub topics with FastAPI.

```python
from fastapi_dapr_helper.pubsub import subscribe

@subscribe(app=app, path="/test", pubsub="test_pubsub", topic="test_topic")
def test_endpoint():
    return {"message": "test"}
```

In the above example, the `subscribe` decorator is used to define a pubsub subscription on the `test_endpoint` route.

## DaprFastAPI Class

The `DaprFastAPI` class is used to handle Dapr subscriptions and the FastAPI application.

```python
from fastapi_dapr_helper.pubsub import DaprFastAPI

app = FastAPI()
dapr = DaprFastAPI()

dapr.generate_subscribe_route(app)
```

In this example, the `DaprFastAPI` class is used to handle subscriptions and to generate a `/dapr/subscribe` route in the FastAPI app.

# Working Examples

Here are some working examples of how to use FastAPI Dapr Helper in your project.

## Working Example with FastAPI

```python
import uvicorn
from fastapi import FastAPI
from fastapi_dapr_helper.pubsub import subscribe, DaprFastAPI

app = FastAPI()
dapr = DaprFastAPI()

@subscribe(app=app, path="/test", pubsub="test_pubsub", topic="test_topic")
def test_endpoint():
    return {"message": "test"}

dapr.generate_subscribe_route(app)

uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Output

```bash
curl -X 'GET' \
  'http://localhost:8000/dapr/subscribe' \
  -H 'accept: application/json'
```

```json
[
  {
    "pubsubname": "test_pubsub",
    "topic": "test_topic",
    "route": "/test",
    "metadata": {}
  }
]
```

## Working Example with APIRouter

```python
import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi_dapr_helper.pubsub import subscribe, DaprFastAPI

app = FastAPI()
router = APIRouter()
dapr = DaprFastAPI()

@subscribe(app=router, path="/test", pubsub="test_pubsub", topic="test_topic")
def test_endpoint():
    return {"message": "test"}

app.include_router(router, prefix="/api")
dapr.generate_subscribe_route(app)

uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Output

```bash
curl -X 'GET' \
  'http://localhost:8000/dapr/subscribe' \
  -H 'accept: application/json'
```

```json
[
  {
    "pubsubname": "test_pubsub",
    "topic": "test_topic",
    "route": "/api/test",
    "metadata": {}
  }
]
```


## Functionality Overview

The main function of FastAPI Dapr Helper is to make it easier to create subscriptions to Dapr pubsub topics within FastAPI applications.
It achieves this by using the decorator `subscribe` to embed subscription information into the OpenAPI schema for the route. 
Then the `DaprFastAPI` class uses this information to generate a `/dapr/subscribe` route in the FastAPI app.

The Dapr sidecar will call the `/dapr/subscribe` route to register the subscriptions.

# Contributing

I welcome contributions from the community!
Follow the basic Githubflow PR process:

1. Fork the repo on GitHub.
2. Clone the project to your own machine.
3. Commit changes to your own branch.
4. Push your work back up to your fork.
5. Submit a Pull Request so that your changes can be reviewed.

## Style Guidelines

### TLDR
```bash
black .
```

We follow stringent style guidelines to ensure the readability and maintainability of our code. 
The primary tools used for enforcing these guidelines are `flake8` and `pylint`.

Please see the pyproject.toml file for the specific configuration of these tools.

## Testing

Testing is a vital part of our development process.
Not only must all tests pass before a change can be merged,
but any new sections of code must also include corresponding tests.
This allows us to ensure the stability and reliability of our codebase.

If you are adding a new feature or fixing a bug,
please include detailed tests to demonstrate the correctness of your changes.
These tests will be automatically run when you submit your pull request.
Any pull request that causes existing tests to fail cannot be merged.

To facilitate the testing process, we use `pytest` as our primary testing framework.
Please familiarize yourself with `pytest` to write effective tests for your contributions.

Remember, good tests are as important as the code itself.
They ensure the functionality of the code and prevent regressions.
Thank you for helping maintain the quality of the codebase.

# Conclusion
Please ensure that your code conforms to our style guidelines before submitting a PR. 
If you have any questions, feel free to open an issue for clarification.

Thank you for your contribution!
Happy coding!
