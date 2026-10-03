from flask import Flask, jsonify, render_template, request
from chemql import Element, Molecule, Reaction, Unknown, execute_query_text # type: ignore


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


@app.route("/", methods=["GET"])
def index():
    query = request.args.get("query")

    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

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
        result=result,
        result_type=result_type,
        item_type=item_type
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)