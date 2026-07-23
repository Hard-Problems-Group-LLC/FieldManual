# Go Tooling Installation and Maintenance

## Purpose

Make a Go development environment easy to reproduce without confusing
machine administration, developer preferences, project requirements, and
download caches. This document is the canonical FieldManual guidance for
selecting, installing, invoking, updating, inventorying, and removing Go
toolchains and Go-based tools.

This guidance was reviewed on 2026-07-23 against current Go documentation,
the Go community wiki, and installation guidance from widely used Go tools.
Recheck original tool guidance before adopting one: installation and
compatibility policies change independently of the Go release cycle.

## Separate Selection From Storage

“Project-local” describes who selects a version and where that requirement is
declared. It does not require a copy of every executable or package inside the
repository.

A normal Go setup deliberately separates:

1. **declaration** — the project records its required Go version, modules, and
   build-affecting tools;
2. **storage** — the Go command keeps authenticated, normally read-only
   module content and disposable build outputs in user-owned caches;
3. **invocation** — a project tool is resolved through project module state,
   while a personal tool may be found on the user's `PATH`; and
4. **machine prerequisites** — an administrator or environment owner
   supplies the Go distribution and any native compiler, library, certificate,
   or operating-system dependency.

Do not copy the module cache into a repository to make dependencies
“project-local.” Do not treat a command found somewhere on `PATH` as a
project declaration.

## Default Ownership and Scope

| Asset | Normal scope and owner | Project responsibility |
| --- | --- | --- |
| Go distribution | System-wide on a managed host or image; user-wide under a version manager on a personal workstation | Declare the minimum and normal toolchain versions and whether automatic toolchain downloads are allowed. |
| Tools shipped with Go | The selected Go distribution | Invoke through that toolchain; do not install separate copies of `gofmt`, `go vet`, or other bundled tools. |
| Editor and interactive debugging tools | User-wide, owned by the developer; centrally managed only on a controlled workstation image | State compatibility expectations, not one universal editor setup. |
| Formatters, generators, linters, analyzers, schema tools, and release tools that affect accepted source or artifacts | Project-declared and versioned | Provide the canonical invocation and use the same selection in local work and CI. |
| Imported Go packages and their module graphs | Project-declared in `go.mod` and `go.sum`; content stored in a user or job cache | Review and maintain the selected graph. Never install library packages system-wide for module resolution. |
| Host fetch and build prerequisites | System-wide or image-local; owned by the administrator | Declare required VCS clients, CA trust, native build tools, and platform behavior without embedding credentials. |
| Native cgo compilers, headers, and libraries | System-wide, image-local, or SDK-local; owned by the administrator or environment definition | Document versions and test the supported environment; `go.mod` cannot describe these inputs. |
| A developer's standalone Go commands | User-wide under `GOBIN` or the default Go binary directory | Do not rely on them for project gates. |
| Product and operational binaries | Installed by the product's package, deployment, image, or administrator | Build from project-declared inputs and retain provenance. |

Use the narrowest ownership scope that matches the effect:

- If a tool can change generated source, API descriptions, migrations,
  formatting, test acceptance, release metadata, or artifacts, the project
  owns its version.
- If a tool only improves one person's editing or investigation, the user
  normally owns it.
- If an input requires elevated privileges, affects every user, or is part of
  a managed host or base image, the system administrator owns it.

An organization may provide all three scopes through one workstation image or
development container. The declarations and ownership duties still remain
distinct.

## Installing and Selecting the Go Distribution

The project must express its minimum Go version with the `go` directive and
its normal main-module toolchain policy as described in
[Modules, Builds, and Security](modules-builds-and-security.md). A version
manager file, development-container definition, or image tag may supplement
that declaration for environment provisioning, but must agree with it.

Choose one installation authority per environment:

- **Managed hosts and base images:** administrators should use an approved OS
  package, official Go archive, or managed image layer. Pin the intended
  release line, define a patching cadence, and make the installation
  root-owned or image-immutable. The OS package manager is a good choice when
  its supported patch level and security-backport policy meet the project's
  needs; distribution packages are not produced or supported by the Go
  project.
- **Personal workstations:** a user-scoped version manager is appropriate when
  developers regularly switch among projects with different Go versions. Pin
  its project configuration in revision control when the team adopts it, but
  do not require a particular version manager unless the project depends on
  its behavior. Document which selector has precedence when combining a
  version manager with Go's own automatic toolchain selection; two unnoticed
  installation authorities create confusing `PATH` and patch behavior.
- **Hermetic or cross-platform development:** a pinned development container,
  build image, or SDK can supply the toolchain and native dependencies.
  Maintain it like any other build input and avoid making it the only
  documented path unless container use is a project requirement.

