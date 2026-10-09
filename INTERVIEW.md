# Interview exercise: rate-limiting proxy

Explore the starter by sending requests through the proxy to the sample upstream.

Add per-client rate limiting to the proxy. Use the `X-Client-ID` header as the client identity for this exercise; it is a test identity, not authentication.

## Required behavior

- Allow each client 5 forwarded requests per 10-second window. Make both values configurable.
- Requests from different clients have independent quotas. Each client's window starts when its first request is admitted.
- Reject excess requests with HTTP 429 and a JSON error. Rejected requests must not reach the upstream or extend the window.
- Include `Retry-After` as a positive integer number of seconds until another request can be admitted.
- At the window boundary, the client can send requests again.
- Reject a missing or blank `X-Client-ID` with HTTP 400 without contacting the upstream.
- Exempt `GET /health` from client identity checks and rate limiting.
- Count admitted requests even when the upstream returns an error or times out.
- Ensure concurrent requests for one client cannot exceed the quota within one running proxy process.

Preserve existing proxy behavior for admitted requests. Add tests demonstrating the requirements, including boundary timing, client isolation, and concurrency. Tests should not depend on long real-time sleeps.

Be ready to explain your algorithm, time and memory costs, clock choice, and what changes would be needed for multiple proxy processes. These are discussion topics; distributed coordination is outside the required implementation.
