# GitHub SSH and Git Identity Across Organizations

Load this knack when one workstation accesses GitHub repositories for more
than one organization, account, or legal identity. The goal is to keep
transport authentication, commit metadata, GitHub attribution, and repository
authorization aligned without assuming they are one mechanism.

All examples are fictional. The `.example` email domain is reserved for
documentation.

## Mental Model

Four independent layers participate:

1. **SSH authentication** selects the private key offered to GitHub.
2. **Git author and committer metadata** records names and email addresses in
   commit objects.
3. **GitHub attribution** maps a commit email to an account when that email or
   an applicable `noreply` address is associated with the account.
4. **Repository authorization** determines whether the authenticated account
   may access the organization, team, or repository.

It is possible to authenticate as one account, create a commit with another
identity, and receive attribution on neither account. Always verify each
layer separately.

## A Predictable Pattern

A practical default is:

- one explicit SSH host alias per account or organization;
- one key per trust boundary when policy calls for separation;
- `IdentitiesOnly yes` so SSH does not offer unrelated agent keys;
- one Git identity include file per commit identity;
- conditional Git includes based on a documented repository location; and
- `user.useConfigOnly = true` so Git does not invent an identity.

Path-based identity selection is a convention, not a security boundary.
Stronger contractual or compliance separation may require different
operating-system users, development environments, or machines.

## SSH Aliases

An illustrative `~/.ssh/config`:

```sshconfig
Host github-alpha
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_alpha
    IdentitiesOnly yes

Host github-bravo
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_bravo
    IdentitiesOnly yes
```

Both aliases contact `github.com`; the alias controls which local SSH policy
and key apply. A corresponding remote has this shape:

```text
git@github-alpha:OWNER/REPOSITORY.git
```

Register each public key with the intended GitHub account before expecting
authentication to succeed.

## Conditional Git Identity

An illustrative `~/.gitconfig`:

```ini
[user]
    useConfigOnly = true

[includeIf "gitdir:~/work/alpha/"]
    path = ~/.gitconfig-alpha

[includeIf "gitdir:~/work/bravo/"]
    path = ~/.gitconfig-bravo
```

The Alpha include:

```ini
[user]
    name = Example Developer
    email = developer@alpha.example
```

The Bravo include:

```ini
[user]
    name = Example Developer
    email = developer@bravo.example
```

Git's `gitdir:` matching applies to the repository's Git directory. Account
for worktrees, bare repositories, case sensitivity, and the trailing slash
rules described by Git before relying on a pattern.

Repository placement now carries policy meaning. Document the convention and
avoid moving a repository across identity roots without rechecking its
effective configuration.

When path-based selection does not fit, use an explicit repository-local
identity or another documented mechanism. Do not add a broad global email
merely to make a failed commit proceed.

## Setup Sequence

1. Decide the actual trust and identity boundaries.
2. Generate or provision keys according to each organization's policy.
3. Add one SSH alias per boundary.
4. Register the public keys with the corresponding GitHub accounts.
5. Associate each intended commit email with the appropriate account, or
   adopt the account's documented `noreply` policy.
6. Create identity include files and conditional rules.
7. Clone or move repositories into their documented ownership roots.
8. Verify authentication and commit identity before the first commit or push.

Key generation, storage, hardware-token use, rotation, and backup are
security-policy decisions. Do not copy private keys between environments
unless the governing policy explicitly permits it.

## Verification

Inside a repository, inspect the independent layers:

```bash
git remote -v
git config user.name
git config user.email
git config --show-origin --get user.email
git config --list --show-origin
```

Inspect SSH's resolved policy without authenticating:

```bash
ssh -G github-alpha
```

Review the resulting hostname, user, identity file, and
`identitiesonly` setting. When network authentication is appropriate, GitHub
documents an `ssh -T` connectivity test; use the configured alias instead of
the default hostname.

Before pushing, answer:

