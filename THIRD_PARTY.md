# Third-party sources and attribution

[Deutsch](THIRD_PARTY.de.md)

PersonaLife implementation code is independently authored and released under Apache-2.0. No implementation code from the research repositories is copied or vendored. Source URLs, inspected paths and hashes appear in `docs/research-comparison.md` and `docs/source-evidence.json`.

| Project | Observed license | Usage | Attribution / distribution decision |
|---|---|---|---|
| Canon-73/crescent-grove | MIT | Heartbeat/state-continuity reference | Named research attribution; no copied code |
| Yuralume/yuralume-core | BUSL-1.1 | Schedule/post-turn architecture reference | No copied code; no claim that BUSL grants unrestricted open-source reuse |
| ddkhan24/hordestudio | No clear root license found | Activity/attention/progress behavior reference | No copied code |
| ericwang915/HerAndHim | AGPL-3.0 | Occupation/date-aware daily planning reference | No copied code or linking dependency |
| joonspk-research/generative_agents | Apache-2.0 | Recency/importance/relevance/reflection concepts | Named research attribution; no copied code |
| mem0ai/mem0 | Apache-2.0 | Optional externally supplied client adapter | SDK is not distributed in this repository |
| letta-ai/letta | Apache-2.0 in current main | Stateful-agent concept; optional caller-provided bridge | Retired implementation is not included |
| hypnosisforcedsissy-bot/AiMemory | Apache-2.0 | Optional installed memory provider; actual API integration tests | Package remains separately installed; no vendored implementation |

Python standard library components retain their own licenses. Windows installation may install the separately distributed `tzdata` package for IANA timezone data. The included Apache-2.0 license text is the standard license, not an imported implementation.

The original English LICENSE remains unchanged and authoritative; the German companion page explains attribution.
