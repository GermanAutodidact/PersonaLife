"""Regression coverage for malformed profiles and incremental replay."""
import copy
import tempfile
import unittest
from pathlib import Path
from personalife import PersonaLife,persona,validate
from personalife.projections import project

class ProfileValidationTests(unittest.TestCase):
 def test_invalid_profiles_rejected_before_persistence(self):
  cases=[]
  p=persona();p['routines'].append(copy.deepcopy(p['routines'][0]));cases.append(('duplicate routine IDs',p))
  p=persona();p['occupation']['exceptions']={'2026-09-08':['bad','17:00']};cases.append(('malformed exception time',p))
  p=persona();p['occupation']['exceptions']={'2026-09-08':{'shift':['10:00','12:00'],'location':'moon'}};cases.append(('unknown exception workplace',p))
  p=persona();p['occupation']['variability']={'overtime_probability':-1};cases.append(('invalid probability',p))
  p=persona();p['occupation']['variability']={'overtime_minutes':-30};cases.append(('negative overtime',p))
  p=persona();p['occupation']['task_types']=[];cases.append(('empty work tasks',p))
  p=persona();p['travel_times']['home->moon']=10;cases.append(('unknown route endpoint',p))
  p=persona();p['routines'][0]['weekdays']=[8];cases.append(('invalid recurrence weekday',p))
  p=persona();p['routines'][0]['participants']=['stranger'];cases.append(('unknown routine participant',p))
  p=persona();p['occupation']['workweek']['tuesday']=['09:00+02:00','17:00'];cases.append(('offset in civil shift',p))
  for name,p in cases:
   with self.subTest(case=name),PersonaLife(':memory:') as app:
    with self.assertRaises(ValueError):app.create_persona(p,'2026-09-08T00:00:00+02:00')
    self.assertEqual(app.ledger.read(),[])
 def test_profile_metadata_updates_preserve_learned_relationship(self):
  with PersonaLife(':memory:') as app:
   app.create_persona(persona(),'2026-09-08T00:00:00+02:00')
   app.advance_to('jenna','2026-09-10T00:00:00+02:00')
   before=app.get_relationships('jenna')[0]
   relationships=copy.deepcopy(app._s('jenna')['persona']['relationships'])
   relationships[0]['name']='Lisa Updated'
   app.update_persona('jenna',{'relationships':relationships})
   after=app.get_relationships('jenna')[0]
   self.assertEqual(after['name'],'Lisa Updated')
   for key in ['strength','last_interaction','shared_history']:self.assertEqual(after[key],before[key])

class ReplayTests(unittest.TestCase):
 def test_incremental_matches_full_replay(self):
  with PersonaLife(':memory:') as app:
   app.create_persona(persona(),'2026-09-08T00:00:00+02:00')
   for now in ['2026-09-08T09:00:00+02:00','2026-09-08T16:20:00+02:00','2026-09-10T00:00:00+02:00']:
    app.advance_to('jenna',now)
    self.assertEqual(app._s('jenna'),project(app.ledger.read('jenna')))
   app.close_day('jenna','2026-09-08')
   self.assertEqual(app._s('jenna'),project(app.ledger.read('jenna')))
 def test_rollback_invalidates_incremental_cache(self):
  with PersonaLife(':memory:') as app:
   app.create_persona(persona(),'2026-09-08T00:00:00+02:00')
   before=app._s('jenna')
   with self.assertRaises(RuntimeError):
    with app.ledger.transaction():
     app._advance('jenna','2026-09-08T12:00:00+02:00')
     self.assertNotEqual(app._s('jenna'),before)
     raise RuntimeError('Abort command')
   self.assertEqual(app._s('jenna'),before)
   app.advance_to('jenna','2026-09-08T11:00:00+02:00')
   self.assertEqual(app._s('jenna'),project(app.ledger.read('jenna')))
 def test_new_events_do_not_replay_old_history(self):
  with PersonaLife(':memory:') as app:
   app.create_persona(persona(),'2026-09-08T00:00:00+02:00')
   app.advance_to('jenna','2026-09-10T00:00:00+02:00')
   app._s('jenna')
   from unittest.mock import patch
   with patch('personalife.service.project',wraps=project) as replay:
    app.mark_hook_used('jenna',app._s('jenna')['stories'][0]['event_id'])
    app._s('jenna')
    self.assertEqual(sum(len(call.args[0]) for call in replay.call_args_list),1)

if __name__=='__main__':unittest.main()
