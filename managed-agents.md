# FieldManual Managed AGENTS Sections

## Purpose

FieldManual manages a small wrapper around a consuming repository's root
`AGENTS.md`. The wrapper directs collaborators to the configured framework
and project roots while preserving project-specific instructions.

## How It Works

- `<FieldManual_FrameworkRoot>/templates/AGENTS-header.md` provides the
  managed header block.
- `<FieldManual_FrameworkRoot>/templates/AGENTS-footer.md` provides the
  managed footer block.
- `bootstrap.py` refreshes `AGENTS.md` by:
  - removing any existing FieldManual-managed header and footer blocks
  - preserving any project-specific body content between them
  - writing the refreshed managed wrapper around that body

## Design Intent

- Keep the managed wrapper short and stable.
- Put repository-specific instructions in the body of `AGENTS.md`.
- Resolve framework and project locations through the tracked configuration
  and optional local override instead of assuming a submodule path.
- Point to canonical standards instead of duplicating them in the wrapper.
- Load language, technology, technique, and knack guidance only when it
  applies.
- Keep executable verification commands project-owned.

## Markers

The managed sections are delimited by:

- `<!-- FIELDMANUAL_MANAGED_HEADER_START -->`
- `<!-- FIELDMANUAL_MANAGED_HEADER_END -->`
- `<!-- FIELDMANUAL_MANAGED_FOOTER_START -->`
- `<!-- FIELDMANUAL_MANAGED_FOOTER_END -->`

## Editing Guidance

- Edit the wrapper by changing `templates/` beneath the configured
  `FieldManual_FrameworkRoot`.
- Edit project-specific instructions by changing the body of the root
  `AGENTS.md`.
- Rerun the configured FieldManual bootstrap after managed templates change.
  The installer changes only the marked sections and preserves the body.
