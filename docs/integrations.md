# Host integrations and public API

[Deutsch](integrations.de.md)

No provider-specific code exists in the simulation core. A chat host can switch LLMs while continuing to use the same SQLite database and persona ID. ChatGPT/Gemini browser or phone applications do not gain access merely by installing this package. Use a host you control or an appropriately configured connector to call the API and inject context.

## Typical host lifecycle

1. Initialize a persona from a full JSON profile, choosing a job preset or custom occupation.
2. Before a live conversation, start a stable session at the actual start timestamp.
3. Fetch bounded persona context and include it as labeled simulation data.
4. Keep the session open across turns; record its end once the voice/text session actually ends.
5. Mark a hook used if the model mentioned it.
6. Catch up and close elapsed days through heartbeat or application calls.

## HTTP

Base: `http://127.0.0.1:8787/v1`. All routes require `Authorization: Bearer <PERSONALIFE_API_TOKEN>`. Use JSON request bodies. Limit: 1 MB. No remote binding or browser cross-origin access is enabled.

| Method / path | Payload or query |
|---|---|
| GET `/presets` | occupation template mapping |
| POST `/personas` | `profile`, `start_time` |
| GET `/personas/{id}/state` | current processed state |
| GET `/personas/{id}/context` | bounded model-ready context |
| GET `/personas/{id}/hooks` | tellable actual events and labeled future plans |
| GET `/personas/{id}/actual` | executed segments |
| GET `/personas/{id}/plan` | `original=true` optional |
| GET `/personas/{id}/day` | `date=YYYY-MM-DD` |
| GET `/personas/{id}/relationships` | persistent NPC relationships |
| GET `/personas/{id}/memories` | `q` optional |
| GET `/personas/{id}/validate` | consistency report |
| POST `/personas/{id}/advance` | `now` |
| POST `/personas/{id}/plan` | `date` |
| POST `/personas/{id}/update` | `changes` |
| POST `/personas/{id}/occupation` | `occupation` |
| POST `/personas/{id}/routine` | `routine` |
| POST `/personas/{id}/activity` | `title`, `start`, `end`, `location`, optional priority/kind/key |
| POST `/personas/{id}/reschedule` | `activity_id`, `start_time`, `reason` |
| POST `/personas/{id}/chat-start` | `start_time`, `chat_id`, optional metadata |
| POST `/personas/{id}/chat-end` | `end_time`, `summary`, `chat_id` |
| POST `/personas/{id}/chat` | `start_time`, `end_time`, `summary`, optional metadata |
| POST `/personas/{id}/close-day` | `date` |
| POST `/personas/{id}/hook-used` | `event_id` |

GET reads do not advance canonical time. Explicitly POST advance before a read outside a live session. Python `get_persona_context(..., now=...)` can combine those operations.

## Language

`Accept-Language: de` or `en` selects API errors and occupation preset labels. Regional variants and quality weights are supported. New personas inherit the requested language when `profile.language` is omitted. Already stored text is returned as recorded. JSON keys, routes and state IDs stay stable. See [languages](languages.md).

## Python model adapters

`OpenAICompatible(base_url, model, api_key='', timeout=30)` targets `/chat/completions`. LM Studio defaults to `http://localhost:1234/v1`; Ollama to `http://localhost:11434/v1`. OpenRouter or other providers can supply their compatible HTTPS base URL. Credentials belong in the caller/environment, never in persona JSON or the Git repository.

`narrate(context)` returns display prose only and requests the language in `context.language`. It is not fact validation and is never written back as canonical history. A model can still embellish its response; keep the structured timeline available to users and implement a host-side grounding check if stronger presentation guarantees are needed.
