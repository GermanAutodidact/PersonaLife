# Englisch und Deutsch

[English](languages.md) · [Deutsche README](../README.de.md)

Alle öffentlichen Anleitungsseiten haben eine englische Fassung und eine vollständige deutsche Entsprechung mit der Endung `.de.md`. Jede Seite verweist auf die andere Sprache. Ereigniskennungen, Schema-Schlüssel, Befehlsnamen, externe Quellenbelege und die ursprüngliche Apache-Lizenz bleiben unverändert.

## Sprache der Bedienung

```sh
personalife --language en --help
personalife --language de --help
personalife --sprache de persona create
```

`PERSONALIFE_LANGUAGE=en` oder `de` legt die Standardsprache der CLI fest. Die globale Sprachoption steht vor dem Befehl. Hilfe, Einrichtungsfragen und eigene PersonaLife-Fehlermeldungen verwenden diese Sprache. Technische Meldungen von Python, SQLite, pip oder externen Anbietern können im Original bleiben, damit hilfreiche Details nicht verloren gehen.

Die Installationsskripte akzeptieren `-Language de` in PowerShell oder `de` als erstes Argument des Shellskripts. Ihre eigenen Meldungen und der vorgeschlagene nächste Befehl werden übersetzt; Ausgaben von Paketinstallern und Testrunnern stammen von externen Werkzeugen.

## Sprache der Persona

Ein Profil besitzt `language: en` oder `de`; ältere Profile verwenden standardmäßig Englisch. `persona(language='de')` erzeugt übersetzte berufliche Aufgabenbeispiele, Ortsnamen, Hobbys und Routinen. `get_presets('de')` liefert übersetzte Bezeichnungen mit gleichbleibenden Vorlagenkennungen.

Neue, von der Engine erzeugte Aktivitätstitel, Erzählereignisse, Gesprächsbezeichnungen, Begründungen und Modellkontext-Hinweise verwenden die gespeicherte Persona-Sprache. Eigene Namen, Aufgabentexte und Gesprächszusammenfassungen bleiben erhalten. Ein Sprachwechsel übersetzt weder historische Ereignisse noch bereits gespeicherte zukünftige Pläne. Neue Tage verwenden die neue Sprache. Maßgebliche Historie wird nicht allein für eine Übersetzung neu geschrieben.

Die CLI-Sprachoption ändert die Bedienung, nicht die gespeicherte Sprache einer bestehenden Persona. Eine ausdrückliche Sprache im JSON-Profil hat Vorrang; fehlt sie, übernimmt die CLI beim Anlegen ihre Bedienungssprache.

## API und LLM

`Accept-Language: de` oder `en` wählt die Sprache der API-Fehler und Vorlagenbezeichnungen. Regionale Varianten und Qualitätswerte werden unterstützt. Ohne passende Präferenz gilt die konfigurierte Serversprache. Neue Personas übernehmen diese nur, wenn ihr Profil kein `language` enthält.

Endpunkte, Befehle und JSON-Schlüssel sind in beiden Sprachen gleich. Strukturierte Werte wie `planned`, `completed` und Ortskennungen bleiben maschinenlesbare Bezeichner. Bereits gespeicherter Text wird so zurückgegeben, wie er erfasst wurde; ein HTTP-Header übersetzt ihn nicht automatisch.

Der Kontext enthält `language`; die Erzähladapter fordern diese Ausgabesprache vom Modell an. Das ist eine Modellanweisung, keine Garantie eines entfernten Anbieters. Die deterministische Simulation erhält dadurch keine Modellabhängigkeit.

## Beispiele

```sh
python examples/three_days.py --language en --output demo-output-en
python examples/three_days.py --language de --output demo-output-de
```

`examples/jenna.json` und `examples/jenna.de.json` sind gleichwertige vollständige Profile. Gespeicherte lesbare Beispiele stehen unter `examples/generated/` und `examples/generated-de/`.

## Repository-Beschreibung

GitHub bietet genau ein About-Beschreibungsfeld. `repository-metadata.json` enthält eine englische, eine deutsche und eine kombinierte zweisprachige Beschreibung sowie gemeinsame passende Topics. Es sind vorbereitete Werte, keine automatisch angewendeten Einstellungen. Paketverzeichnisse haben ebenfalls eine primäre Paketbeschreibung; die verlinkten READMEs stellen beide ausführlichen Fassungen bereit.
