# Anwendungsintegration und öffentliche API

[English](integrations.md)

Der Simulationskern enthält keinen anbieterspezifischen Code. Eine Chat-Anwendung kann das LLM wechseln und dabei dieselbe SQLite-Datenbank sowie Persona-Kennung weiterverwenden. ChatGPT und Gemini im Browser oder auf dem Telefon erhalten nicht allein durch die Installation Zugriff. Eine eigene Anwendung oder ein passend eingerichteter Connector muss die API aufrufen und den Kontext einfügen.

## Typischer Ablauf

1. Eine Persona aus einem vollständigen JSON-Profil mit Berufsvorlage oder eigenem Beruf anlegen.
2. Vor einem Gespräch eine stabile Sitzung zum tatsächlichen Beginn starten.
3. Begrenzten Persona-Kontext abrufen und als gekennzeichnete Simulationsdaten an das Modell geben.
4. Die Sitzung über mehrere Nachrichten offen halten und bei tatsächlichem Ende der Text- oder Sprachsitzung schließen.
5. Einen Gesprächsanlass als verwendet markieren, wenn das Modell ihn erwähnt hat.
6. Verstrichene Zeit nachholen und vergangene Tage per Heartbeat oder Anwendungsaufruf abschließen.

## HTTP

Basisadresse: `http://127.0.0.1:8787/v1`. Alle Endpunkte benötigen `Authorization: Bearer <PERSONALIFE_API_TOKEN>`. Anfragen verwenden JSON; die Grenze beträgt 1 MB. Öffentliches Lauschen und Browser-Anfragen anderer Herkunft sind deaktiviert.

| Methode / Pfad | Inhalt oder Abfrage |
|---|---|
| GET `/presets` | Zuordnung der Berufsvorlagen |
| POST `/personas` | `profile`, `start_time` |
| GET `/personas/{id}/state` | Aktuell verarbeiteter Zustand |
| GET `/personas/{id}/context` | Begrenzter modellgeeigneter Kontext |
| GET `/personas/{id}/hooks` | Erzählbare Ereignisse und gekennzeichnete zukünftige Pläne |
| GET `/personas/{id}/actual` | Ausgeführte Abschnitte |
| GET `/personas/{id}/plan` | Optional `original=true` |
| GET `/personas/{id}/day` | `date=YYYY-MM-DD` |
| GET `/personas/{id}/relationships` | Dauerhafte NPC-Beziehungen |
| GET `/personas/{id}/memories` | Optional `q` |
| GET `/personas/{id}/validate` | Konsistenzbericht |
| POST `/personas/{id}/advance` | `now` |
| POST `/personas/{id}/plan` | `date` |
| POST `/personas/{id}/update` | `changes` |
| POST `/personas/{id}/occupation` | `occupation` |
| POST `/personas/{id}/routine` | `routine` |
| POST `/personas/{id}/activity` | `title`, `start`, `end`, `location`, optional priority/kind/key |
| POST `/personas/{id}/reschedule` | `activity_id`, `start_time`, `reason` |
| POST `/personas/{id}/chat-start` | `start_time`, `chat_id`, optionale metadata |
| POST `/personas/{id}/chat-end` | `end_time`, `summary`, `chat_id` |
| POST `/personas/{id}/chat` | `start_time`, `end_time`, `summary`, optionale metadata |
| POST `/personas/{id}/close-day` | `date` |
| POST `/personas/{id}/hook-used` | `event_id` |

GET-Abfragen verändern die festgeschriebene Zeit nicht. Außerhalb einer laufenden Sitzung wird vor einer Abfrage ausdrücklich POST advance aufgerufen. In Python kann `get_persona_context(..., now=...)` beide Schritte verbinden.

## Sprache

`Accept-Language: de` beziehungsweise `en` wählt die Sprache eigener API-Fehlermeldungen und der Berufsvorlagen. Varianten wie `de-DE` und Qualitätsgewichte werden berücksichtigt. Bei einer neuen Persona gilt die gewählte Sprache, falls `profile.language` nicht ausdrücklich gesetzt wurde. Bereits gespeicherte Texte behalten ihre ursprüngliche Sprache. JSON-Schlüssel, Endpunkte und Zustandskennungen bleiben gleich. Mehr dazu unter [Sprachen](languages.de.md).

## Python-Modelladapter

`OpenAICompatible(base_url, model, api_key='', timeout=30)` verwendet `/chat/completions`. LM Studio nutzt standardmäßig `http://localhost:1234/v1`, Ollama `http://localhost:11434/v1`. OpenRouter und andere Anbieter können ihre kompatible HTTPS-Basisadresse angeben. Zugangsdaten gehören in die aufrufende Anwendung oder Umgebung, nicht in Persona-JSON oder das Repository.

`narrate(context)` liefert ausschließlich Anzeigetext. Es ist keine Faktenprüfung und wird nie als maßgebliche Historie zurückgeschrieben. `context.language` bestimmt die angeforderte Antwortsprache. Ein Modell kann seine Antwort trotzdem ausschmücken; die strukturierte Zeitleiste sollte zugänglich bleiben. Für stärkere Garantien ist eine zusätzliche Prüfung durch die aufrufende Anwendung nötig.
