# Browser Automation

Load this knack when adding a browser test harness, diagnosing an unattended
browser failure, or deciding whether a browser result demonstrates an
environment, harness, or product defect.

Source review: 2026-07-23. Examples use Playwright terminology, but the
diagnostic boundaries apply to other browser drivers.

## Three-Layer Mental Model

Keep these layers separate:

| Layer | Question | Evidence |
| --- | --- | --- |
| Host and runtime | Can this exact driver and browser start and operate under the current OS, container, display, sandbox, and dependency boundary? | Versions, executable source, launch logs, a minimal known-good page, and process exit |
| Harness | Did the scenario select the intended URL, state, viewport, locator, action, wait, and assertion? | Step log, configuration, trace, DOM snapshots, and isolated harness tests |
| Product | Did the application violate its user-visible contract? | Reproducible scenario, application logs, screenshot, DOM/accessibility state, and assertion result |

A browser that cannot launch has not tested the product. A locator that points
at the wrong element has not found a product regression. Prove each earlier
layer before classifying the next.

## Own a Reproducible Browser Stack

The project should pin its browser-automation library and lock its dependency
graph. Record the selected driver version, browser family and revision,
operating-system image, headless or headed mode, and relevant launch options
with every result.

Each Playwright release expects specific browser binaries. Install the
matching Playwright-managed browsers after changing the Playwright version,
and provision their native OS dependencies through the project's documented
workstation or CI mechanism. Do not silently substitute an arbitrary browser
found on `PATH`.

Important distinctions:

- Playwright's default Chromium build is not necessarily the installed
  branded Google Chrome.
- A branded Chrome or Edge channel is a deliberate compatibility target with
  its own policies and headless behavior.
- Playwright's Firefox build contains required patches; branded system
  Firefox is not a supported substitute.
- Playwright WebKit is not branded Safari, and platform-dependent behavior
  can still require a macOS test.

Install only the browser families the project supports, but test every family
claimed by the product's compatibility contract. Update Playwright and its
browsers deliberately through reviewed dependency changes, then rerun the
supported matrix.

## Prove the Execution Boundary

Before debugging an application through a new environment, run a minimal
preflight that launches the selected browser, loads a controlled known-good
page, performs one simple DOM read, and exits cleanly.

Capture:

- driver, runtime, and browser versions;
- resolved browser source or channel;
- operating system and architecture;
- display and headless mode;
- relevant sandbox/container identity;
- exit status, signal, and bounded stderr; and
- whether native dependencies were present.

A code-execution sandbox may correctly forbid browser namespaces, shared
memory, process creation, display access, or downloaded binaries. Do not
weaken the browser's own sandbox or the agent's approval boundary merely to
make a launch succeed. If the project has an authorized host-side browser
command, use it only with the required approval and record that the execution
boundary changed. Otherwise report the environment limitation.

Do not convert “works outside the sandbox” into a universal project rule.
Fix or document the narrow supported boundary and retain a sandboxed
inventory/preflight path when possible.

## Scenario Contract

A scenario should describe user intent rather than a sequence of incidental
DOM operations. Give it:

- a stable name and purpose;
- starting URL and controlled data state;
- authentication and authorization assumptions;
- browser project, viewport or device profile, locale, timezone, color
  scheme, input modality, cache, and network conditions;
- ordered user-visible actions;
- explicit semantic checkpoints;
- requested artifacts; and
- cleanup or isolation behavior.

Keep tests independent. Each should own its cookies, local storage, session
storage, data fixtures, and external-service substitutes unless a deliberate
serial workflow says otherwise. Test services the project controls; mock or
contract-test unstable third-party dependencies instead of making their live
pages a release gate.

For operator-driven investigation, a small scenario runner is often clearer
than one monolithic suite. The same scenario implementation should serve
focused local diagnosis and automated verification so the two paths do not
drift.

## Select a Risk-Based Matrix

Vary dimensions that can change behavior:

- Chromium, Firefox, WebKit, and supported branded channels;
- desktop, tablet, narrow phone, landscape phone, and important custom
  breakpoints;
- pointer, keyboard, and touch-like input;
- anonymous, authenticated, and role-specific state;
- empty, ordinary, large, error, and slow data;
- cold and warm caches;
- headless CI and headed interactive diagnosis; and
- first navigation and client-side route transitions.

Device emulation changes viewport and selected browser capabilities; it does
not prove behavior on physical hardware, its operating system, virtual
keyboard, browser chrome, GPU, or accessibility services. Retain real-device
checks for risks emulation cannot cover.

Do not multiply every dimension blindly. Define a small required matrix from
supported-user risk, then add focused cells for a suspected defect.

## Locators and Waiting

Prefer locators based on user-facing semantics:

1. accessible role and name;
2. associated label;
3. visible text when it is a stable product contract; and
4. a documented test ID when no suitable user-facing contract exists.

