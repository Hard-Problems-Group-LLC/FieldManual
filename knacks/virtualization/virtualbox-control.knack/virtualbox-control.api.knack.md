# VirtualBox `VBoxManage` API Companion

Load this companion after the
[VirtualBox overview](virtualbox-control.overview.knack.md) when concrete
`VBoxManage` command families are needed. The examples use neutral
placeholders and Oracle VirtualBox 7.2 syntax. Inspect local help before
executing them.

## Read-Only Orientation

Begin with the installed release, active registry, and exact VM:

```sh
VBoxManage --version
VBoxManage list systemproperties
VBoxManage list vms
VBoxManage list runningvms
VBoxManage list ostypes
VBoxManage showvminfo "LabVM"
VBoxManage showvminfo "LabVM" --machinereadable
```

Use human-readable output for operator review and machine-readable output for
automation. Machine-readable keys can evolve; parse only keys required by the
operation, reject malformed or duplicate values, and keep fixtures from every
supported release.

Quote VM names. Prefer the UUID when a name is ambiguous or being changed.
Before mutation, correlate the VM's UUID, settings path, storage controller,
media UUID and path, NIC mode and MAC address, and reported state.

`showvminfo` reflects one registry context. Reconcile its running state with
host-appropriate engine inspection as described in the overview.

## Creating A Reviewable VM

The following is a shape for a BIOS-based x86 Linux lab VM, not a universal
hardware prescription. Select an OS type reported by `list ostypes`, choose
resources for the guest and host, and use project-approved artifact
locations outside the source checkout.

```sh
vm="LabVM"
disk="<vm-artifact-directory>/LabVM.vdi"
iso="<installer-image-directory>/installer.iso"

VBoxManage createvm \
  --name="$vm" \
  --platform-architecture=x86 \
  --ostype=RedHat_64 \
  --register

VBoxManage modifyvm "$vm" \
  --memory=4096 \
  --cpus=2 \
  --firmware=bios \
  --graphicscontroller=vmsvga \
  --vram=32 \
  --nic1=nat \
  --cable-connected1=on \
  --clipboard-mode=disabled \
  --drag-and-drop=disabled \
  --audio-enabled=off \
  --boot1=dvd \
  --boot2=disk \
  --boot3=none \
  --boot4=none

VBoxManage storagectl "$vm" \
  --name=SATA \
  --add=sata \
  --controller=IntelAHCI

VBoxManage createmedium disk \
  --filename="$disk" \
  --size=32768 \
  --format=VDI \
  --variant=Standard

VBoxManage storageattach "$vm" \
  --storagectl=SATA \
  --port=0 \
  --device=0 \
  --type=hdd \
  --medium="$disk"

VBoxManage storagectl "$vm" \
  --name=IDE \
  --add=ide \
  --controller=PIIX4

VBoxManage storageattach "$vm" \
  --storagectl=IDE \
  --port=0 \
  --device=0 \
  --type=dvddrive \
  --medium="$iso"
```

VirtualBox 7.2.13 installed help exposes indexed options as `--nicN`,
`--cable-connectedN`, and `--bootX`, producing forms such as `--nic1=nat`,
`--cable-connected1=on`, and `--boot1=dvd`. Check installed help because web
documentation may render index placeholders differently and releases can
change.

Before first start, inspect the completed configuration. Confirm that the
disk and optical paths were not exchanged, the ISO is the intended read-only
input, the disk is not attached to a running VM, and host free space supports
its possible growth.

## Start And State Proof

Run the overview's immediate pre-start reconciliation through the consuming
project's approved procedure. The underlying 7.2 command is:

```sh
VBoxManage startvm --type=gui "LabVM"
```

Use `--type=headless` only when an interactive viewer is unnecessary and
another observation path is available. After start, prove one expected engine
and matching registry state.

Capture the guest framebuffer directly:

```sh
VBoxManage controlvm "LabVM" screenshotpng "<scratch-path>/LabVM-boot.png"
```

