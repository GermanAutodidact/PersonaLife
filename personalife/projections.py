"""Disposable projections reconstructed exclusively from canonical events."""
import copy
from .clock import instant

def project(events):
    s = {"persona": None, "cursor": None, "activities": {}, "original": {}, "actual": [],
         "days": [], "closed": {}, "chat": None, "chats": {}, "stories": [], "hooks_used": [],
         "location": None, "relationships": {}, "exports": [],
         "state": {"energy": 70, "stress": 20, "mood_valence": 60, "social_energy": 70, "hunger": 20, "fatigue": 30}}
    for e in events:
        d, k = copy.deepcopy(e["data"]), e["kind"]
        if k in {"PERSONA_CREATED", "PERSONA_UPDATED"}:
            s["persona"] = d
            for r in d["relationships"]:
                s["relationships"].setdefault(r["id"], r)
            if k == "PERSONA_CREATED":
                s["cursor"], s["location"] = e["at"], d["home"]
        elif k == "DAY_PLANNED":
            s["days"].append(d["date"])
        elif k == "ACTIVITY_PLANNED":
            s["activities"][d["id"]] = d
            s["original"][d["id"]] = copy.deepcopy(d)
        elif k == "ACTIVITY_CHANGED":
            s["activities"][d.pop("id")].update(d)
        elif k == "ACTUAL_SEGMENT":
            s["actual"].append({**d, "event_id": e["id"]})
            if d.get("activity_id"):
                a = s["activities"][d["activity_id"]]
                a["progress"] += (instant(d["end"]) - instant(d["start"])).total_seconds()
            s["state"] = d["state"]
            s["location"] = d["location_after"]
        elif k == "CLOCK_ADVANCED":
            s["cursor"] = e["at"]
        elif k == "CHAT_STARTED":
            s["chat"] = d
            s["chats"][d["id"]] = d
        elif k == "CHAT_ENDED":
            s["chats"][d["id"]].update(d)
            s["chat"] = None
        elif k == "STORY_EVENT":
            s["stories"].append({**d, "event_id": e["id"], "at": e["at"]})
            for rid in d.get("participants", []):
                r = s["relationships"][rid]
                r["strength"] = min(100, max(0, r.get("strength", 50) + d.get("relationship_delta", 1)))
                r["last_interaction"] = e["at"]
                r.setdefault("shared_history", []).append(e["id"])
        elif k == "DAY_CLOSED":
            s["closed"][d["date"]] = d
        elif k == "MEMORY_EXPORTED":
            s["exports"].append(d["key"])
        elif k == "HOOK_USED":
            s["hooks_used"].append(d["event_id"])
    return s
