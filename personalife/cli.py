"""Bilingual CLI; command names and JSON schemas remain integration-stable."""
import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from .service import PersonaLife
from .presets import PRESETS, persona, get_presets
from .validation import validate
from .i18n import language, tr, error_message


def output(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))


class Parser(argparse.ArgumentParser):
    def __init__(self, *args, lang='en', **kwargs):
        self.lang = lang
        super().__init__(*args, **kwargs)
        self._positionals.title = tr('positional arguments', lang)
        self._optionals.title = tr('options', lang)
        for action in self._actions:
            if isinstance(action, argparse._HelpAction):
                action.help = tr('show this help message and exit', lang)

    def format_help(self):
        return super().format_help().replace('usage: ', tr('usage: ', self.lang), 1)

    def format_usage(self):
        return super().format_usage().replace('usage: ', tr('usage: ', self.lang), 1)

    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(2, tr('Error: {message}', self.lang, message=error_message(message, self.lang)) + '\n')


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    probe = argparse.ArgumentParser(add_help=False)
    probe.add_argument('--language', '--sprache')
    requested, _ = probe.parse_known_args(argv)
    try:
        lang = language(requested.language)
    except ValueError as ex:
        probe.error(str(ex))
    parser = Parser(prog='personalife', lang=lang,
                    description=tr('Persistent life simulation for AI characters', lang))
    parser.add_argument('--language', '--sprache', choices=['en', 'de'], default=lang,
                        help=tr('Interface language (en/de)', lang))
    parser.add_argument('--db', default='personalife.sqlite3', help=tr('Database path', lang))
    sub = parser.add_subparsers(dest='command', required=True,
                               parser_class=lambda **kw: Parser(lang=lang, **kw))
    def command(name, help_text):
        return sub.add_parser(name, help=tr(help_text, lang), description=tr(help_text, lang))
    command('presets', 'List occupation presets')
    create = command('persona', 'Create a persona')
    csub = create.add_subparsers(dest='persona_command', required=True,
                                parser_class=lambda **kw: Parser(lang=lang, **kw))
    new = csub.add_parser('create', help=tr('Create a persona', lang))
    for option, help_text in [('file','JSON profile path'),('start','Timezone-aware timestamp'),
                              ('name','Persona name'),('id','Persona identifier')]:
        new.add_argument('--'+option, help=tr(help_text, lang))
    new.add_argument('--occupation', choices=PRESETS, help=tr('Occupation preset ID', lang))
    for name, help_text in [('state','Read current state'),('context','Build model context'),
                           ('hooks','Show conversation hooks'),('actual','Show actual timeline'),
                           ('relationships','Show relationships'),('validate','Validate consistency'),
                           ('memories','Show memories')]:
        command(name, help_text).add_argument('persona_id', help=tr('Persona identifier', lang))
    for name, help_text in [('plan','Generate a daily plan'),('day','Show a day'),('close-day','Close an elapsed day')]:
        p=command(name,help_text);p.add_argument('persona_id',help=tr('Persona identifier',lang));p.add_argument('date',help=tr('Civil date YYYY-MM-DD',lang))
    p=command('advance','Advance simulated time');p.add_argument('persona_id',help=tr('Persona identifier',lang));p.add_argument('--to',help=tr('Timezone-aware timestamp',lang))
    p=command('chat','Record a conversation');p.add_argument('persona_id',help=tr('Persona identifier',lang))
    p.add_argument('--start',required=True,help=tr('Timezone-aware timestamp',lang));p.add_argument('--end',required=True,help=tr('Timezone-aware timestamp',lang))
    p.add_argument('--summary',required=True,help=tr('Conversation summary',lang));p.add_argument('--key',help=tr('Stable retry key',lang))
    p=command('serve','Start the local API');p.add_argument('--port',type=int,default=8787,help=tr('TCP port',lang))
    p=command('heartbeat','Run the heartbeat');p.add_argument('--minutes',type=float,default=15,help=tr('Interval in minutes',lang));p.add_argument('--once',action='store_true',help=tr('Run once and exit',lang))
    p=command('backup','Back up the database');p.add_argument('destination',help=tr('Backup destination',lang))
    args=parser.parse_args(argv)
    ask=lambda message,**values:input(tr(message,lang,**values))
    try:
        if args.command=='presets':output(get_presets(lang));return
        if args.command=='serve':
            from .api import create_server
            server=create_server(args.db,port=args.port,default_language=lang)
            print(tr('PersonaLife API on {url}',lang,url=f'http://127.0.0.1:{server.server_port}'))
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
                if args.file:
                    profile=json.loads(Path(args.file).read_text(encoding='utf-8'))
                    profile.setdefault('language',lang)
                else:
                    name=args.name or ask('Name: ').strip()
                    pid=args.id or ask('Persona ID: ').strip()
                    occupation=args.occupation or ask('Occupation ({choices}): ',choices=', '.join(PRESETS)).strip()
                    if occupation not in PRESETS:parser.error('Choose a preset or use --file for full custom setup')
                    profile=persona(name,pid,occupation,language=lang)
                    if not args.name:
                        profile['age']=int(ask('Age [25]: ') or 25)
                        profile['timezone']=ask('Timezone [Europe/Berlin]: ') or 'Europe/Berlin'
                        profile['occupation']['employer']=ask('Employer: ') or tr('Custom employer',lang)
                        raw=ask('Weekly shifts as JSON, or Enter for preset: ')
                        if raw:profile['occupation']['workweek']=json.loads(raw)
                        profile['occupation']['commute_minutes']=int(ask('Commute minutes [{minutes}]: ',minutes=profile['occupation']['commute_minutes']) or profile['occupation']['commute_minutes'])
                        profile['hobbies']=[s.strip() for s in ask('Hobbies, comma separated: ').split(',') if s.strip()]
                        profile['sleep']['start']=ask('Bedtime [23:00]: ') or '23:00'
                        profile['sleep']['hours']=float(ask('Sleep hours [8]: ') or 8)
                        print(tr('Additional locations, friends and routines can be configured through JSON or the API.',lang))
                output(app.create_persona(profile,args.start or datetime.now(timezone.utc).isoformat()));return
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
    except (ValueError,KeyError,OSError,sqlite3.Error) as ex:
        parser.exit(1,tr('Error: {message}',lang,message=error_message(ex,lang))+'\n')

if __name__=='__main__':main()
