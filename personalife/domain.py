"""Validated, JSON-serializable domain values, independent of model vendors."""
import copy
import math
from datetime import date, time
from zoneinfo import ZoneInfo
from .clock import instant

STATES = {"planned", "active", "paused", "blocked", "completed", "cancelled", "missed", "abandoned"}
TERMINAL = {"completed", "cancelled", "missed", "abandoned"}
WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

def number(value, low, high, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f"{name} must be between {low} and {high}")
    return value

def validate_persona(raw):
    p = copy.deepcopy(raw)
    for key in ("id", "name", "timezone", "home", "occupation"):
        if not p.get(key):
            raise ValueError(f"Persona requires {key}")
    ZoneInfo(p["timezone"])
    number(p.get("age", 18), 0, 200, "age")
    p.setdefault("seed", 1)
    p.setdefault("hobbies", ["reading"])
    p.setdefault("routines", [])
    p.setdefault("relationships", [])
    p.setdefault("locations", [{"id": p["home"], "name": "Home"}])
    ids = [x["id"] for x in p["locations"]]
    if len(ids) != len(set(ids)) or p["home"] not in ids:
        raise ValueError("Location IDs must be unique and include home")
    p.setdefault("travel_times", {})
    for value in p["travel_times"].values():
        number(value, 1, 1440, "travel minutes")
    p.setdefault("sleep", {"start": "23:00", "hours": 8})
    time.fromisoformat(p["sleep"]["start"])
    number(p["sleep"]["hours"], 1, 16, "sleep hours")
    occ = p["occupation"]
    if not isinstance(occ, dict) or not occ.get("title"):
        raise ValueError("Occupation title required; unemployed is a valid occupation")
    occ.setdefault("workweek", {})
    occ.setdefault("workplace", p["home"])
    occ.setdefault("commute_minutes", 0)
    occ.setdefault("coworkers", [])
    occ.setdefault("task_types", ["preparation", "main tasks", "closing"])
    occ.setdefault("exceptions", {})
    if occ["workplace"] not in ids:
        raise ValueError("Unknown workplace")
    number(occ["commute_minutes"], 0, 1440, "commute")
    if occ["workplace"] != p["home"] and not occ["commute_minutes"]:
        raise ValueError("Nonremote work requires positive commute time")
    for k, shift in occ["workweek"].items():
        if k not in WEEKDAYS:
            raise ValueError("Invalid weekday")
        if shift:
            if len(shift) != 2:
                raise ValueError("Shift requires start and end")
            for t in shift:
                time.fromisoformat(t)
    for d, exception in occ["exceptions"].items():
        date.fromisoformat(d)
        if exception is not None and not isinstance(exception, (list, dict)):
            raise ValueError("Work exception must be null, shift pair or configuration")
    rid = [r["id"] for r in p["relationships"]]
    if len(rid) != len(set(rid)) or not set(occ["coworkers"]) <= set(rid):
        raise ValueError("Coworkers must reference unique persistent relationships")
    for r in p["relationships"]:
        r.setdefault("strength", 50)
        number(r["strength"], 0, 100, "relationship strength")
        r.setdefault("shared_history", [])
    for r in p["routines"]:
        validate_routine(r, ids)
    return p

def validate_routine(r, locations):
    if not r.get("id") or not r.get("title"):
        raise ValueError("Routine id/title required")
    if r.get("location") not in locations:
        raise ValueError("Unknown routine location")
    number(r.get("minutes"), 1, 1440, "routine duration")
    number(r.get("priority", 60), 0, 100, "priority")
    if r.get("frequency", "daily") not in {"daily", "weekday", "weekend", "weekly", "monthly", "custom"}:
        raise ValueError("Unknown recurrence")
    time.fromisoformat(r.get("time", "12:00"))

def validate_activity(a):
    if instant(a["end"]) <= instant(a["start"]):
        raise ValueError("Activity must have positive duration")
    if a["state"] not in STATES:
        raise ValueError("Unknown activity state")
    number(a["required"], 0.0001, 172800, "required seconds")
    number(a.get("progress", 0), 0, a["required"] + 0.001, "progress")
    number(a.get("priority", 50), 0, 100, "priority")
    return a