- Which key and GitHub account will authenticate?
- Which author and committer identity will Git record?
- Is the email associated with the intended GitHub account?
- Does the authenticated account have the intended repository access?
- Is the repository stored under the correct identity policy?

## Troubleshooting Order

1. **Inspect configuration origins.** A repository-local value may override a
   conditional include.
2. **Inspect the remote.** Confirm it uses the intended SSH alias.
3. **Inspect SSH resolution.** Confirm the alias selects the expected key and
   uses `IdentitiesOnly yes`.
4. **Inspect environment overrides.** Git author and committer environment
   variables can override configuration.
5. **Inspect the active home and config scope.** Isolated automation
   environments may intentionally use different SSH and Git configuration.
6. **Test account authorization.** Correct key selection does not grant
   organization or repository membership.

Useful environment variables to check include:

```text
GIT_AUTHOR_NAME
GIT_AUTHOR_EMAIL
GIT_COMMITTER_NAME
GIT_COMMITTER_EMAIL
EMAIL
```

Do not print broader environments or private key material merely to diagnose
identity selection.

## Important Edge Cases

### Author and Committer Can Differ

Rebases, cherry-picks, patch application, automation, and history rewriting
can produce different author and committer identities. Check both when
auditing or repairing attribution.

### Web Operations Use Account Settings

GitHub web edits and merges use GitHub-side email preferences rather than the
Git configuration in a local checkout. Verify both policies when consistent
attribution matters.

### `noreply` Can Be Deliberate

GitHub-provided `noreply` addresses can preserve attribution while reducing
email exposure. They may make organization provenance less obvious in raw
commit metadata, so choose the model deliberately.

### One Account or Several

One GitHub account can have multiple verified emails. Separate accounts or
enterprise-managed identities may instead be required. The SSH-alias pattern
supports either, but organization policy decides which model is valid.

### Path Conventions Are Not Isolation

Conditional includes prevent ordinary mistakes; they do not prevent a user or
tool from overriding identity. Use stronger isolation when legal,
contractual, confidentiality, or export-control requirements demand it.

## Incorrect Identity in History

If an incorrect identity exists only in an unpushed recent commit, a reviewed
local amendment may be sufficient. Once commits are shared, rewriting changes
commit identifiers and can disrupt collaborators, signatures, automation,
reviews, and references.

Treat a shared-history rewrite as coordinated incident work. Preserve
evidence, inspect both author and committer fields, agree on the affected
range, and follow GitHub's cleanup guidance. If the metadata contains a secret
or sensitive internal identifier, rotate or revoke the exposed value as
appropriate; rewriting history does not erase copies already obtained.

## Operating Checklist

- Keep aliases stable, descriptive, and neutral.
- Keep private key permissions and storage appropriate to policy.
- Enable `user.useConfigOnly`.
- Verify effective identity in every newly created or moved repository.
- Inspect configuration origins, not only final values.
- Review representative repositories after configuration changes.
- Treat history rewriting as exceptional.

Also follow FieldManual's
[version-control safety guidance](../../standards-and-practices/core/version-control-safety.md).

## Further Information

- Git configuration reference: <https://git-scm.com/docs/git-config.html>
- GitHub authentication overview:
  <https://docs.github.com/en/authentication>
- GitHub, managing multiple accounts:
  <https://docs.github.com/en/account-and-profile/how-tos/account-management/managing-multiple-accounts>
- GitHub, adding an SSH key:
  <https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account>
- GitHub, testing an SSH connection:
  <https://docs.github.com/en/authentication/connecting-to-github-with-ssh/testing-your-ssh-connection>
- GitHub, commit email attribution:
  <https://docs.github.com/en/account-and-profile/concepts/email-addresses>
- GitHub, setting a commit email:
  <https://docs.github.com/en/account-and-profile/how-tos/email-preferences/setting-your-commit-email-address>
- GitHub, sensitive-data history cleanup:
  <https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository>
