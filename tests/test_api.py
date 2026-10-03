import pytest


pytest.importorskip("flask")

from api.app import app


def test_homepage_renders_when_query_is_missing():
    response = app.test_client().get("/")

    assert response.status_code == 200
    assert b'name="query"' in response.data
    assert b'src="/static/logo.png"' in response.data
    assert b'Mohammad Rakibul Islam' in response.data
    assert b'ChemQLAPI' in response.data


def test_logo_is_available_from_static_route():
    response = app.test_client().get("/static/logo.png")

    assert response.status_code == 200
    assert response.mimetype == "image/png"


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
    assert b"\x1b" not in response.data


@pytest.mark.parametrize(
    ("query", "expected_text"),
    [
        ('findel "Hydrogen"', b"Hydrogen"),
        ('findmol "Water"', b"Water"),
        ('findre "Haber process"', b"Haber process"),
        ("search elements limit 2", b"Helium"),
        ("search molecules limit 2", b"Glucose"),
        ("search reactions limit 2", b"Methane combustion"),
    ],
)
def test_html_formats_chemistry_records_without_terminal_ansi(query, expected_text):
    response = app.test_client().get("/", query_string={"query": query})

    assert response.status_code == 200
    assert expected_text in response.data
    assert b"\x1b" not in response.data


def test_query_form_supports_shift_enter_multiline_input():
    response = app.test_client().get("/")

    assert b"<textarea" in response.data
    assert b"Press Shift+Enter to add a line" in response.data
    assert b"event.shiftKey" in response.data
