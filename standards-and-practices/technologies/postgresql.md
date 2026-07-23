# PostgreSQL

## Use When

Use PostgreSQL when an application needs relational constraints, expressive
queries, concurrent access, transactional behavior, or operational features
that exceed an embedded store. Treat it as a durable service with explicit
backup and recovery obligations.

## Project-Declared Version Policy

Declare a supported PostgreSQL major release and record compatibility with
drivers, extensions, migration tools, backup formats, and hosting
infrastructure. Plan major upgrades before the current release leaves the
project's support window.

## Configuration Baseline

- Keep connection settings in runtime configuration, not source code.
- Manage schema through reviewed, versioned migrations.
- Use separate roles for administration, migration, and application access
  when their privileges differ.
- Define connection-pool, statement-timeout, transaction, and timezone
  behavior deliberately.
- Record required extensions and their lifecycle.

## Security and Operations

Use least-privilege roles and authenticated, encrypted connections when data
crosses an untrusted boundary. Protect credentials and backup artifacts.
Restrict network exposure to approved clients and administrative paths.

Observe connection failures, pool saturation, locks, replication state,
migration state, storage growth, and slow queries. Logs and metrics must not
expose sensitive statement parameters.

## Validation

- Apply migrations to a fresh database and a representative existing schema.
- Run integration tests against a real supported PostgreSQL instance.
- Test constraints, transactions, concurrent updates, and failure behavior
  that the application relies on.
- Exercise backup restoration and verify the restored data.
- Evaluate representative queries and indexes with realistic data volume.

Exact commands and automation are project-owned. FieldManual ships no
PostgreSQL verifier.

## Failure Handling and Rollback

Maintain tested backup, restore, and point-in-time recovery procedures
appropriate to the service. Pair risky schema or data changes with a
roll-forward or rollback decision. Never improvise production table edits as
an undocumented recovery process.

## Maintenance Risks

- Connection-pool exhaustion.
- Migration and model drift.
- Untested backups.
- Queries and indexes that work only at development scale.
- Extensions blocking a major-version upgrade.

## Related Guidance

- [Alembic](alembic.md)
- [SQLAlchemy](sqlalchemy.md)
- [Berkeley DB](berkeley-db.md)
- [Podman](podman.md)
