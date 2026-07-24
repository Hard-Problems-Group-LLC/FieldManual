# Authentication Knacks

Authentication knacks cover practical identity, credential-selection, and
trust-boundary problems.

- [GitHub SSH multi-organization sanity](GitHub-SSH-multi-org-sanity.knack.md)
  explains how to keep repository identity, SSH routing, and authorization
  aligned when several GitHub organizations or accounts are in use.

Never infer the active authorization context from a username, process
environment, or successful connection alone. Verify the identity and target
that will actually receive the operation.
