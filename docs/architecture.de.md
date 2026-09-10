# Architektur

[English](architecture.md)

## Zuständigkeiten

`ledger.py` verwaltet das maßgebliche SQLite-Ereignisprotokoll. `projections.py` rekonstruiert daraus Persona-Zustand, Pläne, ausgeführte Abschnitte, Gesprächssitzungen, Beziehungen, Geschichten und Erinnerungsexporte. `service.py` legt die Transaktionsgrenzen fest. Kein Modellanbieter schreibt in das Protokoll.

`planner.py` plant lokale Kalendertage, Arbeitsabläufe, Wiederholungen und Wege. `cognition.py` aktualisiert begrenzte Zustandswerte und bewertet Ereignisse. `memory.py` stellt die Langzeitadapter bereit. `llm.py` erzeugt optional Erzähltext. `api.py`, `cli.py` und `heartbeat.py` sind Schnittstellen für die aufrufende Anwendung.

Die Datenrichtung lautet: Ereignisprotokoll → ausgeführter Alltag → Zustand → Erinnerung → Modellkontext → Antwort. Ein Planereignis hält eine Absicht fest. Ein Ausführungsabschnitt hält tatsächlich verstrichene simulierte Arbeit fest. Eine zukünftige Geschichte kann keinen solchen Abschnitt erzeugen.

## Speicherung und gleichzeitige Zugriffe

SQLite nutzt WAL, eine Wartezeit von 30 Sekunden bei belegter Datenbank und `BEGIN IMMEDIATE`, um schreibende Befehle zu serialisieren. Jede API-Anfrage öffnet eine eigene Verbindung. Eine PersonaLife-Instanz darf nicht zwischen Threads geteilt werden. Datenbanktrigger verhindern gewöhnliche SQL-Änderungen und Löschungen kanonischer Ereignisse. SHA-256-Prüfsummen verketten sämtliche Ereignisse. Wer die Datenbank vollständig kontrolliert, könnte Trigger entfernen und Prüfsummen neu erstellen: Dies ist eine Integritäts- und Nachvollziehbarkeitsprüfung, keine externe kryptografische Beglaubigung.

Die Schemaversion ist 1; unbekannte Versionen werden abgewiesen. Fachliche Modelle sind aus dem Protokoll abgeleitete Ansichten statt unabhängig beschreibbarer Tabellen. `backup()` verwendet die SQLite-Sicherungsfunktion. Eine aktive `.sqlite3`-Datei sollte nicht ohne ihr WAL kopiert werden; dafür gibt es den Sicherungsbefehl.

Persona-Ansichten werden im Arbeitsspeicher zwischengespeichert und anhand des Protokollendes überprüft. Sie sind nicht maßgeblich. Bei gültigem Anker werden nur neue Ereignisse verarbeitet. Nach einem Rollback oder geändertem Anker wird vollständig rekonstruiert. Sequenzgrenzen halten jeden Lesevorgang konsistent zum beobachteten Protokollende. Öffentliche Ergebnisse sind defensive Kopien. Für große Datenmengen und produktiven Masseneinsatz sind weiterhin dauerhafte Rekonstruktions-Checkpoints sinnvoll. Cloud-Dienste, dauernde Modellschleifen, Kubernetes und Embeddings sind nicht erforderlich.

## Planung und Ausführung

Ein Tag ist das halboffene Intervall von lokaler Mitternacht bis zur nächsten lokalen Mitternacht. Nachtschichten dürfen diese Grenze als zusammenhängende Folge überschreiten. Arbeitsaufgaben und Pausen sind eigene Aktivitäten. Fehlende Wegverbindungen führen zu einem Fehler. Heimarbeit verwendet das Zuhause als Ort und keine Wegezeit.

Ursprüngliche Aktivitäten bleiben unverändert. `ACTIVITY_CHANGED` aktualisiert nur die daraus abgeleitete aktuelle Aktivität. Erforderliche und bereits geleistete Sekunden sind getrennt; Umplanung erhält deren Differenz. Eine unterwegs unterbrochene Reise setzt mit der verbleibenden Dauer fort. Verspätungen werden ausdrücklich erfasst. Ein tatsächliches aufgezeichnetes Gespräch kann die rechtzeitige Ankunft zu einem festen Termin verhindern.

Normale Freizeitblöcke dürfen bei der Neuplanung entfallen. Lücken werden als Freizeit am tatsächlichen aktuellen Ort ausgeführt. Feste Verpflichtungen werden vor weichen Aktivitäten eingeplant; anschließend eingefügte Wege können sie weiter verschieben. Dies ist eine nachvollziehbare deterministische Regel, kein globaler Optimierer.

## Erweiterbarkeit und aktueller Umfang

- Berufe bestehen aus Datenvorlagen mit Aufgabentiteln und Verweisen auf Kollegen. Ausnahmen ermöglichen Abwesenheiten, Heimarbeit, eigene Schichten und unregelmäßige freiberufliche oder studentische Abläufe. Optionale Überstunden werden pro Datum reproduzierbar bestimmt.
- Soziale Ereignisse verändern benannte Beziehungen. Verfügbarkeit, Ort und Beruf von NPCs bleiben gespeichert; ein eigener durchgehend simulierter Kalender für jeden NPC ist nicht enthalten.
- Routinen können Aktivitäten mit einem Ziel verknüpfen. Der Fortschritt wird pro Aktivität erfasst; ein unabhängiger Optimierer für mehrere Aktivitäten, Ziele und Fristen ist nicht umgesetzt.
- Der Zustand ist eine vereinfachte Simulation, kein klinisches Modell. Ein Wetter-Netzwerkdienst ist nicht konfiguriert. Eine aufrufende Anwendung kann Umgebungsinformationen ergänzen und die Planung erweitern.
- Rückblicke sind Kandidaten mit Ereignisbezug und keine Behauptungen neuer Ereignisse. Reflexion fasst ausgewählte Inhalte deterministisch zusammen und erfindet keine neue Historie.
- Die Erinnerungsbewertung nimmt mit dem Alter ab, ohne Historie zu löschen. Eine automatische verlustbehaftete Archivkompression ist nicht enthalten.
- Nachträglich importierte Gespräche werden abgewiesen, wenn die festgeschriebene Zeit ihren Beginn bereits überschritten hat. Ein ausdrücklich protokolliertes Revisionssystem wäre eine gesonderte Erweiterung.
- Alle Aktivitätszustände werden validiert. Der Standardablauf nutzt planned/active/paused/completed/cancelled. Besondere Regeln für blocked/missed/abandoned benötigen eine Erweiterung; gewöhnliche Verspätungen verwenden `OBLIGATION_LATE`.

Diese Grenzen sind offen dokumentiert. Das Repository enthält eine ausführbare Grundlage und behauptet keine Produktionszertifizierung aller ursprünglich gewünschten Funktionen.
