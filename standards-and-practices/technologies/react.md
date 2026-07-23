# React

## Use When

Use React for interfaces that benefit from component composition and explicit
state-driven rendering. Keep routing, data access, and application
orchestration visible rather than allowing component boundaries to become the
entire architecture.

## Project-Declared Version Policy

Declare compatible React, renderer, TypeScript, build-tool, and test-library
versions together. Review framework lifecycle and rendering changes before a
major upgrade.

## Configuration Baseline

- Prefer focused components with clear inputs, outputs, and state ownership.
- Separate reusable components from page and application orchestration.
- Centralize network and error-handling boundaries where practical.
- Keep routing and URL state explicit.
- Represent loading, empty, error, retry, stale, and unauthorized states.
- Keep component-only modules compatible with the selected hot-reload model.

## Security, Accessibility, and Operations

Treat API and user-provided content as untrusted. Avoid placing long-lived
credentials in component state or browser storage without an explicit threat
model.

Keyboard operation, focus behavior, semantic structure, readable contrast,
and assistive-technology names are functional requirements. Use error
boundaries at deliberate page or application boundaries and make failures
visible without disclosing sensitive details.

## Validation

- Test component behavior through user-visible outcomes.
- Exercise routing, focus, keyboard, asynchronous, and error transitions.
- Add browser-level coverage for high-risk workflows and integration points.
- Verify portrait, landscape, narrow, wide, and zoomed layouts as applicable.
- Build the production bundle and smoke-test the deployed form.

Exact commands and automation are project-owned. FieldManual ships no React
verifier.

## Failure Handling and Rollback

Keep state, routing, and network boundaries separable enough that one
regression does not require reverting unrelated interface work. Provide
useful fallback states for recoverable failures and preserve user input when
safe to do so.

## Maintenance Risks

- Components that combine rendering, networking, state, and domain logic.
- Effects with stale dependencies or missing cleanup.
- Untyped drift between client and server data contracts.
- Pointer-only or visually encoded interactions.

## Related Guidance

- [TypeScript](../languages/typescript/README.md)
- [Vite](vite.md)
