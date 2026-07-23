# UI Antipatterns

## Scope

These heuristics apply to interactive interfaces across desktop, web, mobile,
and terminal applications. Platform conventions and user research remain
authoritative for a specific product.

## Avoid

- Large flat navigation groups with no meaningful hierarchy.
- Important actions represented only by ambiguous icons or unlabeled
  controls.
- Context changes, navigation, or submission triggered unexpectedly by focus
  or ordinary input.
- Dialogs that launch more dialogs when an inline or navigable flow would be
  clearer.
- Help flows that add another decision instead of taking the user to relevant
  guidance.
- Invisible keyboard focus, broken focus order, or pointer-only operation.
- Meaning conveyed only by color, position, sound, or another single sensory
  cue.
- Insufficient contrast or status text that assistive technology cannot
  identify.
- Inconsistent names, locations, and interaction patterns for the same
  concept.
- Silent long-running work with no progress, cancellation, or recovery path.

## Recommended Default

- Group navigation by user task and reveal detail progressively.
- Label important actions clearly.
- Keep state changes predictable and reversible where practical.
- Treat accessibility defects as design defects.
- Preserve keyboard, assistive-technology, reduced-motion, zoom, and
  responsive-layout behavior appropriate to the platform.
- Test with representative users and supported input modes.

## Sources and Review Caveat

Platform guidance evolves. Verify current platform-specific recommendations
before treating an example pattern as mandatory.

Reviewed: 2026-07-23.

- W3C, [Web Content Accessibility Guidelines 2.2](https://www.w3.org/TR/WCAG22/)
- Apple, [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- Microsoft,
  [Accessibility Overview](https://learn.microsoft.com/en-us/windows/apps/design/accessibility/accessibility-overview)
