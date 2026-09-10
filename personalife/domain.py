"""Validated, JSON-serializable domain values, independent of model vendors."""
import copy
import math
from datetime import date, time
from zoneinfo import ZoneInfo
from .clock import instant
from .i18n import language

STATES = {"planned", "active", "paused", "blocked", "completed", "cancelled", "missed", "abandoned"}
TERMINAL = {"completed", "cancelled", "missed", "abandoned"}
WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

def number(value, low, high, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f"{name} must be between {low} and {high}")
    return value

def text_value(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be nonempty text")
    return value


def civil_time(value):
    text_value(value, "Civil time")
    result = time.fromisoformat(value)
    if result.tzinfo is not None:
        raise ValueError("Civil schedule times must not include UTC offsets")
    return result


def shift_pair(value):
    if value is None:
        return
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError("Shift requires a two-element start/end list or null")
    start, end = map(civil_time, value)
    seconds = lambda t: t.hour * 3600 + t.minute * 60 + t.second + t.microsecond / 1e6
    duration = (seconds(end) - seconds(start)) % 86400 or 86400
    if duration > 16 * 3600:
        raise ValueError("Shift exceeds 16 nominal hours")


def validate_profile_structure(p):
    if not isinstance(p, dict):
        raise ValueError("Persona must be a JSON object")
    for key in ("id", "name", "timezone", "home"):
        text_value(p.get(key), key)
    for key in ("occupation", "sleep", "travel_times"):
        if key in p and not isinstance(p[key], dict):
            raise ValueError(f"{key} must be an object")
    for key in ("locations", "relationships", "routines", "hobbies"):
        if key in p and not isinstance(p[key], list):
            raise ValueError(f"{key} must be a list")
    for key in ("locations", "relationships", "routines"):
        seen = set()
        for item in p.get(key, []):
            if not isinstance(item, dict):
                raise ValueError(f"{key} entries must be objects")
            identifier = text_value(item.get("id"), key + " ID")
            if identifier in seen:
                raise ValueError(f"Duplicate {key} ID: {identifier}")
            seen.add(identifier)
    for hobby in p.get("hobbies", []):
        text_value(hobby, "Hobby")
    locations = {x["id"] for x in p.get("locations", [{"id": p["home"]}])}
    relationships = {x["id"] for x in p.get("relationships", [])}
    for r in p.get("relationships", []):
        text_value(r.get("name"), "Relationship name")
    for edge in p.get("travel_times", {}):
        if not isinstance(edge, str) or len(edge.split("->")) != 2:
            raise ValueError("Travel edge must have origin->destination form")
        if not set(edge.split("->")) <= locations:
            raise ValueError("Unknown travel edge endpoint")
    occ = p.get("occupation", {})
    text_value(occ.get("title"), "Occupation title")
    for key in ("workweek", "exceptions", "variability"):
        if not isinstance(occ.get(key, {}), dict):
            raise ValueError(f"Occupation {key} must be an object")
    for key in ("coworkers", "task_types"):
        if key in occ and not isinstance(occ[key], list):
            raise ValueError(f"Occupation {key} must be a list")
        for value in occ.get(key, []):
            text_value(value, key)
    if "task_types" in occ and not occ["task_types"]:
        raise ValueError("Occupation needs at least one task type")
    for value in occ.get("workweek", {}).values():
        shift_pair(value)
    for day, exception in occ.get("exceptions", {}).items():
        date.fromisoformat(day)
        if isinstance(exception, dict):
            leave = exception.get("leave")
            if leave is not None and leave not in {"vacation", "sick", "off"}:
                raise ValueError("Unknown leave type")
            if leave is None and "shift" not in exception:
                raise ValueError("Work exception requires a shift or leave")
            if exception.get("location", occ.get("workplace", p["home"])) not in locations:
                raise ValueError("Unknown exception workplace")
            shift_pair(exception.get("shift"))
        else:
            shift_pair(exception)
    variation = occ.get("variability", {})
    for key, value in variation.items():
        if key.endswith("_probability"):
            number(value, 0, 1, key)
    if "overtime_minutes" in variation:
        number(variation["overtime_minutes"], 0, 480, "overtime minutes")
    if "sleep" in p:
        civil_time(p["sleep"].get("start"))
    for r in p.get("routines", []):
        civil_time(r.get("time", "12:00"))
        weekdays = r.get("weekdays", [0])
        if not isinstance(weekdays, list) or any(type(d) is not int or not 0 <= d <= 6 for d in weekdays):
            raise ValueError("Routine weekdays must be integers from 0 through 6")
        if type(r.get("month_day", 1)) is not int or not 1 <= r.get("month_day", 1) <= 31:
            raise ValueError("Routine month_day must be an integer from 1 through 31")
        dates = r.get("dates", [])
        if not isinstance(dates, list):
            raise ValueError("Custom routine dates must be a list")
        for day in dates:
            date.fromisoformat(day)
        participants = r.get("participants", [])
        if not isinstance(participants, list) or any(not isinstance(x, str) or x not in relationships for x in participants):
            raise ValueError("Routine participants must reference known relationships")


def validate_persona(raw):
    p = copy.deepcopy(raw)
    validate_profile_structure(p)
    p["language"] = language(p.get("language", "en"))
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
