# Purge Large Or Sensitive Files From Git History

Load this knack after an unwanted large file, generated artifact, private
record, or secret has entered Git history. It covers investigation,
`git-filter-repo`, coordinated publication, and verification. Read the
[core version-control safety standard](../../standards-and-practices/core/version-control-safety.md)
before proceeding.

## First Response

Stop pushes and automated publication while scope is unknown. Repeated push
attempts ordinarily resend pack data rather than resuming an interrupted
upload, and another writer can change the remote refs while a cleanup is
being prepared.

If the content contains a password, token, private key, session material, or
another credential, **revoke or rotate it first**. Rewriting Git does not make
an exposed credential trustworthy again, and old objects may remain in
clones, caches, forks, pull-request refs, logs, or backups.

Record:

- the repository and every relevant remote;
- who may push during the incident;
- the unwanted path, content, and known blob object IDs;
- whether Git LFS, submodules, signed commits or tags, releases, or generated
  artifacts are involved;
- protected branches and provider-managed refs;
- the authority required for a rewrite and force update; and
- the recovery copy and collaborator communication plan.

Do not begin mutation merely because a large object exists. A shared-history
rewrite can cost more than retaining a non-sensitive object. Decide whether
removal is required by security, law, hosting limits, repository usability, or
explicit operator direction.

## Establish Reachability

Distinguish the local repository from what others can fetch. A local object
may never have reached a remote; a file deleted from the current tree may
remain reachable through earlier commits, tags, or other refs.

Use read-only inventory first:

```sh
git remote -v
git show-ref
git count-objects -vH
git ls-remote --refs <remote-url>
```

Create a fresh disposable mirror of the remote and analyze it:

```sh
git clone --mirror <remote-url> <analysis-clone>
git -C <analysis-clone> filter-repo --analyze
```

When the source is a local filesystem repository, use `git clone --no-local`
as recommended by `git-filter-repo`; hard-linked local clones can undermine
the fresh-clone safety assumption.

The analysis reports under the clone's Git directory summarize blob IDs,
paths, extensions, and aggregate sizes. Inspect all relevant refs, not only
the default branch. Git hosting systems may retain provider-managed pull
request, merge request, review, or change refs that an ordinary mirror cannot
update. Consult the provider's current removal procedure before claiming
remote eradication.

If the unwanted object is absent from every relevant remote ref, do not
rewrite the remote. Repair unpublished local commits, or recreate the local
branch from the remote and reapply wanted changes. Prove that the resulting
push is a normal fast-forward before publishing it.

If the object is remotely reachable, freeze shared writes and continue only
with explicit rewrite authority.

## Prepare A Controlled Rewrite

Keep a pristine mirror or another reviewed recovery copy unchanged. Make a
second fresh clone for the rewrite. Restrict access to recovery copies that
contain secrets, and give them an explicit retention and destruction plan.

Before filtering, save a ref plan containing each affected full refname and
its exact remote object ID:

```text
refs/heads/main  <expected-old-oid>  <planned-new-oid>
refs/tags/v1.2   <expected-old-oid>  <planned-new-oid>
```

Also record current tip tree IDs for branches whose present-day content must
remain identical. This evidence will later distinguish an intended historical
change from accidental current-tree damage.

Inspect the installed tool's help. For a credential or private-data event,
current `git-filter-repo` provides `--sensitive-data-removal`, which gathers
additional ref and LFS cleanup information:

```sh
git filter-repo --help
git filter-repo --sensitive-data-removal \
  --path <unwanted-path> \
  --invert-paths
```

Choose the narrowest correct filter:

- Name every historical path when the file moved or was renamed.
- Use an exact path or blob-ID set when only particular objects are unwanted.
- Use `--replace-text` when a sensitive string must be removed while the rest
  of a file remains; protect the expressions file and avoid placing the
  secret itself in shell history.
- Use `--strip-blobs-bigger-than` only when **every** blob above the selected
  size is intentionally out of scope. It is not a substitute for reviewing
  the object list.

`git-filter-repo` normally removes the `origin` remote, expires old reflogs,
and repacks after a full rewrite. These are safety properties. Do not bypass
the fresh-clone check on a working checkout, and do not reconnect a
publication remote until validation is complete.

## Validate The Rewrite Locally

Run the repository's normal checks against the rewritten tips. Then validate
history itself:

1. Re-run `git filter-repo --analyze`.
2. Prove the unwanted blob IDs, paths, or sensitive content are no longer
   reachable from every intended ref.
3. Inspect `commit-map`, `ref-map`, `changed-refs`, and, when generated,
   `first-changed-commits` under the Git directory's `filter-repo/` output.
