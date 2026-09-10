"""Additional regression checks for temporal boundaries and transactional isolation."""
import tempfile
import unittest
from pathlib import Path
from personalife import PersonaLife,persona,validate
from personalife.clock import bounds,civil

class AdversarialTests(unittest.TestCase):
 def test_full_dst_days_execute_actual_duration(self):
  for day,seconds in [('2026-03-29',82800),('2026-10-25',90000)]:
   with self.subTest(day=day),PersonaLife(':memory:') as app:
    p=persona(occupation='unemployed');p['routines']=[]
    lo,hi=bounds(day,p['timezone']);app.create_persona(p,lo);app.advance_to('jenna',hi)
    from personalife.clock import instant
    self.assertEqual(sum((instant(x['end'])-instant(x['start'])).total_seconds() for x in app.get_actual_timeline('jenna')),seconds)
    validate(app,'jenna')
 def test_failed_reschedule_rolls_back(self):
  with PersonaLife(':memory:') as app:
   app.create_persona(persona(),'2026-09-08T00:00:00+02:00');app.advance_to('jenna','2026-09-08T10:00:00+02:00')
   before=app.ledger.read()
   completed=next(a for a in app.get_planned_timeline('jenna') if a['state']=='completed')
   with self.assertRaises(ValueError):app.reschedule('jenna',completed['id'],'2026-09-08T11:00:00+02:00','Rewrite')
   self.assertEqual(before,app.ledger.read())
 def test_two_instances_observe_same_canonical_state(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/'life.db'
   with PersonaLife(path) as one,PersonaLife(path) as two:
    one.create_persona(persona(),'2026-09-08T00:00:00+02:00')
    two.advance_to('jenna','2026-09-08T09:00:00+02:00')
    self.assertEqual(one.get_current_state('jenna'),two.get_current_state('jenna'))
    one.advance_to('jenna','2026-09-08T11:00:00+02:00')
    self.assertEqual(one.get_current_state('jenna'),two.get_current_state('jenna'))
 def test_shift_leave_and_home_office(self):
  from personalife.planner import shift
  from datetime import date
  p=persona();p['occupation']['exceptions']={'2026-09-08':{'leave':'sick'},'2026-09-09':{'shift':['10:00','14:00'],'location':'home'}}
  self.assertIsNone(shift(p,date(2026,9,8)))
  self.assertEqual(shift(p,date(2026,9,9))[2],'home')
 def test_shift_overtime_is_repeatable(self):
  from personalife.planner import shift
  from datetime import date
  p=persona();normal=shift(p,date(2026,9,8))
  p['occupation']['variability']={'overtime_probability':1,'overtime_minutes':30}
  altered=shift(p,date(2026,9,8))
  self.assertEqual((altered[1]-normal[1]).total_seconds(),1800)
  self.assertEqual(altered,shift(p,date(2026,9,8)))

if __name__=='__main__':unittest.main()
