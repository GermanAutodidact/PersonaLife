import copy
import json
import sqlite3
import tempfile
import unittest
from datetime import datetime,timedelta,timezone
from pathlib import Path
from personalife import PersonaLife,persona,validate,JsonMemoryProvider
from personalife.clock import bounds,civil,instant
from personalife.planner import recurrence,travel_time

class SimulationTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory()
  self.path=Path(self.temp.name)/'life.db'
  self.app=PersonaLife(self.path)
  self.p=persona(occupation='unemployed')
  self.p['routines']=[];self.p['hobbies']=[]
  self.app.create_persona(self.p,'2026-09-08T00:00:00+02:00')
 def tearDown(self):self.app.close();self.temp.cleanup()
 def at(self,t,day='2026-09-08'):return f'{day}T{t}:00+02:00'
 def setup_plan(self):self.app.generate_day('jenna','2026-09-08')
 def clean(self):
  self.setup_plan()
  return self.app.add_activity('jenna','Cleaning',self.at('10:00'),self.at('11:00'),'home',key='clean')
 def test_cleaning_preserves_25_minutes(self):
  a=self.clean()
  self.app.apply_chat_event('jenna',self.at('10:25'),self.at('11:10'),'Long conversation')
  b=self.app._s('jenna')['activities'][a['id']]
  self.assertEqual(b['progress'],1500)
  self.assertEqual((instant(b['end'])-instant(b['start'])).total_seconds(),2100)
  self.app.advance_to('jenna',self.at('12:00'))
  self.assertEqual(self.app._s('jenna')['activities'][a['id']]['state'],'completed')
  validate(self.app,'jenna')
 def test_plan_is_not_actual(self):
  self.setup_plan()
  self.assertEqual(self.app.get_actual_timeline('jenna'),[])
  self.assertTrue(all(a['state']=='planned' for a in self.app.get_planned_timeline('jenna')))
 def test_shopping_chat_conflict(self):
  self.setup_plan()
  a=self.app.add_activity('jenna','Shopping',self.at('17:00'),self.at('18:00'),'shop')
  self.app.apply_chat_event('jenna',self.at('16:30'),self.at('18:15'),'We talked instead of shopping.')
  b=self.app._s('jenna')['activities'][a['id']]
  self.assertGreaterEqual(instant(b['start']),instant(self.at('18:30')))
  self.assertEqual(b['progress'],0)
  self.assertTrue(any(e['kind']=='CONFLICT_RESOLVED' for e in self.app.ledger.read()))
  self.app.advance_to('jenna',self.at('23:00'));validate(self.app,'jenna')
 def test_late_work_requires_commute(self):
  self.app.set_occupation('jenna',persona()['occupation'])
  self.setup_plan()
  self.app.apply_chat_event('jenna',self.at('16:20'),self.at('16:55'),'Work can wait a little.')
  work=[a for a in self.app.get_planned_timeline('jenna') if a['kind']=='work']
  first=min(work,key=lambda a:a['start'])
  self.assertGreaterEqual(instant(first['start']),instant(self.at('17:20')))
  self.assertTrue(any(e['kind']=='OBLIGATION_LATE' for e in self.app.ledger.read()))
  self.app.advance_to('jenna',self.at('23:00'));validate(self.app,'jenna')
 def test_duplicate_chat_is_idempotent(self):
  args=('jenna',self.at('10:00'),self.at('10:30'),'Hello',{'idempotency_key':'x'})
  self.app.apply_chat_event(*args);n=len(self.app.ledger.read())
  self.app.apply_chat_event(*args)
  self.assertEqual(n,len(self.app.ledger.read()))
 def test_chat_key_collision(self):
  self.app.apply_chat_event('jenna',self.at('10:00'),self.at('10:30'),'Hello',{'idempotency_key':'x'})
  n=len(self.app.ledger.read())
  with self.assertRaises(ValueError):self.app.apply_chat_event('jenna',self.at('10:00'),self.at('10:30'),'Changed',{'idempotency_key':'x'})
  self.assertEqual(n,len(self.app.ledger.read()))
 def test_late_chat_does_not_rewrite_past(self):
  self.app.advance_to('jenna',self.at('12:00'));before=self.app.ledger.read()
  with self.assertRaises(ValueError):self.app.apply_chat_event('jenna',self.at('10:00'),self.at('11:00'),'Old chat')
  self.assertEqual(before,self.app.ledger.read())
 def test_live_chat_holds_time(self):
  self.app.start_chat_event('jenna',self.at('10:00'),'live')
  self.app.advance_to('jenna',self.at('13:00'))
  self.assertTrue(self.app.get_current_state('jenna')['open_chat'])
  self.assertEqual(self.app.get_actual_timeline('jenna')[-1]['kind'],'chat')
  self.app.end_chat_event('jenna',self.at('13:15'),'Live chat ended','live')
  validate(self.app,'jenna')
 def test_live_chat_cross_midnight(self):
  self.app.start_chat_event('jenna',self.at('23:00'),'live')
  self.app.end_chat_event('jenna',self.at('02:00','2026-09-09'),'Late conversation','live')
  validate(self.app,'jenna')
 def test_parallel_chat_rejected(self):
  self.app.start_chat_event('jenna',self.at('10:00'),'one')
  with self.assertRaises(ValueError):self.app.start_chat_event('jenna',self.at('10:01'),'two')
 def test_offline_catchup_restart(self):
  self.app.advance_to('jenna',self.at('09:00'));self.app.close()
  self.app=PersonaLife(self.path)
  self.app.advance_to('jenna',self.at('15:00'));before=self.app.ledger.read()
  self.app.advance_to('jenna',self.at('15:00'))
  self.assertEqual(before,self.app.ledger.read());validate(self.app,'jenna')
 def test_database_immutable(self):
  with self.assertRaises(sqlite3.IntegrityError):self.app.ledger.db.execute("UPDATE events SET kind='lie'")
  with self.assertRaises(sqlite3.IntegrityError):self.app.ledger.db.execute('DELETE FROM events')
  self.app.ledger.verify()
 def test_duplicate_event_rejected(self):
  e=self.app.ledger.read()[0]
  with self.assertRaises(sqlite3.IntegrityError):
   with self.app.ledger.transaction():self.app.ledger.append('jenna',self.at('00:00'),'OTHER',{},e['id'])
 def test_invalid_timestamp(self):
  with self.assertRaises(ValueError):self.app.advance_to('jenna','2026-09-08T10:00:00')
 def test_negative_chat_duration(self):
  with self.assertRaises(ValueError):self.app.apply_chat_event('jenna',self.at('12:00'),self.at('11:00'),'Invalid')
 def test_no_unknown_location(self):
  with self.assertRaises(ValueError):self.app.add_activity('jenna','Mystery',self.at('10:00'),self.at('11:00'),'moon')
 def test_no_unknown_route(self):
  p=copy.deepcopy(self.p);p['travel_times']={}
  with self.assertRaises(ValueError):travel_time(p,'home','shop')
 def test_route_graph(self):self.assertEqual(travel_time(self.p,'shop','gym'),35)
 def test_day_generation_idempotent(self):
  self.setup_plan();before=self.app.ledger.read();self.setup_plan()
  self.assertEqual(before,self.app.ledger.read())
 def test_spring_dst(self):
  a,b=bounds('2026-03-29','Europe/Berlin');self.assertEqual((b-a).total_seconds(),23*3600)
 def test_fall_dst(self):
  a,b=bounds('2026-10-25','Europe/Berlin');self.assertEqual((b-a).total_seconds(),25*3600)
  a=civil('2026-10-25','02:30','Europe/Berlin',0);b=civil('2026-10-25','02:30','Europe/Berlin',1)
  self.assertEqual((b-a).total_seconds(),3600)
 def test_nonexistent_civil_time(self):
  with self.assertRaises(ValueError):civil('2026-03-29','02:30','Europe/Berlin')
 def test_original_plan_preserved(self):
  self.setup_plan();before=copy.deepcopy(self.app.get_planned_timeline('jenna',True))
  self.app.apply_chat_event('jenna',self.at('10:00'),self.at('13:00'),'We chatted')
  after={a['id']:a for a in self.app.get_planned_timeline('jenna',True)}
  for a in before:self.assertEqual(a,after[a['id']])
 def test_future_day_cannot_close(self):
  with self.assertRaises(ValueError):self.app.close_day('jenna','2026-09-08')
 def test_memory_export_and_namespace(self):
  self.app.memory=JsonMemoryProvider(Path(self.temp.name)/'memory')
  self.app.apply_chat_event('jenna',self.at('10:00'),self.at('11:00'),'A memorable conversation')
  self.app.advance_to('jenna',self.at('00:00','2026-09-09'))
  self.app.close_day('jenna','2026-09-08')
  self.assertTrue(self.app.memory.search('personalife:jenna'))
  self.assertEqual(self.app.memory.search('personalife:other'),[])
  self.assertEqual(self.app.flush_memories('jenna'),0)
 def test_three_days_night_shifts(self):
  self.app.set_occupation('jenna',persona()['occupation'])
  self.app.apply_chat_event('jenna',self.at('16:20'),self.at('16:55'),'Delayed us.')
  self.app.advance_to('jenna',self.at('00:00','2026-09-11'))
  for day in ['2026-09-08','2026-09-09','2026-09-10']:self.app.close_day('jenna',day)
  validate(self.app,'jenna')
  self.assertEqual(self.app.get_relationships('jenna')[0]['id'],'lisa')
  self.assertTrue(self.app.get_relationships('jenna')[0]['shared_history'])
 def test_hook_once(self):
  self.app.apply_chat_event('jenna',self.at('10:00'),self.at('11:00'),'We made plans.')
  h=self.app.get_conversation_hooks('jenna')[0]
  self.app.mark_hook_used('jenna',h['event_id'])
  self.assertNotIn(h['event_id'],[x.get('event_id') for x in self.app.get_conversation_hooks('jenna')])
 def test_bounded_context(self):
  self.app.apply_chat_event('jenna',self.at('10:00'),self.at('11:00'),'X'*20000)
  self.assertLessEqual(len(json.dumps(self.app.get_persona_context('jenna',max_chars=1000),ensure_ascii=False)),1000)
 def test_chat_mid_travel_resume(self):
  self.app.set_occupation('jenna',persona()['occupation']);self.setup_plan()
  self.app.apply_chat_event('jenna',self.at('16:45'),self.at('17:00'),'Paused commute.')
  self.app.advance_to('jenna',self.at('18:00'))
  validate(self.app,'jenna')
 def test_recurrences(self):
  day=datetime(2026,9,8).date()
  self.assertTrue(recurrence({'frequency':'weekday'},day))
  self.assertFalse(recurrence({'frequency':'weekend'},day))
  self.assertTrue(recurrence({'frequency':'monthly','month_day':8},day))
  self.assertTrue(recurrence({'frequency':'custom','dates':['2026-09-08']},day))
 def test_randomness_repeatable(self):
  other=PersonaLife(':memory:')
  try:
   other.create_persona(self.p,self.at('00:00'))
   self.setup_plan();other.generate_day('jenna','2026-09-08')
   self.assertEqual(self.app.get_planned_timeline('jenna'),other.get_planned_timeline('jenna'))
  finally:other.close()

if __name__=='__main__':unittest.main()
