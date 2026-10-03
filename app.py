from flask import Flask, jsonify, render_template, request
from chemql import Element, Molecule, Reaction, ReturnTable, Unknown, execute_query_text


app = Flask(__name__)


def _serialize_result(value):
    if isinstance(value, Unknown):
        return _serialize_result(value.value)
    if isinstance(value, (Element, Molecule, Reaction)):
        return {
            field: _serialize_result(getattr(value, field))
            for field in value.__slots__
        }
    if isinstance(value, dict):
        return {key: _serialize_result(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serialize_result(item) for item in value]
    return value


def _prepare_html_result(result):
    object_types = (Element, Molecule, Reaction)

    if isinstance(result, object_types):
        return {
            "kind": "records",
            "records": [_serialize_result(result)],
            "record_type": type(result).__name__,
        }

    if isinstance(result, list) and result and all(
        isinstance(item, object_types) for item in result
    ):
        return {
            "kind": "records",
            "records": [_serialize_result(item) for item in result],
            "record_type": type(result[0]).__name__,
        }

    if isinstance(result, ReturnTable):
        columns = list(result)
        row_count = max((len(result[column]) for column in columns), default=0)
        rows = [
            [
                _serialize_result(result[column][row_index])
                if row_index < len(result[column])
                else None
                for column in columns
            ]
            for row_index in range(row_count)
        ]
        return {"kind": "table", "columns": columns, "rows": rows}

    if isinstance(result, dict):
        return {
            "kind": "table",
            "columns": ["Field", "Value"],
            "rows": [
                [key, _serialize_result(value)]
                for key, value in result.items()
            ],
        }

    if isinstance(result, list):
        return {"kind": "list", "items": [_serialize_result(item) for item in result]}

    return {"kind": "value", "value": _serialize_result(result)}


@app.route("/", methods=["GET"])
def index():
    query = request.args.get("query")

    if not query:
        return render_template("index.html")

    result = execute_query_text(query)
    result_type = type(result).__name__

    item_type = type(result[0]).__name__ if isinstance(result, list) and result else None

    if request.args.get("json") == "true":
        return jsonify({
            "result": _serialize_result(result),
            "type": result_type
        }), 200

    return render_template(
        "index.html",
        result=_prepare_html_result(result),
        serialized_result=_serialize_result(result),
        terminal_text=str(result),
        result_type=result_type,
        item_type=item_type
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)