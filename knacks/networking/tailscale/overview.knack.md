# Tailscale for Provisioning and Desktop Login

Reviewed: 2026-10-21 against official documentation and upstream CLI source.
Commands and state fields change; validate the actual packaged client used.

## When to Load

Load this fileset when an installer needs private-network connectivity before
application authorization, when a generated image must include an upgradable
Tailscale client, or when a desktop should help a user reauthenticate.

Companions:

- [Console enrollment](enrollment.knack.md)
- [RPM packaging and updates](packaging.knack.md)
- [Identity handoff and desktop sessions](sessions.knack.md)

## Mental Model

Tailscale supplies encrypted connectivity and node identity. The identity
provider authenticates the human; the coordination service admits the node;
tailnet policy permits particular connections. A provisioning application's
own authorization decision remains a separate step.

Joining a tailnet does not imply that an installation is approved. A healthy
daemon does not prove that a particular server is reachable. An approved
server connection does not establish that the intended account or device
owns the node. Keep those observations distinct in status and tests.

Tailscale already uses WireGuard for its data plane. Replacing Tailscale with
plain WireGuard later requires replacing its enrollment, key distribution,
policy, naming and reachability services, not just changing an interface
name. Keep the authorization protocol independent of its network transport.

## Provisioning Sequence

1. Bring up ordinary IP networking, DNS and usable system time.
2. Start a verified client and daemon without modifying unrelated host state.
3. Enroll through the normal identity-provider browser flow, or use a
   separately approved mechanism for noninteractive enrollment.
4. Distinguish authentication from administrator device approval.
5. Verify that the required server and port are reachable through the chosen
   network, then perform the application's own authorization exchange.
6. Finish installation and deliberately retain or discard the node identity.
7. Verify connectivity again after the installed system reboots.

Enrollment needs access to the coordination service and identity provider.
A private server reachable only after enrollment cannot provide the first
credential needed to enroll unless another bootstrap trust path exists.

## Scope and Boundaries

Keep provider passwords, MFA codes, browser cookies and reusable auth keys
out of project files, image manifests and ordinary logs. Treat enrollment
URLs as short-lived sensitive data too. Do not publish them in telemetry.

Choose state ownership explicitly. A persistent identity belongs to one
installed node. A disposable installer identity is temporary. A golden image
or shared USB stick must contain neither an enrolled state directory nor
the credentials used to enroll one test machine.

Use native packaging where supported. Preserve the vendor's unit and update
path rather than layering a second unmanaged daemon over an RPM install.

## Review and Validation

Verify initial enrollment, expired credentials, device approval, interrupted
installation, loss of Internet access, server refusal and installed reboot.
Record which checks exercised real packaged binaries and which used
controlled external-service responses. Never describe a status-machine test
as proof of a real identity-provider login or tailnet ACL.

## Sources

- [Tailscale identity](https://tailscale.com/docs/concepts/tailscale-identity)
- [How connections are secured](https://tailscale.com/kb/1504/encryption)
- [Install on Linux](https://tailscale.com/docs/install/linux)
- [Technology baseline](../../../standards-and-practices/technologies/tailscale.md)
