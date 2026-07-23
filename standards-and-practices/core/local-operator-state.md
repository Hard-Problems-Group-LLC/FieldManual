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
- local wrappers or environments; and
- credentials or private endpoints when a project explicitly permits local
  file storage for them.

The entire `.local/` directory should be excluded from version control.
Projects should create it only when needed.

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
