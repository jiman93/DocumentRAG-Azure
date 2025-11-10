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
  - `DocumentsController` respects cache settings via injected `GatewayOptions`.
- **Rate limiting**
  - Implemented partitioned fixed‑window throttling (per user / IP) driven by `RateLimitingOptions`.
  - Global “no limiter” fallback when rate limiting is disabled.
- **Resilient downstream calls**
  - Named HttpClient (`PythonRagApi`) with exponential back‑off retry and circuit breaker (via Polly) targeting the FastAPI backend.
- **Health checks**
  - Added readiness probes for Redis (when enabled) and the Python API.
  - Exposed `/health`, `/health/ready`, `/health/live`, plus the Health Checks UI dashboard.
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
  - Health checks UI polls `https://localhost:7001/health`; the SSL errors in the console are expected until we host HTTPS.

- **Warnings**
  - `Azure.Identity` 1.10.0 flagged for security advisories → plan to upgrade.
  - `ISystemClock` is obsolete in the custom authentication handler → refactor to new `TimeProvider` when convenient.

## Remaining Work / Ideas

- Harden `AllowAnonymousAuthenticationHandler` (replace obsolete API).
- Wire up HTTPS locally (or change Health Checks UI configuration to poll HTTP).
- Add more granular logging/metrics (Serilog sinks, Application Insights telemetry).
- Document build/test workflow (dotnet test, linting) and CI integration.

Feel free to extend this log as new milestones are completed.

