import pytest


pytest.importorskip("flask")

from api.app import app


def test_api_requires_query_parameter():
    response = app.test_client().get("/")

    assert response.status_code == 400
    assert response.json == {"error": "Query parameter is required"}


def test_api_returns_chemql_objects_as_json():
    response = app.test_client().get(
        "/",
        query_string={
            "query": 'search elements name = "Hydrogen"',
            "json": "true",
        },
    )

    assert response.status_code == 200
    assert response.json["type"] == "Element"
    assert response.json["result"]["name"] == "Hydrogen"


def test_api_renders_html_result():
    response = app.test_client().get(
        "/",
        query_string={"query": 'search elements name = "Hydrogen"'},
    )

    assert response.status_code == 200
    assert b"Hydrogen" in response.data
