# PersonaLife — Ein fortlaufender Alltag für KI-Charaktere

**Dein KI-Charakter hat auch zwischen Gesprächen einen simulierten Alltag.**

PersonaLife ist eine quelloffene Python-Engine für persistente KI-Personas, AI Companions und NPCs. Berufe, Tagespläne, Wege, Beziehungen und Erinnerungen liegen außerhalb des Sprachmodells in einer lokalen SQLite-Datenbank. Du kannst das Modell wechseln und die Geschichte behalten.

Ein Gespräch verändert den Tag: Shopping wird verschoben, Putzen pausiert, der Arbeitsweg kostet weiterhin Zeit. Geplantes und tatsächlich Simuliertes bleiben getrennt und nachvollziehbar.

## Schnell ausprobieren

Python 3.11 oder neuer installieren, das Repository herunterladen oder klonen und im Projektordner ausführen:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install .
.\.venv\Scripts\python.exe examples/three_days.py --output demo-output
```

Die Demo erzeugt drei zusammenhängende Tage mit Chat-Unterbrechungen, Beziehungen, Erinnerungen und überprüfbaren Tagesabläufen. Ein eigener Charakter lässt sich über `personalife persona create` oder die vollständige Beispieldatei `examples/jenna.json` anlegen.

## Was bereits funktioniert

- Zehn Berufsvorlagen und eigene Schichtpläne, einschließlich Nachtschichten und Ausnahmen.
- Tagesroutinen, Schlaf, Reisezeiten und zeitlicher Fortschritt.
- Gesprächsereignisse mit Pause, Fortsetzung und begründeter Umplanung.
- Persistente Beziehungen, einfacher Stimmungszustand und Gesprächsanlässe.
- Lokaler Speicher und AiMemory-Anbindung; optionale weitere Adapter.
- Python-Schnittstelle, lokale HTTP-API, Kommandozeile und automatisierte Tests.

**Stand:** nutzbare Grundlage für Entwickler. Eine grafische Companion-App und eine automatisch installierte ChatGPT-/Gemini-Verbindung sind nicht enthalten. Die simulierten Erlebnisse sind fiktiv; eine Produktionsfreigabe wird nicht behauptet.

[Ausführliche englische Anleitung](README.md) · [Integrationen](docs/integrations.md) · [Geplante Verbesserungen](docs/roadmap.md) · [Testbericht](docs/validation.md)
