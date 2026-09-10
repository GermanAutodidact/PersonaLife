"""Event-boundary catch-up, optional inexpensive daemon, no background LLM calls."""
import threading
from datetime import datetime,timezone
from .clock import bounds,instant
from .service import PersonaLife

def tick(database,now=None,memory=None):
    now=now or datetime.now(timezone.utc)
    with PersonaLife(database,memory=memory) as app:
        ids=list(dict.fromkeys(e['persona'] for e in app.ledger.read()))
        results=[]
        for pid in ids:
            app.advance_to(pid,now)
            s=app._s(pid)
            for day in s['days']:
                if bounds(day,s['persona']['timezone'])[1]<=instant(now):app.close_day(pid,day)
            results.append(app.get_current_state(pid))
        return results

def run(database,interval_minutes=15,stop=None):
    if interval_minutes<=0:raise ValueError('Heartbeat interval must be positive')
    stop=stop or threading.Event()
    while not stop.is_set():
        tick(database)
        stop.wait(interval_minutes*60)
