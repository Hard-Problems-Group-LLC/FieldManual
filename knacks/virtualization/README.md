# Virtualization Knacks

Use these knacks when work crosses a virtual-machine control boundary. They
separate provider-neutral lifecycle and data-safety rules from commands that
belong to one hypervisor.

## Contents

- [Safe Virtual-Machine Control](virtual-machine-control.knack.md) — target
  identity, state evidence, writable-media ownership, backups, overlays, and
  an evidence-driven automated-test lifecycle
- [VirtualBox Control](virtualbox-control.knack/virtualbox-control.overview.knack.md)
  — Oracle VirtualBox control-plane orientation, framebuffer and input
  automation, fixture overlays, and a version-scoped `VBoxManage` companion

Virtual machines hold mutable state outside the source checkout. Treat their
power, storage, network, and device operations as external mutations even
when the command that initiates them is typed from a project directory.
