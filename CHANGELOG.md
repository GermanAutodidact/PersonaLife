# Changelog

## 1.0.1 — 2026-09-10

- Reject duplicate routine IDs, invalid shift exceptions, unknown route endpoints, invalid recurrence values, missing participants and invalid overtime settings before saving a profile.
- Apply updated contact names and metadata while preserving learned relationship strength and shared history.
- Replay only newly appended events when the cached ledger anchor is valid. Rebuild after rollbacks and protect cached state from external mutation.
- Add regression tests for input validation, contact updates, incremental/full replay equivalence and rollback recovery.
- Improve the public README, add a German introduction, contributor guidance, a scoped roadmap and suggested GitHub metadata.

## 1.0.0 — 2026-09-10

Initial executable baseline: event-sourced simulation, occupation/routine planning, travel, chat reconciliation, memory/provider interfaces, CLI, local API, tests and three-day examples.