Avoid long CSS selectors, XPath tied to DOM ancestry, generated class names,
and raw element handles retained across rerenders. A stable test ID is better
than pretending a fragile selector represents user behavior, but it should
name product meaning rather than implementation layout.

Playwright locators re-resolve elements and provide actionability checks,
auto-waiting, and retryable web-first assertions. Use those facilities.
Do not replace them with fixed sleeps or immediate manual visibility checks.

Browser `load`, `DOMContentLoaded`, and generic network idleness do not prove
that an application is usable. For client-rendered products, define an
application-owned readiness signal and a bounded settling rule. See
[Web Page Load and Render Profiling](../../performance/profiling/WebPageLoadAndRenderProfiling.knack.md)
for the semantic-readiness and quiet-window model.

Every wait must have:

- a named condition;
- a bounded timeout;
- evidence on timeout; and
- an explanation of why satisfying it makes the next action valid.

## Interaction and Layout Diagnostics

When a control is unreachable, capture more than a screenshot:

- viewport and document dimensions;
- target and ancestor bounding boxes;
- visibility, enabled, focus, and accessible state;
- clipping and overflow styles;
- window and relevant-container scroll positions before and after input;
- the element that received pointer or wheel input; and
- overlays or hit-test results at the intended coordinates.

For nested scrolling, act on the intended container and prove which scroll
offset changed. “The page moved” does not show that the correct region
accepted input.

Distinguish:

- present in the DOM;
- rendered;
- within a scrollable path;
- fully visible in the viewport;
- unobscured and action-ready;
- keyboard reachable; and
- usable on a real device.

Choose the condition that matches the product contract. Requiring every
control to be immediately fully visible can be as wrong as accepting an
unreachable control.

## Artifact Set

On a meaningful failure, retain enough evidence to replay the reasoning:

- structured result with scenario, step, assertion, timings, and environment;
- screenshot at failure and, when useful, before the failed action;
- DOM or accessibility snapshot for the affected region;
- browser console and page-error output;
- relevant failed network requests;
- application server correlation identifiers or bounded logs; and
- a Playwright trace for retries or selected diagnostic runs.

Traces are rich but expensive and sensitive. A useful default is trace on the
first retry or on failure, rather than on every successful run.

Keep outputs under a project-declared derived-artifact directory, outside
canonical source. Apply retention limits and avoid publishing artifacts by
default. Screenshots, DOM, storage state, network bodies, URLs, console logs,
and traces can contain personal data, credentials, private content, and
tokens. Redact where possible and control access to the raw evidence.

## Failure Classification

Use the earliest failing layer:

- **Environment failure:** browser missing, incompatible revision, native
  library absent, launch denied, display unavailable, process crash before a
  controlled page works.
- **Harness failure:** invalid option, wrong base URL, stale server, ambiguous
  locator, incorrect scenario state, fixed-sleep race, artifact writer error,
  assertion that does not match the stated contract.
- **Product failure:** a proven viable browser and valid scenario reproduce a
  user-visible contract violation.

Retries are evidence only when they target a known transient condition.
Do not use repeated full-test retries to hide deterministic product or harness
defects. Preserve the first failure because later attempts may change cache,
data, focus, or timing.

## Local and CI Workflow

- Keep one documented project command for each supported scenario or suite.
- Use the same dependency lock and browser selection locally and in CI.
- Pin CI images or record their versions and native dependencies.
- Start the system under test through a bounded project-owned fixture or
  verify an explicitly supplied base URL.
- Run focused smoke scenarios before an expensive matrix.
- Use headed mode, inspector, and slow motion for local diagnosis; use traces
  and structured artifacts for unattended failures.
- Parallelize only isolated tests and protect shared accounts or data.
- Shard large matrices without losing per-cell browser and environment
  identity.

## Review Checklist

- Is the driver pinned and paired with its supported browser binaries?
- Does a minimal preflight prove the active execution boundary?
- Are scenarios user-oriented, isolated, and deterministic?
- Does the matrix match the product's actual support claims?
- Do locators use semantic contracts and web-first assertions?
- Are waits bounded and tied to meaningful readiness?
- Can artifacts distinguish environment, harness, and product failures?
- Are nested scroll and reachability claims backed by geometry and event
  evidence?
- Are traces, screenshots, DOM, network, and auth state treated as sensitive?
- Does running outside an automation sandbox require and retain explicit
  authorization?

## Further Information

- Playwright, browsers and release-matched binaries:
  <https://playwright.dev/docs/browsers>
- Playwright, best practices:
  <https://playwright.dev/docs/best-practices>
- Playwright, locators:
  <https://playwright.dev/docs/locators>
- Playwright, actionability and auto-waiting:
  <https://playwright.dev/docs/actionability>
- Playwright, emulation:
  <https://playwright.dev/docs/emulation>
- Playwright, trace viewer:
  <https://playwright.dev/docs/trace-viewer>
- Playwright, continuous integration:
  <https://playwright.dev/docs/ci>
