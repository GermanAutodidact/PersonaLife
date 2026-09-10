# Occupations, routines and travel

Presets: office_worker, developer, bartender, retail_worker, student, freelancer, performer, electrician, shift_worker, unemployed. All use the same generic occupation model.

```json
{
  "title": "bartender",
  "employer": "Example Bar",
  "employment_type": "part_time",
  "workweek": {"tuesday": ["17:00", "01:00"], "friday": ["19:00", "03:00"]},
  "workplace": "work",
  "commute_minutes": 25,
  "coworkers": ["lisa"],
  "task_types": ["Customer service", "Closing the bar"],
  "variability": {"overtime_probability": 0.1, "overtime_minutes": 30},
  "exceptions": {
    "2026-09-11": {"leave": "vacation"},
    "2026-09-15": {"leave": "sick"},
    "2026-09-18": ["18:00", "02:00"],
    "2026-09-22": {"shift": ["10:00", "14:00"], "location": "home"}
  }
}
```

An end time less than or equal to its start means the next civil day. Leave removes work on the specified shift-start date; overnight work started the previous date still belongs to that previous shift. Weekly schedules plus exceptions also represent home office, irregular work, freelance assignments and class periods. Coworkers must already exist in `relationships`.

Work includes preparation, task blocks, a break for sufficiently long shifts, travel and post-shift sleep. Optional overtime is deterministic for a persona seed and date. Small narrative variations are selected after completed activities. The planner does not simulate a full business, employee roster or customer queue.

A routine contains id, title, location, minutes, preferred time and frequency. Use `weekdays` with weekly frequency, `month_day` with monthly frequency, or an explicit `dates` list with custom frequency. Set `hard: true` for an appointment. Routine priorities default to 60; meals use 70, hobbies 40 and free time 20. Custom hard overlaps are rejected rather than silently erased.

Locations are persistent IDs. `travel_times` uses edges such as `home->shop: 15`. Reverse edges are inferred unless separately configured. The route engine finds shortest configured graph paths, including through home. No geographic speed is guessed. A missing route raises an actionable configuration error.

Profile updates affect subsequent day generation. They do not silently regenerate an already-audited day; use explicit `reschedule` for existing work. Home/timezone migrations of a live persona are currently refused to avoid invalidating historical civil-day meaning.
