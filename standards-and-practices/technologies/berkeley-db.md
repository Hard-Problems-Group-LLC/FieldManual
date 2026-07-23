# Berkeley DB

## Use When

Use Berkeley DB when an embedded key-value store fits a single-node
application and its concurrency, query, backup, and recovery requirements.
Do not present it as a relational database or a transparent replacement for a
multi-user database service.

## Project-Declared Version Policy

Declare the Berkeley DB implementation and binding separately. Record their
compatibility with the project's language runtime, host platforms, file
format, and licensing requirements.

## Configuration Baseline

- Isolate Berkeley DB access behind a narrow repository or storage adapter.
- Keep database files under one explicit data root.
- Keep key encoding, value serialization, transaction, and durability choices
  documented.
- Prevent storage-specific cursors, flags, and key layouts from leaking into
  domain or transport code.
- Maintain an export format that does not depend on Berkeley DB internals.

## Security and Operations

Protect the data root with appropriate host permissions. Do not store
credentials merely because the database is local. Make process ownership and
single-writer or multi-process assumptions explicit.

Log open, close, recovery, and write failures with enough context to diagnose
the affected store without logging sensitive values.

## Validation

- Test create, read, update, delete, iteration, and reopen behavior.
- Exercise transaction and concurrent-access behavior actually promised by
  the project.
- Test backup, restore, export, import, and recovery from interrupted writes.
- Verify behavior on every supported binding and platform combination.

Exact commands and automation are project-owned. FieldManual ships no
Berkeley DB verifier.

## Failure Handling and Rollback

Fail without silently recreating or truncating an unreadable store. Preserve
the original files for diagnosis and recovery. Test promotion of exported
records into the project's likely successor storage system.

## Maintenance Risks

- Binding and runtime incompatibility.
- Undocumented file-format dependencies.
- Concurrency assumptions that exceed the configured environment.
- Application logic coupled to storage-specific details.

## Related Guidance

- [Python](../languages/python/README.md)
- [PostgreSQL](postgresql.md)
