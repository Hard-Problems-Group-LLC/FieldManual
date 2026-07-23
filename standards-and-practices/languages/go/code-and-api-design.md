# Go Code and API Design

## Purpose

Make Go code straightforward to read, safe to change, and useful to debug.
This document is the canonical FieldManual guidance for Go source style,
package and API design, errors, context, concurrency, configuration, and
source documentation.

## Formatting and Static Analysis

- Every maintained `.go` file, including generated Go source, must match
  `gofmt`. Do not maintain a competing formatting convention.
- A project may use `goimports` to combine canonical formatting with import
  maintenance. If it does, pin the tool and make the expected invocation
  project-owned.
- Run `go vet` explicitly over every module. Treat its findings as possible
  correctness defects that require investigation, not style suggestions to
  suppress casually.
- Select at most a small set of additional, pinned, high-signal analyzers.
  Staticcheck is a common option. Keep configuration in revision control and
  document narrowly scoped suppressions with the reason.
- Treat `go fix` and other rewriting analyzers as reviewed migration tools,
  not as unreviewed CI mutations.
- Mark generated files in the standard form, record the generator and pinned
  inputs, and verify that regeneration produces no unexplained diff. Do not
  hand-edit generated output.

Go has no fixed source line-length limit. If a line is hard to understand,
improve the expression, name, or API rather than mechanically wrapping clear
code to meet an arbitrary column count.

## Packages and Source Organization

- Start with the smallest coherent package structure. Split a package when
  doing so creates a meaningful responsibility or dependency boundary, not
  merely to reduce file length.
- Name packages with short, clear, lowercase words. Avoid underscores,
  mixed-case package names, and generic dumping grounds such as `util`,
  `common`, `misc`, `api`, `types`, and `interfaces`.
- Read exported names as callers see them. Prefer `http.Server`-style names
  over stuttering forms such as `widget.WidgetClient`.
- Keep names unexported until a real caller requires a supported API.
  Exported identifiers create documentation and compatibility obligations.
- Use `internal/` to prevent accidental external dependencies on
  implementation packages.
- Keep `package main` focused on composition: parse external configuration,
  construct dependencies, establish lifecycle control, call application
  code, and select the process exit status. Put behavior in testable ordinary
  packages.
- Avoid import-time I/O, mutable registration, hidden goroutines, and
  configuration reads. Use `init` only where the language or an established
  registration contract makes it unavoidable.
- Avoid dependency cycles by making ownership and direction explicit. Do not
  create a shared dumping-ground package merely to bypass a poor boundary.

Files organize a package for readers; they do not create sub-namespaces.
Group declarations by responsibility and keep tests near the code they
exercise.

## Naming and Readability

- Use `MixedCaps` or `mixedCaps`, including for constants. Preserve familiar
  initialisms such as `ID`, `URL`, and `HTTP`.
- Make name length proportional to scope. Short conventional names such as
  `i`, `r`, `w`, `ctx`, and `err` are clear in small scopes; longer-lived or
  easily confused values need more descriptive names.
- Keep receiver names short, meaningful abbreviations of the receiver type
  and use the same receiver name across its methods. Do not use `this`,
  `self`, or `me`.
- Do not repeat type information that the declaration or package already
  supplies. Prefer `users` to `userSlice` and `cache.New` to
  `cache.NewCache`.
- Use a noun-like accessor such as `Owner` for a cheap field-like lookup.
  Choose verbs such as `Load`, `Fetch`, or `Compute` when an operation may
  block, fail, or perform material work.
- Keep the successful path visible down the page. Handle failures and special
  cases early and avoid an `else` after a branch that returns.
- Use named results when they distinguish otherwise ambiguous values or help
  a deferred operation update a result. Avoid naked returns outside very
  small, obvious functions.
- Prefer explicit control flow and intermediate names over compressed
  expressions whose behavior must be mentally simulated.

Comments should explain intent, invariants, ownership, hazards, and tradeoffs
that the code cannot express. Do not narrate straightforward syntax.

## Interfaces, Types, and Public APIs

- Begin with concrete types. Add an interface when an actual consumer needs
  substitution or when the protocol itself is the supported product.
- Define a small interface near the code that consumes it. Include only the
  methods that consumer needs. Producer-owned public interfaces are
  appropriate when implementers are intentionally part of the API.
- Accept an interface when callers can usefully provide different
  implementations; normally return a concrete type so the implementation can
  grow without forcing an interface change.
