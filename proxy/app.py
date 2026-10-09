"""HTTP proxy starter. Rate limiting is the interview exercise."""
import os

import requests
from flask import Flask, Response, jsonify, request

# Connection-specific headers must not cross a proxy boundary.
HOP_BY_HOP = {
    "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailer", "transfer-encoding", "upgrade",
}


def forwarded_headers(headers):
    excluded = HOP_BY_HOP | {
        value.strip().lower() for value in headers.get("Connection", "").split(",")
    }
    return {key: value for key, value in headers.items()
            if key.lower() not in excluded | {"host", "content-length"}}


def create_app(upstream_url=None, transport=None):
    app = Flask(__name__)
    app.config["UPSTREAM_URL"] = (
        upstream_url or os.environ.get("UPSTREAM_URL", "http://127.0.0.1:9000")
    ).rstrip("/")
    if transport is None:
        transport = requests.Session()
        transport.trust_env = False

    @app.get("/health")
    def health():
        return jsonify(status="ok", service="proxy")

    @app.route("/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"])
    @app.route("/<path:path>", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"])
    def forward(path):
        # The configured upstream is fixed; callers cannot choose another host.
        url = app.config["UPSTREAM_URL"] + "/" + path
        try:
            upstream = transport.request(
                method=request.method,
                url=url,
                params=list(request.args.items(multi=True)),
                data=request.get_data(),
                headers=forwarded_headers(request.headers),
                timeout=5,
                allow_redirects=False,
                stream=True,
            )
            try:
                # Preserve encoded response bytes and Content-Encoding together.
                body = upstream.raw.read(decode_content=False)
                return Response(body, status=upstream.status_code,
                                headers=forwarded_headers(upstream.headers))
            finally:
                upstream.close()
        except requests.Timeout:
            return jsonify(error="upstream_timeout"), 504
        except requests.RequestException:
            return jsonify(error="upstream_unavailable"), 502

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=8000, debug=True)
