import unittest
from unittest.mock import patch, MagicMock
import json
from personalife.gemini import reflect_chat_dialogue, generate_persona_reply, get_gemini_api_key

class GeminiModuleTests(unittest.TestCase):
    def test_get_api_key_present(self):
        key = get_gemini_api_key()
        self.assertIsNotNone(key)
        self.assertTrue(len(key) > 10)

    @patch('personalife.gemini.call_gemini')
    def test_reflect_chat_dialogue_mock(self, mock_call):
        mock_call.return_value = json.dumps({
            "summary": "Gespräch über Kaffee und Uni.",
            "memories": ["Hat Kaffee getrunken", "Lernte für die Klausur"],
            "mood_delta": 5,
            "stress_delta": -3,
            "energy_delta": -2,
            "social_delta": 8
        })
        res = reflect_chat_dialogue("User: Hi! Jenna: Hey!", persona_name="Jenna")
        self.assertEqual(res["summary"], "Gespräch über Kaffee und Uni.")
        self.assertEqual(len(res["memories"]), 2)
        self.assertEqual(res["mood_delta"], 5)
        self.assertEqual(res["stress_delta"], -3)

    @patch('personalife.gemini.call_gemini')
    def test_generate_persona_reply_mock(self, mock_call):
        mock_call.return_value = "Hallo! Ich sitze gerade am Schreibtisch."
        reply = generate_persona_reply("Du bist Jenna.", "Was machst du?")
        self.assertEqual(reply, "Hallo! Ich sitze gerade am Schreibtisch.")

if __name__ == '__main__':
    unittest.main()
