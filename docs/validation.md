# Validation report

[Deutsch](validation.de.md)

Executed in this build: Linux, Python 3.12, 2026-09-10.

- **67 automated tests passed** in the final local run. Full output is in `test-results.txt`. The wheel also built and installed successfully in an isolated target directory, and its CLI started.
- AiMemory round-trip used the actual fetched `database.py` / `models.py` from its current repository. The ordinary test suite skips this optional external integration when AiMemory is not installed.
- All ten occupation presets passed seven simulated days each with a daily 10:25–12:10 chat and a consistency check after every day.
- Three-day Jenna example: 319 ledger events, 54 executed segments and 11 exported selected memories in the generated example run.
- Original plans remain available after rescheduling; daily examples include relationships and context from the next day.

## 1.1.0 bilingual verification

Seventeen language tests cover English/German CLI help and setup, translated domain errors, environment/default handling, stable preset IDs, locale-aware API responses, requested LLM language and unchanged simulation timing/progress across languages. The suite also checks all public guide pairs and local links, repository descriptions, static application error catalog coverage, unsupported languages and preservation of historical/user text.

Both language versions of the three-day demo produced 319 events, 54 actual segments and 11 selected memories. Default/generated labels and narrative text differ by language; canonical identifiers and time/state calculations stay stable. Updated JSON/Markdown examples are committed in both languages.

Third-party diagnostics, source-code identifiers and the original Apache license are deliberately not translated. GitHub has one About field: the prepared metadata offers English, German and combined text; actual repository settings are not changed by saving that file.

## 1.0.1 hardening checks

The additional tests first reproduced invalid-profile acceptance, stale contact metadata and unnecessary full-history replay. The fixes reject invalid input before persistence, preserve learned relationship history during metadata updates, and compare incremental projections against complete replay including rollback recovery.

A 30-day simulation with a daily 10:25–12:10 conversation passed a consistency check after every day: 3,084 events, 503 actual segments and 517 activity records. It took 16.661 seconds on this execution environment; this single measurement is not a throughput guarantee.

A seven-day catch-up measured 1.380 seconds before and 0.670 seconds after incremental replay in single local runs. Workload and event count were unchanged (606 events). The regression test verifies that an appended hook event processes only that new event, rather than relying on a fragile timing threshold.

The 1.0.1 wheel built successfully without network access. README local links and the suggested 164-character description / 16 topic names were validated. GitHub About settings still need to be applied by a repository administrator; storing the metadata JSON does not change those settings.

## Tested adversarial cases

| Risk | Verification |
|---|---|
| Conversation overlaps shopping | Shopping is postponed; actual chat occupies its interval |
| Chat before work | Commute still consumes 25 minutes; lateness is explicit |
| Lost interrupted work | 25 of 60 minutes completed leaves 35 minutes |
| Mid-journey interruption | Remaining route resumes without teleportation |
| Offline restart | Six-hour catch-up persists, then repeated advance is idempotent |
| Multiple sessions / duplicates | Concurrent open chats rejected; stable retries deduplicated; key collisions rejected |
| Canonical rewrite | SQL update/delete triggers reject ordinary mutation; hash chain verifies |
| Plan asserted as completion | Planning alone creates zero actual progress |
| Invalid time | Naive timestamps, negative durations and nonexistent civil times rejected |
| DST | Spring day 23 hours, autumn day 25 hours; repeated local time folds differ by one hour |
| Wrong place | Unknown locations and missing routes rejected; actual location continuity checked |
| Memory contamination | Separate namespaces; immutable local memory IDs |
| Model access | Narrative adapters do not expose ledger mutation |
| API access | Token required; arbitrary internal method dispatch refused |
| Oversized context | Bounded response under configured context budget |

## What this does not certify

This is not an external penetration test, formal proof, medical simulation validation or production load certification. Live Mem0/Letta/OpenAI accounts were not used. Windows/macOS were not locally available for execution. The committed CI workflow requests Windows and Linux runs; inspect GitHub Actions for their eventual result instead of treating the configuration itself as a passing run.

Provider output grounding is a host-level presentation concern. Core invariants prevent prose from automatically rewriting the timeline; they cannot guarantee that a language model never embellishes a sentence.