Do not unpack a new Go archive over an existing Go tree. Remove or replace the
old installation through its owning package or image mechanism. Never modify
packages beneath `GOROOT`, and do not use `sudo go install` to put third-party
commands beside the Go distribution.

After installation, verify both the version and the executable actually
selected by the shell. A clean onboarding record should be able to explain:

- which `go` executable ran;
- the output of `go version`;
- the active `GOTOOLCHAIN` policy; and
- whether the current project caused a toolchain switch or download.

### Automatic Toolchain Selection

Since Go 1.21, the `go` command can select a newer compatible toolchain based
on the applicable `go` and `toolchain` lines in an active `go.work` or
`go.mod`. With an automatic-download policy, a command may obtain a toolchain
as a special module through the configured module proxy and checksum
infrastructure.

Automatic selection is compatibility handling, not automatic patch
management. If the bundled toolchain already satisfies the applicable
requirements and preferences, an `auto` policy does not promise to find a
newer security patch. The owner must still update the base installation or
project preference deliberately.

This is useful on developer workstations when the organization permits
downloads and wants project declarations to drive selection. It is not
automatically appropriate everywhere:

- release and minimum-version jobs must record the toolchain actually used;
- restricted networks must decide whether the proxy may serve toolchains;
- managed fleets may require only preinstalled approved toolchains; and
- offline builds must preload every selected toolchain or disable downloads.

Set `GOTOOLCHAIN` deliberately in managed environments. Do not change a
developer's persistent `go env` configuration from an onboarding script.
Process, job, shell-profile, or managed environment settings are easier to
attribute and reverse. Toolchain downloads require checksum-database
verification and fail when it is disabled with `GOSUMDB=off`; private-module
exemptions do not exempt the public Go toolchain modules.

## Installing Tools At the Right Scope

### Project Tools On Go 1.24 Or Later

Prefer the standard `tool` directive for tools owned by a module. Add an exact
reviewed version with a command of this form:

```text
go get -tool example.org/tool/cmd/tool@v1.2.3
```

Invoke it through module state:

```text
go tool example.org/tool/cmd/tool
```

The final path component may be used when it is unambiguous, but the full
package path is clearer in automation. Commit and review the resulting
`go.mod` and `go.sum` changes. Keep the project's documented local command
equivalent to CI rather than installing a second copy on `PATH`.

Before adding a tool this way, read its maintainer's installation guidance.
Some projects distribute purpose-built release binaries or discourage
building their command with an arbitrary Go version. A project may pin and
verify that release artifact through its own package or download mechanism;
the requirement remains project-owned even though it is not a `tool`
directive.

### Project Tools On Older Go Baselines

Before Go 1.24, use one documented versioned mechanism consistently. Common
choices are:

- the established build-constrained `tools.go` blank-import pattern together
  with `go run` and a full package path;
- a small separate tools module; or
- a project-controlled artifact installer that verifies version and
  integrity.

Do not raise a library's minimum supported Go version solely to replace a
working tool-pinning mechanism. Do not use an unversioned `@latest`
installation in CI.

### User-Wide Tools

Editor language servers, debuggers, and exploratory commands may be installed
under the user's `GOBIN` or, when unset, the appropriate `GOPATH/bin`
directory. The default for an otherwise unconfigured user is commonly
`$HOME/go/bin`.

For a standalone command, use an explicit version:

```text
go install example.org/tool/cmd/tool@v1.2.3
```

With a version suffix, `go install` resolves the command outside the current
main module. That isolation is useful for personal tools, but it is exactly
why the resulting executable must not silently define a project's CI or
generation behavior. Use `go install`, not `go get`, for this purpose.

Installing another version under the same command name normally replaces the
previous executable. Keep only intentional tools on `PATH`, know which
directory precedes which, resolve the executable's actual file path, and pass
that path to `go version -m` when supported to inspect the toolchain and
module versions embedded in a Go binary.

`gopls` is normally user- or editor-managed because it serves an interactive
workspace. Delve is normally user-managed for the same reason. Their versions
must still support the project's Go versions, and centrally managed
workstations may pin both to a tested compatibility set.

### System-Wide Tools

Install a third-party Go command system-wide only when an administrator is
intentionally providing a versioned command to multiple users, such as in a
managed workstation or immutable CI image. The administrator then owns:

- package source and integrity verification;
- supported host and Go compatibility;
- patching and rollback;
- executable permissions and `PATH` ordering;
- inventory and vulnerability response; and
- removal of obsolete versions.

