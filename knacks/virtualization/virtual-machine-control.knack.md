# Safe Virtual-Machine Control

Load this knack before creating, starting, driving, reconfiguring, recovering,
or deleting a virtual machine. Apply it with the provider-specific reference
for the hypervisor in use.

## Mental Model

A virtual machine has at least three distinct kinds of state:

1. **Declared configuration** identifies its virtual hardware, attached
   media, network, firmware, and intended boot behavior.
2. **Control-plane and engine state** identifies the management context,
   running process or service, locks, and live device ownership.
3. **Guest state** identifies what the firmware, installer, or operating
   system has actually reached.

Evidence at one layer does not prove another. A management command returning
success means the control plane accepted it; it does not prove the guest
completed the requested transition. A listed running process does not prove a
usable boot. A screenshot proves only what one display showed at one instant.

Use a closed loop:

1. inspect identity and current state;
2. perform one narrow, authorized action;
3. wait for an observable transition;
4. collect evidence from the layer whose outcome matters; and
5. continue only when that evidence supports the next action.

Avoid long open-loop scripts built from fixed sleeps. Guest initialization,
storage checks, network acquisition, and installers vary with host load and
may stop for input.

## Identify The Exact Target

Before mutation, correlate enough identifiers to distinguish the intended
machine:

- hypervisor and host;
- management context or account;
- VM name and immutable identifier;
- configuration and writable-media paths;
- virtual network identity;
- guest hostname or another in-guest identity when available; and
- current engine, session, and power state.

Names are labels and can be reused or changed. Prefer an immutable VM
identifier for automation, while retaining the human-readable name in
diagnostics. Stop when registry, process, storage, or guest identity
disagrees.

An automation sandbox may hide the host driver, IPC endpoint, management
socket, or another account's process state. Do not diagnose a missing VM,
stopped guest, or broken hypervisor solely from a restricted view. Obtain
narrow authorization to repeat the read-only observation in the real host
context.

## Storage And Recovery Boundaries

Treat a virtual disk as a real writable block device:

- Give a normal mutable disk one compatible writer at a time. Shared-disk
  arrangements are exceptions that require an intentionally selected image
  mode, guest software designed for shared storage, and an explicit recovery
  plan.
- Reconcile disk identity and live ownership immediately before starting a
  VM. A stale registry state is not proof that no engine still holds the disk.
- Serialize competing start operations. Verify ownership again after launch.
- Keep installer images and immutable bases read-only. Give destructive tests
  and demonstrations separate overlays or differencing disks.
- Keep durable virtual disks, installer images, exports, and framebuffer
  captures outside source checkouts. Ignore any deliberately local scratch
  state.
- Check host free space before a disk may grow. A dynamically allocated disk
  can still exhaust its host filesystem later.

A snapshot or same-filesystem copy is not an off-host backup. Before risky
storage work, establish the recovery point appropriate to the value of the
guest, record where it is, and prove it can be distinguished from the live
disk. Do not attach an evidence copy with a duplicated media identity beside
the original without understanding the provider's registration rules.

If duplicate writers, unexplained engine state, or filesystem corruption is
suspected:

1. stop new starts and writes;
2. identify and quiesce every writer without guessing which state is safe;
3. preserve the affected media before repair when practical;
4. inspect provider logs and guest-visible evidence;
5. perform filesystem-specific checks offline; and
6. validate a complete boot and important services before returning the VM to
   use.

Repeated reboot attempts can compound damage and destroy evidence.

## Mutating Operations

Classify actions by effect:

- Inspection, screenshots, and non-secret log collection are normally
  read-only.
- Start, pause, resume, input injection, removable-media changes, and network
  changes alter external runtime state.
- Reset and hard power-off can lose guest data.
- Disk conversion, snapshot deletion, media compaction, restore, and clone
  operations can replace or invalidate recovery state.
- VM unregister-and-delete operations can remove configuration and storage.

Approval for inspection is not approval for shutdown, deletion, device
passthrough, network exposure, or storage mutation. Confirm the exact target
and consequence at the destructive boundary.

