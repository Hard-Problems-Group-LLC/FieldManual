# Ubersight Development Observability

Load this knack when adopting, operating, or publishing status to Ubersight
during extended development work.

## Mental Model

Ubersight is a compact terminal sidecar. It projects enough current state for
an operator to see what a long-running development session is doing, whether
the published status is stale, whether local Git work appears protected, and
whether monitored processes or background jobs are active.

It is not the source of truth. Keep durable scope, decisions, work items,
recovery notes, and completion evidence in the consuming project's tracked
records. Regenerate Ubersight state from those records after a new checkout,
workstation change, cache loss, or context recovery. Never reconstruct
durable history from a stale dashboard file alone.

Current Ubersight has three distinct state planes:

1. tracked project records, owned by the consuming project;
2. one checkout-local agent status and cache area under `.local/`; and
3. file-per-job runtime telemetry under a per-user Ubersight context.

Do not combine their authority or retention rules.

## Establish The Project Context

Use the installed `ubersight` console command for ordinary operation. The
scripts under the Ubersight source checkout are compatibility and development
launchers, not the integration boundary.

At the reviewed revision, run `./install.sh` from the Ubersight checkout for a
user-local standard installation. Use `./install.sh --mode dev` only while
maintaining Ubersight itself. A system installation belongs under system
administrator ownership, because it changes the tool for every user. Record
the version or revision tested by producer projects rather than copying
Ubersight's source launchers into each project.

Run Ubersight from the intended project root. Its default status, cache,
location-memory, and repository paths are relative to the process working
directory. `--repo-root` changes Git inspection, but it does not re-anchor the
other relative paths.

Choose and reuse an explicit, portable context name:

```bash
ubersight \
  --project-name example-service-main \
  --repo-root .
```

`--project-name` selects the banner and background-job runtime context. It
does not relocate `.local/ubersight/status.json`. Without an explicit value,
Ubersight uses `UBERSIGHT_PROJECT_NAME` when set and otherwise the working
directory's final component. Two checkouts with the same directory name can
therefore collide in the background-job context; give them distinct explicit
names.

For a one-shot text rendering, use `--once`. It performs the same status and
environment refreshes as an interactive draw; it is not a side-effect-free
file renderer.

Press `Q` to quit a directly launched interactive dashboard. When a wrapper
supervises the side pane, upstream uses `ubersight-stop` to trigger a restart,
but that helper matches Ubersight processes for the entire current user, not
one project context. Use `ubersight-stop --dry-run` before stopping processes
when several project sessions may be active.

## Understand Current Side Effects

An ordinary display reads the local status file, Git state, optional process
metadata, background-job files, and operator-environment state. By default it
may also:

- run `git fetch origin`;
- inspect hostname, user, WiFi, routes, and local network identifiers;
- invoke the local Tailscale CLI; and
- contact BeaconDB, IP-geolocation services, OpenStreetMap Nominatim, or
  OpenStreetMap Overpass.

An invocation that disables the current intentional external service calls
is:

```bash
ubersight \
  --project-name example-service-main \
  --repo-root . \
  --no-origin-fetch \
  --no-geolocate \
  --no-tailscale
```

This still performs local host, user, WiFi, worktree, and network inspection.
The reviewed version has no switch that disables all operator-location
collection. If local observation itself violates project policy, do not run
that version merely because public geolocation is disabled.

## Publish Agent Status

The default agent-owned file is:

```text
$(PROJECTROOT)/.local/ubersight/status.json
```

The entire `.local/` tree must remain ignored. Prefer the supplied writer,
which publishes by same-directory temporary file and atomic replacement:

```bash
ubersight --write-status \
  --phase-row "prepare:done:Prepare test environment" \
  --phase-row "verify:active:Verify release candidate" \
  --phase-row "publish:pending:Publish approved result" \
  --slice "smoke:done:Run smoke checks" \
  --slice "system:active:Run system verification" \
  --slice "review:pending:Review evidence" \
  --notes "System verification is running."
```

Rows use `ID:STATE:TITLE`. IDs are compact project-owned strings; Ubersight
does not require numeric IDs, globally increasing slices, or a reset to
`Slice 1` for each phase. Supported row states are:

```text
pending  active  done  failed  blocked  skipped
```

`deferred`, `running`, and `complete` are not row states. Keep deferred work
in durable planning or deliberately map it to a supported display state.
Completion is the separate `--complete` flag.

With a phase stack, the display shows the two rows before the active phase,
the active phase, and up to five later rows. Phase and slice titles each
occupy one physical row and are clipped rather than wrapped; notes wrap.
Publish a slice list for the current phase or work segment, with concise
titles that remain useful in a narrow pane.

At the reviewed revision, a new CLI write requires:

- at least one phase row and exactly one active phase;
- at least one slice;
- no more than one active slice; and
- one active slice unless `--complete` is present.

The optional `--phase-id` and `--phase-title` must match the active phase;
omit them and let the writer derive both. `--blocked` alone does not remove
the active-slice requirement. When representing a blocked operation, keep the
owning current slice active, mark a related row blocked only when that row is
genuinely blocked, and make the blocker explicit in high-level notes. Verify
the rendered result because the current phase-stack display does not render
the global `[BLOCKED]` or `[COMPLETE]` label.

