import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from personalife import PersonaLife,persona,JsonMemoryProvider
from personalife.api import create_server
from personalife.llm import OpenAICompatible,LMStudio,Ollama

class APITests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'life.db'
  self.server=create_server(self.path,port=0,token='test-secret')
  self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
  self.base=f'http://127.0.0.1:{self.server.server_port}'
 def tearDown(self):self.server.shutdown();self.server.server_close();self.thread.join();self.tmp.cleanup()
 def request(self,path,body=None,token='test-secret'):
  req=Request(self.base+path,data=json.dumps(body).encode() if body is not None else None,
       headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'})
  with urlopen(req,timeout=5) as r:return json.loads(r.read())
 def test_api_full_flow(self):
  self.request('/v1/personas',{'profile':persona(),'start_time':'2026-09-08T00:00:00+02:00'})
  result=self.request('/v1/personas/jenna/advance',{'now':'2026-09-08T09:00:00+02:00'})
  self.assertEqual(result['persona_id'],'jenna')
  self.assertTrue(self.request('/v1/personas/jenna/validate')['valid'])
  self.assertIn('truth_policy',self.request('/v1/personas/jenna/context'))
 def test_auth_required(self):
  with self.assertRaises(HTTPError) as cm:self.request('/v1/presets',token='wrong')
  self.assertEqual(cm.exception.code,401)
 def test_no_arbitrary_method(self):
  with self.assertRaises(HTTPError) as cm:self.request('/v1/personas/jenna/_emit',{'kind':'FAKE'})
  self.assertEqual(cm.exception.code,404)
 def test_token_required(self):
  with self.assertRaises(ValueError):create_server(self.path,port=0)

class ProviderTests(unittest.TestCase):
 def test_json_immutable(self):
  with tempfile.TemporaryDirectory() as d:
   p=JsonMemoryProvider(d);r={'id':'x','content':'hello','created_at':'2026-01-01T00:00:00Z'}
   p.put('one',r);p.put('one',r)
   with self.assertRaises(ValueError):p.put('one',{**r,'content':'rewrite'})
   self.assertEqual(p.search('two'),[])
 def test_openai_compatible_contract(self):
  from unittest.mock import patch,MagicMock
  response=MagicMock();response.__enter__.return_value.read.return_value=b'{"choices":[{"message":{"content":"A fictional day."}}]}'
  with patch('personalife.llm.urlopen',return_value=response) as call:
   self.assertEqual(OpenAICompatible('https://example.com/v1','model','key').narrate({'actual':[]}), 'A fictional day.')
   request=call.call_args[0][0]
   self.assertEqual(request.full_url,'https://example.com/v1/chat/completions')
   self.assertEqual(json.loads(request.data)['messages'][0]['role'],'system')
 def test_local_llm_adapters(self):
  self.assertEqual(LMStudio('local').base_url,'http://localhost:1234/v1')
  self.assertEqual(Ollama('local').base_url,'http://localhost:11434/v1')
 def test_remote_http_rejected(self):
  with self.assertRaises(ValueError):OpenAICompatible('http://example.com','model')
 def test_aimemory_real_roundtrip(self):
  try:import aimemory.database
  except ImportError:self.skipTest('Install AiMemory to run external-provider integration')
  from personalife import AiMemoryProvider
  with tempfile.TemporaryDirectory() as d:
   provider=AiMemoryProvider(Path(d)/'memory.db')
   record={'id':'event-1','content':'A real integration test','kind':'episode','created_at':'2026-09-08T09:00:00+00:00','metadata':{'persona_id':'jenna','source':'simulated_execution'}}
   try:
    provider.put('personalife:jenna',record);provider.put('personalife:jenna',record)
    self.assertEqual(len(provider.search('personalife:jenna')),1)
    self.assertEqual(provider.search('personalife:other'),[])
   finally:provider.close()

if __name__=='__main__':unittest.main()
