# FieldManual Templates

These are create-only skeletons for projects that consume FieldManual. The
installed copies become project-owned records; the copies here remain clean
starters.

Install them into the repository root with:

```bash
python FieldManual/bootstrap.py
```

When FieldManual is nested somewhere other than `FieldManual/`, invoke the
script at its actual path. Use `--project-root` for the first installation
when the project root cannot be inferred safely, and use `--dry-run` to
preview changes.

The layout and installation policies are declared in
`../FieldManual-layout.toml`. The installer:

- creates required directories;
- creates missing skeleton files without replacing live records;
- creates the tracked and local FieldManual configuration files;
- refreshes only the marked FieldManual sections of `AGENTS.md`; and
- ensures the required `.gitignore` entries while preserving other content.

The installed `ECRs/` skeleton includes a ready FieldManual target and a
non-live `_target-template/` that projects copy for any other target.
Existing ECR files are project-owned and remain create-only on framework
upgrades; reconcile older skeletons deliberately instead of expecting a
bootstrap overwrite.

See `../docs/bootstrap.md` for the complete contract.
