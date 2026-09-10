"""Occupation templates are editable data, not special cases in the engine."""
import copy
from .domain import WEEKDAYS
from .i18n import tr, language as normalize_language

PRESETS = {}
for title, days, start, end, tasks in [
 ('office_worker',range(5),'09:00','17:00',['Meetings','Administration']),
 ('developer',range(5),'09:00','17:00',['Development','Code review']),
 ('bartender',range(1,6),'17:00','01:00',['Customer service','Closing the bar']),
 ('retail_worker',range(1,6),'10:00','18:00',['Stocking','Customer service']),
 ('student',range(5),'09:00','14:00',['Lectures','Study group']),
 ('freelancer',[0,2,4],'10:00','15:00',['Client project','Planning']),
 ('performer',[2,4,5],'18:00','23:00',['Rehearsal','Performance']),
 ('electrician',range(5),'07:00','15:00',['Installation','Inspection']),
 ('shift_worker',[0,1,3,4],'19:00','03:00',['Operations','Shift handover']),
 ('unemployed',[],'09:00','17:00',['Personal project','Job search'])]:
    PRESETS[title]=dict(title=title,employer='Example employer',employment_type='part_time' if title=='bartender' else 'custom',
        workweek={WEEKDAYS[d]:[start,end] for d in days},workplace='home' if title in {'freelancer','unemployed'} else 'work',
        commute_minutes=0 if title in {'freelancer','unemployed'} else 25,
        coworkers=[],task_types=tasks,exceptions={})

def get_presets(language='en'):
    language=normalize_language(language)
    result=copy.deepcopy(PRESETS)
    for key,o in result.items():
        o['label']=tr(key,language)
        o['employer']=tr(o['employer'],language)
        o['task_types']=[tr(t,language) for t in o['task_types']]
    return result

def persona(name='Jenna',pid='jenna',occupation='bartender',language='en'):
    language=normalize_language(language)
    o=get_presets(language)[occupation]
    o['coworkers']=['lisa'] if occupation!='unemployed' else []
    p = dict(id=pid,name=name,language=language,age=25,timezone='Europe/Berlin',home='home',seed=42,
        occupation=o,locations=[{'id':'home','name':'Home'},{'id':'work','name':'Workplace'},
                              {'id':'shop','name':'Supermarket'},{'id':'gym','name':'Gym'}],
        travel_times={'home->shop':15,'home->gym':20},sleep={'start':'23:00','hours':8},
        hobbies=['Gaming','Reading','Music'],relationships=[dict(id='lisa',name='Lisa',relationship_type='coworker',
            personality_tags=['helpful','funny'],strength=55,availability='work shifts',location='work',occupation='coworker')],
        routines=[dict(id='shopping',title='Shopping',kind='routine',time='14:00',minutes=45,location='shop',frequency='weekly',weekdays=[1,4],priority=70),
                  dict(id='cleaning',title='Clean apartment',kind='routine',time='12:00',minutes=60,location='home',frequency='daily',priority=60)])

    for location in p["locations"]:
        location["name"]=tr(location["name"],language)
    p["hobbies"]=[tr(h,language) for h in p["hobbies"]]
    for routine in p["routines"]:
        routine["title"]=tr(routine["title"],language)
    for relationship in p['relationships']:
        relationship['personality_tags']=[tr(t,language) for t in relationship['personality_tags']]
        relationship['availability']=tr(relationship['availability'],language)
        relationship['occupation']=tr(relationship['occupation'],language)
    return p