Write each transition to a new file or replace it atomically so a stale
capture cannot be mistaken for current evidence. Inspect both pixels and
dimensions. A blank or partially redrawn frame calls for a new observation,
not an assertion that the guest failed.

`setvideomodehint` is not a general firmware or installer solution:

```sh
VBoxManage controlvm "LabVM" setvideomodehint 1024 768 32
```

Oracle documents that it requires Guest Additions and does not work for every
guest. Prefer a usable firmware or installer mode and a known viewer scale
when Guest Additions are absent.

## Keyboard Input

Firmware and installer menus may require PC keyboard scancodes:

```sh
VBoxManage controlvm "LabVM" keyboardputscancode 1c 9c
```

This sends Enter's set-1 make code and break code. Always release a key; a
missing break code can leave it logically held. Extended keys and non-US
layouts need deliberate handling. Use:

```sh
VBoxManage controlvm "LabVM" keyboardputstring "example text"
```

only for a text field known to accept literal text. A menu accelerator may
select an action without activating it; observe the result and send Enter
only when the interface requires confirmation.

## Automated Test Harness Shape

FieldManual does not supply a language-specific runner. A consuming project's
harness can implement this VirtualBox 7.2 API shape:

- **Provision:** verify the declared base digest; use
  `createmedium disk --filename=<run-overlay> --diffparent=<verified-base>`
  for a run-specific differencing disk; create or clone the fixture and
  attach only that overlay as writable. Record the exact base, VM UUID,
  controller, and overlay identity.
- **Reconcile and start:** use `showvminfo --machinereadable`,
  `list runningvms`, and host engine inspection before `startvm`. Require one
  control context, no conflicting writer, and one expected engine.
- **Wait:** poll fresh `controlvm ... screenshotpng` captures, serial evidence,
  a Guest Additions-backed check, or a probe from the relevant network
  boundary. Require the declared readiness condition before a bounded
  deadline.
- **Interact:** prefer a guest or service operation. Otherwise use
  `keyboardputstring` for a known text field or complete
  `keyboardputscancode` make-and-break sequences after recognizing the
  intended screen, prompt, or control.
- **Assert:** require another fresh frame, guest state, or service response
  that proves the declared transition. Command success is not the assertion.
- **Diagnose:** capture `showvminfo --machinereadable`, timestamped frames,
  relevant `VBox.log` files, guest or service output, timings, and optionally
  the overlay before teardown. Remove secrets from retained artifacts.
- **Teardown:** only when the run created or acquired the exact fixture and
  its engine and media ownership still reconcile, request
  `controlvm ... acpipowerbutton`, wait a bounded time for powered-off state,
  and prove that engine stopped. Only then unregister the ephemeral fixture
  and discard, preserve, or restore its overlay according to policy. When
  ownership is ambiguous, collect non-mutating evidence and stop.

Express the orchestration as an inspectable state machine:

```text
fixture := provision(declared_fixture, verified_base, new_overlay)
owns_fixture := prove_exact_uuid_and_overlay(fixture)
reconcile()
startvm()
owns_engine := prove_one_matching_engine_and_media(fixture)
wait_until(framebuffer_or_guest_or_service_ready, startup_deadline)
inject(semantic_action_or_scancode_sequence)
assert_until(expected_transition, action_deadline)
on_failure: collect_artifacts_before_teardown()
if owns_engine and ownership_still_reconciles(fixture):
    graceful_stop()
    prove_powered_off(fixture)
if owns_fixture and fixture_is_proven_offline(fixture):
    apply_declared_overlay_retention(fixture)
```

Generate unique VM, overlay, and artifact names from the run identity rather
than reusing a mutable fixture concurrently. If the harness loses the
VirtualBox control context, cannot reconcile media ownership, or reaches its
deadline, classify the run as an infrastructure failure and preserve
evidence. Do not turn a timeout or ambiguous ownership into an unreviewed
shutdown, `poweroff`, or deletion.

## Installer-Media Handoff

