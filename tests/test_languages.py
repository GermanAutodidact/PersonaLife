"""User-visible language parity without translating canonical identifiers."""
import ast
import contextlib
import io
import json
import os
from pathlib import Path
import re
import tempfile
import threading
import unittest
from unittest.mock import patch,MagicMock
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from personalife import PersonaLife,persona,get_presets,validate
from personalife.cli import main
from personalife.i18n import DE,error_message
from personalife.api import create_server
from personalife.llm import OpenAICompatible

class LanguageTests(unittest.TestCase):
 def test_both_help_languages(self):
  for lang,phrase in [('en','Generate a daily plan'),('de','Tagesplan erstellen')]:
   with self.subTest(language=lang),contextlib.redirect_stdout(io.StringIO()) as out:
    with self.assertRaises(SystemExit) as ex:main(['--language',lang,'--help'])
    self.assertEqual(ex.exception.code,0);self.assertIn(phrase,out.getvalue())
 def test_environment_and_alias(self):
  for args,environment in [(['--sprache','de','--help'],'en'),(['--help'],'de')]:
   with patch.dict(os.environ,{'PERSONALIFE_LANGUAGE':environment}),contextlib.redirect_stdout(io.StringIO()) as out:
    with self.assertRaises(SystemExit):main(args)
    self.assertIn('Optionen:',out.getvalue())
 def test_german_subcommand_help(self):
  with contextlib.redirect_stdout(io.StringIO()) as out:
   with self.assertRaises(SystemExit):main(['--language','de','persona','create','--help'])
   self.assertIn('Pfad zum JSON-Profil',out.getvalue())
 def test_invalid_cli_choice_localized(self):
  with contextlib.redirect_stderr(io.StringIO()) as out:
   with self.assertRaises(SystemExit):main(['--language','de','not-a-command'])
   self.assertIn('ungültige Auswahl',out.getvalue())
 def test_cli_domain_error_localized(self):
  with tempfile.TemporaryDirectory() as d,contextlib.redirect_stderr(io.StringIO()) as out:
   with self.assertRaises(SystemExit):main(['--language','de','--db',str(Path(d)/'life.db'),'state','missing'])
   self.assertIn('Unbekannte Persona',out.getvalue())
 def test_noninteractive_german_creation(self):
  with tempfile.TemporaryDirectory() as d,contextlib.redirect_stdout(io.StringIO()) as out:
   main(['--language','de','--db',str(Path(d)/'life.db'),'persona','create','--name','Jenna','--id','jenna','--occupation','bartender','--start','2026-09-08T00:00:00+02:00'])
   result=json.loads(out.getvalue());self.assertEqual(result['language'],'de')
   self.assertEqual(result['routines'][0]['title'],'Einkaufen')
 def test_preset_identity_and_translations(self):
  en,de=get_presets('en'),get_presets('de')
  self.assertEqual(en.keys(),de.keys())
  self.assertEqual(de['bartender']['label'],'Barkeeper/in')
  self.assertEqual(de['bartender']['task_types'][0],'Kundenbetreuung')
  self.assertEqual(en['bartender']['workweek'],de['bartender']['workweek'])
 def test_same_timing_both_languages(self):
  results=[]
  for lang in ['en','de']:
   with PersonaLife(':memory:') as app:
    app.create_persona(persona(language=lang),'2026-09-08T00:00:00+02:00')
    app.apply_chat_event('jenna','2026-09-08T16:20:00+02:00','2026-09-08T16:55:00+02:00','custom user text',{'idempotency_key':'same-session'})
    app.advance_to('jenna','2026-09-10T00:00:00+02:00');validate(app,'jenna')
    actual=app.get_actual_timeline('jenna')
    results.append([(e['start'],e['end'],e['kind'],e['location_after'],e['state']) for e in actual])
    context=app.get_persona_context('jenna');self.assertEqual(context['language'],lang)
    titles={e['title'] for e in actual}
    self.assertIn('Schlafen' if lang=='de' else 'Sleep',titles)
    self.assertIn('Gespräch mit dem Nutzer' if lang=='de' else 'Conversation with user',titles)
    self.assertIn('custom user text',[e['description'] for e in app._s('jenna')['stories']])
  self.assertEqual(results[0],results[1])
 def test_language_change_preserves_existing_history(self):
  with PersonaLife(':memory:') as app:
   app.create_persona(persona(),'2026-09-08T00:00:00+02:00');app.advance_to('jenna','2026-09-08T10:00:00+02:00')
   before=app.get_actual_timeline('jenna')
   app.update_persona('jenna',{'language':'de'})
   self.assertEqual(before,app.get_actual_timeline('jenna'))
   self.assertEqual(app.get_persona_context('jenna')['language'],'de')
 def test_unknown_language_rejected(self):
  with PersonaLife(':memory:') as app:
   p=persona();p['language']='fr'
   with self.assertRaises(ValueError):app.create_persona(p,'2026-09-08T00:00:00+02:00')
   self.assertEqual(app.ledger.read(),[])
 def test_legacy_profile_defaults_to_english(self):
  p=persona();p.pop('language')
  with patch.dict(os.environ,{'PERSONALIFE_LANGUAGE':'de'}),PersonaLife(':memory:') as app:
   self.assertEqual(app.create_persona(p,'2026-09-08T00:00:00+02:00')['language'],'en')
 def test_llm_requests_context_language(self):
  response=MagicMock();response.__enter__.return_value.read.return_value=b'{"choices":[{"message":{"content":"ok"}}]}'
  for lang,expected in [('de','Antworte auf Deutsch'),('en','Answer in English')]:
   with patch('personalife.llm.urlopen',return_value=response) as call:
    OpenAICompatible('https://example.com/v1','model').narrate({'language':lang})
    self.assertIn(expected,json.loads(call.call_args[0][0].data)['messages'][0]['content'])
 def test_own_static_errors_have_german_catalog_entries(self):
  root=Path(__file__).resolve().parents[1]/'personalife'
  missing=[]
  for file in root.glob('*.py'):
   for node in ast.walk(ast.parse(file.read_text(encoding='utf-8'))):
    if isinstance(node,ast.Raise) and isinstance(node.exc,ast.Call) and node.exc.args:
     first=node.exc.args[0]
     if isinstance(first,ast.Constant) and isinstance(first.value,str) and first.value not in DE:
      missing.append((file.name,first.value))
  self.assertEqual(missing,[])
 def test_dynamic_errors_preserve_identifiers(self):
  self.assertEqual(error_message('Duplicate routines ID: morning','de'),'Doppelte Kennung in routines: morning')
  self.assertIn('muss zwischen',error_message('energy must be between 0 and 100','de'))
 def test_document_pairs_and_links(self):
  root=Path(__file__).resolve().parents[1]
  files=list(root.glob('*.md'))+list((root/'docs').glob('*.md'))
  for file in files:
   if not file.name.endswith('.de.md'):
    self.assertTrue(file.with_name(file.stem+'.de.md').exists(),file.name)
   content=file.read_text(encoding='utf-8')
   for target in re.findall(r'\]\(([^)]+)\)',content):
    if '://' in target or target.startswith('#'):continue
    self.assertTrue((file.parent/target.split('#')[0]).exists(),str(file)+': '+target)
 def test_bilingual_repository_metadata(self):
  root=Path(__file__).resolve().parents[1]
  m=json.loads((root/'docs/repository-metadata.json').read_text(encoding='utf-8'))
  for key in ['description_en','description_de','description_bilingual']:
   self.assertTrue(m[key]);self.assertLessEqual(len(m[key]),350)
  self.assertEqual(m['description'],m['description_bilingual'])

class APILanguageTests(unittest.TestCase):
 def test_german_errors_and_quality_weighted_presets(self):
  with tempfile.TemporaryDirectory() as d:
   server=create_server(Path(d)/'life.db',port=0,token='test')
   thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
   try:
    url=f'http://127.0.0.1:{server.server_port}/v1/presets'
    req=Request(url,headers={'Accept-Language':'de-DE'})
    with self.assertRaises(HTTPError) as ex:urlopen(req,timeout=5)
    self.assertEqual(json.loads(ex.exception.read())['error'],'Authentifizierung erforderlich')
    req=Request(url,headers={'Authorization':'Bearer test','Accept-Language':'en;q=0.2,de-DE;q=0.9'})
    with urlopen(req,timeout=5) as result:self.assertEqual(json.loads(result.read())['bartender']['label'],'Barkeeper/in')
    req=Request(url,headers={'Authorization':'Bearer test','Accept-Language':'de;q=0,en;q=1'})
    with urlopen(req,timeout=5) as result:self.assertEqual(json.loads(result.read())['bartender']['label'],'bartender')
   finally:server.shutdown();server.server_close();thread.join()

if __name__=='__main__':unittest.main()
