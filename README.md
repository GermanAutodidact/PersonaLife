# PersonaLife

PersonaLife gives an existing LLM / ChatGPT persona a continuous simulated life outside the LLM itself.

A local Python engine maintains an occupation, routines, locations, relationships, plans, executed activities and memories. Conversations occupy simulated time and change the remaining schedule. An append-only SQLite event ledger owns history; model-generated prose never changes it.

**This is fictional life simulation.** It does not assert that an AI has real-world experiences. A host chat application must call the integration API; installing this package alone does not connect ChatGPT or Gemini.

## Quick start

Python 3.11 or newer. Windows 11, Linux and macOS are supported by the code; the tests in this build were run on Linux/Python 3.12. Windows includes `tzdata` as a platform dependency.

```powershell
# In the downloaded/cloned PersonaLife directory
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install .
.\.venv\Scripts\personalife.exe --db life.sqlite3 persona create --file examples/jenna.json --start 2026-09-08T00:00:00+02:00
.\.venv\Scripts\personalife.exe --db life.sqlite3 advance jenna --to 2026-09-08T09:00:00+02:00
.\.venv\Scripts\personalife.exe --db life.sqlite3 context jenna
```

On Linux/macOS use `python3`, `.venv/bin/python` and `.venv/bin/personalife`. From the repository root, `python -m personalife` also runs without installing the package on systems with timezone data.

For an actual new persona, omit `--start` to initialize at the current time. A historical start is useful for simulation and examples. All date/time arguments must contain a UTC offset.

Run the connected three-day example:

```sh
python examples/three_days.py --output demo-output
python -m unittest discover -s tests -v
```

The example produces a SQLite database, original/current plans, actual timelines, daily stories, persistent memory records, relationship history and a validation report. Committed example output is under `examples/generated/`; its binary database and private memory files are excluded from Git.

## What is implemented

- Transactional append-only ledger, hash-chain verification and rebuildable projections.
- Original plan, current plan and executed timeline kept separately.
- Civil-day planning, overnight shifts, DST-aware boundaries and explicit travel.
- Ten editable occupation presets, custom weekly schedules, date-specific shifts, vacation/sick/off exceptions, work breaks and deterministic optional overtime.
- Daily/weekday/weekend/weekly/monthly/custom-date routines, hard commitments and priority-based conflict resolution.
- Activity progression, pause/resume, completed/cancelled states and late-obligation events.
- Live start/end chat hooks and atomic bounded chat import with idempotency checks.
- Persistent mood, energy, fatigue, stress, hunger, social energy and recurring relationships.
- Seeded narrative events, tellability ranking, consumed-hook tracking and rare contextual flashback candidates.
- Day closing, evidence-linked reflection, unfinished-task carryover and retryable long-term-memory export.
- AiMemory integration, local JSON memory, optional Mem0 client adapter and explicit Letta bridge contract.
- OpenAI-compatible narrative provider, LM Studio and Ollama adapters. Core operation makes no LLM requests.
- CLI, authenticated loopback HTTP API, heartbeat, SQLite backup, examples and consistency tests.

## Creating and configuring a persona

```sh
personalife presets
personalife persona create
personalife persona create --name Jenna --id jenna --occupation bartender
personalife persona create --file examples/jenna.json
```

Interactive setup offers occupation selection and primary fields. JSON/API setup exposes the full profile including employer, locations, home, schedules, coworkers, friends, hobbies, routines and transport. `examples/jenna.json` is a complete editable profile. IDs are persistent references; coworkers must reference entries in `relationships`.

See [occupation engine](docs/occupation-engine.md) for custom jobs and [architecture](docs/architecture.md) for ownership boundaries.

## Conversations change the day

```python
from personalife import PersonaLife

with PersonaLife('life.sqlite3') as life:
    life.start_chat_event('jenna', '2026-09-08T16:20:00+02:00', 'session-1')
    # The host supplies actual session timing. Repeated user/assistant turns
    # remain within this session; heartbeat may continue to advance its time.
    life.end_chat_event('jenna', '2026-09-08T16:55:00+02:00',
                        'We talked before my shift.', 'session-1')
    context = life.get_persona_context('jenna')
```

A 25-minute commute means arriving no earlier than 17:20 after this chat. The original 17:00 work start remains auditable. A completed 25 minutes of a 60-minute task leaves 35 minutes to resume.

For a fully recorded session, `apply_chat_event(persona_id, start_time, end_time, summary, metadata=None)` runs atomically. Pass `metadata={"idempotency_key": "stable-host-session-id"}` for safe retries. Past intervals already processed as canonical cannot be silently replaced by a newly submitted chat. See [chat reconciliation](docs/chat-reconciliation.md).

## API and continuous time

Set `PERSONALIFE_API_TOKEN` to a private random value, then:

```sh
personalife --db life.sqlite3 serve --port 8787
personalife --db life.sqlite3 heartbeat --minutes 15
```

API requests require `Authorization: Bearer <token>`. The API listens on loopback and refuses browser cross-origin calls. No public service is deployed. `heartbeat --once` catches up and closes elapsed days. Host applications can call `advance_to()` lazily before context retrieval instead of running a daemon. An unfinished chat remains open until the host ends it; idle-time policy belongs to the host.

Endpoint examples and integration responsibilities are in [integrations](docs/integrations.md).

## Memory and narrative providers

```python
from personalife import PersonaLife, AiMemoryProvider
memory = AiMemoryProvider('/path/to/AiMemory/memory.sqlite3')
with PersonaLife('life.sqlite3', memory=memory) as life:
    life.flush_memories('jenna')
memory.close()
```

Install your existing AiMemory package into the same environment first. PersonaLife uses its real `SQLiteMemoryStore` and `MemoryRecord` interfaces. The namespace is `personalife:<persona_id>`. See [memory](docs/memory.md).

```python
from personalife.llm import LMStudio
text = LMStudio('your-loaded-model').narrate(context)
```

Provider calls are opt-in and only generate presentation text. No paid provider, API key or model is required for the simulation. Optional integrations may have their own service costs.

## Verification and limits

`personalife validate jenna` verifies ledger integrity, actual overlaps, location continuity, progress and chat duration. The test suite covers the required chat/work/shopping/cleaning scenarios, restart catch-up, three-day relationships, immutable history, timezone errors, DST, API authorization and actual AiMemory import/retrieval. See [validation report](docs/validation.md).

The API/CLI form a usable engine, not an installed ChatGPT connector or graphical app. Mem0 is tested at its adapter boundary, not against a live account. Letta is an injected bridge because its current main repository no longer contains the supported server. Generated prose remains untrusted presentation, not canonical truth. Replay currently favors auditability over large-scale throughput; there is no production load certification. Detailed behavioral limits and extension points are documented under [architecture](docs/architecture.md).

## License and source research

Apache-2.0. External implementation code was not incorporated into PersonaLife. AiMemory remains a separately installed dependency. The eight requested projects were inspected through current source files, license files and available tests; findings and deviations are in [research comparison](docs/research-comparison.md) and [THIRD_PARTY.md](THIRD_PARTY.md).
