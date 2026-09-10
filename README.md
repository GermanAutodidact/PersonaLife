# PersonaLife — Persistent Life Simulation for AI Characters

**Give your AI characters a life between conversations.**

[![Tests](https://github.com/GermanAutodidact/PersonaLife/actions/workflows/tests.yml/badge.svg)](https://github.com/GermanAutodidact/PersonaLife/actions/workflows/tests.yml)
[Apache-2.0](LICENSE) · Python 3.11+ · Local-first · [Deutsch](README.de.md)

PersonaLife is an **open-source Python life simulation engine for LLM personas, AI companions and persistent NPCs**. It gives a character a job, daily routines, travel time, relationships and a continuing history—stored outside the language model.

When you return to a conversation, the character has a simulated day to draw from. When you stay and talk, that conversation takes time: shopping can move, cleaning can pause, and a work shift can start late. **What was planned and what actually happened in the simulation remain separate.**

Switch language models without starting the character's history over. The core runs locally with SQLite, needs no API key and makes no LLM calls. Optional adapters connect long-term memory and narrative providers.

[Run the three-day demo](#quick-start) · [Python / HTTP integration](docs/integrations.md) · [Architecture](docs/architecture.md) · [Contribute](CONTRIBUTING.md)

## A character's day can change because you were there

| Situation | PersonaLife records |
|---|---|
| Shopping was planned for 17:00; you chat from 16:30 to 18:15 | The conversation occupies that time; shopping moves and the reason is recorded. |
| Cleaning needs 60 minutes; the chat starts after 25 minutes | 25 minutes stay completed, with 35 minutes left to resume. |
| A shift starts at 17:00; your conversation ends at 16:55 with a 25-minute commute | Arrival is no earlier than 17:20. The character cannot teleport to work. |
| The program has been offline for six hours | Deterministic catch-up advances the simulated life when it returns. |
| You change the LLM provider | The same persona, relationships, timeline and memories remain available. |

This continuity gives a character something grounded to talk about: a work moment, an unfinished task, a changed plan or a shared conversation. Conversation hooks surface suitable topics without forcing one into every response.

## Built for developers of persistent characters

Use PersonaLife as the simulation layer in an AI companion, roleplay application, virtual-character experience or NPC prototype. A Python API and authenticated local HTTP API let your chat host supply session timing and retrieve bounded model context.

- **Daily life:** editable occupation presets, custom shifts, recurring routines, sleep and travel.
- **Continuity:** append-only event history, activity progress and persistent social relationships.
- **Chat-aware scheduling:** real session intervals interrupt activities and reshape future plans.
- **Memory:** local JSON or AiMemory, with optional Mem0 and Letta bridge interfaces.
- **Model choice:** OpenAI-compatible endpoints, LM Studio and Ollama for optional narrative rendering.

**Project status:** working developer baseline with automated tests, not a turnkey companion app or a production-certified service. No native ChatGPT/Gemini connection is installed automatically. All character experiences are fictional simulation. See the [tested behavior and limits](docs/validation.md) before integrating.

## Quick start

Python 3.11 or newer. Windows 11, Linux and macOS are supported by the code; local tests run on Linux/Python 3.12, with GitHub CI covering Windows and Linux on Python 3.11–3.13. Windows includes `tzdata` as a platform dependency.

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

## Questions developers ask

**Is this another chatbot or memory database?**  
PersonaLife supplies the state and simulated events a chatbot can talk about. Your host handles conversation and model access; an optional memory provider stores selected long-term records.

**Does it require a paid model or a constantly running agent?**  
The simulation needs neither. Use lazy catch-up or an inexpensive heartbeat. Optional external providers have their own requirements and costs.

**Can it connect directly to ChatGPT, Gemini or a game engine?**  
It provides Python and local HTTP interfaces for a host to integrate. Dedicated browser, mobile and game-engine connectors are not bundled.

**Will the persona always tell the truth about its simulated day?**  
The ledger separates plans from executed events and model output cannot rewrite it. A language model can still embellish its response; stronger output grounding belongs in the host.

**Where can I help?**  
Start with [CONTRIBUTING.md](CONTRIBUTING.md) and [the roadmap](docs/roadmap.md). Reproducible timeline bugs, integration examples and installation feedback are especially useful.

## License and source research

Apache-2.0. External implementation code was not incorporated into PersonaLife. AiMemory remains a separately installed dependency. The eight requested projects were inspected through current source files, license files and available tests; findings and deviations are in [research comparison](docs/research-comparison.md) and [THIRD_PARTY.md](THIRD_PARTY.md).
