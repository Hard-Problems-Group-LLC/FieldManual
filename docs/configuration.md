# FieldManual Configuration

## Required Files

Every project that adopts FieldManual has a tracked configuration:

```text
$(PROJECTROOT)/FieldManual-config.toml
```

The bootstrap also creates a checkout-local override:

```text
$(PROJECTROOT)/.local/FieldManual-localconfig.toml
```

The tracked file loads first. The local file loads second and replaces the
recognized values it declares. Both distributed skeletons declare all
required keys:

```toml
FieldManual_ConfigVersion = 1
FieldManual_FrameworkRoot = "FieldManual"
FieldManual_ProjectRoot = "."
```

The local file is an override, not a tracked source of project policy.
`.local/` must remain ignored by version control. The bootstrap also creates
`.local/tmp/` as the default private parent for disposable project-local test
and tool workspaces; see
[Local Operator State](../standards-and-practices/core/local-operator-state.md).

## Path Semantics

Relative values in both files resolve from the directory containing the
tracked `FieldManual-config.toml`. They never resolve from the ambient working
directory or from `.local/`.

Absolute paths are accepted in the local file. For portability, use forward
slashes in TOML paths, including on Windows.

The bootstrap canonicalizes the paths before comparison:

- `FieldManual_ProjectRoot` must identify the selected project root.
- `FieldManual_FrameworkRoot` must identify the directory containing the
  running `bootstrap.py` and `FieldManual-layout.toml`.
- Equal roots mean FieldManual is maintaining itself.
- Unequal roots mean consuming-project mode, and the framework root must be a
  strict descendant of the project root.

The final structural check does not replace Git's own submodule registration.
Consuming projects should keep FieldManual as a real submodule as project
policy requires.

## Local Override Precedence

The local file must be internally complete even when only one value differs.
This makes the effective pair visible whenever the file is inspected.
Both files are always schema- and version-checked. When an existing local
file is present, root placement is checked after applying its overrides. When
the local file is absent, the tracked roots must already be valid before the
bootstrap will generate a matching local file.

For example:

```toml
FieldManual_ConfigVersion = 1
FieldManual_FrameworkRoot = "/work/project/vendor/FieldManual"
FieldManual_ProjectRoot = "/work/project"
```

The bootstrap rejects:

- missing or unknown keys;
- unsupported configuration versions;
- duplicate keys or case-only key collisions;
- unsupported TOML syntax;
- nonexistent or disagreeing roots; and
- a framework outside the project in consuming-project mode.

It does not expand environment variables or infer an operator home.

## Supported TOML Subset

Python 3.9 and 3.10 do not include `tomllib`. To remain dependency-free and
behave identically on every supported interpreter, the bootstrap implements a
strict TOML subset:

- top-level bare keys;
- double-quoted or single-quoted strings;
- decimal integers;
- booleans; and
- arrays of those scalar values, including multiline arrays.

Comments begin with `#` outside strings. Tables, dotted keys, inline tables,
dates, floats, multiline strings, and other TOML features are rejected.
FieldManual's own configuration and layout files stay within this subset.

## Layout Declaration

`FieldManual-layout.toml` is framework-owned and version controlled. It
declares:

- every required directory;
- `.local/` and `.local/tmp/` as private directories;
- the allowed roots for create-only skeletons;
- every create-only skeleton file;
- the project and local configuration sources and destinations;
- the managed AGENTS templates and destination; and
- the `.gitignore` path and required entries.

The file list is explicit. Adding a file beneath `templates/` does not install
it until the layout declaration also names it.
