# Virtualization Knacks

Use these knacks when work crosses a virtual-machine control boundary. They
separate provider-neutral lifecycle and data-safety rules from commands that
belong to one hypervisor.

## Contents

- [Safe Virtual-Machine Control](virtual-machine-control.knack.md) — target
  identity, state evidence, writable-media ownership, backups, overlays, and
  an evidence-driven automated-test lifecycle
- [VirtualBox Control](virtualbox/overview.knack.md)
  — Oracle VirtualBox control-plane orientation, framebuffer and input
  automation, fixture overlays, and a version-scoped `VBoxManage` companion
- [Windows Sandbox](windows-sandbox/overview.knack.md) — testing on a
  fresh, disposable Windows: `.wsb` configuration and the `wsb` command,
  self-closing test drivers, the one-good-launch-per-boot defect, and what
  a never-used Windows lacks
  - [Configuration](windows-sandbox/configuration.knack.md)
  - [Test drivers](windows-sandbox/test-drivers.knack.md)
  - [Fresh install](windows-sandbox/fresh-install.knack.md)

Virtual machines hold mutable state outside the source checkout. Treat their
power, storage, network, and device operations as external mutations even
when the command that initiates them is typed from a project directory.
