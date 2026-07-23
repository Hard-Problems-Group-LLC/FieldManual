# SQLAlchemy

## Use When

Use SQLAlchemy when a Python application needs a deliberate relational
database abstraction, SQL expression construction, or ORM mapping. Keep
database behavior visible enough that application correctness does not depend
on accidental session or lazy-loading behavior.

## Project-Declared Version Policy

Declare a SQLAlchemy major release compatible with the project's Python
baseline, database drivers, and migration tooling. Treat major-version
upgrades as behavioral changes and review transaction, query, and mapping
semantics.

## Configuration Baseline

- Centralize engine and session-factory creation.
- Give each request, job, or unit of work an explicit session lifecycle.
- Keep database URLs and credentials in runtime configuration.
- Keep direct engine and session access inside the data layer.
- Do not expose ORM models as external API contracts by default.
- Make transaction ownership and commit behavior explicit.

## Security and Operations

Use parameterized SQL and least-privilege database roles. Enable verbose SQL
logging only for bounded diagnosis; ordinary logs should remain useful and
must not expose secrets or sensitive parameters.

Observe pool checkout failures, transaction failures, slow queries, and
unexpected query volume. Make session cleanup reliable on both success and
exception paths.

## Validation

- Run representative integration tests against each supported database.
- Test transaction boundaries, rollback, and session cleanup.
- Detect N+1 queries and unintended lazy loads in important paths.
- Verify migrations against the same metadata and mappings used by the
  application.
- Exercise connection loss, constraint failures, and retry policy where
  applicable.

Exact commands and automation are project-owned. FieldManual ships no
SQLAlchemy verifier.

## Failure Handling and Rollback

Roll back failed units of work before reusing or closing their sessions.
Translate storage failures at a deliberate boundary without discarding their
diagnostic cause. Use migrations, not ORM startup behavior, for schema
changes.

## Maintenance Risks

- Leaked sessions or connections.
- Hidden autocommit or transaction assumptions.
- N+1 query behavior.
- ORM models growing into domain-wide objects.
- API code coupled to persistence details.

## Related Guidance

- [Python](../languages/python/README.md)
- [Alembic](alembic.md)
- [PostgreSQL](postgresql.md)
