# Web Page Load and Render Profiling

Load this knack when a page reaches browser load events long before it is
stable and usable. The goal is a repeatable audit that measures structural
completion, semantic readiness, and visual settling rather than one generic
"loaded" timestamp.

## Mental Model

`DOMContentLoaded` means the document was parsed. The `load` event means
document-tied subresources completed. Neither proves that client code fetched
data, populated the route, finished hydration, stopped resizing content, or
made the primary interaction usable.

Treat readiness as at least four milestones:

1. navigation reached a browser milestone;
2. the route shell and expected elements exist;
3. the first meaningful route render is complete; and
4. a bounded quiet window passes without meaningful structural churn.

"Fully rendered" is a product contract, not a browser standard.

## Signal Families

Combine:

- browser timing for navigation and resource milestones;
- application-owned readiness signals for semantic meaning; and
- observer-based evidence for structural and visual stability.

Browser timing explains when platform events occurred. Application signals
explain when owned work became usable. Observers test whether the page
continued to change after that claim.

## Harness Shape

Playwright is a strong option because it can instrument a page before
application code runs, drive realistic scenarios, inspect DOM-side state, and
capture traces.

The audit harness belongs to the application project. Its location,
dependencies, commands, and thresholds are project-owned; FieldManual does
not ship a profiling script.

A useful harness should:

1. define viewport, authentication, cache, data, network, and CPU conditions;
2. install instrumentation before application code runs;
3. navigate and perform representative actions;
4. wait for semantic readiness plus a quiet window;
5. emit structured measurements; and
6. retain a trace or equivalent evidence for failures and outliers.

## Instrument Before Application Code

Install lightweight observers before navigation work begins. Record:

- navigation timing;
- mutations in the critical application container;
- size changes in important layout containers;
- layout-shift and long-task entries when supported;
- application readiness attributes or performance marks; and
- the last meaningful structural-change timestamp.

Observe the narrowest stable containers that answer the audit question.
Watching the whole DOM creates noise and observer overhead.

## Application-Owned Readiness

If the project owns rendering, expose an explicit readiness contract. A route
container might use attributes such as:

```text
data-load-state="loading|loaded"
data-update-state="idle|updating"
data-route-key="..."
data-render-revision="..."
```

Use `loading` for initial structural work and switch to `loaded` only when
critical content is present. Use `updating` for later refreshes that should
not redefine initial route readiness.

Custom Performance API marks such as `route:shell-ready`,
`route:content-ready`, and `route:first-usable` can provide additional
milestones.

Do not infer semantic readiness solely from spinner disappearance or arbitrary
text.

## Quiet-Window Rule

Do not treat `networkidle` as a universal readiness signal. Polling,
analytics, websockets, lazy work, and unrelated requests can make network
silence too strict or too weak.

A route may be considered settled after semantic readiness is true and a
bounded interval passes with:

- load state still `loaded`;
- update state still `idle`;
- no meaningful mutations in the critical container;
- no meaningful critical-container resize;
- no new relevant layout-shift entry; and
- no main-thread task above the project's threshold.

After the quiet window, allow one or two animation frames before recording the
final timestamp so measurement does not stop immediately before presentation.

## Measurements

Keep distinct milestones:

- `DOMContentLoaded`;
- `load`;
- shell ready;
- content ready or first usable;
- semantic loaded;
- initial-update idle; and
- quiet-window complete.

Attach supporting evidence:

- mutation and resize counts;
- last structural-change time;
- cumulative layout shift where available;
- long-task count and worst duration;
- scenario, viewport, cache, authentication, and data profile; and
- trace or capture location for an outlier.

One aggregate number hides the cause of regressions.

## Scenario Matrix

Select scenarios based on actual risk:

- cold and warm cache;
- narrow and wide viewports;
- anonymous and authenticated state;
- ordinary and data-heavy routes;
- supported network and CPU constraints; and
- first navigation and client-side route transition.

Use stable fixtures when comparing trends. Measure enough repetitions to
distinguish persistent change from ordinary variance.

## Anti-Patterns

- Equating `load` with usable.
- Treating `networkidle` as authoritative.
- Using fixed sleeps.
- Measuring only a warm local happy path.
- Watching the full document when one stable container is sufficient.
- Returning one timing number without evidence.
- Failing to capture diagnostics for slow or timed-out scenarios.
- Changing the readiness contract without versioning the baseline.

## Further Information

- Playwright `Page` API:
  <https://playwright.dev/docs/api/class-page>
- Playwright page evaluation:
  <https://playwright.dev/docs/evaluating>
- Playwright tracing:
  <https://playwright.dev/docs/api/class-tracing>
- MDN `PerformanceNavigationTiming`:
  <https://developer.mozilla.org/en-US/docs/Web/API/PerformanceNavigationTiming>
- MDN `PerformanceObserver`:
  <https://developer.mozilla.org/en-US/docs/Web/API/PerformanceObserver>
- MDN `MutationObserver`:
  <https://developer.mozilla.org/en-US/docs/Web/API/MutationObserver>
- MDN Resize Observer:
  <https://developer.mozilla.org/en-US/docs/Web/API/Resize_Observer_API>
- MDN `requestAnimationFrame()`:
  <https://developer.mozilla.org/en-US/docs/Web/API/Window/requestAnimationFrame>
- MDN `PerformanceLongTaskTiming`:
  <https://developer.mozilla.org/en-US/docs/Web/API/PerformanceLongTaskTiming>
- web.dev, debugging layout shifts:
  <https://web.dev/articles/debug-layout-shifts>
