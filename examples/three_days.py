"""Run from repository root: python examples/three_days.py --output demo-output"""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from personalife import PersonaLife,persona,JsonMemoryProvider,validate

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',default='demo-output');args=parser.parse_args()
 out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
 database=out/'personalife.sqlite3'
 if database.exists():raise SystemExit('Choose a fresh output directory to preserve the previous demo.')
 with PersonaLife(database,memory=JsonMemoryProvider(out/'memories')) as app:
  profile=persona()
  app.create_persona(profile,'2026-09-08T00:00:00+02:00')
  app.advance_to('jenna','2026-09-08T09:00:00+02:00')
  morning=app.get_persona_context('jenna')
  app.apply_chat_event('jenna','2026-09-08T12:25:00+02:00','2026-09-08T13:10:00+02:00','We talked while cleaning; I will finish the remaining work later.')
  app.apply_chat_event('jenna','2026-09-08T16:20:00+02:00','2026-09-08T16:55:00+02:00','We talked before my shift; I left late.')
  app.advance_to('jenna','2026-09-09T00:00:00+02:00');app.close_day('jenna','2026-09-08')
  next_morning=app.get_persona_context('jenna','2026-09-09T10:00:00+02:00')
  app.advance_to('jenna','2026-09-11T00:00:00+02:00')
  for day in ['2026-09-08','2026-09-09','2026-09-10']:
   closing=app.close_day('jenna',day)
   (out/(day+'.json')).write_text(json.dumps(app.get_day('jenna',day),indent=2,ensure_ascii=False),encoding='utf-8')
   (out/(day+'.md')).write_text('# '+day+' — simulated life\n\n'+closing['story']+'\n\n'+closing['reflection'],encoding='utf-8')
  result={'validation':validate(app,'jenna'),'morning_context':morning,'next_day_context':next_morning,
          'hooks':app.get_conversation_hooks('jenna'),'relationships':app.get_relationships('jenna'),
          'memory_count':len(app.memory.search('personalife:jenna'))}
  (out/'report.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
  print(json.dumps({'output':str(out),'validation':result['validation'],'memory_count':result['memory_count']},indent=2))

if __name__=='__main__':main()
