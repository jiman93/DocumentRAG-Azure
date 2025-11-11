# Gateway Progress Log

This document tracks the main milestones we have completed while bringing the .NET API Gateway online, plus the important follow‑ups that remain.

## Current Capabilities

- **Project setup**
  - Upgraded solution to `net9.0` (`Gateway.Api`, `Gateway.Core`, and test project).
  - Added required NuGet packages for authentication, Redis caching, rate limiting, health checks, and Polly resilience policies.
- **Configuration binding**
  - Introduced strongly‑typed options: `GatewayOptions`, `AuthenticationOptions`, `RateLimitingOptions`.
  - `appsettings.json` updated with `Gateway`, `Authentication`, `RateLimiting`, `Cors`, `ConnectionStrings`, and redis defaults.
- **Authentication**
  - Primary path uses JWT Bearer with configurable authority/audience.
  - Added `AllowAnonymousAuthenticationHandler` so the gateway can operate unsecured when `Authentication.Enabled = false`.
- **Distributed caching**
  - Conditional StackExchange Redis cache if `ConnectionStrings:Redis` is provided; falls back to in‑memory cache when disabled.
  - Document list responses cached for 5 minutes (`documents:list` key) and invalidated on upload/delete.
  - Chat query responses cached for 60 minutes with version-based busting when documents change.
- **Chat proxy**
  - `/api/v1/chat/query` forwards to the Python RAG endpoint with retry policies.
  - Cache keys hash the request payload; streaming responses are rejected early (not supported yet).
- **Rate limiting**
  - Implemented partitioned fixed‑window throttling (per user / IP) driven by `RateLimitingOptions`.
  - Global “no limiter” fallback when rate limiting is disabled.
- **Resilient downstream calls**
  - Named HttpClient (`PythonRagApi`) with exponential back‑off retry and circuit breaker (via Polly) targeting the FastAPI backend.
- **Health checks**
  - Added readiness probes for Redis (when enabled) and the Python API.
  - Exposed `/health`, `/health/ready`, `/health/live`, plus the Health Checks UI dashboard (UI now targets HTTP for the gateway probe to avoid local TLS noise).
- **Swagger / OpenAPI**
  - Always-on Swagger UI mapped to `/swagger/index.html`.
  - Documented three primary controller endpoints: list documents, upload document, chat query.

## Development Tips

- **Run locally**
  ```bash
  cd dotnet-gateway/src/Gateway.Api
  dotnet run --urls http://localhost:7001
  ```
  Swagger UI: `http://localhost:7001/swagger/index.html`

- **Kill stuck instances**
  ```bash
  pkill -f Gateway.Api
  ```
  (Use before restarting on the same port.)

- **Environment**
  - Default port: 7001 (HTTP only)
  - Health checks UI polls `http://localhost:7001/health`, eliminating the earlier HTTPS handshake warnings.

- **Testing strategy**
  - Smoke test with both services running locally (`python-rag-api` on 8000, gateway on 7001) and exercise Swagger endpoints (`/documents`, `/chat/query`).
  - Optional automation: consider xUnit integration tests via `WebApplicationFactory` and a containerized Python API once regression coverage is needed.

- **Warnings**
  - `Azure.Identity` 1.10.0 flagged for security advisories → plan to upgrade.
  - Redis health check will surface as unhealthy when no server is available; disable caching locally if you don't want the noise.

## Remaining Work / Ideas

- ~~Harden `AllowAnonymousAuthenticationHandler` (replace obsolete API).~~
- ~~Wire up HTTPS locally (or change Health Checks UI configuration to poll HTTP).~~ (Switched UI probe to HTTP.)
- Add more granular logging/metrics (Serilog sinks, Application Insights telemetry).
- Document build/test workflow (dotnet test, linting) and CI integration.

Feel free to extend this log as new milestones are completed.

