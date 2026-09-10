"""Loopback JSON HTTP API; one SQLite connection per request, no arbitrary dispatch."""
import hmac
import json
import os
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlparse,parse_qs
from .service import PersonaLife
from .presets import PRESETS, get_presets
from .i18n import language, error_message
from .validation import validate

MAX_BODY=1_000_000

def create_server(database,host='127.0.0.1',port=8787,token=None,default_language='en'):
    default_language=language(default_language)
    if host not in {'127.0.0.1','::1','localhost'}:raise ValueError('API binds to loopback only; use an authenticated proxy for remote access')
    token=token or os.environ.get('PERSONALIFE_API_TOKEN')
    if not token:raise ValueError('Set PERSONALIFE_API_TOKEN before starting the API')
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def send_json(self,status,body):
            if isinstance(body,dict) and 'error' in body:
                body={**body,'error':error_message(body['error'],getattr(self,'response_language',default_language))}
            data=json.dumps(body,ensure_ascii=False,allow_nan=False).encode()
            self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8')
            self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store')
            self.end_headers();self.wfile.write(data)
        def dispatch(self,method):
            self.response_language=default_language
            choices=[]
            for entry in self.headers.get('Accept-Language','').split(','):
                parts=entry.strip().split(';')
                code=parts[0].split('-')[0].lower()
                try:quality=float(parts[1].strip().removeprefix('q=')) if len(parts)>1 else 1.0
                except ValueError:continue
                if code in {'en','de'} and 0<quality<=1:choices.append((quality,code))
            if choices:self.response_language=max(choices,key=lambda x:x[0])[1]
            if not hmac.compare_digest(self.headers.get('Authorization',''),'Bearer '+token):
                return self.send_json(401,{'error':'Authentication required'})
            if self.headers.get('Origin'):
                return self.send_json(403,{'error':'Browser cross-origin requests are disabled'})
            try:
                parsed=urlparse(self.path);parts=parsed.path.strip('/').split('/')
                query=parse_qs(parsed.query)
                if method=='GET' and parts==['v1','presets']:return self.send_json(200,get_presets(self.response_language))
                body={}
                if method=='POST':
                    size=int(self.headers.get('Content-Length','0'))
                    if not 0<size<=MAX_BODY:return self.send_json(413,{'error':'Body must be 1..1000000 bytes'})
                    body=json.loads(self.rfile.read(size))
                    if not isinstance(body,dict):raise ValueError('JSON object required')
                with PersonaLife(database) as app:
                    if method=='POST' and parts==['v1','personas']:
                        profile=body['profile']
                        if isinstance(profile,dict):profile={**profile,'language':profile.get('language',self.response_language)}
                        return self.send_json(201,app.create_persona(profile,body['start_time']))
                    if len(parts)!=4 or parts[:2]!=['v1','personas']:
                        return self.send_json(404,{'error':'Unknown route'})
                    pid,action=parts[2:]
                    if method=='GET':
                        commands={
                            'state':lambda:app.get_current_state(pid),
                            'context':lambda:app.get_persona_context(pid),
                            'hooks':lambda:app.get_conversation_hooks(pid),
                            'actual':lambda:app.get_actual_timeline(pid),
                            'plan':lambda:app.get_planned_timeline(pid,query.get('original',['false'])[0]=='true'),
                            'day':lambda:app.get_day(pid,query['date'][0]),
                            'relationships':lambda:app.get_relationships(pid),
                            'memories':lambda:app.get_memories(pid,query.get('q',[''])[0]),
                            'validate':lambda:validate(app,pid)}
                    else:
                        commands={
                            'advance':lambda:app.advance_to(pid,body['now']),
                            'plan':lambda:app.generate_day(pid,body['date']),
                            'update':lambda:app.update_persona(pid,body['changes']),
                            'occupation':lambda:app.set_occupation(pid,body['occupation']),
                            'routine':lambda:app.set_routine(pid,body['routine']),
                            'activity':lambda:app.add_activity(pid,**body),
                            'reschedule':lambda:app.reschedule(pid,body['activity_id'],body['start_time'],body['reason']),
                            'chat-start':lambda:app.start_chat_event(pid,body['start_time'],body['chat_id'],body.get('metadata')),
                            'chat-end':lambda:app.end_chat_event(pid,body['end_time'],body['summary'],body['chat_id']),
                            'chat':lambda:app.apply_chat_event(pid,body['start_time'],body['end_time'],body['summary'],body.get('metadata')),
                            'close-day':lambda:app.close_day(pid,body['date']),
                            'hook-used':lambda:app.mark_hook_used(pid,body['event_id'])}
                    if action not in commands:return self.send_json(404,{'error':'Unknown route'})
                    result=commands[action]()
                self.send_json(200,result)
            except KeyError as ex:self.send_json(400,{'error':'Missing or unknown field: '+str(ex)})
            except (ValueError,TypeError) as ex:self.send_json(400,{'error':str(ex)})
            except Exception:self.send_json(500,{'error':'Internal error; inspect configuration and database locally'})
        def do_GET(self):self.dispatch('GET')
        def do_POST(self):self.dispatch('POST')
    return ThreadingHTTPServer((host,port),Handler)
