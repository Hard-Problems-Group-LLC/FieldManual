# Knacks

Knacks are focused, reusable knowledge units intended to be loaded for a
concrete task or investigation. They capture practical mental models,
workflows, sharp edges, and authoritative references without requiring
executable tooling.

A single-file knack lives in a topic directory as `name.knack.md`. A related
set may use an overview plus API companions:

- `topic.overview.knack.md`
- `topic.api.knack.md`
- `topic.api.C.knack.md`
- `topic.api.CPP.knack.md`
- `topic.api.Python.knack.md`

See [the authoring guide](authoring-guide.md) for sizing, naming, sourcing,
currency, and review guidance.

## Stock Areas

- [`AI/`](AI/) — integration boundaries for AI development systems,
  including OpenAI Codex and Anthropic Claude Code, and product-neutral
  agent-orchestration patterns
- [`auditing/`](auditing/) — evidence-oriented review, including software
  bills of materials
- [`authentication/`](authentication/) — identity and authentication
  boundaries
- [`debugging/`](debugging/) — language-neutral debugging methods
- [`desktop/`](desktop/) — graphical session selection, extension lifecycle,
  and desktop integration
- [`dotnet/`](dotnet/) — .NET plugins for closed hosts: shared
  `netstandard2.0` libraries, .NET Framework builds, Visual Studio from
  scripts, closed-assembly inspection, and culture-safe formatting
- [`games/`](games/) — developing, testing, and modding games on a
  workstation the player also uses, starting with Steam
- [`knowledge-management/`](knowledge-management/) — FieldManual's
  knowledge-management profile and its specifications
- [`performance/`](performance/) — measurement and profiling practices
- [`sandboxing/`](sandboxing/) — process-isolation and execution-boundary
  guidance, including isolating coding agents on Windows
- [`software-engineering/`](software-engineering/) — design, code-quality,
  development-observability, and reusable tool-integration techniques,
  plus testing (in-host smoke testing), procedural generation, and
  directed demonstrations
- [`UI/`](UI/) — terminal and browser interface engineering and automation
- [`version-control/`](version-control/) — repository inspection, repair, and
  collaboration
- [`virtualization/`](virtualization/) — virtual-machine safety and control, including Windows Sandbox
- [`windows/`](windows/) — working on a Windows workstation as or beside an
  AI agent: shells and encodings, Git, processes and files, event logs,
  desktop automation, and porting command-line tools

Start with the narrowest area that matches the task, then follow its local
index. Load related knacks together when one describes a general boundary and
another describes a specific product or API.

## Project-Owned Knacks

A consuming project may keep proprietary, third-party, or project-specific
knacks in the `knacks/` tree that it owns. "Project-owned" describes storage,
maintenance authority, and applicability. It is not permission for stock
FieldManual knacks to name a consuming project, copy local paths, or present
checkout-specific facts as reusable guidance.

If a project-owned path resembles a stock knack path, readers should inspect
both and apply the more specific project guidance deliberately. FieldManual
does not ship a collision resolver or knack validator.

## Legal and License Material

License knacks are not included in this migration and are not available in
this checkout. License obligations and compatibility can change with facts,
jurisdiction, distribution model, and authoritative interpretation. Any
future adoption requires a legal and currency review before the material is
presented as reusable guidance.

## Maintenance Model

Knacks are maintained prose, not generated output. Review them for:

- accurate scope and explicit assumptions
- absence of secrets, local identities, and machine-specific paths
- working internal links
- current authoritative references
- clear separation between general guidance and project-owned policy

FieldManual supplies no knack-specific scripts, caches, or automated
validators.
