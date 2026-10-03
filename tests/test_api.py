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
    assert b"query-history" in response.data
    assert b"localStorage" in response.data


def test_element_fields_render_lists_dictionaries_and_image_previews():
    response = app.test_client().get(
        "/", query_string={"query": 'findel "Hydrogen"'}
    )

    assert response.status_code == 200
    assert b'class="nested-list"' in response.data
    assert b'class="nested-table"' in response.data
    assert b'<img src="https://storage.googleapis.com/' in response.data
    assert b'Hydrogenglow.jpg' in response.data
    assert b"<model-viewer" in response.data
    assert (
        b'src="https://storage.googleapis.com/search-ar-edu/periodic-table/'
        b'element_001_hydrogen/element_001_hydrogen.glb"' in response.data
    )
    assert b"camera-controls" in response.data
    assert b"auto-rotate" in response.data


def test_molecule_fields_render_nested_lists_and_dictionaries_as_html():
    response = app.test_client().get(
        "/", query_string={"query": 'findmol "Water"'}
    )

    assert response.status_code == 200
    assert b'class="nested-list"' in response.data
    assert b'class="nested-table"' in response.data
    assert b">Elements<" in response.data
    assert b">Bonds<" in response.data


def test_html_result_includes_copy_and_json_download_controls():
    response = app.test_client().get(
        "/", query_string={"query": 'findel "Hydrogen"'}
    )

    assert response.status_code == 200
    assert b"Copy terminal text" in response.data
    assert b"Download JSON" in response.data
    assert b"chemql-result.json" in response.data
    assert b'id="serialized-result"' in response.data
    assert b'id="terminal-result"' in response.data
