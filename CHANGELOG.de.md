# Änderungsverlauf

[English](CHANGELOG.md)

## 1.1.0 — 2026-09-10

- Gleichwertige englische und deutsche README sowie vollständige Übersetzungen der öffentlichen Dokumentation mit Sprachverweisen.
- Englische, deutsche und kombinierte Repository-Beschreibungen; Topics und Paketverweise angepasst.
- CLI-Sprachwahl mit `--language`, `--sprache` und `PERSONALIFE_LANGUAGE`; übersetzte Hilfe, Einrichtungsfragen und eigene Fehlermeldungen.
- Gespeicherte Persona-Sprache für Berufsvorlagen, erzeugte Aktivitätstitel, Geschichten, Gesprächsanlässe und Modellkontext.
- Sprachabhängige API-Fehler und Vorlagen über `Accept-Language`; stabile JSON-Schlüssel und Befehle.
- Englische und deutsche Drei-Tage-Beispiele, Installationsmeldungen und Sprachtests.
- Vorhandene historische Texte und eigene Eingaben bleiben unverändert; externe Diagnoseausgaben bleiben bei Bedarf im Original.

## 1.0.1 — 2026-09-10

- Doppelte Routinenkennungen, ungültige Schicht-Ausnahmen, unbekannte Weg-Endpunkte, ungültige Wiederholungswerte, unbekannte Teilnehmer und fehlerhafte Überstundenwerte werden vor dem Speichern abgewiesen.
- Änderungen von Kontaktnamen und Metadaten erhalten gelernte Beziehungsstärke und gemeinsame Historie.
- Bei gültigem Protokollanker werden nur neue Ereignisse verarbeitet; nach Rollbacks wird rekonstruiert. Zurückgegebene Daten können den internen Cache nicht verändern.
- Regressionstests für Eingaben, Kontaktänderungen, Vergleich inkrementeller und vollständiger Rekonstruktion sowie Rollbacks ergänzt.
- Öffentliche README verbessert, deutsche Einführung, Beitragsleitfaden, eingegrenzte Weiterentwicklung und Metadatenvorschläge hinzugefügt.

## 1.0.0 — 2026-09-10

Erste ausführbare Grundlage mit Ereignissimulation, Beruf und Routinen, Wegen, Gesprächs-Neuplanung, Erinnerungs- und Anbieterschnittstellen, CLI, lokaler API, Tests und Drei-Tage-Beispielen.
