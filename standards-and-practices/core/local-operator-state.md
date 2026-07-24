# Local Operator State and Policy Inputs

## Purpose

Keep shared project policy separate from checkout-local state, secrets, and
operator-specific overrides.

## Tracked Baseline

Configuration and policy needed by every collaborator should be tracked in
the project repository. The tracked form is the reviewable shared baseline
and must not contain secrets or workstation-specific absolute paths.

## Local State

Use the project root's `.local/` directory for checkout-local mutable state,
including:

- local configuration overrides;
- operator notes intended for local agents;
- caches and transient tool state;
- disposable test workspaces and temporary artifacts under `.local/tmp/`;
- local wrappers or environments; and
- credentials or private endpoints when a project explicitly permits local
  file storage for them.

The entire `.local/` directory must be excluded from version control. A
project adopting FieldManual must keep `.local/` as an effective `.gitignore`
rule even when another tool owns the matching ignore block. Ignored state is
still subject to the project's security, retention, and cleanup policy.

## Project-Local Temporary Workspaces

By default, tools, tests, developers, and AI assistants should allocate
disposable project work beneath:

```text
$(PROJECTROOT)/.local/tmp/
```

Use a uniquely named child for each tool, task, or test run. Keeping temporary
work inside the configured, ignored project boundary makes ownership obvious,
avoids dirty worktrees, and reduces unnecessary permission or cleanup
approval prompts caused by using unrelated filesystem locations. In
consuming-project mode, use the consuming project's `.local/tmp/`, never a
`.local/` directory inside the FieldManual submodule.

Treat `.local/tmp/` as disposable, not durable storage:

- publish required reports or retained artifacts to a documented project
  location before removing the run directory;
- retain a failed run only when its diagnostic value warrants the local disk
  and sensitivity cost;
- use restrictive permissions when data, credentials, endpoints, or captured
  sessions could be sensitive;
- resolve and verify the cleanup target as a descendant of `.local/tmp/`;
- remove only a run directory the current operation created or explicitly
  acquired; and
- never recursively remove `.local/` or `.local/tmp/` itself based only on an
  environment variable, unchecked string, glob, or ambient working directory.

Use an operating-system or runner-provided temporary directory when a test
specifically requires system temporary-directory semantics, cross-user
access, a different filesystem, or an ephemeral CI facility. Apply the same
unique-run, ownership, confinement, sensitivity, and cleanup rules there, and
document the exception when it affects reproducibility.

## Override Rules

- Local overrides must be deliberate and documented by schema or policy.
- Merge precedence must be deterministic: a reader should be able to identify
  the effective value and its source.
- Unknown keys, invalid types, and ambiguous conflicts should fail clearly
  rather than being ignored.
- Local overrides should not silently weaken mandatory safety boundaries.
- A tool must not copy local notes, secrets, or private provenance into
  tracked files.

## Agent and Operator Responsibilities

Load applicable local policy notes before broad mutation, validation, staging,
or cleanup when project instructions identify such files.

Treat local policy inputs as instructions for that checkout, but do not stage,
publish, summarize, or disclose their contents unless the operator explicitly
authorizes it.

Executable enforcement of tracked-versus-local policy belongs to consuming
projects or future verifier submodules.
