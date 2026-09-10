# Contributing to PersonaLife

[Deutsch](CONTRIBUTING.de.md)

Help make persistent AI characters more consistent, explainable and easier to integrate.

## Useful contributions

- A reproducible timeline contradiction with timestamps, timezone and a minimal synthetic persona.
- Tests for interruption, travel, overnight work, recurrence and restart behavior.
- Small host-integration examples using the public Python or HTTP API.
- Installation feedback from Windows, Linux or macOS.
- Clear documentation and accessibility improvements.

Read the architecture and roadmap before larger changes. Keep simulation arithmetic deterministic and model-independent. New prose must not silently become canonical history. Every change to future plans needs an explicit reason; executed progress must survive interruptions.

## Development

```sh
python -m venv .venv
# Activate the environment, then:
python -m pip install -e .
python -m unittest discover -s tests -v
python examples/three_days.py --output demo-output
```

AiMemory's real integration test runs when that optional package is installed; otherwise it is explicitly skipped. Tests should not require paid providers or private accounts.

Submit a pull request explaining the problem, behavior change and relevant test evidence. Use synthetic data in reports; do not include API keys, private chats or personal memory databases. Discuss substantive new dependencies and architecture changes before investing in them. No response-time commitment or support SLA is offered.

## Maintain both languages

Changes to a public Markdown guide must be reflected in its paired translation. Keep technical identifiers and commands stable. Put application-owned presentation strings in `personalife/i18n.py`. Language tests check document pairs, links and runtime behavior.