Even then, project gates should check or select the declared version rather
than accept any ambient command with the same name. OS distribution packages
are appropriate when their support and patch policy meets the project need;
they may lag upstream feature releases, which is a compatibility fact to
manage rather than a reason to bypass the package owner.

### Physically Project-Local Executables

Go 1.24 project tools normally need no durable repository-local executable:
`go tool` resolves the declaration and places build output in the Go build
cache. A private ignored binary directory such as `.local/bin/` is reasonable
when a project must provision:

- a tool distributed only as a release executable;
- a non-Go command used by generation or release work;
- a legacy tool on a pre-1.24 baseline; or
- a tool whose publisher requires isolation from the project's Go graph.

The project must pin the release; verify its checksum, signature, or supplied
provenance as appropriate; key stored artifacts by tool, version, OS, and
architecture; install without privilege; and invoke the explicit local path
or a version-checking wrapper. Do not add the directory to a process-wide
`PATH`. Keep downloaded executables out of revision control, provision them
afresh in CI, and do not silently overwrite an unmanaged file already at the
destination.

### Common Tools

- `gofmt`, `go test`, `go vet`, `go tool pprof`, and the compiler and linker
  come from the selected Go distribution. Never update them separately.
- `gopls` and Delve normally belong to the user or editor. Keep them
  compatible with supported project versions, but make explicit commands—not
  incidental editor diagnostics—the project acceptance contract.
- `goimports` may be user-owned as an editing convenience. If its exact
  rewriting is enforced, declare its version as a project tool and use that
  version in CI.
- A static analyzer used as a gate is project-owned. Upgrade it intentionally
  because a new release can add findings that change acceptance.
- `govulncheck` is project-owned when it is a required check. Pin the command
  interface, while recognizing that its advisory database changes over time;
  retain the scanner version, database or scan time, Go version, tags, and
  mode with important results.
- Generators are project-owned. Prefer a project-declared full tool path in
  `//go:generate`, remember that `go generate` is never run automatically by
  build or test, and verify generated output for unexplained changes.

Pin non-Go commands used by a Go tool, such as `protoc`, a schema compiler, or
a native linker, through their own project or system mechanism. A Go `tool`
directive cannot version them.

## Packages, Tools, and Their Dependency Graphs

Go does not have a separate npm-style development-dependency graph. A Go 1.24
`tool` directive identifies a command package, while ordinary `require`
directives select the modules that provide the tool and everything it imports.
Those requirements participate in the main module's minimal version selection
alongside application and test dependencies.

Consequences:

- adding or upgrading a tool can raise a module version used by production
  code;
- `replace` and `exclude` directives in the main module also affect tools;
- `go mod tidy` loads every declared tool and its recursive imports; and
- `go.sum` changes may represent tool dependencies even when application
  imports did not change.

Tool-only requirements declared by a dependency module do not usually
propagate into the main module because module-graph pruning omits them. Tools
declared by the main module—or exposed through the active workspace—are the
ones the project must treat as its tool graph. Do not promise absolute
separation without inspecting the selected graph.

Review a tool update like any other dependency update:

1. inspect the tool's release and installation guidance;
2. use an exact version;
3. review the complete `go.mod` and `go.sum` diff;
4. inspect `go list -m all`, `go mod graph`, or `go mod why -m` where the
   selection is surprising;
5. run tidy, tests, analysis, generation checks, and artifact comparisons
   affected by the tool; and
6. inventory and assess the tool's own transitive and native dependencies.

Remove a no-longer-needed Go 1.24 tool with:

```text
go get -tool example.org/tool/cmd/tool@none
```

Then run tidy and review everything it removes or downgrades. Removal
deserves the same graph review as addition.

### When To Isolate A Tool Graph

Keep ordinary, compatible project tools in the main module: one graph is
simple, visible, and supported directly by the Go command. Use a separate
module when a large or conflict-prone tool graph would otherwise distort the
application graph, or when the tool's maintainer explicitly recommends
isolation.

A separate module creates real maintenance work. It needs its own `go.mod`,
`go.sum`, tidy check, update process, vulnerability review, and documented
invocation. Merely adding that module to `go.work` is not strict dependency
isolation while workspace mode is active: workspace builds use a unified
selected module graph and expose the union of workspace tool directives.
Run isolated verification from the intended module with workspace influence
disabled or deliberately controlled.

An alternate `-modfile` can also isolate tool requirements, but it is easier
for people and editors to overlook. Prefer a clearly named tools directory
with an ordinary module unless the project has a documented reason to use
alternate module files.

### Go Module And Build Caches

