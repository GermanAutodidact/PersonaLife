# Prüfbericht

[English](validation.md)

Die lokalen Prüfungen liefen unter Linux mit Python 3.12 am 10.09.2026. GitHub CI prüft zusätzlich Windows und Linux mit Python 3.11 bis 3.13.

- In Version 1.0.1 bestanden **50 automatisierte lokale Tests**. Die aktuelle vollständige Ausgabe steht in `test-results.txt`; mit der zweisprachigen Fassung kommen Sprachtests hinzu.
- Der tatsächliche AiMemory-Rundlauf verwendete `database.py` und `models.py` aus dessen aktuellem Repository. Ohne installiertes AiMemory überspringt die gewöhnliche Testsuite diese optionale externe Integration ausdrücklich.
- Alle zehn Berufsvorlagen bestanden je sieben simulierte Tage mit täglichem Gespräch von 10:25 bis 12:10 und Konsistenzprüfung nach jedem Tag.
- Das ursprüngliche Drei-Tage-Beispiel für Jenna erzeugte 319 Protokollereignisse, 54 ausgeführte Abschnitte und elf ausgewählte exportierte Erinnerungen.
- Ursprüngliche Pläne bleiben nach Neuplanung verfügbar. Die Tagesbeispiele enthalten Beziehungen und Kontext vom Folgetag.

## Zweisprachige Prüfung in 1.1.0

Im abschließenden lokalen Lauf bestanden **67 Tests**. Davon prüfen 17 Sprachtests englische/deutsche CLI-Hilfe und Einrichtung, übersetzte eigene Fehler, Umgebungsvariablen und Standardwerte, stabile Vorlagenkennungen, sprachabhängige API-Antworten, LLM-Sprachanweisung sowie unveränderte Zeit- und Fortschrittsberechnung zwischen den Sprachen. Auch sämtliche öffentlichen Dokumentpaare, lokale Links, Repository-Beschreibungen, der Katalog statischer eigener Fehler, ungültige Sprachen und die Erhaltung historischer/eigener Texte werden geprüft.

Beide Drei-Tage-Demos erzeugten 319 Ereignisse, 54 tatsächliche Abschnitte und elf ausgewählte Erinnerungen. Erzeugte Bezeichnungen und Erzähltexte unterscheiden sich sprachlich, während kanonische Kennungen und Zeit-/Zustandsberechnungen stabil bleiben. Aktualisierte JSON-/Markdown-Beispiele sind in beiden Sprachen gespeichert.

Fremde Diagnoseausgaben, Quellcodebezeichner und die ursprüngliche Apache-Lizenz bleiben absichtlich unübersetzt. GitHub hat ein About-Feld: Vorbereitet sind englischer, deutscher und kombinierter Text; das Speichern der Metadatendatei ändert nicht die Repository-Einstellungen.

## Zusätzliche Prüfungen in 1.0.1

Die ergänzten Tests reproduzierten zuerst die Annahme fehlerhafter Profile, veraltete Kontaktmetadaten und unnötige vollständige Historienrekonstruktion. Die Korrekturen weisen ungültige Eingaben vor dem Speichern ab, erhalten gelernte Beziehungshistorie bei Metadatenänderungen und vergleichen inkrementelle Ansichten mit vollständiger Rekonstruktion einschließlich Rollback.

Eine 30-Tage-Simulation mit täglichem Gespräch von 10:25 bis 12:10 bestand nach jedem Tag die Konsistenzprüfung: 3.084 Ereignisse, 503 tatsächliche Abschnitte und 517 Aktivitätsdatensätze. Sie dauerte in dieser Ausführungsumgebung 16,661 Sekunden. Diese Einzelmessung garantiert keinen Durchsatz.

Eine siebentägige Zeitaufholung benötigte in lokalen Einzelmessungen vorher 1,380 und nach inkrementeller Verarbeitung 0,670 Sekunden. Aufgabe und Ereigniszahl blieben gleich: 606 Ereignisse. Der Regressionstest prüft, dass ein neues Gesprächsanlass-Ereignis nur dieses neue Ereignis verarbeitet, statt eine empfindliche Laufzeitgrenze vorauszusetzen.

Das Wheel von 1.0.1 ließ sich ohne Netzwerkzugriff bauen. Lokale README-Verweise sowie die vorgeschlagene Kurzbeschreibung und Topic-Namen wurden geprüft. Die About-Einstellungen müssen weiterhin von einer Person mit Repository-Verwaltungsrechten angewendet werden; die JSON-Datei ändert diese Einstellungen nicht selbst.

## Geprüfte Gegenfälle

| Risiko | Prüfung |
|---|---|
| Gespräch überschneidet sich mit Einkauf | Einkauf wird verschoben; das Gespräch belegt sein Intervall |
| Gespräch vor der Arbeit | 25 Minuten Arbeitsweg bleiben erforderlich; Verspätung wird erfasst |
| Verlust unterbrochener Arbeit | 25 von 60 Minuten bleiben erhalten; 35 Minuten fehlen noch |
| Unterbrechung unterwegs | Restweg wird ohne Teleportation fortgesetzt |
| Offline-Neustart | Sechs Stunden werden dauerhaft nachgeholt; Wiederholung verändert nichts |
| Mehrere Sitzungen und Duplikate | Gleichzeitige offene Gespräche werden abgewiesen; stabile Wiederholungen dedupliziert; widersprüchliche Schlüssel abgewiesen |
| Umschreiben der Historie | SQL-Trigger verhindern normale Änderungen/Löschungen; Prüfsummenkette wird geprüft |
| Plan als Abschluss ausgegeben | Planung allein erzeugt keinen tatsächlichen Fortschritt |
| Ungültige Zeit | Zeitstempel ohne Zeitzone, negative Dauer und nicht existierende Ortszeiten werden abgewiesen |
| Zeitumstellung | Frühlingstag 23 Stunden, Herbsttag 25 Stunden; doppelte Ortszeit unterscheidet sich um eine Stunde |
| Falscher Ort | Unbekannte Orte und fehlende Wege werden abgewiesen; Ortskontinuität wird geprüft |
| Vermischte Erinnerungen | Getrennte Namensräume und unveränderliche lokale Erinnerungskennungen |
| Modellzugriff | Erzähladapter bieten keine Änderung des Ereignisprotokolls an |
| API-Zugriff | Token erforderlich; beliebiger Aufruf interner Methoden nicht zugelassen |
| Zu großer Kontext | Antwort bleibt innerhalb des konfigurierten Zeichenbudgets |

## Was damit nicht zertifiziert wird

Dies ist kein externes Penetrationstesting, formaler Beweis, klinischer Modelltest oder produktives Lastzertifikat. Live-Konten bei Mem0, Letta oder OpenAI wurden nicht verwendet. Windows und macOS standen lokal nicht zur Verfügung. Der CI-Workflow fordert Windows-/Linux-Läufe an; deren Ergebnis steht in GitHub Actions und ergibt sich nicht allein aus der Konfiguration.

Die Bindung freier Modellantworten an belegte Ereignisse bleibt eine Aufgabe der aufrufenden Anwendung. Die Kernregeln verhindern das automatische Umschreiben der Historie durch Prosa, garantieren aber nicht, dass ein Sprachmodell niemals einen Satz ausschmückt.
