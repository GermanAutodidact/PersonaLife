# Memory integration

[Deutsch](memory.de.md)

PersonaLife keeps raw event history, daily closing projections and episodic story events. Selected day-closing candidates are exported to a separate long-term provider. Namespace: `personalife:<persona-id>`.

A record includes stable event ID, content, occurrence timestamp, kind, persona ID, date, importance, participants, location, source and confidence. Source/confidence describe the simulated evidence provenance; they do not assert that an event happened in the physical world.

## AiMemory (first supported external provider)

Install the user's AiMemory package in the same Python environment. `AiMemoryProvider` uses `aimemory.database.SQLiteMemoryStore.import_records(namespace, records)` and `search(namespace, query)` with `MemoryRecord.from_dict`. The actual current source was inspected and exercised in integration tests at commit `a5879350bc8d59eda08ad81da29eac6a0e32ceaa`.

Existing Windows database example: `C:\Users\elect\AppData\Local\AiMemory\memory.sqlite3`. Pass the local path from the machine running PersonaLife. PersonaLife here does not remotely access that Windows file.

## Local JSON

`JsonMemoryProvider(directory)` publishes one immutable event file at a time. Namespace and ID path components are hashed. An identical export is idempotent; conflicting data under an existing ID is rejected. No external dependency or network call is required.

## Failure/retry

Day closing commits before provider export. Export failures preserve canonical history and pending candidates. `flush_memories` retries pending candidates and appends a provider acknowledgement. AiMemory/JSON use stable IDs and tolerate a process crash after provider write but before ledger acknowledgement. Mem0 and a custom Letta bridge must provide their own deduplication policy for this crash window; exactly-once external delivery is not claimed for those optional adapters.

## Ranking, reflection and flashbacks

Importance, novelty, emotional intensity and social relevance determine tellability. Retrieval combines age decay with query-token relevance. Raw history is retained. Day reflection selects notable, evidence-linked descriptions; it does not ask an LLM to invent factual conclusions. Old events can resurface at a matching location/query through a rare seeded flashback opportunity. A host calls `mark_hook_used` to avoid repeated mentions.

## Optional providers

Mem0 accepts an injected configured client. `infer=False` avoids asking Mem0 to re-extract already-selected records. Letta accepts explicit `put_memory(namespace, record)` / `search_memory(namespace, query)` callables. This is intentionally a bridge, not a guessed legacy API: the current Letta repository is now a landing page with retired server code in `archive`.

German-generated memories remain German and English-generated memories remain English. User text is not automatically translated, and changing language does not rewrite existing memories.
