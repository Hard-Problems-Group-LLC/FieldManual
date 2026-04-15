# Field Manual Managed AGENTS Sections

## Purpose

FieldManual can manage a lightweight wrapper around a consuming repository's
root `AGENTS.md` file when that repository wants FieldManual-based guidance for
non-coding worker agents and their human collaborators.

## How It Works

- `FieldManual/templates/AGENTS-header.md` provides the managed header block.
- `FieldManual/templates/AGENTS-footer.md` provides the managed footer block.
- `python FieldManual/bootstrap.py` rewrites `AGENTS.md` by:
  - removing any existing FieldManual-managed header and footer blocks
  - preserving any project-specific body content between them
  - writing the refreshed managed wrapper around that body

## Design Intent

- Keep the managed wrapper short and stable.
- Put repository-specific instructions in the body of `AGENTS.md`.
- Keep the managed sections oriented toward data-centric, non-coding workflows
  unless the consuming repository explicitly broadens that scope.
- Avoid baking heavy tooling or unrelated software-development rules into the
  managed sections.

## Markers

The managed sections are delimited by:

- `<!-- FIELDMANUAL_MANAGED_HEADER_START -->`
- `<!-- FIELDMANUAL_MANAGED_HEADER_END -->`
- `<!-- FIELDMANUAL_MANAGED_FOOTER_START -->`
- `<!-- FIELDMANUAL_MANAGED_FOOTER_END -->`

## Editing Guidance

- Edit the wrapper by changing the templates in `FieldManual/templates/`.
- Edit project-specific instructions by changing the body of the root
  `AGENTS.md`.
- Re-run `python FieldManual/bootstrap.py --template AGENTS.md --force` after
  changing the managed templates when you want to refresh only the root file.
