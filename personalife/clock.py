"""Civil-time boundaries; arithmetic always uses absolute UTC instants."""
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

UTC = timezone.utc

def instant(value):
    value = datetime.fromisoformat(value) if isinstance(value, str) else value
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Timezone-aware timestamp required")
    return value.astimezone(UTC)

def stamp(value):
    return instant(value).isoformat()

def civil(day, hour, zone, fold=0):
    day = date.fromisoformat(day) if isinstance(day, str) else day
    naive = datetime.combine(day, time.fromisoformat(hour))
    local = naive.replace(tzinfo=ZoneInfo(zone), fold=fold)
    result = instant(local)
    if result.astimezone(ZoneInfo(zone)).replace(tzinfo=None) != naive:
        raise ValueError(f"Nonexistent local time: {day} {hour} in {zone}")
    return result

def bounds(day, zone):
    day = date.fromisoformat(day) if isinstance(day, str) else day
    return civil(day, "00:00", zone), civil(day + timedelta(days=1), "00:00", zone)

def local_date(value, zone):
    return instant(value).astimezone(ZoneInfo(zone)).date()

def minutes(value):
    return timedelta(minutes=value)
