<!-- FIELDMANUAL_MANAGED_FOOTER_START -->
---

## Field Manual Managed Guidance

- Treat the configured project root as the boundary for project-owned files,
  local state, and project-management records.
- Treat the configured framework root as read-only guidance when it is a
  submodule. Do not write project state into the FieldManual subtree.
- Use `project-management/` for the backlog, active and completed work, bugs,
  proposals, reviews, decisions, open questions, and bounded human requests.
- Keep durable behavior and interface contracts in `docs/specifications/`.
- Keep checkout-local state and policy inputs under `.local/`; never commit
  `.local/FieldManual-localconfig.toml`.
- Put cross-project change requests under `ECRs/<target-project>/`. Use the
  ready `ECRs/FieldManual/` tree for FieldManual requests and copy
  `ECRs/_target-template/` for another target.
- FieldManual supplies prose standards, not language-specific verification
  programs. Use the consuming project's declared build, test, lint, security,
  and release commands.
- Project-specific instructions may specialize FieldManual defaults. Record
  intentional exceptions explicitly instead of allowing silent drift.
<!-- FIELDMANUAL_MANAGED_FOOTER_END -->
