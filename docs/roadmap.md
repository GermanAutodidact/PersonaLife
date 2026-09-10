# Roadmap and release readiness

[Deutsch](roadmap.de.md)

These are open directions, not promises of implemented features or delivery dates.

## Working developer baseline

Event-ledger persistence, daily life planning, occupation presets, travel, chat reconciliation, bounded state, persistent relationships, memory interfaces, CLI and local HTTP API have working implementations and automated tests. The demo illustrates a connected three-day life.

## Next engineering priorities

1. Longer randomized simulations and stricter invariants for every travel and scheduling transition.
2. Persisted replay checkpoints and repeatable load measurements for months of character history.
3. Additional conflict policies for missed obligations, infeasible routines and multi-activity goals.
4. More complete job and social-event variation with evidence-linked outcomes.
5. A small, end-to-end chat-host example with session expiry and grounded model responses.
6. Integration testing against optional providers, including retry/deduplication behavior.

## Before describing it as production-ready

Document operating limits, exercise migrations and recovery, test long-running service behavior, and validate at least one supported host integration end to end. Passing unit tests alone does not establish those properties.

## Public presentation and discovery

The English and German documentation explain intended users, concrete benefits, supported behavior and limits with equivalent coverage. Package metadata points to source, documentation and issues. Suggested GitHub About text and relevant topics are in `repository-metadata.json`; that file does not apply repository settings automatically.

Still useful for a public launch: apply About/topics, record a short real demonstration, publish an explicitly scoped release, and share it with relevant developer communities. A PyPI package, release announcement and dedicated demo website have not been published. Clear metadata improves classification and reader understanding; it cannot guarantee traffic, ranking or adoption.