Downloaded module source belongs in `GOMODCACHE`; compiled build outputs
belong in `GOCACHE`. These are performance and availability caches, not
project declarations, library installation directories, or evidence that a
dependency was approved.

- Leave module-cache contents under Go command ownership. Do not edit,
  vendor by copying, change permissions to make ad hoc patches, or commit
  cached content.
- Prefer a separate cache per user or CI trust boundary. Go supports
  concurrent commands using its caches, but sharing a writable cache between
  mutually untrusted users creates an avoidable permissions and
  confidentiality boundary. This is a FieldManual security default, not a
  claim that ordinary Go cache concurrency is unsafe.
- A persistent CI cache may improve speed, but its namespace and restoration
  policy must respect trust boundaries. Go's build cache already keys most
  build inputs and its module cache addresses module versions and content;
  choose outer cache partitions for the runner's compatibility and
  performance behavior rather than treating their names as integrity.
  Explicitly invalidate native changes Go cannot detect. A clean job must
  still be able to reconstruct and authenticate inputs.
- Use `go clean -cache` and `go clean -modcache` for intentional cleanup.
  Avoid scripts that recursively delete a guessed cache path.

Module caches have no automatic size limit. Administrators should monitor
quotas and use an announced cleanup policy rather than surprising developers
with unexplained deletion during a build.

### Native Dependency Chains

cgo tools and packages can add a second graph that Go module files do not
capture: compiler, linker, SDK, headers, shared libraries, runtime loader, and
OS packages. The project must name these prerequisites and supported versions;
the administrator or pinned environment must provide them.

For each release, record enough native package and image information to
reconstruct and assess that graph. A clean pure-Go build should declare and
test `CGO_ENABLED=0`; it must not be assumed merely because Go often produces
standalone binaries. The Go build cache does not detect changes to system C
libraries. After a relevant native compiler or library update, start a clean
release build or explicitly invalidate the affected build cache.

## Controlled CI And Release Environments

CI should make hidden user and workspace state irrelevant:

- use an exact patched Go toolchain and verify `go version`;
- use `GOTOOLCHAIN=local`, or an equally explicit pre-provisioned policy,
  when the job must not select or download another compiler;
- use `GOENV=off` so persistent user `go env` settings cannot alter the job;
- use `GOWORK=off` unless the repository intentionally tests a declared
  workspace;
- set proxy, checksum, private-module, and VCS policy explicitly before any
  download;
- fetch dependencies in a controlled step, then use read-only module mode
  when later commands must not edit `go.mod` or `go.sum`; and
- separate caches populated by untrusted changes from privileged release
  caches.

For an offline build, either populate and authenticate an isolated cache
before disabling network resolution, or maintain a reviewed vendor tree and
test vendor mode. Vendoring does not cause Go to authenticate hand-edited
vendored files; regenerate it and require a clean diff.

External cache partitioning should account for the runner, Go toolchain,
target, and project state to the degree needed for useful, compatible reuse.
In particular, include native compiler and library identity or clear the
cache when they change because Go does not detect every native-library
change. Release evidence should come from fresh or verified inputs rather
than relying on cache presence.

## Clean Developer Onboarding

The fastest reliable onboarding path minimizes privileged and persistent
mutation. A project's contributor documentation should lead a new developer
through these outcomes:

1. Identify the module roots, supported host platforms, required Go version,
   toolchain-download policy, cgo/native prerequisites, private-module
   policy, and canonical local verification commands.
2. Install Go using the workstation's one approved system or user mechanism.
   Verify the selected executable and `go version`.
3. Configure private module routing and credentials before the first
   dependency request. Keep secrets in approved credential storage.
4. Clone the project and check `go env GOWORK` so an unrelated parent or user
   workspace does not silently change module selection.
5. Let the Go command download project-declared modules and tools into
   user-owned caches. Do not require a privileged global tool install.
6. Invoke project tools through `go tool`, the declared isolated tools
   module, or the project's version-checking wrapper.
7. Run a small build or test smoke check, then the documented pre-submit
   verification.

An optional onboarding command should be idempotent, non-root, and explicit
about every persistent change. It should diagnose a missing prerequisite and
link to owner-approved installation instructions instead of silently:

- editing shell startup files;
- running `go env -w`;
- installing system packages;
- changing proxy, checksum, or private-module policy;
- adding unpinned commands to `PATH`; or
- downloading a different toolchain than project and site policy allow.

Developers should be able to run the same build, test, generation, and
analysis entry points as CI. Editor integration may call those entry points,
but it is not their canonical definition.

`go env -changed` is useful when the installed Go version supports it: it
surfaces effective settings that differ from an empty/default environment,
including process, persistent user, and installation or toolchain defaults.
Review the origin before changing anything.

