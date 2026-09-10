"""Adversarial consistency checks for executed and planned projections."""
from .clock import instant
from .domain import validate_activity,TERMINAL

def validate(service,pid):
    service.ledger.verify()
    s=service._s(pid);errors=[]
    now=instant(s['cursor'])
    prior=None
    for e in s['actual']:
        start,end=instant(e['start']),instant(e['end'])
        if end<=start:errors.append('Nonpositive actual duration')
        if end>now:errors.append('Future canonical event')
        if prior:
            if start<instant(prior['end']):errors.append('Overlapping actual events')
            if e['location']!=prior['location_after']:errors.append('Impossible location change')
        prior=e
    pending=sorted([a for a in s['activities'].values() if a['state'] not in TERMINAL],key=lambda a:a['start'])
    if not s['chat']:
        for a,b in zip(pending,pending[1:]):
            if instant(b['start'])<instant(a['end']):errors.append('Overlapping planned activities')
    for a in s['activities'].values():
        try:validate_activity(a)
        except (ValueError,KeyError) as ex:errors.append(str(ex))
        actual=sum((instant(e['end'])-instant(e['start'])).total_seconds() for e in s['actual'] if e['activity_id']==a['id'])
        if abs(actual-a['progress'])>.01:errors.append('Activity progress disagrees with actual history')
        if a['state']=='completed' and abs(a['required']-a['progress'])>.01:errors.append('Incomplete activity marked completed')
    for chat in s['chats'].values():
        if not chat.get('end'):continue
        duration=sum((instant(e['end'])-instant(e['start'])).total_seconds() for e in s['actual'] if e['chat_id']==chat['id'])
        expected=(instant(chat['end'])-instant(chat['start'])).total_seconds()
        if abs(duration-expected)>.01:errors.append('Conversation duration mismatch')
    if errors:raise ValueError('; '.join(sorted(set(errors))))
    return {'valid':True,'events':len(service.ledger.read(pid)),'actual_segments':len(s['actual']),'activities':len(s['activities'])}
