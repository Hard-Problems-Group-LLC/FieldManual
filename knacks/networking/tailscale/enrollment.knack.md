# Console Enrollment

Reviewed: 2026-10-22. Verify options with the packaged client's help output.

## When to Load

Use this reference when a console installer must join a tailnet before its
own authorization or provisioning work can continue.

## Use the Identity Provider's Browser

A console need not collect identity-provider credentials. Run the standard
Tailscale enrollment flow and display its login URL and, where useful, QR
code. The operator opens the link on a trusted phone or laptop, completes
Google or another configured provider's sign-in, and returns to the console.
This preserves the provider's normal password, passkey and MFA handling.

A QR code can be printed in a text console; it does not require a graphical
server or framebuffer browser. Always show the plain URL too. Serial
terminals, limited fonts, clipped lines or a camera that cannot scan the
display must not remove the operator's alternative enrollment path.

A console inherited from an installer or terminal multiplexer can have raw
output processing: LF moves down without returning to column zero. This
staircases ordinary text and destroys a text QR code. Temporarily enable
normal newline translation for the whole enrollment interaction, including
the native client subprocess, then restore the caller's terminal settings
on success, skip, timeout and interruption. Restoring raw output immediately
after the opt-in prompt can still corrupt the subsequent native QR display.

First give the interaction a terminal that the installer does not own.
Anaconda's tmux can reset a shared console to raw mode after an initially
readable prompt, overriding the application's newline settings. Allocate
and activate a separate Linux virtual terminal where available, outside
consoles reserved for installer UI/shell and automatic gettys. Verify the
switch before redirecting input/output; return and release it on every exit.
Serial and hypervisor consoles must keep their actual connected channel.

Check utilities in the installation runtime itself. A minimal installer can
contain `chvt` while omitting `fgconsole`; the installed distribution's
package contents do not establish availability during early boot. A small
stdlib helper can use Linux's VT ioctl interface without those commands.
Bound activation waits and keep restoration independent of mounted media.

Test actual PTY output with translation initially disabled, not only captured
strings. Boot the actual remastered EFI/USB path, including the installer's
terminal multiplexer startup; direct-kernel probes can miss timing failures.
Check the packaged client in the installer's VGA console and, when
available, decode the QR from its rendered pixels without logging the URL.
A public synthetic URL is appropriate for generic rendering tests; real
provider login remains a separate private operator step.

For unattended installations, offer a bounded opt-in window before starting
interactive enrollment. A conspicuous banner can accept one key to begin,
Esc to skip, and default to skip after a countdown. Keep this offer deadline
separate from the enrollment deadline. Skipping network enrollment must not
silently bypass the application's independent authorization policy.

Before an operator signs in, stop AI framebuffer capture, input injection,
console recording and guest inspection. Enter credentials on a trusted
second device outside the automation account's access when hard isolation
is required. Pausing capture in a VM controlled by the same account is an
operational boundary, not a cryptographic guarantee. Resume observation
only after the operator explicitly finishes the private stage.

For an interactive console, the CLI can display its own enrollment UI:

```sh
tailscale up --qr --timeout=10m
```

Use a finite application-level deadline too. A timeout does not authorize
the installer to proceed. Cancellation, daemon exit or exhausted enrollment
time must return control without beginning destructive installation work.

Do not ask for a Gmail password in a custom TUI, scrape Google's forms, use
an application password as an OAuth substitute, or assume a terminal web
browser supports the provider's current security requirements. An email
address may be an optional account hint, but it proves no identity.

## Resolve the Name Before Enrollment

A temporary installer often starts with `localhost`. Set its intended live
OS hostname before starting the native daemon or requesting an enrollment
URL. Writing the future target's `/etc/hostname` alone does not rename the
running installer. Other services that read the kernel hostname can report
that temporary name too.

Choose the long-term naming policy explicitly. With an empty hostname
preference, Tailscale derives its name from the OS. An explicit
`tailscale up --hostname=NAME` or `tailscale set --hostname=NAME` stores an
override; carrying native state to the installed system also carries that
preference. A later OS rename does not clear it. The control server may
normalize the machine name, add a collision suffix or retain an
administrator's manual name, so the advertised hostname and MagicDNS name
need not be identical.

