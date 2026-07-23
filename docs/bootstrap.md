# FieldManual Bootstrap

## Responsibility

`bootstrap.py` has one responsibility: establish FieldManual's declared
filesystem skeleton inside the configured project root.

It may:

- create required directories;
- create missing project-owned skeleton files;
- create the tracked and checkout-local root configurations;
- refresh only FieldManual-marked sections of `AGENTS.md`; and
- create or update only FieldManual's marked `.gitignore` block when a
  required entry is otherwise absent.

It does not run Git, access the network, install packages or runtimes, modify
shell startup files, inspect or write a user home, install hooks, or execute
project verification.

## Invocation

Typical consuming project:

```bash
python FieldManual/bootstrap.py --project-root .
```

FieldManual itself:

```bash
python bootstrap.py --project-root .
```

Preview without writing:

```bash
python FieldManual/bootstrap.py --project-root . --dry-run
```

The first consuming-project run should pass `--project-root` explicitly.
Later runs can discover a valid parent configuration. Standard Git submodule
placement may also be inferred, but ambiguous layouts fail with an actionable
message.

## Rerun Policy

The bootstrap is conservative and idempotent:

- identical project-owned skeletons are preserved;
- differing project-owned skeletons are reported and preserved;
- there is no broad force-overwrite option;
- existing configuration files are validated and preserved;
- only marked AGENTS and `.gitignore` content is refreshed; and
- a compliant rerun leaves project files byte-for-byte unchanged.

To replace a live project-owned record with a new starter, review the
difference and perform that replacement deliberately outside the bootstrap.

## Safety Model

Before writing, the bootstrap validates the complete declared layout:

- manifest paths must be portable relative paths without `..`;
- every template source must be an explicit regular file beneath
  `templates/`;
- duplicate and case-fold-colliding destinations are rejected;
- required directories cannot collide with files;
- destination traversal through symlinks is rejected;
- every destination remains beneath the canonical project root;
- malformed or duplicate managed markers are rejected; and
- unresolved FieldManual placeholders are rejected.

Writes use same-directory temporary files and atomic publication. Before each
write, the bootstrap verifies that the destination still matches its
preflight state. On platforms with directory-descriptor support, mutations
are anchored to the preflighted project root and each parent is opened without
following symlinks. Create-only files use an atomic no-replace publication, so
a file that appears concurrently is preserved and causes a failure.

On platforms whose Python and operating-system APIs do not support anchored
directory-descriptor mutations, the bootstrap uses the portable path API and
repeats its confinement and symlink checks immediately before each mutation.
Existing symlinks are still rejected, but the standard library cannot close
a hostile concurrent parent-renaming race on those platforms. Do not run the
bootstrap while another actor can rewrite the project directory tree.

Managed-file updates are rechecked immediately before replacement. Portable
filesystems do not provide a universal compare-and-swap operation for an
existing pathname, so do not edit `AGENTS.md` or `.gitignore` concurrently
with the bootstrap.

No multi-file filesystem operation is perfectly transactional. A late
filesystem failure may leave earlier independent creations in place, but each
written file is complete and the idempotent rerun resumes safely.

## Managed AGENTS Sections

The templates contain these markers:

```text
<!-- FIELDMANUAL_MANAGED_HEADER_START -->
<!-- FIELDMANUAL_MANAGED_HEADER_END -->
<!-- FIELDMANUAL_MANAGED_FOOTER_START -->
<!-- FIELDMANUAL_MANAGED_FOOTER_END -->
```

The bootstrap removes one valid prior header and footer, preserves the
project-owned body, and writes refreshed managed sections around it. Partial,
duplicated, or misordered markers are hard failures.

## Managed `.gitignore`

If every required entry already exists as an active `.gitignore` line, the
bootstrap changes nothing. This allows another reviewed managed block or
project-authored policy to own `.local/`.

When an entry is missing, the bootstrap creates or refreshes one block:

```text
# BEGIN FieldManual managed local state
.local/
# END FieldManual managed local state
```

All content outside that block is preserved. Partial or duplicate FieldManual
markers are hard failures.

## Exit Behavior

Success exits with status `0`, including normal preservation of differing
project-owned records. Configuration, manifest, confinement, marker, or
filesystem failures exit nonzero and print a concise `FAIL` message without a
dependency traceback.