Update status on meaningful observable transitions:

- extended work starts or resumes;
- the active work segment or substep changes;
- a long validation, publication, or external wait begins;
- progress becomes blocked or fails;
- work resumes after interruption; and
- final closeout begins and completes.

Do not publish every command. Short, truthful, stale-aware status is more
useful than a transcript or invented progress.

## Main Status Protocol

The writer emits `ubersight.status.v1` JSON with:

- timezone-aware `updated_at`;
- one `phase` summary plus ordered `phases`;
- ordered `slices`;
- high-level `notes`; and
- global `blocked` and `complete` booleans.

Ubersight normally marks the display stale when `updated_at` is more than 900
seconds old. Producers that cannot call the CLI must write the exact protocol
expected by their deployed Ubersight revision, publish atomically in the same
directory, and test malformed, interrupted, and concurrent updates. Do not
rely on the current reader's permissive coercions as a producer contract.

The versioned contracts are not yet shipped as independently consumable
schemas and the main reader does not consistently reject unsupported schemas
or invalid state. Track that limitation through
[FieldManual-ECR-2026-003 in the Ubersight request
index](../../../ECRs/ubersight/README.md).

## Publish Background-Job Telemetry

Long-lived tools can publish independent active-job files using:

```text
ubersight.background-job-status.v1
```

The default directory is:

```text
$XDG_RUNTIME_DIR/ubersight/<context>/background-jobs/
```

When `XDG_RUNTIME_DIR` is unset, Ubersight selects
`/run/user/$UID/ubersight/...` if that user directory exists and otherwise
selects `/tmp/ubersight-$UID/...`. It does not retry a different root after
selecting one. The directory, not a JSON `context` field, is the effective
context boundary in the reviewed implementation.

Use one uniquely named `*.json` file per job and atomically replace it on
updates. The reader's minimum is the exact schema and a positive live `pid`.
A safe producer baseline must also include `updated_at`, `boot_id`,
`process_start_ticks`, and a unique `job_id`; omitting process identity can
associate stale telemetry with a reused PID. For useful output, include:

- `app`, `category`, `subject`, `verb`, and `source`;
- one of `starting`, `running`, `paused`, `error`, `interrupted`, or
  `complete`;
- bounded `ticker` and `message` text; and
- applicable item, byte, rate, and ETA fields.

Ubersight ignores malformed and wrong-schema files. It may remove a file
after observing `complete` or a dead process. It can also remove a
different-boot or PID-reuse file when the producer supplied `boot_id` or
`process_start_ticks` and comparable current identity is available. The
protocol represents active telemetry, not job history. Writers must own their
file lifecycle and must not use the runtime directory as durable evidence.

Use a private, user-owned runtime directory. In the `/tmp` fallback case,
verify ownership, permissions, and symlink confinement before creating or
replacing files. Never clean an entire shared context merely because one job
finished.

## Privacy And Recovery Boundary

Keep prompts, transcripts, credentials, session identifiers, client-private
names, raw commands, environment dumps, private endpoints, location details,
WiFi and Tailnet names, and sensitive log fragments out of agent and
background-job status.

Ubersight's own local operator-location files are more sensitive than the
agent status. At the reviewed revision they may contain literal SSIDs,
hostname and username, subnets, coordinates, raw BSSID and gateway MAC
observations, safe location aliases, and Tailnet cache data. An ignored path
is not encryption or retention control. Keep `.local/` private, restrict
access, do not stage or summarize those files, and remove obsolete local
observations under an explicit retention policy.

The live pane can itself disclose hostname, username, WiFi, Tailnet, location,
repository, and work-status facts. `--once` prints those facts to standard
output. Review and redact the display before screen sharing, taking
screenshots, or capturing terminal logs; ignored storage does not prevent
observer or log disclosure.

During recovery, read the project's tracked active-work and decision records
first. Treat `.local/ubersight/status.json` as a hint, verify its age and
project identity, then republish current truth. Before committing, confirm
the entire `.local/` tree and runtime telemetry are absent from the change
set.

## Review Checklist

- Is Ubersight a projection from declared durable records?
- Is the process working directory the intended project root?
- Is the project/runtime context explicit and collision-resistant?
- Are visible IDs and state names valid for the deployed version?
- Are status writes atomic, bounded, and free of sensitive content?
- Are external network probes appropriate or explicitly disabled?
- Are `.local/` and runtime files ignored, private, and outside the commit?
- Can a fresh checkout regenerate useful status without copying local facts?

## Further Information

- [Ubersight repository](https://github.com/Hard-Problems-Group-LLC/ubersight)
- [Ubersight command and protocol documentation at the reviewed
  revision](https://github.com/Hard-Problems-Group-LLC/ubersight/blob/1ec5d3ccb662f89f7b8c8b8cfd47349894094545/docs/scripts/ubersight.py.md)
- [Ubersight operator-location security documentation at the reviewed
  revision](https://github.com/Hard-Problems-Group-LLC/ubersight/blob/1ec5d3ccb662f89f7b8c8b8cfd47349894094545/docs/security/operator-location-memory.md)

Reviewed: 2026-07-24 against Ubersight `0.1.0` at
`1ec5d3ccb662f89f7b8c8b8cfd47349894094545`.
