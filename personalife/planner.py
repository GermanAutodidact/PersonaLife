"""Deterministic occupation/routine planner with travel and civil-day coverage."""
import hashlib
import random
from datetime import date, timedelta
from .clock import civil, bounds, stamp, instant, minutes
from .domain import WEEKDAYS, validate_activity
from .i18n import tr


def stable_rng(persona, key):
    return random.Random(hashlib.sha256(f"{persona['id']}:{persona['seed']}:{key}".encode()).digest())


def travel_time(p, origin, destination):
    if origin == destination:
        return 0
    o = p['occupation']
    if {origin, destination} == {p['home'], o['workplace']}:
        return o['commute_minutes']
    key = f'{origin}->{destination}'
    reverse = f'{destination}->{origin}'
    if key in p['travel_times'] or reverse in p['travel_times']:
        return p['travel_times'].get(key, p['travel_times'].get(reverse))
    # Configured graph routes may pass through home; unknown paths are errors.
    graph = {}
    for edge, duration in p['travel_times'].items():
        a, b = edge.split('->')
        graph.setdefault(a, {})[b] = duration
        graph.setdefault(b, {}).setdefault(a, duration)
    if o['workplace'] != p['home']:
        graph.setdefault(p['home'], {})[o['workplace']] = o['commute_minutes']
        graph.setdefault(o['workplace'], {})[p['home']] = o['commute_minutes']
    costs, todo = {origin: 0}, [(0, origin)]
    import heapq
    while todo:
        cost, node = heapq.heappop(todo)
        if node == destination:
            return cost
        for next_node, length in graph.get(node, {}).items():
            if cost + length < costs.get(next_node, float('inf')):
                costs[next_node] = cost + length
                heapq.heappush(todo, (cost + length, next_node))
    raise ValueError(f'No travel route: {origin} -> {destination}')


def activity(pid, key, title, kind, start, end, location, priority=50, **extra):
    aid = hashlib.sha256(f'{pid}:{key}'.encode()).hexdigest()[:24]
    a = dict(id=aid, title=title, kind=kind, start=stamp(start), end=stamp(end),
             location=location, priority=priority, state='planned', progress=0.0,
             required=(instant(end)-instant(start)).total_seconds(), interruptible=priority < 80,
             hard=priority >= 80, **extra)
    return validate_activity(a)


def shift(p, day):
    o = p['occupation']
    entry = o['exceptions'].get(day.isoformat(), o['workweek'].get(WEEKDAYS[day.weekday()]))
    location = o['workplace']
    if isinstance(entry, dict):
        if entry.get('leave') in {'vacation', 'sick', 'off'}:
            return None
        location = entry.get('location', location)
        entry = entry.get('shift')
    if not entry:
        return None
    start = civil(day, entry[0], p['timezone'])
    end = civil(day + timedelta(days=int(entry[1] <= entry[0])), entry[1], p['timezone'])
    if (end-start).total_seconds() > 16*3600:
        raise ValueError('Shift exceeds 16 hours; check configuration')
    variation=o.get('variability',{})
    rng=stable_rng(p,'shift:'+day.isoformat())
    if rng.random()<variation.get('overtime_probability',0):
        end+=minutes(variation.get('overtime_minutes',30))
    return start, end, location


def recurrence(r, day):
    f = r.get('frequency', 'daily')
    return (f == 'daily' or f == 'weekday' and day.weekday() < 5 or
            f == 'weekend' and day.weekday() >= 5 or
            f == 'weekly' and day.weekday() in r.get('weekdays', [0]) or
            f == 'monthly' and day.day == r.get('month_day', 1) or
            f == 'custom' and day.isoformat() in r.get('dates', []))


