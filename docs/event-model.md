# Canonical event model

[Deutsch](event-model.de.md)

Each row contains sequence, globally unique event ID, persona ID, UTC occurrence time, kind, JSON data, predecessor hash and hash. Commands append atomically. Ordering is by sequence; timestamps describe simulated time.

| Event | Meaning |
|---|---|
| PERSONA_CREATED / PERSONA_UPDATED | Validated profile and future configuration |
| DAY_PLANNED | Idempotent civil-date planning marker |
| ACTIVITY_PLANNED | Original intended activity, required work and location |
| ACTIVITY_CHANGED | Explicit future/progress-state revision with reason |
| ACTUAL_SEGMENT | Executed half-open time interval, before/after location, bounded state |
| CLOCK_ADVANCED | Canonical processed-time watermark |
| CHAT_STARTED / CHAT_ENDED | Persistent live session and recorded summary |
| CONFLICT_RESOLVED | Why future work and routes were adjusted |
| OBLIGATION_LATE | Planned start, expected arrival and reason |
| STORY_EVENT | Evidence-linked event produced at an execution/chat boundary |
| HOOK_USED | The host already mentioned this event |
| DAY_CLOSED | Daily story, reflection, open tasks and memory candidates |
| MEMORY_EXPORTED | A provider acknowledged a stable memory event ID |

Execution progress is the sum of actual segment durations for an activity. A plan itself contributes zero progress. Closing a day does not claim its unfinished activities completed. Live chat segments occupy their interval exclusively, including across midnight.

Timestamps are normalized to UTC at boundaries. Civil recurrence uses `zoneinfo`. Ambiguous fall-back times use fold 0 unless explicitly specified through `clock.civil`; nonexistent spring-forward times are rejected. Callers can use an explicit offset for either occurrence of an ambiguous local timestamp.

Use public application methods to mutate the simulation. Direct `Ledger.append` is an internal primitive requiring an explicit transaction; it is not exposed by the HTTP API. Model replies cannot call it.
