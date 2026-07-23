# Bubblewrap

Load this knack when a Linux tool, test harness, or agent runtime uses
bubblewrap and its filesystem or namespace boundary is unclear or failing.
Bubblewrap is a low-level sandbox constructor, not a general-purpose container
or policy engine.

## Mental Model

Bubblewrap creates a new mount namespace with a synthetic root. Host paths are
not visible until the command exposes them. The sandbox is the combination of:

1. the filesystem assembled through bind mounts, tmpfs, proc, dev, and
   overlays; and
2. the user, process, IPC, network, UTS, and cgroup namespaces that are
   unshared or retained.

The command line is the sandbox contract.

Consequences:

- Missing binaries, libraries, configuration, and devices were often never
  bound into the synthetic root.
- Read-only host content should use `--ro-bind`.
- Writable host binds define the write blast radius.
- Ephemeral writable areas should prefer `--tmpfs` or an appropriate overlay.

## Common Building Blocks

- `--ro-bind SRC DEST` exposes a host path read-only.
- `--bind SRC DEST` exposes a host path read-write.
- `--proc DEST` and `--dev DEST` create process and device views.
- `--tmpfs DEST` creates an empty writable memory filesystem.
- `--dir DEST` creates a directory in the synthetic root.
- `--chdir DIR` selects the child working directory.
- `--setenv` and `--unsetenv` control environment inheritance.
- `--unshare-user`, `--unshare-pid`, and `--unshare-net` create namespace
  boundaries.
- `--unshare-all` starts strict and permits deliberate opt-backs-in such as
  `--share-net`.
- `--new-session` creates a new session.
- `--die-with-parent` terminates the sandbox when its parent exits.

For a general sandbox, the manual recommends considering `--new-session` or
an appropriate seccomp restriction against terminal input injection.

## Read-Mostly Pattern

The broad shape is:

```bash
bwrap \
  --unshare-all \
  --share-net \
  --ro-bind /usr /usr \
  --ro-bind /bin /bin \
  --ro-bind /lib /lib \
  --ro-bind /lib64 /lib64 \
  --ro-bind /etc /etc \
  --proc /proc \
  --dev /dev \
  --tmpfs /tmp \
  --dir /work \
  --ro-bind "$PWD" /work \
  --chdir /work \
  --new-session \
  --die-with-parent \
  sh
```

This is illustrative, not portable as written. Distribution layouts differ;
some paths may be symlinks, absent, or supplemented by other library
directories. Network sharing is a deliberate relaxation and should be removed
when not required.

## Narrow Writable Pattern

When a command must write to host state, expose only the required subtree:

```bash
bwrap \
  --unshare-all \
  --share-net \
  --ro-bind /usr /usr \
  --ro-bind /bin /bin \
  --ro-bind /lib /lib \
  --ro-bind /lib64 /lib64 \
  --proc /proc \
  --dev /dev \
  --tmpfs /tmp \
  --dir /work \
  --bind "$PWD/output" /work \
  --chdir /work \
  --new-session \
  --die-with-parent \
  sh
```

Binding one output directory is safer than making an entire repository
writable. Confirm that symlinks inside the writable subtree do not expand the
effective target unexpectedly.

## Wrapper and Nested-Sandbox Failures

Tooling may generate bubblewrap commands. Diagnose the resulting boundary in
layers:

1. inspect the actual generated command;
2. compare requested flags with `bwrap --help` and the installed version;
3. reproduce with a minimal direct command;
4. distinguish wrapper defects from kernel or outer-sandbox policy; and
5. add namespaces and mounts back one at a time.

A command valid on an ordinary host may fail in a container, CI runner, or
outer agent sandbox that prohibits nested namespaces.

## High-Value Troubleshooting

### Unknown Option

The caller and installed bubblewrap have different feature expectations.
Inspect help and version output, then compare with the caller's documented
minimum. An operating-system package update may not provide a new enough
feature; a wrapper-specific fallback is not universal.

### `Operation not permitted`

Common causes include:

- disabled unprivileged user namespaces;
- kernel, security-module, or container policy;
- differences between setuid and unprivileged builds; and
- an outer sandbox blocking nested namespace creation.

Remove optional namespace flags one at a time to identify the rejected
boundary. Do not weaken isolation permanently merely to make the error
disappear.

### Network Namespace Setup Failure

A netlink or loopback setup error often means bubblewrap is present but the
outer environment forbids network-namespace administration. This is distinct
from an unsupported command-line flag.

### Immediate `ENOENT`

Confirm:

- the executable and dynamic loader are visible;
- required libraries and configuration were bound;
- destination parent directories exist; and
- `--chdir` names a path inside the synthetic root.

Do not diagnose permission policy before proving the path exists in the
sandbox.

### Setuid Differences

Some namespace and overlay options differ in setuid builds. Compare build
mode as well as version when behavior varies across systems.

## Working Habits

- Start with the smallest filesystem and namespace surface.
- Keep host writes narrow and explicit.
- Control environment leakage.
- Use `--new-session` and `--die-with-parent` when appropriate.
- Reproduce wrapper failures with a minimal direct command.
- Treat the outer execution environment as part of the diagnosis.
- Record every intentional relaxation and the requirement it serves.

## Further Information

- Bubblewrap repository:
  <https://github.com/containers/bubblewrap>
- Bubblewrap reference manual:
  <https://github.com/containers/bubblewrap/blob/main/bwrap.xml>
- Bubblewrap releases:
  <https://github.com/containers/bubblewrap/releases>
- Flatpak sandbox permissions:
  <https://docs.flatpak.org/en/latest/sandbox-permissions.html>
- Linux namespaces manual:
  <https://man7.org/linux/man-pages/man7/namespaces.7.html>
- Linux user namespaces manual:
  <https://man7.org/linux/man-pages/man7/user_namespaces.7.html>
