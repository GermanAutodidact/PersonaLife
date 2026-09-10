# Vergleich der recherchierten Quellen

[English](research-comparison.md)

Geprüft am 10.09.2026 über die verbundene GitHub-Quellcode-API. `source-evidence.json` hält Repository-Commits und Blob-Prüfsummen der gelesenen Lizenz-, Implementierungs- und Testdateien fest. Die Prüfung war gezielt, kein vollständiges Sicherheitsaudit und keine Ausführung sämtlicher Fremdtests. PersonaLife wurde eigenständig implementiert; fremde Implementierungsdateien werden nicht mitgeliefert.

| Repository | Tatsächlich geprüfte Module und Tests | Nützlicher Gedanke | Beobachtete Lizenz | Entscheidung |
|---|---|---|---|---|
| [Crescent Grove](https://github.com/Canon-73/crescent-grove) | `core/scheduler.py`, `memory/manager.py`, `tests/test_moontide_v2.py` | Moonbeat verwaltet regelmäßige Impulse, Zeitintervalle und Erweiterungszustand; Arbeitsplatz-Erinnerungen sind getrennt | MIT | Eigener Heartbeat und dauerhaft gespeicherte begrenzte Zustandswerte. Der geprüfte Dateiverwalter wird nicht mit einer vollständigen LETHE-Implementierung gleichgesetzt. |
| [Yuralume](https://github.com/Yuralume/yuralume-core) | `domain/entities/schedule.py`, `application/services/schedule_service.py`, `tests/unit/test_post_turn_schedule_adjustments.py` unter `src/kokoro_link` | Lokale Tagespläne mit UTC-Aktivitätsgrenzen, wiederholungssichere Bedarfserzeugung, geschützte historische Zusammenhänge und Änderungen nach Gesprächsrunden | BUSL-1.1 einschließlich tatsächlich vorhandener Zusatzbedingungen | Nur Architekturvorbild; eigenständige Neuplanung und Schutz der festgeschriebenen Historie. |
| [Horde Studio](https://github.com/ddkhan24/hordestudio) | `vh-simulation-core.js`, `scratch/living_world_stress_test.js` | Aufmerksamkeit berücksichtigt Kapazität, Bereitschaft und Unterbrechbarkeit; Fortschritt bleibt über Zeitschritte erhalten | Keine Repository-Hauptlizenz im geprüften Verzeichnisbaum gefunden | Kein kopierter Code; eigene Restarbeits- und Reisefortsetzungslogik. |
| [HerAndHim](https://github.com/ericwang915/HerAndHim) | `herandhim/scheduler/planner.py`, `tests/test_persistence.py` | Persona, Beruf, Gewohnheiten und Datum formen einen Tagesplan; der geprüfte Planer schreibt den aktuellen Plan in den Kontext | AGPL-3.0 | Kein kopierter Code; berufsabhängige Planung mit Ereignisprotokoll statt ausschließlich einer aktuellen Markdown-Datei. |
| [Generative Agents](https://github.com/joonspk-research/generative_agents) | `reverie/backend_server/persona/cognitive_modules/plan.py`, `retrieve.py`, `reflect.py` | Wiederfinden trennt Aktualität, Wichtigkeit und Embedding-Relevanz; Reflexion verwendet ausgewählte Belege | Apache-2.0 | Eigenständige Wort-, Alters- und Wichtigkeitsbewertung sowie belegbezogene Zusammenfassung. Embeddings bleiben eine mögliche Erweiterung. |
| [Mem0](https://github.com/mem0ai/mem0) | `mem0/memory/main.py`, `tests/memory/test_session_scope.py` | Ausdrücklich abgegrenzte add/search-API, Metadaten und optionale Extraktion | Apache-2.0 | Optionaler Adapter mit bereitgestelltem Client; keine vorgeschriebenen SDK-, Vektor- oder Cloud-Abhängigkeiten. |
| [Letta](https://github.com/letta-ai/letta) | Aktuelle `README.md`, `LICENSE`, Repository-Verzeichnisbaum | Modellunabhängiger Zustand bleibt eine nützliche Architekturgrenze | Apache-2.0-Datei weiterhin in main | **Der aktuelle Hauptzweig ist eine Projektseite, nicht der frühere Server.** Die README verweist auf den stillgelegten Zweig `archive`; aktuelle Serverdateien und Tests waren dort nicht vorhanden. Ausdrückliche Brücke statt behaupteter Prüfung einer unterstützten alten API. |
| [AiMemory](https://github.com/GermanAutodidact/AiMemory) | `src/aimemory/database.py`, `models.py`, `store.py`, `tests/test_store.py`, Paketmetadaten | Transaktionale unveränderliche Datensätze nach Namensraum, Konflikterkennung sowie Kontext/Suche | Apache-2.0 | Erster externer Erinnerungsanbieter; mit tatsächlich abgerufenem Quellcode getestet. PersonaLife behält die maßgebliche Zeitleiste. |

## Architekturentscheidungen

1. Absicht und Ausführung getrennt erhalten. Ein zukünftiger Plan beweist keinen Abschluss.
2. Gesprächsdauer gehört in dieselbe exklusive tatsächliche Zeitleiste wie andere Aktivitäten.
3. Deterministische Zeitberechnung verwenden; Sprachmodelle dienen der Darstellung und späteren Erzähl-Erweiterungen.
4. Erinnerungskandidaten aus bestätigten simulierten Ereignisgrenzen erzeugen und nach dem maßgeblichen Speichern exportieren.
5. Stabile Persona-, Orts- und NPC-Kennungen über Anbieter und Sitzungen hinweg verwenden.
6. Ausdrückliche Wege, verbleibende Arbeit und Verspätungsereignisse verwenden statt die Historie still anzupassen.

## Grenzen der Prüfung

Die große rekursive Verzeichnisantwort von Generative Agents war abgeschnitten. Deshalb wurde `reverie/backend_server` gesondert abgerufen, bevor die kognitiven Module gelesen wurden. Der tatsächliche Hauptzweig von Letta weicht deutlich von der gelieferten Ausgangsbeschreibung ab. Die Recherche behauptet nicht, sämtliche gewünschten Fremdkonzepte in den geprüften Dateien gefunden zu haben. Der implementierte Kern benötigt dafür keine unbelegten Annahmen.
