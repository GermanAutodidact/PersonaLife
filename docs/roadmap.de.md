# Weiterentwicklung und Veröffentlichungsreife

[English](roadmap.md)

Dies sind offene Entwicklungsrichtungen, keine Zusagen umgesetzter Funktionen oder Liefertermine.

## Funktionierende Grundlage für Entwickler

Ereignisbasierte Speicherung, Tagesplanung, Berufsvorlagen, Wege, Gesprächs-Neuplanung, begrenzte Zustandswerte, dauerhafte Beziehungen, Erinnerungsschnittstellen, Kommandozeile und lokale HTTP-API sind implementiert und automatisiert getestet. Die Demo zeigt drei zusammenhängende Tage.

## Nächste technische Prioritäten

1. Längere zufallsgesteuerte Simulationen und strengere Bedingungen für sämtliche Reise- und Planungsübergänge.
2. Dauerhafte Rekonstruktions-Checkpoints und wiederholbare Lastmessungen für monatelange Charakterhistorien.
3. Weitere Konfliktregeln für verpasste Verpflichtungen, nicht passende Routinen und Ziele mit mehreren Aktivitäten.
4. Vielfältigere berufliche und soziale Ereignisse mit nachvollziehbaren Ergebnissen.
5. Eine kleine vollständige Chat-Integration mit Sitzungsablauf und am Protokoll orientierten Modellantworten.
6. Integrationstests mit optionalen Anbietern einschließlich Wiederholungen und Duplikatvermeidung.

## Vor der Bezeichnung als produktionsreif

Betriebsgrenzen dokumentieren, Migrationen und Wiederherstellung prüfen, dauerhaft laufende Dienste testen und mindestens eine unterstützte Chat-Anwendung vollständig anbinden. Erfolgreiche Unit-Tests allein belegen diese Eigenschaften nicht.

## Öffentliche Vorstellung und Auffindbarkeit

Die englische und deutsche Dokumentation erklären Zielgruppe, konkreten Nutzen, unterstütztes Verhalten und Grenzen mit demselben Umfang. Paketmetadaten verweisen auf Quellcode, Dokumentation und Fehlermeldungen. Vorschläge für GitHubs About-Feld und passende Topics liegen in `repository-metadata.json`; diese Datei ändert keine Repository-Einstellungen automatisch.

Für eine öffentliche Vorstellung bleiben sinnvoll: About/Topics anwenden, eine kurze tatsächliche Demonstration aufnehmen, eine ausdrücklich eingegrenzte Veröffentlichung erstellen und das Projekt in passenden Entwicklergemeinschaften vorstellen. Ein PyPI-Paket, eine Veröffentlichungsankündigung und eine eigene Demo-Website wurden nicht veröffentlicht. Klare Metadaten erleichtern Einordnung und Verständnis, garantieren aber keine Besucherzahlen, Rangfolge oder Verbreitung.
