# FastAPI

## Use When

Use FastAPI for Python HTTP APIs that benefit from typed request and response
models, generated OpenAPI descriptions, and asynchronous-capable handlers.
Do not let framework convenience erase service, authorization, or persistence
boundaries.

## Project-Declared Version Policy

Declare compatible FastAPI, validation-library, ASGI-server, and Python
versions together. Treat major validation-library changes as interface
changes that require focused review.

## Configuration Baseline

- Keep one explicit application entry point.
- Group routers by stable API area and version public interfaces deliberately.
- Load configuration through explicit settings objects.
- Keep authentication and authorization outside ordinary route-body logic.
- Keep routes thin and delegate domain work to services.
- Keep database sessions and storage adapters behind owned dependencies.

## Security and Operations

Treat request data and backend responses as untrusted at their boundaries.
Do not hardcode secrets, credentials, or connection URLs. Define request-size,
timeout, CORS, proxy-trust, and error-disclosure policies explicitly.

Expose health signals appropriate to the deployment and keep structured
request, exception, and dependency-failure logs. Avoid placing sensitive
payloads or credentials in logs.

## Validation

- Test request validation, response schemas, authorization, and error shapes.
- Exercise asynchronous paths with the same concurrency model used in
  production.
- Test the real service and storage wiring for representative integrations.
- Start the deployed server form and run smoke checks against live endpoints.
- Verify generated API descriptions when clients depend on them.

Exact commands and automation are project-owned. FieldManual ships no FastAPI
verifier.

## Failure Handling and Rollback

Return stable, non-sensitive error responses and retain actionable internal
diagnostics. Pair incompatible API or schema changes with an explicit
migration, compatibility, or rollback plan.

## Maintenance Risks

- Blocking work in asynchronous handlers.
- Oversized route modules containing domain logic.
- Hidden import-time or startup side effects.
- API models coupled directly to database models.

## Related Guidance

- [Python](../languages/python/README.md)
- [SQLAlchemy](sqlalchemy.md)
- [Alembic](alembic.md)
