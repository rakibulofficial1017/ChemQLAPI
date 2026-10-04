# ChemQL Flask API

The Flask application, dependencies, templates, static files, and API tests live
in this directory.

Install the ChemQL library and API dependency:

```bash
python -m pip install -r requirements.txt
```

Start the development server:

```bash
flask --app api.app run
```

Send a query using the `query` parameter. Add `json=true` to receive JSON:

```text
/?query=search%20elements&json=true
```

The web interface renders nested lists and dictionaries as HTML, previews
element images, and displays available element Bohr models in an interactive
3D viewer with camera controls and auto-rotation. The viewer uses Google's
`model-viewer` component from its CDN, so the browser needs internet access to
load it. The page also copies the ChemQL terminal representation, downloads
structured JSON results, and stores recent queries locally in the browser;
history can be cleared from the page.
