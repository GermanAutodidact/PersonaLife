"""CLI setup and operations, usable without API keys or cloud services."""
import argparse
import json
from datetime import datetime,timezone
from pathlib import Path
from .service import PersonaLife
from .presets import PRESETS,persona
from .validation import validate

def output(value):print(json.dumps(value,ensure_ascii=False,indent=2))
def main(argv=None):
    parser=argparse.ArgumentParser(prog='personalife')
    parser.add_argument('--db',default='personalife.sqlite3')
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('presets')
    create=sub.add_parser('persona');csub=create.add_subparsers(dest='persona_command',required=True)
    new=csub.add_parser('create');new.add_argument('--file');new.add_argument('--start');new.add_argument('--name');new.add_argument('--id');new.add_argument('--occupation',choices=PRESETS)
    for name in ['state','context','hooks','actual','relationships','validate','memories']:
        p=sub.add_parser(name);p.add_argument('persona_id')
    for name in ['plan','day','close-day']:
        p=sub.add_parser(name);p.add_argument('persona_id');p.add_argument('date')
    p=sub.add_parser('advance');p.add_argument('persona_id');p.add_argument('--to')
    p=sub.add_parser('chat');p.add_argument('persona_id');p.add_argument('--start',required=True);p.add_argument('--end',required=True);p.add_argument('--summary',required=True);p.add_argument('--key')
    p=sub.add_parser('serve');p.add_argument('--port',type=int,default=8787)
    p=sub.add_parser('heartbeat');p.add_argument('--minutes',type=float,default=15);p.add_argument('--once',action='store_true')
    p=sub.add_parser('backup');p.add_argument('destination')
    args=parser.parse_args(argv)
    if args.command=='presets':output(PRESETS);return
    if args.command=='serve':
        from .api import create_server
        server=create_server(args.db,port=args.port)
        print(f'PersonaLife API on http://127.0.0.1:{server.server_port}')
        try:server.serve_forever()
        except KeyboardInterrupt:pass
        finally:server.server_close()
        return
    if args.command=='heartbeat':
        from .heartbeat import tick,run
        if args.once:output(tick(args.db))
        else:run(args.db,args.minutes)
        return
    with PersonaLife(args.db) as app:
        if args.command=='persona':
            if args.file:profile=json.loads(Path(args.file).read_text(encoding='utf-8'))
            else:
                name=args.name or input('Name: ').strip()
                pid=args.id or input('Persona ID: ').strip()
                occupation=args.occupation or input('Occupation ('+', '.join(PRESETS)+'): ').strip()
                if occupation not in PRESETS:parser.error('Choose a preset or use --file for full custom setup')
                profile=persona(name,pid,occupation)
                if not args.name:
                    profile['age']=int(input('Age [25]: ') or 25)
                    profile['timezone']=input('Timezone [Europe/Berlin]: ') or 'Europe/Berlin'
                    profile['occupation']['employer']=input('Employer: ') or 'Custom employer'
                    raw=input('Weekly shifts as JSON, or Enter for preset: ')
                    if raw:profile['occupation']['workweek']=json.loads(raw)
                    profile['occupation']['commute_minutes']=int(input('Commute minutes ['+str(profile['occupation']['commute_minutes'])+']: ') or profile['occupation']['commute_minutes'])
                    profile['hobbies']=[s.strip() for s in input('Hobbies, comma separated: ').split(',') if s.strip()]
                    profile['sleep']['start']=input('Bedtime [23:00]: ') or '23:00'
                    profile['sleep']['hours']=float(input('Sleep hours [8]: ') or 8)
                    print('Additional locations, friends and routines can be configured through JSON or the API.')
            start=args.start or datetime.now(timezone.utc).isoformat()
            output(app.create_persona(profile,start));return
        if args.command=='backup':app.ledger.backup(args.destination);output({'backup':args.destination});return
        pid=args.persona_id
        commands={
          'state':lambda:app.get_current_state(pid),'context':lambda:app.get_persona_context(pid),
          'hooks':lambda:app.get_conversation_hooks(pid),'actual':lambda:app.get_actual_timeline(pid),
          'relationships':lambda:app.get_relationships(pid),'validate':lambda:validate(app,pid),
          'memories':lambda:app.get_memories(pid),'plan':lambda:app.generate_day(pid,args.date),
          'day':lambda:app.get_day(pid,args.date),'close-day':lambda:app.close_day(pid,args.date),
          'advance':lambda:app.advance_to(pid,args.to or datetime.now(timezone.utc)),
          'chat':lambda:app.apply_chat_event(pid,args.start,args.end,args.summary,{'idempotency_key':args.key} if args.key else None)}
        output(commands[args.command]())

if __name__=='__main__':main()