- Do not use a pointer to an interface. When interface conformance is a
  durable contract, a compile-time assignment may document and verify it.
- Prefer a useful zero value where it is natural and unambiguous. Use a
  constructor when dependencies, validation, resource ownership, or
  invariants require one.
- Use one receiver kind consistently for a type. Use a pointer receiver when
  methods mutate the receiver, the value is large, or it contains a mutex or
  another non-copyable value.
- Never copy a mutex, wait group, atomic value, or type documented as
  non-copyable after first use.
- Copy slices and maps at an API boundary when retaining caller input or
  returning internal state would create surprising aliasing. Otherwise
  document mutation, borrowing, lifetime, and concurrency behavior.
- Use keyed struct literals across package boundaries. Be cautious about
  embedding types in public structs because promoted fields and methods can
  become accidental API.
- Document nil and empty behavior. Choose one representation when callers can
  observe a difference and keep it consistent.
- Use typed constants where a domain has a closed or recognizable set of
  values. Reserve a zero `Unknown` or `Unspecified` value when it makes
  default initialization safer.
- Use generics when several real types need the same operation and the result
  is clearer for callers. If code only invokes methods on a value, an
  interface is usually simpler than a type parameter.
- Start ordinary configuration with explicit parameters or a transparent
  options struct. Use functional options only when their extension and
  ergonomics justify the added indirection; document defaults, ordering,
  duplicates, and failures.

For a published v1-or-later module, preserve compatibility within the major
version. Adding a method to a public interface, changing a signature,
removing a name, or changing observable error identity can break users. Add a
new API or publish a new major module path when compatibility cannot be
preserved.

## Errors, Panics, and Cleanup

Every error must be handled, translated, returned, or deliberately ignored
with a reason supported by the called API's contract.

- Add concise operation or domain context that is useful at the next layer.
  Do not repeat paths, identifiers, or generic "failed to" text already
  supplied by the underlying error.
- Error strings normally begin lowercase and omit terminal punctuation so
  they compose cleanly.
- Never branch by matching error text. Expose a sentinel or structured error
  only when callers can take a meaningful distinct action.
- Use `errors.Is` and `errors.As` for documented error identities and types.
- Wrap with `%w` only when callers should be able to inspect the underlying
  error. That exposure becomes part of the API. Translate the error or use
  non-wrapping context when an implementation detail must remain private.
- Normally log an error or return it, not both. Lower layers add useful
  context; the layer that handles, degrades, retries, or terminates records
  the event once.
- Name exported sentinel errors `Err...`, unexported sentinels `err...`, and
  error types `...Error`.
- Do not use `panic` for ordinary failures, external input, or unavailable
  resources. A library returns errors. A `Must...` helper may panic for
  programmer-supplied invariant setup when that contract is explicit.
- Recover only at a deliberate boundary that can restore a valid contract.
  Re-panic values outside that boundary's known domain.
- Use the comma-ok form when a failed type assertion or lookup is possible.
  Remember that an interface holding a typed nil pointer is not itself nil.

Place `defer` cleanup immediately after successful acquisition so later
returns cannot bypass it. If `Close`, `Flush`, or commit-like cleanup can
affect correctness, capture its error. Scope repeated acquisitions so defers
do not accumulate across a long loop. Resource-returning APIs must state who
closes or stops the resource.

Only the application boundary should choose a process exit. Libraries and
helpers return errors so callers, tests, and deferred cleanup retain control.

## Context and Cancellation

- Pass `context.Context` explicitly as the first parameter, conventionally
  named `ctx`, to operations that block or cross request, API, or process
  boundaries.
- Never pass a nil context, create a custom context interface, or store a
  request context in a long-lived struct under ordinary circumstances.
- Propagate the caller's context through the call chain. Do not introduce
  `context.Background()` in the middle of request work to evade cancellation.
- Derive deadlines and cancellation close to the work they govern and always
  invoke the returned cancel function.
- Use context values only for request-scoped metadata that crosses an API or
  process boundary. Do not use them for optional parameters, configuration,
  loggers, or general dependency injection.
- Use private typed keys and package accessors for context values.
- Make blocking loops, sends, receives, and external calls observe
  cancellation promptly.
- Use cancellation causes when the reason materially improves diagnosis.
  Detached work must have its own bounded lifetime, shutdown owner, and error
  path.
- When compatibility prevents adding a context parameter to an existing
  method, add a clearly named context-aware companion rather than storing
  context invisibly.