## Developer Maintenance Duties

- Keep project tools declared, pinned, and invoked through the project
  mechanism.
- Update personal tools deliberately; do not assume an editor's automatic
  update has also updated CI.
- Review dependency and generated-output diffs before committing.
- Periodically inspect which executables the shell resolves and remove stale
  duplicates.
- Report `go version`, selected tool versions, `GOWORK`, target settings, and
  the failing project command when asking for help. Redact credentials and
  sensitive private paths.
- Do not repair cache or permissions problems with `sudo` against a
  user-owned Go tree; correct the ownership or installation boundary.

## System Administrator Maintenance Duties

- Define approved toolchain sources, supported release lines, patch timing,
  end-of-life removal, and rollback.
- Keep system installations immutable to ordinary users and never layer a new
  official archive over an old Go tree.
- Decide whether automatic toolchain download, direct VCS access, public
  proxies, and public checksum services are permitted. Configure
  `GOPROXY`, `GOSUMDB`, `GOPRIVATE`, related no-proxy/no-sum settings, and
  `GOVCS` as one coherent supply-chain policy.
- Prefer a managed module proxy when centralized availability, retention,
  audit, or allow/deny policy is required. A comma-separated proxy fallback
  respects a policy denial and falls through on not-found responses; a
  pipe-separated fallback continues after any error and can bypass that
  denial. Omit direct VCS fallback in locked-down jobs.
- Give developers private, least-privilege cache and binary locations with
  predictable quotas. Make CI caches ephemeral or segmented by trust
  boundary.
- Supply and inventory native cgo dependencies outside the Go module graph.
- Preserve enough egress, proxy, package, and image evidence to investigate
  a compromised or unexpectedly selected input.
- Test the supported editor-server/debugger set against supported Go lines
  when those tools are centrally managed.
- Communicate maintenance windows and cleanup. Remove obsolete toolchains,
  binaries, image layers, and cached private modules through their owning
  mechanism.

A managed environment should expose its effective policy without exposing
credentials. Record the Go distribution version and origin, image or package
identity, native packages, and important selection settings. For Go-built
commands and product binaries, `go version -m` provides useful embedded
module evidence; supplement it with OS-package and artifact provenance.

Updating Go on a host does not patch programs already built with an affected
toolchain or standard library, and updating a module source does not patch
previous binaries. Rebuild, verify, and redeploy every affected application
and installed Go command. Patch dynamically loaded native libraries through
their system owner and rebuild artifacts that contain static native code.

## Review Questions

- Does every tool have a clear system, user, or project owner?
- Can a clean checkout select project tools without trusting an unrelated
  executable on `PATH`?
- Can a new developer start without root access or unexplained persistent
  configuration changes?
- Can administrators patch or retire the Go distribution without replacing
  developer-owned tools?
- Did a tool addition or upgrade change the application module graph?
- Are separate tool modules genuinely verified separately, or accidentally
  reunited by workspace mode?
- Are proxy, checksum, private-module, and automatic-toolchain policies
  compatible before the first download?
- Are native libraries and release packaging inputs inventoried outside
  `go.mod`?
- Can the team identify and remove every stale installation and cache through
  its owning mechanism?

## Sources

Go project documentation:

- [Download and install Go](https://go.dev/doc/install)
- [Managing Go installations](https://go.dev/doc/manage-install)
- [Go toolchains](https://go.dev/doc/toolchain)
- [Managing dependencies, including tool dependencies](https://go.dev/doc/modules/managing-dependencies)
- [Go modules reference](https://go.dev/ref/mod)
- [`go` command documentation](https://go.dev/cmd/go/)
- [Deprecation of `go get` for installing executables](https://go.dev/doc/go-get-install-deprecation)
- [Go release and support history](https://go.dev/doc/devel/release)
- [Go supply-chain security model](https://go.dev/blog/supply-chain)
- [`gopls` documentation](https://go.dev/gopls/)
- [Go vulnerability management](https://go.dev/doc/security/vuln/)
- [Go Wiki: Modules](https://go.dev/wiki/Modules)

Original tool and environment guidance used to test the general rules:

- [Delve installation](https://github.com/go-delve/delve/tree/master/Documentation/installation)
- [Staticcheck installation](https://staticcheck.dev/docs/getting-started/)
- [golangci-lint installation](https://golangci-lint.run/docs/welcome/install/)
- [Development Containers specification](https://containers.dev/)
- [mise Go toolchain management](https://mise.jdx.dev/lang/go.html)

These sources illustrate available approaches; FieldManual does not require
those optional products.
