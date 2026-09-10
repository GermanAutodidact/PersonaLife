# PersonaLife — Fortlaufende Lebenssimulation für KI-Charaktere

**Gib deinen KI-Charakteren einen Alltag zwischen den Gesprächen.**

[![Tests](https://github.com/GermanAutodidact/PersonaLife/actions/workflows/tests.yml/badge.svg)](https://github.com/GermanAutodidact/PersonaLife/actions/workflows/tests.yml)
[Apache-2.0](LICENSE) · Python 3.11+ · Lokal nutzbar · [English](README.md)

PersonaLife ist eine **quelloffene Python-Engine zur Lebenssimulation für LLM-Personas, KI-Begleiter und dauerhafte NPCs**. Ein Charakter bekommt einen Beruf, Routinen, Reisezeiten, Beziehungen und eine fortlaufende Geschichte – gespeichert außerhalb des Sprachmodells.

Wenn du zum Gespräch zurückkehrst, kann der Charakter auf einen simulierten Tag zurückgreifen. Wenn du bleibst und mit ihm sprichst, kostet dieses Gespräch Zeit: Einkaufen kann sich verschieben, Putzen pausieren und eine Arbeitsschicht verspätet beginnen. **Geplantes und tatsächlich innerhalb der Simulation Ausgeführtes bleiben getrennt.**

Wechsle das Sprachmodell, ohne die Geschichte des Charakters neu zu beginnen. Der Kern läuft lokal mit SQLite, benötigt keinen API-Schlüssel und ruft kein LLM auf. Optionale Adapter ergänzen Langzeitgedächtnis und Erzählanbieter.

[Drei-Tage-Demo starten](#schnellstart) · [Python-/HTTP-Anbindung](docs/integrations.de.md) · [Architektur](docs/architecture.de.md) · [Mitwirken](CONTRIBUTING.de.md)

## Deine Anwesenheit kann den Tag des Charakters verändern

| Situation | PersonaLife hält fest |
|---|---|
| Einkaufen war für 17:00 geplant; ihr redet von 16:30 bis 18:15 | Das Gespräch belegt diese Zeit. Der Einkauf wird mit Begründung verschoben. |
| Putzen dauert 60 Minuten; nach 25 Minuten beginnt der Chat | 25 Minuten bleiben erledigt, 35 Minuten werden später fortgesetzt. |
| Die Schicht beginnt um 17:00; euer Gespräch endet um 16:55 und der Arbeitsweg dauert 25 Minuten | Ankunft frühestens um 17:20. Der Charakter teleportiert nicht zur Arbeit. |
| Das Programm war sechs Stunden ausgeschaltet | Beim Wiederöffnen wird der simulierte Alltag deterministisch nachgeholt. |
| Du wechselst den LLM-Anbieter | Dieselbe Persona mit Beziehungen, Zeitleiste und Erinnerungen bleibt erhalten. |

Diese Kontinuität liefert nachvollziehbare Gesprächsthemen: einen Moment bei der Arbeit, eine unerledigte Aufgabe, einen geänderten Plan oder ein gemeinsames Gespräch. Gesprächsanlässe heben passende Themen hervor, ohne in jeder Antwort eine Erwähnung zu erzwingen.

## Für die Entwicklung dauerhafter Charaktere

Verwende PersonaLife als Simulationsebene einer KI-Begleiter-App, Rollenspielanwendung, virtuellen Charaktererfahrung oder eines NPC-Prototyps. Über Python und eine authentifizierte lokale HTTP-API liefert die Chat-Anwendung Sitzungszeiten und erhält begrenzten Modellkontext.

- **Alltag:** anpassbare Berufsvorlagen, eigene Schichten, Routinen, Schlaf und Wege.
- **Kontinuität:** nur erweiterbare Ereignishistorie, Aktivitätsfortschritt und dauerhafte soziale Beziehungen.
- **Gesprächsabhängige Planung:** tatsächliche Sitzungsintervalle unterbrechen Aktivitäten und verändern zukünftige Pläne.
- **Erinnerungen:** lokales JSON oder AiMemory, ergänzt durch optionale Mem0- und Letta-Brückenschnittstellen.
- **Modellwahl:** OpenAI-kompatible Endpunkte, LM Studio und Ollama für optionale Erzähltexte.

**Projektstand:** funktionierende, automatisiert getestete Grundlage für Entwickler; keine schlüsselfertige Begleiter-App und kein produktionszertifizierter Dienst. Eine native ChatGPT-/Gemini-Verbindung wird nicht automatisch installiert. Alle Charaktererlebnisse sind fiktive Simulation. Vor der Integration bitte [geprüftes Verhalten und Grenzen](docs/validation.de.md) lesen.

## Englisch und Deutsch

Öffentliche Anleitungen, CLI-Bedienung und erzeugte Alltagstexte sind auf Englisch und Deutsch verfügbar. Jede Anleitungsseite verlinkt ihre andere Sprachfassung.

```sh
personalife --language en --help
personalife --language de --help
personalife --sprache de persona create
```

`PERSONALIFE_LANGUAGE` legt die CLI-Standardsprache fest. Die gespeicherte Persona-Eigenschaft `language` wählt die Sprache neuer Simulationstexte. Bestehende Historie, eigene Texte, Befehle und JSON-Schlüssel werden nicht umgeschrieben. [Ausführliche Sprachregeln](docs/languages.de.md).

## Schnellstart

Python 3.11 oder neuer. Windows 11, Linux und macOS werden vom Code unterstützt. Lokale Tests laufen unter Linux/Python 3.12; GitHub CI prüft Windows und Linux mit Python 3.11 bis 3.13. Unter Windows gehört `tzdata` zu den plattformspezifischen Abhängigkeiten.

```powershell
# Im heruntergeladenen oder geklonten PersonaLife-Verzeichnis
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install .
.\.venv\Scripts\personalife.exe --language de --db life.sqlite3 persona create --file examples/jenna.de.json --start 2026-09-08T00:00:00+02:00
.\.venv\Scripts\personalife.exe --language de --db life.sqlite3 advance jenna --to 2026-09-08T09:00:00+02:00
.\.venv\Scripts\personalife.exe --language de --db life.sqlite3 context jenna
```

Unter Linux/macOS lauten die Werkzeuge `python3`, `.venv/bin/python` und `.venv/bin/personalife`. Auf Systemen mit Zeitzonendaten lässt sich im Repository auch `python -m personalife` ohne Paketinstallation ausführen.

Für eine neue aktuelle Persona `--start` weglassen: Sie beginnt dann zum aktuellen Zeitpunkt. Ein historischer Beginn eignet sich für Simulation und Beispiele. Sämtliche Datum/Uhrzeit-Argumente benötigen einen UTC-Offset.

Das zusammenhängende Drei-Tage-Beispiel starten:

```sh
python examples/three_days.py --language de --output demo-output-de
python examples/three_days.py --language en --output demo-output-en
python -m unittest discover -s tests -v
```

Die Demo erzeugt eine SQLite-Datenbank, ursprüngliche und aktuelle Pläne, ausgeführte Abläufe, Tagesgeschichten, dauerhafte Erinnerungen, Beziehungshistorie und einen Prüfbericht. Mitgelieferte Beispiele liegen unter `examples/generated/` und `examples/generated-de/`. Binäre Datenbanken und private Erinnerungsdateien werden nicht in Git aufgenommen.

## Implementierte Funktionen

- Transaktionales, nur erweiterbares Ereignisprotokoll mit Prüfsummenkette und rekonstruierbaren Ansichten.
- Trennung von ursprünglichem Plan, aktuellem Plan und ausgeführtem Ablauf.
- Planung lokaler Tage, Nachtschichten, Zeitumstellungsgrenzen und ausdrückliche Wege.
- Zehn bearbeitbare Berufsvorlagen, eigene Wochenpläne, datumsbezogene Schichten, Urlaub/Krankheit/freie Tage, Pausen und reproduzierbare optionale Überstunden.
- Tägliche, werktägliche, wochenendliche, wöchentliche, monatliche und eigene datumsbasierte Routinen; feste Termine und Prioritäten.
- Aktivitätsfortschritt, Pause/Fortsetzung, Abschluss/Aufhebung und ausdrückliche Verspätungsereignisse.
- Laufende Gesprächsbeginn-/Ende-Schnittstellen und atomarer Import begrenzter Gespräche mit Wiederholungsprüfung.
- Dauerhafte Werte für Stimmung, Energie, Erschöpfung, Stress, Hunger und soziale Energie sowie wiederkehrende Beziehungen.
- Reproduzierbare Erzählereignisse, Bewertung der Erzählwürdigkeit, Markierung verwendeter Gesprächsanlässe und seltene passende Rückblicke.
- Tagesabschluss, belegbezogene Reflexion, Weiterführung offener Aufgaben und wiederholbarer Langzeitexport.
- AiMemory-Anbindung, lokale JSON-Erinnerungen, optionaler Mem0-Clientadapter und ausdrücklicher Letta-Brückenvertrag.
- OpenAI-kompatibler Erzählanbieter sowie LM-Studio- und Ollama-Adapter. Der Kern ruft kein LLM auf.
- CLI, authentifizierte lokale HTTP-API, Heartbeat, SQLite-Sicherung, Beispiele und Konsistenztests.

## Persona anlegen und konfigurieren

```sh
personalife --language de presets
personalife --language de persona create
personalife --language de persona create --name Jenna --id jenna --occupation bartender
personalife --language de persona create --file examples/jenna.de.json
```

Die interaktive Einrichtung bietet Berufsauswahl und die wichtigsten Felder. JSON/API machen das gesamte Profil einschließlich Arbeitgeber, Orten, Zuhause, Schichten, Kollegen, Freunden, Hobbys, Routinen und Wegen zugänglich. `examples/jenna.de.json` ist ein vollständiges bearbeitbares Profil. Kennungen sind dauerhafte Verweise; Kollegen müssen auf Einträge in `relationships` verweisen.

Eigene Berufe beschreibt die [Berufsplanung](docs/occupation-engine.de.md); die [Architektur](docs/architecture.de.md) erklärt Zuständigkeiten.

## Gespräche verändern den Tag

```python
from personalife import PersonaLife

with PersonaLife('life.sqlite3') as life:
    life.start_chat_event('jenna', '2026-09-08T16:20:00+02:00', 'session-1')
    # Die Chat-Anwendung liefert die tatsächlichen Sitzungszeiten.
    # Mehrere Nachrichten gehören zu dieser Sitzung; ein Heartbeat
    # kann die Zeit währenddessen weiter fortschreiben.
    life.end_chat_event('jenna', '2026-09-08T16:55:00+02:00',
                        'Wir haben vor meiner Schicht gesprochen.', 'session-1')
    context = life.get_persona_context('jenna')
```

Bei 25 Minuten Arbeitsweg ist die Ankunft nach diesem Gespräch frühestens um 17:20 möglich. Der ursprünglich geplante Arbeitsbeginn um 17:00 bleibt nachvollziehbar. Bei 25 erledigten Minuten einer 60-Minuten-Aufgabe bleiben 35 Minuten zur Fortsetzung.

Für eine vollständig aufgezeichnete Sitzung arbeitet `apply_chat_event(persona_id, start_time, end_time, summary, metadata=None)` atomar. `metadata={"idempotency_key": "stabile-sitzungskennung"}` ermöglicht sichere Wiederholungen. Bereits festgeschriebene vergangene Intervalle können nicht still durch neu eingereichte Gespräche ersetzt werden. Siehe [Gespräche und Neuplanung](docs/chat-reconciliation.de.md).

## API und fortlaufende Zeit

`PERSONALIFE_API_TOKEN` auf einen privaten zufälligen Wert setzen und starten:

```sh
personalife --language de --db life.sqlite3 serve --port 8787
personalife --language de --db life.sqlite3 heartbeat --minutes 15
```

API-Anfragen benötigen `Authorization: Bearer <token>`. Die API lauscht lokal und verweigert Browser-Anfragen anderer Herkunft. Kein öffentlicher Dienst wird bereitgestellt. `heartbeat --once` holt Zeit nach und schließt vergangene Tage ab. Statt eines dauerhaft laufenden Diensts kann die Anwendung vor dem Kontextabruf `advance_to()` aufrufen. Eine unbeendete Gesprächssitzung bleibt offen, bis die Anwendung sie beendet; Inaktivitätsregeln gehören in diese Anwendung.

Endpunkte und Integrationsaufgaben stehen unter [Integrationen](docs/integrations.de.md). `Accept-Language: de` wählt deutsche API-Fehler und Vorlagenbezeichnungen.

## Erinnerungs- und Erzählanbieter

```python
from personalife import PersonaLife, AiMemoryProvider
memory = AiMemoryProvider('/pfad/zu/AiMemory/memory.sqlite3')
with PersonaLife('life.sqlite3', memory=memory) as life:
    life.flush_memories('jenna')
memory.close()
```

Das vorhandene AiMemory-Paket muss vorher in derselben Umgebung installiert werden. PersonaLife verwendet dessen tatsächliche Schnittstellen `SQLiteMemoryStore` und `MemoryRecord`. Der Namensraum lautet `personalife:<persona_id>`. Mehr unter [Erinnerungen](docs/memory.de.md).

```python
from personalife.llm import LMStudio
text = LMStudio('dein-geladenes-modell').narrate(context)
```

Anbieteraufrufe sind optional und erzeugen nur Anzeigetext. Die Sprache wird aus `context.language` angefordert. Für die Simulation sind weder ein bezahlter Anbieter noch ein API-Schlüssel oder Modell erforderlich. Optionale Integrationen können eigene Kosten verursachen.

## Prüfung und Grenzen

`personalife --language de validate jenna` prüft Protokollintegrität, tatsächliche Überschneidungen, Ortskontinuität, Fortschritt und Gesprächsdauer. Die Tests decken die beschriebenen Gesprächs-/Arbeits-/Einkaufs-/Putzfälle, Neustarts, mehrtägige Beziehungen, unveränderliche Historie, Zeitzonenfehler, Zeitumstellungen, API-Authentifizierung und tatsächlichen AiMemory-Import/Abruf ab. Siehe [Prüfbericht](docs/validation.de.md).

API und CLI bilden eine nutzbare Engine, keine installierte ChatGPT-Verbindung und keine grafische App. Mem0 ist an seiner Adaptergrenze getestet, nicht mit einem Live-Konto. Letta wird über eine bereitgestellte Brücke angebunden, weil der aktuelle Hauptzweig keinen unterstützten Server mehr enthält. Erzeugte Prosa ist nicht maßgebliche Historie. Die Rekonstruktion bevorzugt Nachvollziehbarkeit; es gibt keine Zertifizierung produktiver Lastgrenzen. Einzelheiten stehen in der [Architektur](docs/architecture.de.md).

## Fragen aus der Entwicklung

**Ist das ein weiterer Chatbot oder eine Erinnerungsdatenbank?**  
PersonaLife liefert Zustand und simulierte Ereignisse, über die ein Chatbot sprechen kann. Die aufrufende Anwendung übernimmt Gespräch und Modellzugriff; ein optionaler Erinnerungsanbieter speichert ausgewählte Langzeiterinnerungen.

**Braucht es ein bezahltes Modell oder einen ständig laufenden Agenten?**  
Die Simulation benötigt beides nicht. Sie kann Zeit bei Bedarf nachholen oder einen einfachen Heartbeat nutzen. Externe optionale Anbieter haben eigene Voraussetzungen und Kosten.

**Verbindet es sich direkt mit ChatGPT, Gemini oder einer Spiel-Engine?**  
Python und lokale HTTP-Endpunkte stehen zur Integration bereit. Fertige Browser-, Telefon- und Spiel-Engine-Connectoren sind nicht enthalten.

**Erzählt die Persona immer korrekt von ihrem simulierten Tag?**  
Das Protokoll trennt Pläne und ausgeführte Ereignisse, und Modellantworten können es nicht umschreiben. Ein Sprachmodell kann dennoch ausschmücken; eine stärkere Ausgabekontrolle gehört in die aufrufende Anwendung.

**Wo kann ich helfen?**  
Mit [CONTRIBUTING.de.md](CONTRIBUTING.de.md) und dem [Weiterentwicklungsplan](docs/roadmap.de.md) beginnen. Reproduzierbare Zeitablauffehler, Integrationsbeispiele und Installationsrückmeldungen helfen besonders.

## Lizenz und Quellenrecherche

Apache-2.0. Fremder Implementierungscode wurde nicht in PersonaLife übernommen. AiMemory bleibt eine separat installierte Abhängigkeit. Die acht angegebenen Projekte wurden anhand tatsächlicher Quelldateien, Lizenzen und verfügbarer Tests geprüft. Ergebnisse und Abweichungen stehen im [Recherchevergleich](docs/research-comparison.de.md) und in [THIRD_PARTY.de.md](THIRD_PARTY.de.md). Die [Original-Lizenz](LICENSE) bleibt unverändert.
