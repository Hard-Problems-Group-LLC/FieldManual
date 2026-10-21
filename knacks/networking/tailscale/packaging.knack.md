# Native RPM Packaging and Updates

Reviewed: 2026-10-21 against the official stable repository and RPM metadata.
Version examples are illustrative; validate the release and architecture
selected for each generated image.

## When to Load

Use this reference when provisioning RHEL-family installations that must
remain upgradeable through the normal package manager.

## Preserve Package Ownership

Install the official Tailscale RPM and configure the matching official
repository. DNF or Yum must own the installed binaries and service unit.
Do not copy release tarballs over packaged paths or install another daemon
under a different prefix. Those approaches can leave an upgraded package
present while the machine continues running an older shadowing binary.

Official repository configurations distinguish the distribution major
release and architecture. At review, RHEL 9 and 10 each have a stable
repository. Follow the current official instructions for the target release
rather than assuming one release's repository is the permanent fallback.

Normal installation and subsequent upgrades use commands such as:

```sh
dnf install tailscale
systemctl enable --now tailscaled
dnf upgrade tailscale
```

Adding a repository through `dnf config-manager` may require a plugin, and
DNF 4 and DNF 5 use different command syntax. Generated installers can write
an explicitly reviewed repository configuration instead of depending on a
particular plugin. Retain package and repository signature checks.

## Building Offline-Capable Media

Downloading during first login couples a user's desktop to repository and
Internet availability. An image builder can instead bundle the official
signed RPM and install it with the target's package manager.

Keep a reproducible receipt: package name, version, release, architecture,
source URL, digest and signing-key identity. Resolve and include dependencies
or ensure the target's selected distribution package set supplies them.
The reviewed RPM requires `iptables` and `iproute`; inspect the actual
selected RPM because requirements can change and capability providers may
have different package names on different distributions.

Verify the package signature against a deliberately trusted vendor key.
A checksum detects corruption but is not independent authenticity evidence
when both bytes and checksum come from an untrusted source. A temporary
unprivileged RPM database lets a builder validate a vendor key without
altering the workstation's trusted keys or installing the package there.

On the target, import the approved public key, install the bundled package
using DNF's local-package signature verification, and leave the official
repository configured for later updates. An offline install can disable
remote repositories for that transaction; subsequent updates must retain
the normal online repository. Do not use `--nodeps`, `--nogpgcheck`, or
manual binary copying to hide an incomplete dependency plan.

## Using a Client Before Target Installation

An installer may need the client before its target package database exists.
It can use an independently staged copy extracted from the verified RPM,
while installing the complete RPM normally into the final system. This is
a temporary execution environment, not a replacement target installation.

Authenticate the RPM before extraction. Extract only known regular files
into a private scratch directory; refuse traversal paths, links, unexpected
architectures and overwrites. Never execute package scriptlets merely to
obtain the temporary client. Confirm that the installer has the runtime,
kernel TUN and firewall facilities the client expects.

## Validation and Maintenance

Check the installed package with RPM, inspect the executable selected by
the service, confirm the enabled repository and signature policy, and test
an ordinary upgrade. Distinguish a dry-run transaction from a completed
upgrade. Avoid installing or upgrading a developer workstation as an
incidental image-building side effect.

Bound the download cache. Replace superseded releases only after the new
package is verified, preserve small receipts, and remove disposable test
images after their contents are proven. An ignored directory is still real
disk usage.

## Sources

- [Official stable packages](https://pkgs.tailscale.com/stable/)
- [Linux installation](https://tailscale.com/docs/install/linux)
- [Official installer implementation](https://github.com/tailscale/tailscale/blob/main/scripts/installer.sh)
- [RPM signature verification](https://rpm.org/docs/6.0.x/man/rpmkeys.8)
