# Source research comparison

Inspected 2026-09-10 through the connected GitHub source API. The source-evidence JSON records repository commits and blob hashes for inspected license, implementation and test files. Inspection was targeted, not a full security audit or execution of every upstream test suite. PersonaLife's implementation is independently authored; no upstream implementation files are included.

| Repository | Actual inspected modules/tests | Useful idea | Observed license | Decision |
|---|---|---|---|---|
| [Crescent Grove](https://github.com/Canon-73/crescent-grove) | `core/scheduler.py`, `memory/manager.py`, `tests/test_moontide_v2.py` | Moonbeat manages periodic pulses, schedule intervals and extension state; workspace memory is separate from scheduling | MIT | Independent heartbeat and persistent bounded state. Do not mistake the inspected file manager for a complete LETHE implementation. |
| [Yuralume](https://github.com/Yuralume/yuralume-core) | `domain/entities/schedule.py`, `application/services/schedule_service.py`, `tests/unit/test_post_turn_schedule_adjustments.py` under `src/kokoro_link` | Civil-day schedule with UTC activity boundaries; idempotent lazy generation, historical context protection and post-turn adjustments | BUSL-1.1, including its actual additional-use terms | Architecture reference only. Independently implemented reconciliation and canonical-history protection. |
| [Horde Studio](https://github.com/ddkhan24/hordestudio) | `vh-simulation-core.js`, `scratch/living_world_stress_test.js` | Attention gate uses capacity/willingness/interruptibility; procedural progression preserves progress across ticks | No repository-level license file found in inspected tree | No copied source. Independent remaining-work and transit-resume logic. |
| [HerAndHim](https://github.com/ericwang915/HerAndHim) | `herandhim/scheduler/planner.py`, `tests/test_persistence.py` | Persona/job/habit/date context shapes a daily plan; inspected planner writes a current plan into context | AGPL-3.0 | No copied source. Use occupation-aware planning, but canonical history is an event ledger rather than only a current Markdown plan. |
| [Generative Agents](https://github.com/joonspk-research/generative_agents) | `reverie/backend_server/persona/cognitive_modules/plan.py`, `retrieve.py`, `reflect.py` | Retrieval separates recency, importance and embedding relevance; reflection uses selected evidence | Apache-2.0 | Independent lexical/age/importance ranking and extractive evidence-linked reflection; embeddings remain optional future work. |
| [Mem0](https://github.com/mem0ai/mem0) | `mem0/memory/main.py`, `tests/memory/test_session_scope.py` | Explicit scoped add/search API, metadata and optional inference | Apache-2.0 | Optional injected-client adapter. No compulsory SDK, vectors or cloud dependency. |
| [Letta](https://github.com/letta-ai/letta) | Current `README.md`, `LICENSE`, repository tree | Model-independent state remains a useful architectural boundary | Apache-2.0 file remains in main | **Current main is a landing page, not the earlier server.** README points to retired `archive`; no current server/tests were present to inspect. Provide an explicit bridge rather than pretend a supported legacy API was verified. |
| [AiMemory](https://github.com/hypnosisforcedsissy-bot/AiMemory) | `src/aimemory/database.py`, `models.py`, `store.py`, `tests/test_store.py`, packaging metadata | Transactional namespace-scoped immutable records, collision handling and context/search | Apache-2.0 | First external memory provider; exercised against fetched actual source. PersonaLife's ledger remains authoritative. |

## Architecture decisions

1. Preserve intention and execution independently. A future plan never proves completion.
2. Make chat duration part of the same exclusive actual timeline as physical activities.
3. Use deterministic interval arithmetic; reserve language models for rendering and later narrative extensions.
4. Generate memory candidates from confirmed simulated event boundaries; export after canonical commit.
5. Use stable persona/location/NPC IDs across providers and sessions.
6. Use explicit routes, remaining-work progress and late-obligation events rather than silently repairing reality.

## Verification caveats

The large Generative Agents recursive tree response was truncated; its `reverie/backend_server` subtree was fetched separately before reading cognitive modules. Letta's actual main-branch status differs materially from the supplied brief. The research does not claim that all requested upstream concepts were present in the inspected files, and no unsupported assumption was needed to run the implemented core.
