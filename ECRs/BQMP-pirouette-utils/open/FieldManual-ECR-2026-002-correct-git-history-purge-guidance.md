# Engineering Change Request: Correct Git History Purge Guidance

- ECR ID: `FieldManual-ECR-2026-002`
- Request revision: 1
- Source project or origin namespace: FieldManual
- Target project: BQMP-pirouette-utils
- Target canonical locator:
  `https://github.com/BuildQM/BQMP-pirouette-utils`
- Target component, version, or revision:
  `knacks/git/purge-large-files-from-git-history.knack.md` at
  `c5cf9b625966781ff3a26273d6a17c2bd7df0bf7`
- Request owner: FieldManual maintainers
- Drafted: 2026-07-23
- Submitted: Not yet submitted
- Submitted-content digest: Not yet recorded
- Source lifecycle: Open
- Target handling status as reported: Not submitted
- Target intake ID or authoritative reference: None
- Sensitivity and reuse classification: Public, reusable version-control
  safety guidance
- Related, duplicate, or superseded ECR IDs: None
- Origin and provenance: FieldManual codebase knack assessment,
  FM-TASK-007

## Submitted Request

Freeze this section after first transport. Preserve a prior revision when a
material change must be resubmitted.

### Problem And Source Impact

The history-purge knack contains two unsafe conclusions in a workflow whose
purpose is destructive repository repair.

First, equal pre- and post-rewrite `HEAD^{tree}` values prove only that the
current tip snapshot is unchanged. A blob reachable solely from older commits
can be removed successfully while those tree identifiers remain equal.
Treating equality as proof that “nothing was removed” can reject a correct
repair or lead an operator to misunderstand the verification evidence.

Second, a generic `git push --force-with-lease --mirror` recipe is not a safe
publication plan. `--mirror` force-updates or deletes every mirrored ref, and
a lease without explicit expected object IDs can rely on stale or incomplete
remote-tracking information. The result can overwrite concurrent work or
mutate refs the operator never reviewed.

The source also needs explicit secret rotation, forge-hidden-ref and cache
handling, LFS consideration, and recontamination guidance.

### Requested Outcome

Correct the history-purge knack so it teaches an inspection-first,
exact-ref, independently verified repair workflow without presenting a broad
mirror push as a normal safe command.

### Acceptance Criteria

- Tip-tree comparison is described only as evidence that an intended current
  snapshot was preserved.
- Secret or credential exposure begins with revocation or rotation, before
  repository rewriting.
- Analysis and rewriting occur in separate disposable mirrors of the
  authoritative remote, with old ref names and object IDs recorded.
- Verification checks intended refs, removed paths or objects, filter-repo
  reports, tags, signatures, LFS state, submodules, and current snapshots as
  applicable.
- Publication re-reads remote object IDs immediately beforehand and uses
  explicitly reviewed refspecs with explicit expected-old-ID leases, or a
  provider-specific complete-ref runbook whose broader effects are stated.
- Hidden pull-request or merge-request refs, forge caches, branch protection,
  releases, and server-side garbage collection are addressed through the
  target provider's documented procedure.
- A fresh independent clone verifies the published result.
- Collaborators are told to re-clone or deliberately transplant unpublished
  work so an old clone cannot restore removed history.
- The document makes “no rewrite required” an acceptable outcome when the
  unwanted object is not reachable from relevant history.

### Non-Goals

- Remove history-repair guidance.
- Claim that one size threshold, forge workflow, or push shape fits every
  repository.
- Delete a remote, rewrite target history, or submit the ECR as part of this
  source-side draft.

### Constraints And Risks

History rewriting changes commit IDs and may invalidate signatures, tags,
open reviews, links, releases, caches, and collaborator clones. Backup
retention must follow incident policy; a backup containing a secret remains
sensitive. Provider-side hidden refs may require support or administrator
action.

### Evidence At Submission

- The target knack at the named revision.
- `git-filter-repo` documentation on fresh-clone safety, analysis, sensitive
  data removal, and rewrite reports.
- Git's `push` documentation for `--mirror`, explicit refspecs, and
  `--force-with-lease=<ref>:<expect>`.
- FieldManual's corrected history-repair knack created during the 2026-07-23
  codebase assessment.

## Source Tracking

After first transport, maintain this section as an append-only history.

### Local Mitigation

FieldManual imported the useful mental model and rewrote the workflow around
exact refs, explicit old object IDs, primary tool evidence, independent
verification, and collaborator coordination. It does not reproduce the unsafe
tip-tree conclusion or generic mirror-push recipe.

### Transport And Receipt Log

- 2026-07-23 — Drafted locally; not yet submitted.

### Discussion And Amendments

None.

### Target Disposition

No target disposition has been reported.

### Source Closure

Open.