## Concurrency and Ownership

Prefer synchronous APIs when callers can trivially choose to introduce
concurrency. Hidden background work makes ownership, shutdown, errors, tests,
and debugging harder.

- Every goroutine has an identifiable owner, stop condition, error path, and
  way to wait for completion. Do not fire and forget.
- Bound goroutine counts, queues, and external-resource concurrency. A
  channel capacity is a backpressure and memory decision, not a magic tuning
  number.
- Use channels for ownership transfer, coordination, and stream flow. A
  mutex is often clearer for protecting shared state. Do not force either
  mechanism into a problem it does not fit.
- The sending owner or coordinating sender closes an outbound channel after
  all sends complete. A receiver does not close a channel merely to stop an
  upstream producer.
- A stage that stops receiving early must cancel or drain upstream work so
  senders cannot leak.
- Synchronize every concurrent mutable access. Prefer conventional
  synchronization over lock-free code unless measurement and a documented
  invariant justify the complexity.
- Document whether exported values are safe for concurrent use and which
  methods may block.
- Do not rely on map iteration order or scheduler timing for correctness.
- Do not start goroutines from `init`.

The race detector only observes executed paths. Design data ownership so a
reviewer can reason about it, then exercise realistic concurrent behavior
under the detector.

## Configuration and Diagnostic Design

- Parse flags, environment variables, and files at the composition root.
  Libraries accept validated configuration and dependencies explicitly.
- Establish one documented precedence order for defaults, files,
  environment, flags, and programmatic overrides.
- Convert external strings into typed configuration, normalize and validate
  it once, and report the field, rejected value when safe, and remediation.
- Use `time.Duration`, `time.Time`, and domain types instead of unitless
  numbers and loosely interpreted strings.
- Avoid mutable global configuration and hidden initialization order.
  Publish complete validated snapshots if live reload is required.
- Give marshaled fields explicit tags when their external names are
  contracts.
- Preserve operation, safe object identity, and causal error information
  across layers so failures can be located without reproducing them first.
- Prefer structured application logging with stable keys. On supported
  baselines, `log/slog` is the standard-library default for new projects.
- Use context-aware logging when handlers extract trace or request metadata.
  Do not smuggle a logger through context.
- Libraries must not replace a process-wide default logger unexpectedly.
  Inject a logger only where a component genuinely owns logging.
- Never log secrets, credentials, raw sensitive payloads, or unnecessary
  personal information. Make redaction part of the type or handler contract.
- Record build revision, toolchain, relevant non-secret configuration modes,
  request or trace identity, and triggering input references when they are
  needed to reproduce a defect.

## Documentation

Follow Go's doc-comment syntax and preview the rendered result.

- Every package and exported name has a useful doc comment.
- Package documentation states purpose, scope, important entry points, and
  major behavioral conventions.
- Declaration comments are complete sentences and normally begin with the
  declaration name.
- Document observable blocking, concurrency safety, mutation and aliasing,
  nil and zero behavior, units and defaults, inspectable errors,
  cancellation, ownership, and cleanup obligations.
- Put runnable examples for important public APIs in `*_test.go` so they are
  compiled, rendered, and regression tested.
- Keep design rationale close to delicate code and update documentation in
  the same change as the contract.

## Review Questions

- Can a new reader follow the successful path and each ownership transfer?
- Is every exported identifier necessary, documented, and compatible?
- Are error identity, resource cleanup, and cancellation behavior explicit?
- Does each interface or generic abstraction have more than a hypothetical
  use?
- Can every goroutine stop, report failure, and be joined?
- Are shared data, mutable aliases, and global state controlled?
- Will logs and returned errors identify the failed operation without
  duplicate noise or sensitive data?

## Sources

- [Google Go Style Guide](https://google.github.io/styleguide/go/guide)
- [Google Go Style Decisions](https://google.github.io/styleguide/go/decisions)
- [Google Go Best Practices](https://google.github.io/styleguide/go/best-practices)
- [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments)
- [Package names](https://go.dev/blog/package-names)
- [Go doc comments](https://go.dev/doc/comment)
- [Working with errors](https://go.dev/blog/go1.13-errors)
- [Contexts and structs](https://go.dev/blog/context-and-structs)
- [The Go memory model](https://go.dev/ref/mem)
- [`log/slog` package documentation](https://pkg.go.dev/log/slog)
- [Uber Go Style Guide](https://github.com/uber-go/guide/blob/master/style.md)