4. Compare the resulting ref set with the plan and explain every changed or
   removed ref.
5. Inspect tags, releases, submodule gitlinks, Git LFS results, and rewritten
   commit-message references.
6. Check signatures and provenance expectations. History rewriting changes
   commit IDs, and `git-filter-repo` removes commit and tag signatures that
   cannot remain valid.

### What Tip Trees Prove

For a branch whose current files must remain the same, compare:

```sh
git rev-parse <old-tip>^{tree}
git rev-parse <new-tip>^{tree}
```

Equal tree IDs prove that those two **tip snapshots** contain the same paths,
modes, and content. They do **not** prove that no historical object was
removed. Removing a blob that existed only in an earlier commit should
normally leave the current tip tree unchanged.

Conversely, a changed tip tree may be correct when the unwanted file still
exists at the current tip. Review the actual tree difference rather than
using equality or inequality alone as the purge test.

Historical removal is proved by reachability analysis across the intended
refs, exact object or content checks, the filter reports, and a second
analysis—not by one `HEAD^{tree}` comparison.

## Coordinate Exact Remote Updates

Immediately before publication, retrieve the remote refs again and compare
each affected object ID with the recorded expected old value. If any ref
diverged, abort. Determine whether to preserve the new work and redo the
rewrite; never overwrite an unexplained update.

Create a deliberately named publication remote only after the ref plan and
local validation are approved. Push explicit source and destination refs with
explicit leases. A single-branch shape is:

```sh
git push \
  --force-with-lease=refs/heads/main:<expected-old-oid> \
  <reviewed-remote> \
  <new-main-oid>:refs/heads/main
```

For multiple branches and tags, provide a reviewed refspec and an explicit
expected old OID for each forced update. Make ref deletions explicit. Use
`--atomic` only when the server supports it and the planned updates must
succeed or fail together.

Do not use a generic `--force-with-lease --mirror` recipe. `--mirror`
force-updates or deletes all refs under `refs/`, while a lease without an
explicit expected value relies on local remote-tracking state. That
combination does not express a reviewable remote snapshot.

A complete sensitive-data purge may require a provider-specific full-ref
force update. Use such an operation only when:

- the provider's current runbook calls for it;
- the mirror is known to contain every ref that should survive;
- hidden and protected refs have an explicit disposition;
- all shared writes are frozen; and
- the exact deletion and overwrite effects have been reviewed.

Temporarily changing branch protection, deleting release artifacts, or asking
the provider to purge cached or hidden objects are separate external
mutations and require their own authority.

## Verify From The Remote

After publication, use a new independent clone—not the rewrite worktree—to:

- confirm the expected branch and tag object IDs;
- repeat history analysis;
- prove the unwanted content is absent from fetchable refs;
- inspect current trees and submodule references;
- run the project's required build and tests; and
- check that expected releases and integrations still resolve.

For private-data removal, complete the host's process for pull-request or
review refs, server garbage collection, forks, cached views, LFS objects,
release assets, CI artifacts, and support escalation. A successful branch
push alone is not proof of server-wide removal.

## Prevent Recontamination

The safest collaborator recovery is a fresh clone. An old clone can merge or
push the pre-rewrite history back into the cleaned repository. Tell clone
holders:

- stop pulls and pushes until cleanup is declared complete;
- re-clone rather than merge the unrelated histories;
- transplant unpublished patches only after reviewing their base and
  contents; and
- delete or isolate obsolete local tags and refs.

Record old-to-new commit mappings needed by issue trackers, submodules,
deployment records, or audit trails. Add project-owned prevention such as
artifact placement rules, staged-blob checks, reviewed Git LFS policy, and
secret scanning. Prevention does not retroactively validate the rewrite; keep
the incident and verification evidence.

## Review Checklist

- Was a credential revoked before history work?
- Is remote reachability proven rather than assumed from one checkout?
- Are all refs, hidden provider state, LFS objects, and artifacts accounted
  for?
- Is the rewrite performed in a disposable clone with a protected recovery
  path?
- Do filter reports and repeat analysis prove removal?
- Are tip-tree comparisons interpreted only as snapshot comparisons?
- Does every remote update name an exact ref and expected old OID?
- Was the published result independently cloned and verified?
- Can an old clone recontaminate the remote?

## Further Information

- `git-filter-repo`,
  [User Manual](https://github.com/newren/git-filter-repo/blob/main/Documentation/git-filter-repo.txt)
- Git,
  [`git push` Documentation](https://git-scm.com/docs/git-push)
- Git,
  [`git fast-export` Signature Behavior](https://git-scm.com/docs/git-fast-export)
- GitHub,
  [Removing Sensitive Data From A Repository](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)

Reviewed: 2026-07-23.
