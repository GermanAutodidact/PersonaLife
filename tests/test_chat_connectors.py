"""Tests for chat connectors: roleplay prompt renderer, OpenAPI schema, and MCP server."""
import json
import tempfile
import threading
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.request import Request, urlopen
from personalife import PersonaLife, persona
from personalife.api import create_server
from personalife.prompt import render_roleplay_prompt, _mood_description
from personalife.openapi import get_openapi_spec
from personalife.mcp_server import MCPServer

class PromptRendererTests(unittest.TestCase):
    def test_mood_description(self):
        desc_de = _mood_description({'energy': 80, 'mood_valence': 85, 'stress': 20}, lang='de')
        self.assertIn('voller Tatendrang', desc_de)
        self.assertIn('heiterer', desc_de)

        desc_en = _mood_description({'energy': 20, 'fatigue': 80, 'stress': 70}, lang='en')
        self.assertIn('exhausted', desc_en)
        self.assertIn('stressed', desc_en)

    def test_render_roleplay_prompt(self):
        p = persona('Jenna', 'jenna', 'bartender', language='de')
        ctx = {
            'language': 'de',
            'now': {
                'now': '2026-09-08T14:30:00+02:00',
                'location': 'home',
                'activity': {'title': 'Pause'},
                'state': {'energy': 60, 'mood_valence': 75}
            },
            'recent': [{'start': '12:00:00', 'end': '14:00:00', 'title': 'Schicht', 'location': 'cafe'}],
            'hooks': [{'description': 'Habe heute viel Trinkgeld bekommen'}],
            'memory': [{'content': 'Katze vom Nachbarn gestreichelt'}]
        }
        prompt = render_roleplay_prompt(ctx, p)
        self.assertIn('DU BIST JENNA', prompt)
        self.assertIn('Pause', prompt)
        self.assertIn('Trinkgeld', prompt)
        self.assertIn('Rollenspiel-Regeln', prompt)

class OpenAPIAndAPIExtensionsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / 'life.db'
        self.server = create_server(self.db, port=0, token='secret', enable_cors=True)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f'http://127.0.0.1:{self.server.server_port}'

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        try:
            self.tmp.cleanup()
        except Exception:
            pass

    def request(self, path, method='GET', body=None, token='secret', headers=None):
        req_headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
        if headers:
            req_headers.update(headers)
        data = json.dumps(body).encode() if body is not None else None
        req = Request(self.base + path, data=data, headers=req_headers, method=method)
        with urlopen(req, timeout=10) as r:
            res = json.loads(r.read())
            return res, r.headers

    def test_openapi_endpoint(self):
        req = Request(self.base + '/openapi.json')
        with urlopen(req, timeout=5) as r:
            spec = json.loads(r.read())
        self.assertEqual(spec['openapi'], '3.1.0')
        self.assertIn('/v1/personas/{persona_id}/prompt', spec['paths'])
        self.assertIn('/v1/personas/{persona_id}/quick-chat', spec['paths'])

    def test_cors_options(self):
        req = Request(self.base + '/v1/presets', method='OPTIONS')
        with urlopen(req, timeout=5) as r:
            self.assertEqual(r.status, 204)
            self.assertEqual(r.headers.get('Access-Control-Allow-Origin'), '*')

    def test_prompt_and_quick_chat_flow(self):
        # Create persona 2 hours ago
        start_time = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        self.request('/v1/personas', method='POST', body={'profile': persona(), 'start_time': start_time})

        # Get roleplay prompt with auto_advance
        res, headers = self.request('/v1/personas/jenna/prompt?auto_advance=true')
        self.assertEqual(res['persona_id'], 'jenna')
        self.assertIn('prompt', res)
        self.assertIn('JENNA', res['prompt'])
        self.assertEqual(headers.get('Access-Control-Allow-Origin'), '*')

        # Quick chat
        chat_res, _ = self.request('/v1/personas/jenna/quick-chat', method='POST', body={'summary': 'Tolles Gespräch über Kaffee', 'duration_minutes': 5})
        self.assertEqual(chat_res['summary'], 'Tolles Gespräch über Kaffee')

        # Verify memory created
        mem_res, _ = self.request('/v1/personas/jenna/memories?q=Kaffee')
        self.assertTrue(len(mem_res['episodic']) > 0)
        self.assertIn('Kaffee', mem_res['episodic'][0]['description'])

class MCPServerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / 'mcp_life.db'
        start_time = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        with PersonaLife(self.db) as app:
            app.create_persona(persona(), start_time)
        self.server = MCPServer(database=self.db)

    def tearDown(self):
        try:
            self.tmp.cleanup()
        except Exception:
            pass

    def test_mcp_initialize(self):
        resp = self.server.process_message({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {}})
        self.assertEqual(resp['result']['serverInfo']['name'], 'personalife-mcp')

    def test_mcp_tools_list(self):
        resp = self.server.process_message({'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list'})
        tools = {t['name'] for t in resp['result']['tools']}
        self.assertIn('get_roleplay_prompt', tools)
        self.assertIn('record_chat_interaction', tools)
        self.assertIn('get_persona_state', tools)

    def test_mcp_tools_call_prompt(self):
        resp = self.server.process_message({
            'jsonrpc': '2.0',
            'id': 3,
            'method': 'tools/call',
            'params': {
                'name': 'get_roleplay_prompt',
                'arguments': {'persona_id': 'jenna', 'auto_advance': True}
            }
        })
        text = resp['result']['content'][0]['text']
        self.assertIn('JENNA', text)

    def test_mcp_tools_call_quick_chat_and_search(self):
        resp = self.server.process_message({
            'jsonrpc': '2.0',
            'id': 4,
            'method': 'tools/call',
            'params': {
                'name': 'record_chat_interaction',
                'arguments': {'persona_id': 'jenna', 'summary': 'Spaziergang im Park besprochen', 'duration_minutes': 15}
            }
        })
        self.assertNotIn('isError', resp['result'])

        search_resp = self.server.process_message({
            'jsonrpc': '2.0',
            'id': 5,
            'method': 'tools/call',
            'params': {
                'name': 'search_memories',
                'arguments': {'persona_id': 'jenna', 'query': 'Spaziergang'}
            }
        })
        search_text = search_resp['result']['content'][0]['text']
        self.assertIn('Spaziergang', search_text)

if __name__ == '__main__':
    unittest.main()
