# Changelog and History

## Purpose

Keep user-facing change history, operational traceability, and
version-control history distinct so each record can serve its audience.

## Record Roles

- A changelog explains notable delivered changes to users, operators, or
  downstream maintainers.
- Completed-task records explain what work was cleared and how.
- Proposal and decision records preserve why a direction was chosen.
- Bug records preserve symptoms, causes, and resolutions.
- Commit history records the exact repository changes.
- Temporary notes or commit-draft queues are not durable history.

Do not rely on one record to substitute for all the others.

## Changelog Practice

Maintain a top-level changelog when the project has durable release-facing or
operator-facing history needs.

Keep an unreleased section and use categories suited to the project, such as:

- Added;
- Changed;
- Fixed;
- Security;
- Deprecated; and
- Removed.

Write entries for the affected audience and describe impact, not internal file
churn. Link to migrations, compatibility notes, security advisories, or
decisions when readers need them.

## Preservation

- Append corrections and decisions rather than erasing earlier history.
- Keep timestamps in a documented, consistent form.
- Do not place secrets, private local context, or unnecessary client identity
  in durable records.
- Mark derived summaries as derived and keep their source records available.
- When a record is superseded, link old and new records in both directions
  when practical.

Automation may assist with history maintenance, but it must remain explicit,
reviewable, and owned by the consuming project or a separate verifier.
