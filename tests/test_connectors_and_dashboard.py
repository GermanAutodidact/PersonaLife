"""Tests for mobile dashboard and platform connectors (ChatGPT, Claude, Gemini, Grok)."""
import json
import tempfile
import threading
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.request import Request, urlopen
from personalife import PersonaLife, persona
from personalife.api import create_server
from personalife.connectors import get_all_platform_integrations, get_platform_integration
from personalife.dashboard import render_dashboard_html

class ConnectorsAndDashboardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / 'dashboard_life.db'
        self.server = create_server(self.db, port=0, token='dash-secret', enable_cors=True)
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

    def test_connectors_generation(self):
        p = persona('Jenna', 'jenna', 'bartender', language='de')
        all_integrations = get_all_platform_integrations(p, base_url='https://example.com', language='de')
        self.assertIn('chatgpt', all_integrations)
        self.assertIn('claude', all_integrations)
        self.assertIn('gemini', all_integrations)
        self.assertIn('grok', all_integrations)

        # Check ChatGPT custom instructions
        chatgpt = all_integrations['chatgpt']
        self.assertEqual(chatgpt['platform'], 'chatgpt')
        self.assertIn('getRoleplayPrompt', chatgpt['instructions'])
        self.assertIn('openapi.json', chatgpt['openapi_url'])

        # Check Claude instructions
        claude = all_integrations['claude']
        self.assertIn('ROLLENSPIEL-DIREKTIVE', claude['instructions'])

        # Check Gemini Gem instructions
        gemini = all_integrations['gemini']
        self.assertIn('GEMINI GEM SYSTEM-DIREKTIVE', gemini['instructions'])

        # Check Grok instructions
        grok = all_integrations['grok']
        self.assertIn('GROK-MODUS DIREKTIVE', grok['instructions'])

    def test_dashboard_html_rendering(self):
        req = Request(self.base + '/dashboard')
        with urlopen(req, timeout=5) as r:
            html = r.read().decode('utf-8')
            self.assertEqual(r.status, 200)
            self.assertIn('PersonaLife Mobile', html)
            self.assertIn('ChatGPT', html)
            self.assertIn('Claude', html)
            self.assertIn('Gemini', html)
            self.assertIn('Grok', html)

        # Root / should also render dashboard
        req_root = Request(self.base + '/')
        with urlopen(req_root, timeout=5) as r:
            self.assertEqual(r.status, 200)

    def test_api_connectors_endpoints(self):
        # Create persona
        start_time = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        req_create = Request(self.base + '/v1/personas',
                             data=json.dumps({'profile': persona(), 'start_time': start_time}).encode(),
                             headers={'Authorization': 'Bearer dash-secret', 'Content-Type': 'application/json'},
                             method='POST')
        with urlopen(req_create, timeout=5) as r:
            self.assertEqual(r.status, 201)

        # Fetch all connectors
        req_all = Request(self.base + '/v1/personas/jenna/connectors',
                          headers={'Authorization': 'Bearer dash-secret'})
        with urlopen(req_all, timeout=5) as r:
            res = json.loads(r.read())
            self.assertIn('chatgpt', res)
            self.assertIn('gemini', res)

        # Fetch specific connector (e.g. gemini)
        req_gemini = Request(self.base + '/v1/personas/jenna/connectors/gemini',
                             headers={'Authorization': 'Bearer dash-secret'})
        with urlopen(req_gemini, timeout=5) as r:
            res_gem = json.loads(r.read())
            self.assertEqual(res_gem['platform'], 'gemini')
            self.assertIn('GEMINI GEM', res_gem['instructions'])

if __name__ == '__main__':
    unittest.main()
