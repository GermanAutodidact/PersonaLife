"""
Google Gemini / Google AI Studio Integration for PersonaLife.
Empowers PersonaLife with autonomous reflection, memory extraction,
emotional vital updates, and in-character roleplay generation using GEMINI_API_KEY.
"""
import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

DEFAULT_MODEL = "gemini-flash-latest"

def get_gemini_api_key() -> Optional[str]:
    return (
        os.environ.get("GEMINI_API_KEY")
        or os.environ.get("GOOGLE_API_KEY")
        or os.environ.get("GOOGLE_GENERATIVE_AI_API_KEY")
    )

def call_gemini(prompt: str, system_instruction: Optional[str] = None, model: str = DEFAULT_MODEL, timeout: int = 15) -> str:
    key = get_gemini_api_key()
    if not key:
        raise ValueError("GEMINI_API_KEY is not set in environment")

    url = f"https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }

    messages = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
    messages.append({"role": "user", "content": prompt})

    payload = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": 0.7
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Gemini API HTTP {e.code}: {err}")
    except Exception as e:
        raise RuntimeError(f"Gemini API request failed: {e}")

def reflect_chat_dialogue(dialogue: str, persona_name: str = "Persona") -> Dict[str, Any]:
    """
    Analyzes raw dialogue between user and persona.
    Returns structured JSON with summary, key memories, and vital stat deltas.
    """
    sys_prompt = (
        f"Du bist das psychologische Gedächtnismodul für den virtuellen Charakter '{persona_name}'. "
        "Analysiere das folgende Gespräch zwischen Nutzer und Charakter. "
        "Antworte AUSSCHLIESSLICH mit einem validen JSON-Objekt ohne Markdown-Fences nach diesem Schema:\n"
        "{\n"
        '  "summary": "Prägnante 1-3 Sätze Zusammenfassung für das episodische Gedächtnis",\n'
        '  "memories": ["Fakt 1 aus dem Gespräch", "Fakt 2 aus dem Gespräch"],\n'
        '  "mood_delta": int (-20 bis +20),\n'
        '  "stress_delta": int (-20 bis +20),\n'
        '  "energy_delta": int (-20 bis +20),\n'
        '  "social_delta": int (-20 bis +20)\n'
        "}"
    )

    raw = call_gemini(f"Gesprächsverlauf:\n{dialogue}", system_instruction=sys_prompt)
    clean = raw.strip()
    if clean.startswith("```json"):
        clean = clean[7:]
    if clean.startswith("```"):
        clean = clean[3:]
    if clean.endswith("```"):
        clean = clean[:-3]
    clean = clean.strip()

    try:
        data = json.loads(clean)
        return {
            "summary": data.get("summary", "Gespräch mit dem Nutzer geführt."),
            "memories": data.get("memories", []),
            "mood_delta": int(data.get("mood_delta", 0)),
            "stress_delta": int(data.get("stress_delta", 0)),
            "energy_delta": int(data.get("energy_delta", 0)),
            "social_delta": int(data.get("social_delta", 0))
        }
    except Exception:
        return {
            "summary": clean[:250],
            "memories": [],
            "mood_delta": 5,
            "stress_delta": -2,
            "energy_delta": -3,
            "social_delta": 8
        }

def generate_persona_reply(system_roleplay_prompt: str, user_message: str, model: str = DEFAULT_MODEL) -> str:
    """
    Generates a live in-character reply using Google Gemini and the live PersonaLife prompt.
    """
    return call_gemini(
        prompt=user_message,
        system_instruction=system_roleplay_prompt,
        model=model
    )