def plan_day(p, day, existing, cursor):
    day = date.fromisoformat(day) if isinstance(day, str) else day
    lo, hi = bounds(day, p['timezone'])
    lo = max(lo, instant(cursor))
    if hi <= lo:
        raise ValueError('Cannot plan a fully elapsed day')
    pid = p['id']
    label = lambda message, **values: tr(message,p.get('language','en'),**values)
    occupied = [a for a in existing if a['state'] not in {'cancelled', 'missed', 'abandoned'} and instant(a['end']) > lo and instant(a['start']) < hi]
    out = []

    def overlap(s, e):
        return [a for a in occupied + out if instant(a['start']) < e and instant(a['end']) > s]

    def add(key, title, kind, s, e, loc, priority=50, **extra):
        if e <= lo or s >= hi:
            return
        s = max(s, lo)
        if s >= e:
            return
        a = activity(pid, f'{day}:{key}', title, kind, s, e, loc, priority, **extra)
        if overlap(s, e):
            return False
        out.append(a)
        return a

    # Work blocks include explicit preparation, tasks and a break. Overnight
    # shifts are stored whole, never duplicated at midnight.
    for sd in (day-timedelta(days=1), day):
        sh = shift(p, sd)
        if not sh:
            continue
        s, e, location = sh
        route = minutes(travel_time(p, p['home'], location))
        if e + route <= lo or s-route >= hi:
            continue
        if any(a.get('shift_date') == sd.isoformat() for a in occupied):
            continue
        add(f'{sd}:commute-out', label('Travel to work'), 'travel', s-route, s, location, 90,
            origin=p['home'], shift_date=sd.isoformat()) if route else None
        # Check each contiguous occupation block rather than assuming planned work happened.
        points = [(s, min(s+minutes(15), e), label('Preparation'), 'work')]
        if e-s > minutes(90):
            mid = s+(e-s)/2
            points += [(points[0][1], mid, p['occupation']['task_types'][0], 'work'),
                       (mid, min(mid+minutes(20), e), label('Work break'), 'break'),
                       (min(mid+minutes(20), e), e, p['occupation']['task_types'][-1], 'work')]
        elif points[0][1] < e:
            points.append((points[0][1], e, label('Work tasks'), 'work'))
        for i, (a,b,title,kind) in enumerate(points):
            added = add(f'{sd}:work:{i}', title, kind, a,b,location,100,
                        shift_date=sd.isoformat(), participants=p['occupation']['coworkers'], deadline=stamp(a))
            if added is False:
                raise ValueError('Work overlaps an existing commitment')
        if route:
            add(f'{sd}:commute-home', label('Travel home'), 'travel', e,e+route,p['home'],90,
                origin=location, shift_date=sd.isoformat())

    # Sleep follows a prior late shift and its commute instead of resetting at 00:00.
    bedtime = civil(day-timedelta(days=1), p['sleep']['start'],p['timezone'])
    prev = shift(p,day-timedelta(days=1))
    if prev:
        bedtime = max(bedtime, prev[1]+minutes(travel_time(p,prev[2],p['home']))+minutes(30))
    # Delays from the previous day's executed/rescheduled occupation take priority.
    late_ends=[instant(a['end']) for a in occupied if a['kind'] in {'work','travel'}
               and instant(a['end']) <= civil(day,'12:00',p['timezone'])]
    if late_ends:
        bedtime=max(bedtime,max(late_ends)+minutes(30))
    wake = bedtime + timedelta(hours=p['sleep']['hours'])
    for key, s,e in [('sleep-morning',bedtime,wake),
                     ('sleep-night',civil(day,p['sleep']['start'],p['timezone']),hi)]:
        # Sleep after today's late shift is generated with tomorrow's morning block.
        if e>s and not overlap(max(s,lo),e):
            add(key,label('Sleep'),'sleep',s,e,p['home'],75)

    def fit(r, key, desired, duration, priority):
        location = r.get('location', p['home'])
        route = minutes(travel_time(p,p['home'],location))
        s = max(desired,lo+route)
        for _ in range(200):
            e = s+duration
            hits = overlap(s-route,e+route)
            if not hits:
                if e+route > hi:
                    return False
                if route:
                    add(key+':out',label('Travel to {location}',location=next((place.get('name',location) for place in p['locations'] if place['id']==location),location)),'travel',s-route,s,location,priority,origin=p['home'])
                add(key,r['title'],r.get('kind','routine'),s,e,location,priority,
                    goal=r.get('goal'), participants=r.get('participants', []))
                if route:
                    add(key+':home',label('Travel home'),'travel',e,e+route,p['home'],priority,origin=location)
                return True
            if r.get('hard'):
                raise ValueError('Hard routine overlaps another obligation')
            s = max(instant(a['end']) for a in hits)+route
        raise ValueError('Planner failed to find bounded slot')

    for r in sorted(p['routines'], key=lambda r:-r.get('priority',60)):
        if recurrence(r,day):
            fit(r,r['id'],civil(day,r.get('time','12:00'),p['timezone']),minutes(r['minutes']),
                80 if r.get('hard') else r.get('priority',60))
    for i,h in enumerate([8,13,19]):
        fit({'title':label('Meal'),'kind':'meal'},f'meal:{i}',civil(day,f'{h:02}:00',p['timezone']),minutes(30),70)
    rng = stable_rng(p, day.isoformat())
    if p['hobbies']:
        fit({'title':rng.choice(p['hobbies']),'kind':'hobby'},'hobby',civil(day,'15:00',p['timezone']),minutes(60),40)
    # Explicit idle/rest blocks cover remaining civil-day intervals, including
    # 23/25-hour DST days. They are expendable when chats/commitments shift.
    all_blocks = sorted(occupied+out,key=lambda a:a['start'])
    pos = lo
    for i,a in enumerate(all_blocks):
        start,end = instant(a['start']),instant(a['end'])
        if start>pos:
            add(f'rest:{i}',label('Free time'),'rest',pos,min(start,hi),p['home'],20)
        pos=max(pos,end)
    if pos<hi:
        add('rest:last',label('Free time'),'rest',pos,hi,p['home'],20)
    return sorted(out,key=lambda a:a['start'])
