# Architecture

## Ownership

`ledger.py` owns the canonical SQLite event log. `projections.py` reconstructs persona state, plans, actual segments, chat sessions, relationships, stories and memory exports from it. `service.py` exposes transaction boundaries. No model provider writes to the ledger.

`planner.py` performs civil-day planning, occupation expansion, recurrence checks and routing. `cognition.py` applies bounded state rates and ranks events. `memory.py` implements long-term adapters. `llm.py` renders optional prose. `api.py`, `cli.py` and `heartbeat.py` are host interfaces.

The logical direction is ledger → executed life → state → memory → model context → response. A plan event records an intention. An execution segment records simulated elapsed work. A future story cannot create an execution segment.

## Storage and concurrency

SQLite WAL, a 30-second busy timeout and `BEGIN IMMEDIATE` serialize command writers. Each API request opens its own connection. Do not share a PersonaLife instance between threads. Database triggers prohibit normal SQL UPDATE/DELETE on canonical events. SHA-256 hashes chain all events. A database owner could remove triggers and rebuild hashes; this is audit/integrity protection, not cryptographic external attestation.

The schema is versioned at 1 and unknown versions are refused. Named application models are ledger projections rather than separate writable tables. `backup()` uses SQLite's backup API. Do not copy an active `.sqlite3` file without its WAL; use the backup command.

Per-persona snapshots are currently cached in memory and invalidated by the ledger tip. They are not authoritative. New events are replayed incrementally after validating the cached ledger anchor. Rollbacks and changed anchors force a full rebuild, and sequence bounds keep each read consistent with its observed tip. Public results are defensive copies. Large histories should still gain persisted checkpoint projections before high-volume production use. There are no cloud services, permanent model loops, Kubernetes components or required embeddings.

## Planning/execution

A day is the half-open interval from local midnight to next local midnight. Night shifts may span that boundary as one continuous sequence. Work tasks and breaks are separate activities. Missing routes raise errors. Remote occupations use the home location and zero commute.

Original activities never change. `ACTIVITY_CHANGED` updates only the derived current activity. An activity has required seconds and actual progress seconds; rescheduling preserves their difference. A journey interrupted in transit resumes its remaining duration. Lateness is recorded explicitly, and fixed appointments can become late when a real recorded chat prevents arrival.

Ordinary free-time blocks may be cancelled during reconciliation. Gaps execute as free time at the actual current location. Hard commitments are scheduled before soft activities; route insertion may subsequently delay them. This is an explainable deterministic policy, not a global schedule optimizer.

## Extensibility and current scope

- Jobs are data templates with generic task labels and coworker references. Exception entries support leave, home office, custom shifts and irregular freelance/student work. Optional overtime is seeded per date.
- Social events update named relationships. NPC availability/location/occupation fields are retained, but there is no independent continuously simulated schedule for every NPC.
- Activity goals may be tagged in routine configuration. Progress is tracked per activity; an independent multi-activity goal/deadline optimizer is not implemented.
- State is lightweight simulation, not a clinical model. No weather network service is configured; a host may supply environmental context in persona traits and use a custom planner extension.
- Flashbacks are evidence-linked candidates, not claims of new events. Reflection is a deterministic extractive summary; it does not infer new canon.
- Memory ranking decays with age without deleting history. Automatic lossy archival compression is not implemented.
- Historical imported conversations are rejected after canonical time passed their start. An explicit audited revision system is a separate future extension, not an automatic rewrite.
- All activity state names are validated. The standard engine uses planned/active/paused/completed/cancelled. Specialized blocked/missed/abandoned policies need a host extension; generic lateness uses `OBLIGATION_LATE`.

These are explicit functional boundaries, not hidden placeholder implementations. The repository is an executable baseline; it is not a claim that every aspirational feature in the initial brief has been production-certified.
