# Identity Handoff and Desktop Reauthentication

Reviewed: 2026-10-21 against the upstream daemon unit and status definitions.

## When to Load

Load this reference when carrying enrollment from an installer into its
installed system, or when opening a browser to help a desktop user log in.

## Give Every Identity One Owner

Persistent Tailscale state contains machine and node credentials. It must
belong to one installed node and remain readable only by its privileged
service. Never include enrolled state in a master image, reusable USB
partition, public manifest, diagnostic attachment or shared cache.

Choose one of two lifecycles explicitly. A temporary installer identity can
be discarded after installation; the target enrolls separately. Alternatively,
an installer can hand the same node identity to the system installed on that
same physical machine. This needs a coordinated, private transfer.

For a handoff, finish all operations that need installer connectivity, stop
the installer daemon cleanly, then copy the complete authoritative state
with private ownership and permissions into the target. Use an atomic
publication step rather than a partially overwritten state file. Account
for daemon-version changes, SELinux labels and the target service's expected
state path. Start the target daemon only after the source daemon stops;
two simultaneously active copies of one machine identity are not a migration.

Do not guess that copying a file from a running daemon produced a consistent
snapshot. Follow the supported state layout for the packaged version and
test the reboot transition. Interrupted installation must leave a clear
recovery state. Avoid silently falling back to a different enrolled identity
from an earlier attempt.

## Keep Browser and Daemon Privileges Separate

The daemon runs with its required system privileges. Firefox runs as the
logged-in desktop user, with that session's display, bus and profile.
Launching Firefox from a root boot unit with guessed display variables can
fail, create root-owned profile files or display private material in the
wrong session. Prefer an XDG autostart entry or session-owned user service.

A system helper can start or refresh enrollment and pass the current URL
through a private runtime file readable only by the intended account. A
user helper then opens that URL in the real session. This avoids granting
an arbitrary desktop process privileged control of network settings.

Resolve the account's actual primary group from the target account database;
do not assume its group has the same name as the user. Check both directory
traversal and file-read permissions, including denial for another account.

An alternative is explicitly assigning the account as Tailscale's operator.
That grants daemon-management authority; document and review the permission
rather than treating it as a harmless browser-launch setting. Do not add a
general passwordless sudo rule solely to obtain a login URL.

## Open a Browser for Authentication, Not Every Failure

Use structured status. `NeedsLogin` signals authentication work; `Running`
with a temporary network failure does not. `NeedsMachineAuth` waits for an
administrator. `Stopped` may be an intentional user choice. Malformed JSON,
a missing socket, or an absent binary means observation failed, not that the
user has logged out.

On the first actual login requirement, use the URL provided by the trusted
daemon. Validate the scheme and provider origin before opening it; do not
pass arbitrary output or local file URLs to a browser. Keep the URL out of
ordinary logs, persistent user preferences and general telemetry.

Allow one helper per session. Open a window once for a login episode, with
a retry policy that does not create another window on every polling cycle.
Reset suppression after an authenticated state is observed so later expiry
can prompt again. Explain how an operator can retry after closing the window.
Preserve existing network preferences during reconnect; avoid `--reset` and
`--force-reauth` unless the operator deliberately requests them.

Keep the browser's address bar and close control available during login.
Setup tours can obscure the enrollment page on a fresh desktop. Firefox's
`OverrideFirstRunPage` policy with an empty string disables its welcome tour;
`OverridePostUpdatePage` can suppress update tabs, and
`DontCheckDefaultBrowser` suppresses the default-browser startup question.
Merge these narrow startup settings into existing policy, preserving
unrelated DNS and certificate rules. Do not edit or inspect a user's
credential-bearing profile to remove onboarding. Test a fresh profile
separately from real login.

Some distribution builds also open a separate legacy data-reporting notice
tab. This is independent of the welcome tour. Firefox's supported
`Preferences` policy can set `datareporting.policy.firstRunURL` to an empty
string with `Status: default`, preserving other administrator preferences.
Verify the actual packaged browser with a fresh disposable profile; a policy
file alone does not prove a quiet first launch. This setting is distinct
from `SkipTermsOfUse`, which represents acceptance on behalf of users and
must not be treated as a cosmetic startup control.

## Validate the Actual Boundaries

Exercise fresh login, logout after successful login, expired keys, canceled
browser login, multiple helper launches, a stopped daemon, offline mode and
device approval pending. Confirm that browser processes run as the intended
user and that no startup code calls them before a desktop session exists.

Test identity handoff with the source daemon stopped and the installed target
booted independently. Application-server reachability and administrator
approval still need separate checks. A fake status stream can prove prompt
suppression logic, but cannot prove real enrollment or key migration.

Order installed-system provisioning after the native daemon and network
startup, then wait for usable connectivity within an explicit deadline.
An enabled service or an ordering target alone does not prove the overlay
route is ready. Preserve a retryable outcome when the deadline expires.

## Sources

- [Identity and machine keys](https://tailscale.com/docs/concepts/tailscale-identity)
- [Key expiry](https://tailscale.com/kb/1028/key-expiry)
- [CLI reference](https://tailscale.com/kb/1080/cli)
- [Packaged daemon unit source](https://github.com/tailscale/tailscale/blob/main/cmd/tailscaled/tailscaled.service)
- [Live user-session targeting](../../desktop/live-user-session-targeting.knack.md)
- [Firefox first-run policy](https://firefox-admin-docs.mozilla.org/reference/policies/overridefirstrunpage/)
- [Firefox update-page policy](https://firefox-admin-docs.mozilla.org/reference/policies/overridepostupdatepage/)
- [Firefox default-browser policy](https://firefox-admin-docs.mozilla.org/reference/policies/dontcheckdefaultbrowser/)
- [Firefox Preferences policy](https://firefox-admin-docs.mozilla.org/reference/policies/preferences/)
- [Reporting first-run preference](https://firefox-source-docs.mozilla.org/toolkit/components/telemetry/internals/preferences.html#data-choices-notification)
- [Terms-of-use policy](https://firefox-admin-docs.mozilla.org/reference/policies/skiptermsofuse/)
