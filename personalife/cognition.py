"""Bounded affect updates, evidence-based ranking and deterministic story events."""
import math
from .clock import instant
from .planner import stable_rng
from .i18n import tr

RATES = {
 'sleep': {'energy': 7,'fatigue':-7,'stress':-2,'hunger':2},
 'work': {'energy':-5,'fatigue':5,'stress':3,'hunger':4,'social_energy':-3},
 'travel': {'energy':-3,'fatigue':3,'stress':1,'hunger':3},
 'meal': {'energy':4,'hunger':-70,'stress':-3},
 'chat': {'energy':-1,'social_energy':-2,'mood_valence':2,'stress':-1,'hunger':3},
 'rest': {'energy':2,'fatigue':-2,'stress':-2,'hunger':3},
 'break': {'energy':3,'fatigue':-3,'stress':-3,'hunger':2},
 'hobby': {'energy':-1,'stress':-3,'mood_valence':2,'hunger':3},
 'routine': {'energy':-3,'fatigue':3,'stress':-1,'hunger':3},
}

def evolve(state,kind,seconds):
    return {k: max(0,min(100,v+RATES.get(kind,RATES['routine']).get(k,0)*seconds/3600)) for k,v in state.items()}

def story_for(p,a):
    rng=stable_rng(p,a['id'])
    if a['kind'] not in {'work','hobby','routine'} or rng.random() > .65:
        return None
    people=a.get('participants',[])
    names={r['id']:r['name'] for r in p['relationships']}
    lang=p.get('language','en')
    who=names.get(people[0],tr('Someone',lang)) if people else None
    templates = (["{who} and I solved a small problem during {title}.",
                  "{who} made me laugh during {title}.",
                  "{title} was unusually busy; we helped each other."] if who else
                 ["I made satisfying progress with {title}.",
                  "A small mistake during {title} gave me an idea for next time."])
    options=[tr(message,lang,who=who,title=a['title']) for message in templates]
    importance=rng.randint(3,7)
    return dict(description=rng.choice(options),participants=people,location=a['location'],
                activity_id=a['id'],importance=importance,novelty=rng.randint(4,9),
                emotional_intensity=rng.randint(3,7),social_relevance=7 if people else 3,
                source='deterministic_simulation',confidence=1.0,relationship_delta=1)

def scores(event,now,query=''):
    age=max(0,(instant(now)-instant(event['at'])).total_seconds()/86400)
    tell=(event.get('importance',0)*.2+event.get('novelty',0)*.35+
          event.get('emotional_intensity',0)*.25+event.get('social_relevance',0)*.2)
    relevance=len(set(query.casefold().split()) & set(event['description'].casefold().split()))
    return dict(tellability=tell, memory_score=event.get('importance',0)*.6+event.get('social_relevance',0)*.4,
                retrieval_score=tell*math.exp(-age/30)+relevance*2)

def hooks(s,now,limit=5):
    candidates=[]
    for e in s['stories']:
        if e['event_id'] not in s['hooks_used'] and instant(e['at'])<=instant(now):
            candidates.append({**e,**scores(e,now),'type':'actual'})
    candidates.sort(key=lambda e:e['retrieval_score'],reverse=True)
    result=candidates[:limit]
    if len(result)<limit:
        for a in sorted(s['activities'].values(),key=lambda x:x['start']):
            if a['state'] in {'planned','paused'} and instant(a['start'])>=instant(now) and a['priority']>=70:
                result.append(dict(type='plan',activity_id=a['id'],description=a['title'],start=a['start']))
                if len(result)>=limit:break
    return result

def flashbacks(s,now,query='',limit=1):
    candidates=[{**e,**scores(e,now,query)} for e in s['stories']
                if (instant(now)-instant(e['at'])).total_seconds()>7*86400
                and e['event_id'] not in s['hooks_used']
                and (e.get('location')==s['location'] or query.casefold() in e['description'].casefold() and query)]
    # At most one candidate, deterministic 1/8 daily opportunity.
    rng=stable_rng(s['persona'],'flashback:'+instant(now).date().isoformat())
    return sorted(candidates,key=lambda x:x['retrieval_score'],reverse=True)[:min(limit,1)] if rng.randrange(8)==0 else []
