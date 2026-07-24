# VirtualBox Control Overview

Load this overview before using Oracle VirtualBox to create, start, drive,
observe, or troubleshoot a VM. Read the
[provider-neutral safety knack](../virtual-machine-control.knack.md) first and
use the [API companion](virtualbox-control.api.knack.md) for command patterns.

## Scope And Version

The command forms and vendor links in this fileset were reviewed against
Oracle VirtualBox 7.2 documentation. `VBoxManage` evolves, and some indexed
options changed form across releases. Inspect the installed command's
version and help before mutation:

```sh
VBoxManage --version
VBoxManage help createvm
VBoxManage help modifyvm
VBoxManage help storageattach
VBoxManage help controlvm
```

Treat the installed help as authoritative when it differs from an example.

## Three Layers Of State

VirtualBox exposes the general VM layers through specific components:

1. Registered VM configuration describes virtual hardware, media, networks,
   boot order, and the default frontend.
2. `VBoxSVC`, a frontend, and a running VM engine own live control and device
   state.
3. Guest firmware, an installer, or the guest operating system determines
   what is actually happening inside the VM.

`VBoxManage list runningvms` proves what one VirtualBox control context
reports. It does not prove the guest booted or that no engine exists outside
that context. A successful `controlvm` command proves command acceptance, not
the guest's intended response.

Use the closed loop:

1. inspect the registry, VM identity, engines, and attached media;
2. perform one narrow action;
3. wait for the guest-visible transition;
4. capture the framebuffer or other guest-level evidence; and
5. continue only when the evidence supports the next action.

## Per-User Control Context

VirtualBox configuration and services are per user. On Linux and Oracle
Solaris, Oracle documents `VBOX_USER_HOME` and `XDG_CONFIG_HOME` as ways to
select an alternate configuration directory; otherwise the user's home
contributes to the default. `VBoxSVC` maintains the configuration and
coordinates clients through local IPC.

An automation process with an isolated home can therefore see an empty or
different registry from the operator. Before treating that result as a lost
VM, inspect:

```sh
VBoxManage list systemproperties
VBoxManage list vms
VBoxManage list runningvms
```

The default machine folder helps identify which context is active. Use an
alternate configuration only when it is deliberate and keep its environment
consistent for every client that participates in the session. Do not edit
VirtualBox XML configuration directly; Oracle reserves the right to change
its format and supplies `VBoxManage` and APIs for supported changes.

During diagnosis, record whether each selector is set as well as the
configuration and registry that the client actually observes. Do not infer
that two clients share a control context merely because their resolved
directory strings appear equal; prove agreement through the registered and
running VM identities.

## Pre-Start Reconciliation

Immediately before a start:

- identify the intended user and configuration context;
- inspect registered and reported-running VM UUIDs;
- use host-appropriate process or service inspection to find every supported
  frontend or engine process, including `VirtualBoxVM`, `VBoxHeadless`, and
  any other frontend the project permits, then correlate each process to its
  VM UUID;
- reject an unexplained registry/process disagreement;
- reject more than one engine for the same VM UUID;
- identify every writable medium attached to running and target VMs;
- reject accidental overlapping writable ownership; and
- confirm that the target is not already active.

Multiple configurations can be intentional, and multiple users can have
separate `VBoxSVC` instances. Their mere existence is not a universal error.
Ambiguous ownership, one UUID in multiple engines, or ordinary mutable media
held by incompatible writers is the safety failure.

Serialize competing start attempts. After launch, confirm that the expected
engine exists once, the same control context reports it running, and its
writable media match the reviewed configuration. A consuming project may
implement these outcomes with its own guarded launcher; FieldManual does not
provide one.

If an automation sandbox cannot observe VirtualBox IPC, the host driver, or
process state, obtain narrowly scoped permission to repeat the read-only
preflight in the host context. Never weaken reconciliation merely to make a
start command succeed.

## Storage Pattern

For repeatable installers and destructive tests:

1. validate and preserve an installer or base image as read-only;
2. create a separate disk or differencing overlay for each run;
3. never attach the base as an ordinary mutable disk;
4. verify disk and optical paths before first start; and
5. discard, preserve, or promote the run-specific disk deliberately.

VirtualBox snapshots and differencing images are useful lifecycle tools, but
they are not off-host backups. Check host capacity and keep a recovery copy
appropriate to the guest's value.

Normal VDI/VMDK attachment must not become an accidental shared-disk
arrangement. VirtualBox offers special medium modes such as `immutable`,
`shareable`, and `multiattach`; select one only after reading its storage
semantics and confirming that the guest workload supports the resulting
ownership model.

## Guest Evidence And Input

Use direct framebuffer captures when firmware, an installer, or a graphical
guest is the system under test. Viewer scaling is presentation state and can
reset across restarts. Establish 100% mapping or another known geometry
before image matching or coordinate input, then compare screenshot dimensions
with the guest display mode.

Keyboard scancodes do not depend on viewer scale, but mouse and image
coordinates do. Scancode input must include both make and break codes.
Prefer literal string input only in ordinary text fields with a known layout.

Plan the installer-media handoff before installation begins. DVD-first boot
is useful initially but can restart the installer after completion. Observe
the safe transition, eject or detach the ISO, make the disk first in boot
order, and prove the installed disk reaches a login or service state.

## VirtualBox As A Test Fixture

For automated tests, make the VM definition and evidence gates part of the
fixture contract. Verify the base or installer digest, create a per-run
differencing medium, register the VM in one declared VirtualBox context, and
perform the full pre-start reconciliation before `startvm`. Wait on fresh
framebuffer, guest, serial, or service evidence; inject input only after the
semantic target is present; then assert a new observable state.

On failure, retain the machine-readable configuration, timestamped
framebuffers, relevant `VBox.log` files, guest or service evidence, command
timing, and—when policy and sensitivity permit—the run overlay. Request a
graceful shutdown, prove the VM engine stopped, and only then discard or
restore the run-specific overlay. The API companion gives a concrete,
scriptless harness shape.

## Security Defaults

Disable clipboard sharing, file transfer, drag-and-drop, shared folders,
audio input, USB passthrough, remote display, and bridged networking unless
the task requires them. Guest Additions features widen the host/guest
boundary. Use a narrow NAT or host-only arrangement for an untrusted test
guest unless the threat model requires another mode.

Do not put passwords in command arguments, shell history, screenshots, or
tracked files. Use the product's protected prompt or password-file mechanism
when encrypted media require credentials, and protect that file outside the
repository.

## Further Information

- Oracle,
  [VirtualBox 7.2 Troubleshooting](https://docs.oracle.com/en/virtualization/virtualbox/7.2/user/Troubleshooting.html)
- Oracle,
  [VirtualBox 7.2 Security Guide](https://docs.oracle.com/en/virtualization/virtualbox/7.2/user/Security.html)
- Oracle,
  [VirtualBox 7.2 Storage](https://docs.oracle.com/en/virtualization/virtualbox/7.2/user/storage.html)
- [VirtualBox `VBoxManage` API Companion](virtualbox-control.api.knack.md)

Reviewed: 2026-07-23.
