"""A local upstream service for exercising the proxy."""
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify(status="ok", service="upstream")


@app.route("/echo", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
def echo():
    return jsonify(
        method=request.method,
        query=list(request.args.items(multi=True)),
        body=request.get_data(as_text=True),
        client_id=request.headers.get("X-Client-ID"),
    )


@app.get("/items")
def items():
    return jsonify(items=[{"id": 1, "name": "Example item"}])


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=9000, debug=True)
