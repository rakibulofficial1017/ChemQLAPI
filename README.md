# ChemQL Flask API

The Flask application, dependencies, templates, static files, and API tests live
in this directory.

From the `Language/` directory, install the ChemQL library and API dependency:

```bash
python -m pip install -e ./chemql
python -m pip install -r api/requirements.txt
```

Start the development server from `Language/`:

```bash
flask --app api.app run
```

Send a query using the `query` parameter. Add `json=true` to receive JSON:

```text
/?query=search%20elements&json=true
```
