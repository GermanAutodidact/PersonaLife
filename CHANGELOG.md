# Changelog

[Deutsch](CHANGELOG.de.md)

## 1.1.0 — 2026-09-10

- Provide equivalent English/German READMEs and complete translated public guides with language links.
- Prepare English, German and combined repository descriptions with shared topics and package links.
- Add `--language`, `--sprache` and `PERSONALIFE_LANGUAGE` for CLI help, setup and application-owned errors.
- Store persona language for localized preset examples, generated activities, stories, conversation hooks and model context.
- Localize API errors/presets through `Accept-Language`, keeping schema keys and commands stable.
- Add English/German three-day examples, installer messages and localization tests.
- Preserve existing history and custom text; retain external technical diagnostics when needed.

## 1.0.1 — 2026-09-10

- Reject duplicate routine IDs, invalid shift exceptions, unknown route endpoints, invalid recurrence values, missing participants and invalid overtime settings before saving a profile.
- Apply updated contact names and metadata while preserving learned relationship strength and shared history.
- Replay only newly appended events when the cached ledger anchor is valid. Rebuild after rollbacks and protect cached state from external mutation.
- Add regression tests for input validation, contact updates, incremental/full replay equivalence and rollback recovery.
- Improve the public README, add a German introduction, contributor guidance, a scoped roadmap and suggested GitHub metadata.

## 1.0.0 — 2026-09-10

Initial executable baseline: event-sourced simulation, occupation/routine planning, travel, chat reconciliation, memory/provider interfaces, CLI, local API, tests and three-day examples.
