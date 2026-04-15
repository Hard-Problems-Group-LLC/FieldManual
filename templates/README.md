# FieldManual Templates

These files are starter material for a consuming repository's lightweight
process layer for non-coding worker agents and their human collaborators.

They are intended primarily for data-centric repositories and private knowledge
stores rather than as a general software-engineering operating system.

Install them into the repository root with:

```bash
python FieldManual/bootstrap.py
```

Use `--dry-run` to preview and `--force` to overwrite existing files.
Use `--template AGENTS.md --force` when you only want to refresh the managed
`AGENTS.md` wrapper without rewriting other installed files.

The installed copies become the repository's live records. Keep templates here
as reusable starters and evolve the live files in the project root as the
project proceeds.

`FieldManual/bootstrap.py` also manages `AGENTS.md` in the repository root.
It uses `AGENTS-header.md` and `AGENTS-footer.md` to wrap project-specific
content. Before rewriting `AGENTS.md`, it removes any existing
FieldManual-managed header and footer blocks so rerunning the bootstrap does
not duplicate them.