Prefer a guest-initiated or ACPI shutdown and then prove the engine stopped.
Use hard power-off only when the loss risk is understood and authorized.

Disable host integration that is not required by the task. Shared
clipboards, drag-and-drop, shared folders, USB passthrough, bridged networks,
and management services expand the boundary between host and guest. Choose
them from a threat model rather than convenience alone.

## Proving Outcomes

Match evidence to the claim:

| Claim | Useful evidence |
| --- | --- |
| configuration is correct | provider configuration plus media and network identity |
| one intended engine is running | provider state reconciled with host process or service state |
| guest reached a screen | fresh console or framebuffer capture |
| guest accepted input | subsequent guest-visible state, not command exit alone |
| network path works | probe originating on the relevant side of the boundary |
| installed system works | boot from its disk plus in-guest health or service evidence |
| guest stopped cleanly | guest shutdown evidence and absence of its engine |

Record request time, control-plane acceptance, observed guest transition, and
operator wait separately when timing an operation. Timing only the host
command measures command submission, not guest completion.

Keep captures and logs free of passwords, tokens, private keys, clipboard
contents, and unnecessary host or network identifiers. A guest console is an
information boundary, not merely a test fixture.

## Automated Test Runs

Treat VM automation as a closed-loop test harness, not a recording of delayed
keystrokes. Declare the hypervisor and guest inputs, immutable base or
installer digest, virtual hardware, network boundary, per-run overlay,
readiness evidence, actions, expected transitions, deadlines, artifact
policy, and teardown policy. Give every run a unique identity and artifact
location.

Prefer a semantic guest, serial-console, or service operation when one
expresses the behavior under test. When firmware, an installer, or a TUI is
the subject, wait for a fresh framebuffer or console state that identifies
the intended control before injecting complete make-and-break scancodes.
Coordinates and fixed sleeps are weak substitutes for a recognized state.

The provider-neutral harness contract is:

```text
fixture := load and validate declared inputs
run := provision fixture from verified base plus a new run-specific overlay
result := failed
owns_fixture := exact VM UUID and overlay were created for this run
owns_engine := false

try:
    reconcile control context, VM identity, engines, and writable-media owners
    start the exact VM once
    owns_engine := prove one matching engine and the reviewed writable media
    require readiness evidence before the declared startup deadline
    capture the pre-action guest state
    inject one semantic action or complete scancode sequence
    require the expected guest or service transition before its deadline
    result := passed
finally:
    if result is failed:
        retain fresh frames, console or service evidence, configuration,
        provider logs, timing, and the reviewed overlay when policy permits
    if owns_engine and ownership still reconciles:
        request graceful shutdown and prove that exact engine stopped
    else if an engine may be running:
        collect non-mutating evidence and report unresolved ownership
    if owns_fixture and the exact fixture is proven offline:
        discard, preserve, or restore its overlay according to declared policy
```

Artifact collection must occur before teardown destroys useful state. Teardown
should run after assertion or infrastructure failure only for resources the
run provably acquired and still identifies unambiguously. It must not silently
hard-power a valuable guest or delete an undeclared disk. A test that cannot
establish safe ownership should collect read-only evidence and stop as an
infrastructure failure rather than attempt recovery by shutdown, deletion, or
repeated starts.

## Review Checklist

- Is the host, management context, VM identifier, and writable medium
  unambiguous?
- Were registry and live engine state reconciled immediately before start?
- Is every writable medium intentionally owned by compatible writers?
- Is a usable recovery point available for the planned risk?
- Are host-integration and network features no broader than required?
- Does each mutation have the needed authority?
- Is guest success proved at the guest or service layer?
- Would a failure preserve enough evidence for safe recovery?
- Does an automated run use declared inputs, bounded waits, fresh evidence,
  and a deliberate overlay-retention policy?

## Further Information

- NIST SP 800-125,
  [Guide to Security for Full Virtualization Technologies](https://csrc.nist.gov/pubs/sp/800/125/final)
- [Oracle VirtualBox Control](virtualbox-control.knack/virtualbox-control.overview.knack.md)

Reviewed: 2026-07-23.