Validate names after adding any uniqueness suffix. Linux limits the complete
kernel hostname to 64 characters and DNS labels to 63. The native client's
OS-derived host information uses the first DNS label; a suffix placed after
an FQDN's domain can disappear from the default advertised name. Use the
actual target's interface identity, not a builder or preview value. Resolve
an installation-specific name once instead of changing it during retries,
reauthentication or reboot. If a clock-derived identifier is used, record
its timezone and whether the clock was synchronized or guessed.

Treat a temporary override as a separate lifecycle. Clear it deliberately
when the installed OS has the intended hostname, then verify the advertised
name after refresh/restart. A successful clear of the preference does not
prove the current backend host information has already been regenerated.
Renaming does not require logging out or editing private native state JSON.

Verify preference persistence across daemon restart and first successful
authentication. A successful local `set` before authentication is not proof
that an authenticated profile exists. Keep an initial naming operation
retryable until the required native state is established, and preserve later
deliberate administrator changes. Exercise unauthenticated behavior in a
disposable guest; actual provider login remains the operator's private step.

## State and Process Ownership

Use the daemon's real state, not a success-looking line in CLI output.
`tailscale status --json` exposes `BackendState` and `AuthURL`. A nonzero
CLI exit may still accompany meaningful JSON while the node needs login.
Parse and validate the JSON before treating the exit status alone as proof
that the daemon is unavailable.

The documented states have different consequences:

| State | Meaning for an installer |
| --- | --- |
| `NoState`, `NeedsLogin` | Start or continue enrollment |
| `NeedsMachineAuth` | Authentication finished; administrator approval waits |
| `Starting` | Wait within the connection deadline |
| `Running` | Check the intended server separately |
| `Stopped` | Do not silently override an intentional stop |

Use a private daemon socket and state directory when running in a temporary
environment. Do not attach test automation to the workstation's existing
daemon. Use kernel TUN mode when ordinary application connections need the
overlay route; userspace networking requires deliberately configuring its
proxy or forwarding path. Check kernel and firewall support in the actual
installer environment, not only in the installed distribution.

Daemon logging has its own directory policy. A private `--state` file and
`--statedir` do not by themselves confine log files to that directory. For
temporary environments, create a private RAM-backed log directory and set
`TS_LOGS_DIR` for both the daemon and every client subprocess. Verify this
against the deployed version; a missing directory can trigger a fallback to
the normal system state directory. Treat diagnostic logs as sensitive even
when enrollment output is not deliberately captured.

Capture only the data needed to drive the UI. Keep the login URL on the
interactive console or in a private session handoff. Avoid `tee`, shell
tracing, screenshots retained without review, and general-purpose process
logs that copy the URL into durable records.

## Noninteractive Alternatives

Auth keys can enroll unattended machines. Scope them through an approved
secret-delivery path, use short lifetimes and appropriate tags, and apply
least-privilege tailnet policy. A reusable key baked into shared installation
media remains reusable by anyone who can read that medium.

OAuth clients and workload identity are separate deployment designs. They
require a trust and secret-delivery decision; they are not a reason to
request a user's Google password. Device approval may still be required.

An ephemeral node can use an ephemeral auth key or a daemon with in-memory
state. Choose this only when losing its identity at shutdown is intended.
Do not promise seamless installed-system continuity for an ephemeral node.

## Failure Checks

Verify offline startup, provider unavailability, approval pending, user
cancellation, expiration, daemon termination and denied server access.
Do not disable TLS verification or fall back to unauthenticated installation
to make a failed enrollment look successful.

## Sources

- [Up command](https://tailscale.com/docs/reference/tailscale-cli/up)
- [Machine names](https://tailscale.com/docs/concepts/machine-names)
- [Native hostname preference, version 1.104.2](https://github.com/tailscale/tailscale/blob/v1.104.2/ipn/prefs.go)
- [Native host information, version 1.104.2](https://github.com/tailscale/tailscale/blob/v1.104.2/hostinfo/hostinfo.go)
- [Linux hostname limits](https://www.freedesktop.org/software/systemd/man/latest/hostname.html)
- [Add a device](https://tailscale.com/docs/features/access-control/device-management/how-to/set-up)
- [Auth keys](https://tailscale.com/kb/1085/auth-keys)
- [Ephemeral nodes](https://tailscale.com/docs/features/ephemeral-nodes)
- [Daemon log directory policy, version 1.104.2](https://github.com/tailscale/tailscale/blob/v1.104.2/logpolicy/logpolicy.go)
- [Upstream status fields](https://github.com/tailscale/tailscale/blob/main/ipn/ipnstate/ipnstate.go)
