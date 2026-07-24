# Sandboxing Knacks

Sandboxing knacks describe practical process-isolation boundaries and their
failure modes.

- [Bubblewrap](bubblewrap.knack.md) covers Linux namespace construction,
  filesystem exposure, user and network choices, and diagnostic techniques.

A sandbox is a declared capability boundary, not a synonym for safety.
Document what remains shared, how identity and credentials are selected, and
which operations require explicit authority to cross the boundary.
