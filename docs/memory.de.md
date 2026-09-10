# Erinnerungsanbindung

[English](memory.md)

PersonaLife hält rohe Ereignishistorie, Tagesabschlussansichten und episodische Erzählereignisse vor. Ausgewählte Kandidaten eines Tagesabschlusses werden an einen getrennten Langzeitanbieter exportiert. Namensraum: `personalife:<persona-id>`.

Ein Datensatz enthält eine stabile Ereigniskennung, Inhalt, Ereigniszeitpunkt, Typ, Persona-Kennung, Datum, Wichtigkeit, Teilnehmer, Ort, Quelle und Konfidenz. Quelle und Konfidenz beschreiben die Herkunft innerhalb der Simulation; sie behaupten kein Ereignis in der physischen Welt.

## AiMemory: erster unterstützter externer Anbieter

Das vorhandene AiMemory-Paket muss in derselben Python-Umgebung installiert sein. `AiMemoryProvider` verwendet `aimemory.database.SQLiteMemoryStore.import_records(namespace, records)` und `search(namespace, query)` mit `MemoryRecord.from_dict`. Der tatsächliche Quellcode wurde geprüft und in Integrationstests verwendet, Stand Commit `a5879350bc8d59eda08ad81da29eac6a0e32ceaa`.

Beispiel einer vorhandenen Windows-Datenbank: `C:\Users\elect\AppData\Local\AiMemory\memory.sqlite3`. Angegeben wird der lokale Pfad auf dem Rechner, auf dem PersonaLife läuft. PersonaLife greift aus dieser Entwicklungsumgebung nicht aus der Ferne auf diese Windows-Datei zu.

## Lokales JSON

`JsonMemoryProvider(directory)` veröffentlicht jede Erinnerung als eigene unveränderliche Ereignisdatei. Namensraum und Kennung werden für die Pfadbildung gehasht. Derselbe Export ist wiederholungssicher; abweichende Daten unter derselben Kennung werden abgewiesen. Es sind keine externen Abhängigkeiten oder Netzwerkaufrufe erforderlich.

## Fehler und Wiederholung

Der Tagesabschluss wird vor dem Export festgeschrieben. Bei einem Anbieterfehler bleiben Historie und ausstehende Kandidaten erhalten. `flush_memories` versucht ausstehende Exporte erneut und protokolliert eine Anbieterbestätigung. AiMemory und JSON verwenden stabile Kennungen. Dadurch verkraften sie auch einen Absturz nach dem Schreiben beim Anbieter, aber vor der Bestätigung im Protokoll. Mem0 und eigene Letta-Brücken benötigen dafür eine eigene Regel gegen Duplikate; exakt einmalige externe Zustellung wird für diese optionalen Adapter nicht behauptet.

## Bewertung, Reflexion und Rückblicke

Wichtigkeit, Neuheit, emotionale Intensität und soziale Relevanz bestimmen die Erzählwürdigkeit. Das Wiederfinden kombiniert Altersabnahme mit der Relevanz von Suchwörtern. Die rohe Historie bleibt erhalten. Tagesreflexion wählt bemerkenswerte Beschreibungen mit Ereignisbezug aus und lässt kein LLM Fakten erfinden. Alte Ereignisse können bei passendem Ort oder Suchtext selten und reproduzierbar als Rückblick auftauchen. `mark_hook_used` verhindert wiederholte Erwähnungen durch die aufrufende Anwendung.

## Optionale Anbieter

Mem0 erhält einen fertig konfigurierten Client. `infer=False` vermeidet eine erneute Extraktion bereits ausgewählter Erinnerungen. Letta erhält ausdrücklich bereitgestellte Funktionen `put_memory(namespace, record)` und `search_memory(namespace, query)`. Dies ist eine Brücke und keine angenommene alte API: Das aktuelle Letta-Repository ist eine Projektseite; der frühere Server liegt im Zweig `archive`.

Deutsch erzeugte Erinnerungen bleiben deutsch, englische englisch. Benutzertexte werden nicht automatisch übersetzt, und ein Sprachwechsel schreibt bestehende Erinnerungen nicht um.
