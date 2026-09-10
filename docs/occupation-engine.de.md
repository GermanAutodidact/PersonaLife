# Berufe, Routinen und Wege

[English](occupation-engine.md)

Die Vorlagen heißen office_worker, developer, bartender, retail_worker, student, freelancer, performer, electrician, shift_worker und unemployed. Alle verwenden dasselbe allgemeine Berufsmodell. Die Kennungen bleiben sprachunabhängig; die Bedienung zeigt zusätzlich übersetzte Bezeichnungen.

```json
{
  "title": "Barkeeperin",
  "employer": "Beispielbar",
  "employment_type": "part_time",
  "workweek": {"tuesday": ["17:00", "01:00"], "friday": ["19:00", "03:00"]},
  "workplace": "work",
  "commute_minutes": 25,
  "coworkers": ["lisa"],
  "task_types": ["Gäste bedienen", "Bar abschließen"],
  "variability": {"overtime_probability": 0.1, "overtime_minutes": 30},
  "exceptions": {
    "2026-09-11": {"leave": "vacation"},
    "2026-09-15": {"leave": "sick"},
    "2026-09-18": ["18:00", "02:00"],
    "2026-09-22": {"shift": ["10:00", "14:00"], "location": "home"}
  }
}
```

Liegt die Endzeit vor oder gleich der Startzeit, ist der nächste lokale Kalendertag gemeint. Abwesenheit entfernt die Arbeit am angegebenen Schichtbeginn-Datum; eine Nachtschicht des Vortags gehört weiterhin zu diesem Vortag. Wochenpläne plus Ausnahmen können auch Heimarbeit, unregelmäßige Arbeit, freiberufliche Aufträge und Unterricht abbilden. Kollegen müssen in `relationships` vorhanden sein.

Arbeit umfasst Vorbereitung, Aufgabenblöcke, bei hinreichend langen Schichten eine Pause, Wege und Schlaf nach der Schicht. Optionale Überstunden sind für Persona-Zufallsstartwert und Datum reproduzierbar. Kleine Erzählvariationen entstehen nach abgeschlossenen Aktivitäten. Die Planung simuliert keinen vollständigen Betrieb, Personalplan oder Warteschlangen von Kunden.

Eine Routine enthält id, title, location, minutes, bevorzugte Uhrzeit und frequency. Wöchentliche Routinen nutzen `weekdays`, monatliche `month_day`, eigene Wiederholungen eine ausdrückliche Liste `dates`. `hard: true` kennzeichnet einen festen Termin. Routinen haben standardmäßig Priorität 60, Mahlzeiten 70, Hobbys 40 und Freizeit 20. Sich überschneidende eigene feste Termine werden abgewiesen statt still gelöscht.

Orte besitzen dauerhafte Kennungen. `travel_times` enthält Verbindungen wie `home->shop: 15`. Rückwege werden angenommen, sofern sie nicht ausdrücklich anders konfiguriert sind. Die Wegberechnung sucht die kürzeste konfigurierte Verbindung, gegebenenfalls über das Zuhause. Sie schätzt keine geografische Geschwindigkeit. Eine fehlende Verbindung führt zu einem Konfigurationsfehler.

Profiländerungen beeinflussen die spätere Tagesplanung. Ein bereits protokollierter Tag wird dadurch nicht still neu erzeugt; vorhandene Aktivitäten werden ausdrücklich mit `reschedule` verschoben. Ein Wechsel von Zuhause oder Zeitzone einer bestehenden Persona wird derzeit abgewiesen, um die Bedeutung historischer Kalendertage zu erhalten.
