"""JSON HTTP API, Web Dashboard and Connectors; one SQLite connection per request."""
import hmac
import json
import os
from datetime import datetime, timezone, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from .service import PersonaLife
from .presets import PRESETS, get_presets
from .i18n import language, error_message
from .validation import validate
from .prompt import render_roleplay_prompt
from .openapi import get_openapi_spec
from .clock import instant
from .dashboard import render_dashboard_html
from .connectors import get_all_platform_integrations, get_platform_integration

MAX_BODY = 1_000_000

def create_server(database, host='127.0.0.1', port=8787, token=None, default_language='en', allow_remote=False, enable_cors=False):
    default_language = language(default_language)
    allow_remote = allow_remote or (os.environ.get('PERSONALIFE_ALLOW_REMOTE', '').lower() in {'1', 'true', 'yes'})
    enable_cors = enable_cors or (os.environ.get('PERSONALIFE_ENABLE_CORS', '').lower() in {'1', 'true', 'yes'})
    if not allow_remote and host not in {'127.0.0.1', '::1', 'localhost'}:
        raise ValueError('API binds to loopback only; use an authenticated proxy for remote access')
    token = token or os.environ.get('PERSONALIFE_API_TOKEN')
    if not token:
        raise ValueError('Set PERSONALIFE_API_TOKEN before starting the API')

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def send_json(self, status, body):
            if isinstance(body, dict) and 'error' in body:
                body = {**body, 'error': error_message(body['error'], getattr(self, 'response_language', default_language))}
            data = json.dumps(body, ensure_ascii=False, allow_nan=False).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-store')
            if enable_cors:
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type, Accept-Language')
            self.end_headers()
            self.wfile.write(data)

        def do_OPTIONS(self):
            if enable_cors:
                self.send_response(204)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type, Accept-Language')
                self.send_header('Access-Control-Max-Age', '86400')
                self.end_headers()
            else:
                self.send_response(405)
                self.end_headers()

        def dispatch(self, method):
            self.response_language = default_language
            choices = []
            for entry in self.headers.get('Accept-Language', '').split(','):
                parts = entry.strip().split(';')
                code = parts[0].split('-')[0].lower()
                try:
                    quality = float(parts[1].strip().removeprefix('q=')) if len(parts) > 1 else 1.0
                except ValueError:
                    continue
                if code in {'en', 'de'} and 0 < quality <= 1:
                    choices.append((quality, code))
            if choices:
                self.response_language = max(choices, key=lambda x: x[0])[1]

            parsed = urlparse(self.path)
            parts = [p for p in parsed.path.strip('/').split('/') if p]

            host_header = self.headers.get('Host', f'{host}:{port}')
            scheme = 'https' if self.headers.get('X-Forwarded-Proto') == 'https' else 'http'
            base_url = f'{scheme}://{host_header}'

            # Public Web Dashboard
            if method == 'GET' and parts in ([], ['dashboard'], ['v1', 'dashboard']):
                html = render_dashboard_html(persona_id='jenna', base_url=base_url)
                data = html.encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(data)))
                self.send_header('Cache-Control', 'no-store')
                if enable_cors:
                    self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(data)
                return

            # Public OpenAPI schema inspection
            if method == 'GET' and parts in (['openapi.json'], ['v1', 'openapi.json']):
                return self.send_json(200, get_openapi_spec(base_url, language=self.response_language))

            if not hmac.compare_digest(self.headers.get('Authorization', ''), 'Bearer ' + token):
                return self.send_json(401, {'error': 'Authentication required'})

            if not enable_cors and self.headers.get('Origin'):
                return self.send_json(403, {'error': 'Browser cross-origin requests are disabled'})

            try:
                query = parse_qs(parsed.query)
                if method == 'GET' and parts == ['v1', 'presets']:
                    return self.send_json(200, get_presets(self.response_language))

                body = {}
                if method == 'POST':
                    size = int(self.headers.get('Content-Length', '0'))
                    if not 0 < size <= MAX_BODY:
                        return self.send_json(413, {'error': 'Body must be 1..1000000 bytes'})
                    body = json.loads(self.rfile.read(size))
                    if not isinstance(body, dict):
                        raise ValueError('JSON object required')

                with PersonaLife(database) as app:
                    if method == 'POST' and parts == ['v1', 'personas']:
                        profile = body['profile']
                        if isinstance(profile, dict):
                            profile = {**profile, 'language': profile.get('language', self.response_language)}
                        return self.send_json(201, app.create_persona(profile, body['start_time']))

                    if len(parts) < 3 or parts[:2] != ['v1', 'personas']:
                        return self.send_json(404, {'error': 'Unknown route'})

                    pid = parts[2]
                    auto_advance = query.get('auto_advance', ['false'])[0].lower() in {'true', '1', 'yes'}
                    now_val = datetime.now(timezone.utc) if auto_advance else None

                    # Specific platform connector endpoint
                    if len(parts) == 5 and parts[3] == 'connectors' and method == 'GET':
                        target = parts[4]
                        return self.send_json(200, get_platform_integration(target, app._s(pid).get('persona', {}), base_url=base_url, language=self.response_language))

                    if len(parts) != 4:
                        return self.send_json(404, {'error': 'Unknown route'})

                    action = parts[3]

                    def _get_prompt():
                        ctx = app.get_persona_context(pid, now=now_val)
                        profile = app._s(pid).get('persona')
                        rendered = render_roleplay_prompt(ctx, profile)
                        return {
                            'prompt': rendered,
                            'persona_id': pid,
                            'location': ctx.get('now', {}).get('location'),
                            'now': ctx.get('now', {}).get('now'),
                            'activity': ctx.get('now', {}).get('activity')
                        }

                    def _quick_chat():
                        summary = body.get('summary')
                        if not summary:
                            raise ValueError('summary is required')
                        mins = max(1.0, float(body.get('duration_minutes', 10)))
                        cur = instant(app._s(pid)['cursor'])
                        now_utc = datetime.now(timezone.utc)
                        start_t = max(cur, now_utc)
                        end_t = start_t + timedelta(minutes=mins)
                        return app.apply_chat_event(pid, start_t, end_t, summary)

                    def _get_state():
                        if auto_advance:
                            app.advance_to(pid, datetime.now(timezone.utc))
                        return app.get_current_state(pid)

                    if method == 'GET':
                        commands = {
                            'state': _get_state,
                            'context': lambda: app.get_persona_context(pid, now=now_val),
                            'prompt': _get_prompt,
                            'connectors': lambda: get_all_platform_integrations(app._s(pid).get('persona', {}), base_url=base_url, language=self.response_language),
                            'hooks': lambda: app.get_conversation_hooks(pid),
                            'actual': lambda: app.get_actual_timeline(pid),
                            'plan': lambda: app.get_planned_timeline(pid, query.get('original', ['false'])[0] == 'true'),
                            'day': lambda: app.get_day(pid, query['date'][0]),
                            'relationships': lambda: app.get_relationships(pid),
                            'memories': lambda: app.get_memories(pid, query.get('q', [''])[0]),
                            'validate': lambda: validate(app, pid)
                        }
                    else:
                        commands = {
                            'advance': lambda: app.advance_to(pid, body['now']),
                            'plan': lambda: app.generate_day(pid, body['date']),
                            'update': lambda: app.update_persona(pid, body['changes']),
                            'occupation': lambda: app.set_occupation(pid, body['occupation']),
                            'routine': lambda: app.set_routine(pid, body['routine']),
                            'activity': lambda: app.add_activity(pid, **body),
                            'reschedule': lambda: app.reschedule(pid, body['activity_id'], body['start_time'], body['reason']),
                            'chat-start': lambda: app.start_chat_event(pid, body['start_time'], body['chat_id'], body.get('metadata')),
                            'chat-end': lambda: app.end_chat_event(pid, body['end_time'], body['summary'], body['chat_id']),
                            'chat': lambda: app.apply_chat_event(pid, body['start_time'], body['end_time'], body['summary'], body.get('metadata')),
                            'quick-chat': _quick_chat,
                            'close-day': lambda: app.close_day(pid, body['date']),
                            'hook-used': lambda: app.mark_hook_used(pid, body['event_id'])
                        }

                    if action not in commands:
                        return self.send_json(404, {'error': 'Unknown route'})
                    result = commands[action]()
                self.send_json(200, result)
            except KeyError as ex:
                self.send_json(400, {'error': 'Missing or unknown field: ' + str(ex)})
            except (ValueError, TypeError) as ex:
                self.send_json(400, {'error': str(ex)})
            except Exception:
                self.send_json(500, {'error': 'Internal error; inspect configuration and database locally'})

        def do_GET(self):
            self.dispatch('GET')

        def do_POST(self):
            self.dispatch('POST')

    return ThreadingHTTPServer((host, port), Handler)
