# Maßgebliches Ereignismodell

[English](event-model.md)

Jede Zeile enthält Sequenznummer, weltweit eindeutige Ereigniskennung, Persona-Kennung, UTC-Ereigniszeit, Typ, JSON-Daten, vorherige Prüfsumme und eigene Prüfsumme. Befehle hängen Ereignisse atomar an. Die Reihenfolge richtet sich nach der Sequenz; Zeitstempel beschreiben die simulierte Zeit.

| Ereignis | Bedeutung |
|---|---|
| PERSONA_CREATED / PERSONA_UPDATED | Geprüftes Profil und Konfiguration zukünftiger Abläufe |
| DAY_PLANNED | Wiederholungssicherer Planungsmarker für ein lokales Datum |
| ACTIVITY_PLANNED | Ursprünglich beabsichtigte Aktivität mit erforderlicher Arbeit und Ort |
| ACTIVITY_CHANGED | Ausdrückliche zukünftige Änderung oder Fortschrittszustand mit Begründung |
| ACTUAL_SEGMENT | Ausgeführtes halboffenes Zeitintervall, Ort davor/danach und begrenzte Zustandswerte |
| CLOCK_ADVANCED | Grenze der festgeschriebenen verarbeiteten Zeit |
| CHAT_STARTED / CHAT_ENDED | Dauerhafte Gesprächssitzung und aufgezeichnete Zusammenfassung |
| CONFLICT_RESOLVED | Begründung für Änderungen zukünftiger Arbeit und Wege |
| OBLIGATION_LATE | Geplanter Beginn, erwartete Ankunft und Begründung |
| STORY_EVENT | Ereignis mit Bezug zu einer Ausführungs- oder Gesprächsgrenze |
| HOOK_USED | Die aufrufende Anwendung hat dieses Ereignis bereits erwähnt |
| DAY_CLOSED | Tagesgeschichte, Reflexion, offene Aufgaben und Erinnerungskandidaten |
| MEMORY_EXPORTED | Ein Anbieter hat eine stabile Erinnerungskennung bestätigt |

Der Fortschritt einer Aktivität ist die Summe ihrer ausgeführten Abschnitte. Ein Plan allein erzeugt keinen Fortschritt. Ein Tagesabschluss behauptet nicht, dass unerledigte Aktivitäten abgeschlossen seien. Laufende Gespräche belegen ihr Zeitintervall exklusiv, auch über Mitternacht hinweg.

Zeitstempel werden an den Schnittstellen auf UTC normalisiert. Lokale Wiederholungen verwenden `zoneinfo`. Bei mehrdeutigen Zeiten der herbstlichen Umstellung gilt fold 0, sofern über `clock.civil` nichts anderes angegeben wurde. Nicht existierende Frühlingszeiten werden abgewiesen. Ein ausdrücklicher UTC-Offset erlaubt es, beide Vorkommen einer mehrdeutigen Uhrzeit anzusprechen.

Änderungen erfolgen über die öffentlichen Anwendungsmethoden. `Ledger.append` ist ein interner Baustein, benötigt eine ausdrückliche Transaktion und steht nicht über die HTTP-API zur Verfügung. Modellantworten können ihn nicht aufrufen. Ereigniskennungen, JSON-Schlüssel und Zustandsnamen bleiben in beiden Bedienungssprachen gleich.
