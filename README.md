# Rate-limiting proxy interview practice

A working HTTP proxy starter with a local upstream service. Rate limiting is intentionally unimplemented. There is no implementation plan or reference solution.

## Run locally

Requires Python 3.9 or newer.

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

In one terminal, start the upstream:

```sh
source .venv/bin/activate
python -m proxy.upstream
```

In another terminal, start the proxy:

```sh
source .venv/bin/activate
python -m proxy.app
```

The proxy listens on http://127.0.0.1:8000 and forwards to http://127.0.0.1:9000. Set `UPSTREAM_URL` to use a different trusted upstream.

```sh
curl 'http://127.0.0.1:8000/echo?tag=a&tag=b' -H 'X-Client-ID: alice'
curl http://127.0.0.1:8000/echo -X POST -H 'X-Client-ID: bob' -d 'hello'
curl http://127.0.0.1:8000/items
```

`GET /health` is handled locally. Other routes are forwarded with their method, query parameters, body, and end-to-end headers. Upstream timeouts produce 504; connection failures produce 502. Responses are buffered, and this small local practice app does not support WebSockets or streaming. Keep it on localhost; it is not a production gateway.

## Tests

```sh
python -m pytest -q
```

Tests use a fake upstream, so neither server needs to be running. See [INTERVIEW.md](INTERVIEW.md) for the exercise.