After the installer completes, prefer a guest or ACPI shutdown:

```sh
VBoxManage controlvm "LabVM" acpipowerbutton
```

Prove the guest and engine stopped. If Guest Additions are installed,
`controlvm shutdown` is another guest-aware option. `controlvm poweroff`
resembles pulling a physical power cable and may lose data; use it only with
specific authorization.

With the VM stopped, detach the ISO and change boot order:

```sh
VBoxManage storageattach "LabVM" \
  --storagectl=IDE \
  --port=0 \
  --device=0 \
  --type=dvddrive \
  --medium=emptydrive

VBoxManage modifyvm "LabVM" \
  --boot1=disk \
  --boot2=dvd \
  --boot3=none \
  --boot4=none
```

Oracle permits some removable-media changes while a VM runs, but controller
and guest behavior vary. When a live detach is rejected, inspect the
controller and move to a clean offline change instead of repeatedly forcing
it. Confirm the empty optical slot and disk-first order with `showvminfo`,
then start through a fresh preflight and prove an installed-system boot.

## Networking Checks

Inspect the configured adapter and cable state before diagnosing the guest:

```sh
VBoxManage showvminfo "LabVM" --machinereadable
```

For NAT, treat the guest's assigned address and route as authoritative. A
host service can be healthy locally yet unreachable from the guest because it
binds only to loopback, a firewall blocks it, or the wrong address or port is
used.

Check in boundary order:

1. host listener and health endpoint;
2. guest address and route;
3. guest-to-host reachability when permitted;
4. guest-originated TCP connection to the exact port; and
5. application request plus server-side receipt.

NAT does not automatically make a guest service reachable from the host. Add
only the narrow port-forwarding rule required by the test, or deliberately
choose a different network mode. Bridged mode places the guest directly on a
host network segment and should not be the default for an untrusted guest.

## Timing

Timing `VBoxManage` measures control-command duration, not guest completion.
For a meaningful transition, record:

- request time;
- command acceptance;
- first guest evidence of the target state; and
- operator approval or wait time separately.

Fixed sleeps are fallback pacing, not success criteria. Poll a safe
guest-visible or service-visible condition with a documented timeout.

## High-Value Diagnostics

- **Empty VM list:** verify the user, `VBOX_USER_HOME`,
  `XDG_CONFIG_HOME`, home, and default machine folder.
- **Registry says powered off but an engine exists:** stop starts, preserve
  writable media, and investigate the control-context split.
- **One UUID appears in multiple engines:** treat its writable media as at
  immediate corruption risk and quiesce writers before inspection.
- **A writable disk is attached to another engine:** determine whether this
  is a reviewed shared-storage design; otherwise do not start.
- **Start succeeds but boot is wrong:** capture the framebuffer and inspect
  boot order and attached media.
- **Installer repeats after reboot:** detach the ISO and verify disk-first
  boot.
- **Input appears stuck or repeated:** verify every scancode has a release.
- **Coordinates drift:** restore known viewer scaling and recalculate from a
  fresh framebuffer.
- **Guest cannot reach a host service:** test from the guest and verify host
  binding, firewall, route, and exact port.
- **Driver or IPC appears absent only in a sandbox:** repeat the read-only
  check in the authorized host context before diagnosing the host.

## Further Information

- Oracle,
  [VirtualBox 7.2 `VBoxManage` Command Reference](https://docs.oracle.com/en/virtualization/virtualbox/7.2/user/vboxmanage.html)
- Oracle,
  [Creating a New Virtual Machine](https://docs.oracle.com/en/virtualization/virtualbox/7.2/user/create-vm.html)
- Oracle,
  [VirtualBox 7.2 Networking](https://docs.oracle.com/en/virtualization/virtualbox/7.2/user/networkingdetails.html)
- Oracle,
  [VirtualBox 7.2 Guest Additions](https://docs.oracle.com/en/virtualization/virtualbox/7.2/user/guestadditions.html)

Reviewed: 2026-07-23.
