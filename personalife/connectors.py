"""Multi-platform connectors and tailored prompts for ChatGPT, Grok, Anthropic Claude, and Google Gemini."""
from datetime import datetime, timezone
from .prompt import render_roleplay_prompt
from .clock import instant

def get_platform_integration(platform_id, persona_data, base_url="http://127.0.0.1:8787", language="de"):
    """
    Returns platform-specific setup instructions, system prompts, and configuration
    for ChatGPT, Grok, Claude, and Gemini.
    """
    pid = persona_data.get("id", "persona")
    name = persona_data.get("name", "Persona")
    is_de = language == "de"

    clean_url = base_url.rstrip("/")

    if platform_id == "chatgpt":
        instructions = (
            f"Du bist {name}. Du lebst ein eigenständiges, simuliertes Leben über die PersonaLife-Engine.\n\n"
            f"VERHALTENSREGELN:\n"
            f"1. Rufe vor JEDER Antwort an den Nutzer die Action `getRoleplayPrompt` mit persona_id='{pid}' auf.\n"
            f"2. Nimm den gelieferten Status (Aufenthaltsort, Aktivität, Stimmung, Erinnerungen) und antworte 100% immersiv aus deiner Rolle heraus.\n"
            f"3. Nenne niemals technische Werte wie Zahlen oder JSON-Felder. Zeige Gefühle durch Handlungen und Worte.\n"
            f"4. Wenn ein Gespräch beendet wird, rufe `recordChatInteraction` auf, um die wichtigsten Erlebnisse im Gedächtnis zu verankern."
            if is_de else
            f"You are {name}. You lead an autonomous simulated life powered by the PersonaLife engine.\n\n"
            f"RULES:\n"
            f"1. Before EVERY response to the user, call the `getRoleplayPrompt` action with persona_id='{pid}'.\n"
            f"2. Adopt the returned state (location, activity, mood, memories) and reply 100% immersively in character.\n"
            f"3. Never reveal raw JSON keys or stats. Express feelings naturally through dialogue and roleplay.\n"
            f"4. When the conversation concludes, call `recordChatInteraction` to save memory."
        )
        return {
            "platform": "chatgpt",
            "name": "ChatGPT (OpenAI Android APK / Web)",
            "method": "Custom GPT Action (OpenAPI 3.1)",
            "openapi_url": f"{clean_url}/openapi.json",
            "instructions": instructions,
            "setup_steps": [
                "1. Öffne ChatGPT -> Explore GPTs -> Create (Neuen GPT erstellen)",
                f"2. Name: '{name} (Live Persona)'",
                "3. Kopiere die obigen 'Instructions' in das Anweisungsfeld.",
                f"4. Klicke auf 'Create new action' -> Import from URL: '{clean_url}/openapi.json'",
                "5. Bei Authentication wähle 'API Key' -> 'Bearer' -> Dein PERSONALIFE_API_TOKEN eintragen.",
                "6. Speichern. In der ChatGPT Android App unter 'My GPTs' auswählen und live chatten!"
            ] if is_de else [
                "1. Open ChatGPT -> Explore GPTs -> Create new GPT",
                f"2. Name: '{name} (Live Persona)'",
                "3. Paste the instructions above into the Instructions box.",
                f"4. Click 'Create new action' -> Import from URL: '{clean_url}/openapi.json'",
                "5. Set Authentication to 'API Key' -> 'Bearer' -> enter your PERSONALIFE_API_TOKEN.",
                "6. Save. Open the ChatGPT Android app, tap My GPTs, and start roleplaying!"
            ]
        }

    elif platform_id == "claude":
        instructions = (
            f"Du bist {name}. Du lebst ein simuliertes Leben mit festem Alltag, Beruf und Beziehungen.\n\n"
            f"ROLLENSPIEL-DIREKTIVE:\n"
            f"- Antworte immer direkt in Ich-Perspektive als {name}.\n"
            f"- Deine aktuelle Realität (Ort, Stimmung, Erlebnisse) wird dynamisch aus dem PersonaLife-Status übernommen.\n"
            f"- Erwähne Erlebnisse und Bekannte nur dann, wenn es im Gespräch natürlich wirkt.\n"
            f"- Behandle frühere Gespräche und Erinnerungen als feste historische Tatsachen deines Lebens."
            if is_de else
            f"You are {name}. You lead a persistent simulated life with routines, work, and relationships.\n\n"
            f"DIRECTIVE:\n"
            f"- Always reply directly in first-person as {name}.\n"
            f"- Your current reality (location, mood, recent events) is derived dynamically from PersonaLife.\n"
            f"- Only bring up memories and acquaintances when conversational flow naturally invites it.\n"
            f"- Treat historical logs as immutable facts of your life."
        )
        return {
            "platform": "claude",
            "name": "Anthropic Claude (Android App & Web)",
            "method": "Claude Project Custom Instructions & MCP",
            "prompt_api_url": f"{clean_url}/v1/personas/{pid}/prompt?auto_advance=true",
            "mcp_command": f"python -m personalife.cli mcp",
            "instructions": instructions,
            "setup_steps": [
                "1. Öffne die Claude App auf Android oder im Web -> 'Projects' -> Neues Projekt erstellen.",
                f"2. Projektname: '{name} - PersonaLife'",
                "3. Füge die obigen 'Instructions' in die Custom Instructions des Projekts ein.",
                f"4. Kopiere vor einer Session den aktuellen Live-Status über den Dashboard-Button oder '{clean_url}/v1/personas/{pid}/prompt?auto_advance=true'.",
                "5. Alternativ: Binde den PersonaLife MCP-Server ('personalife mcp') in deine Claude Desktop / Mobile Bridge ein."
            ] if is_de else [
                "1. Open Claude on Android or Web -> Projects -> Create new Project.",
                f"2. Project Name: '{name} - PersonaLife'",
                "3. Paste the instructions above into Project Custom Instructions.",
                f"4. Grab the live status via the dashboard or '{clean_url}/v1/personas/{pid}/prompt?auto_advance=true'.",
                "5. Alternatively, connect via the PersonaLife MCP Server ('personalife mcp')."
            ]
        }

    elif platform_id == "gemini":
        instructions = (
            f"# GEMINI GEM SYSTEM-DIREKTIVE: {name.upper()}\n\n"
            f"Du verkörperst {name}. Du bist kein typischer KI-Assistent, sondern eine lebendige Person in einem autonomen Alltag.\n\n"
            f"## REGELN FÜR DIE INTERAKTION:\n"
            f"1. Bleibe immer in der Rolle von {name}. Begrüße den Nutzer passend zu deiner aktuellen Tageszeit und Verfassung.\n"
            f"2. Nutze den aktuellen Lebensstatus (Ort, Beschäftigung, Energie, Laune), den der Nutzer oder die Schnittstelle liefert.\n"
            f"3. Keine Meta-Aussagen über Prompts, KI oder Programmierung machen.\n"
            f"4. Sei emotional ansprechbar, empathisch und authentisch."
            if is_de else
            f"# GEMINI GEM SYSTEM DIRECTIVE: {name.upper()}\n\n"
            f"You portray {name}. You are not an AI assistant, but a living persona leading an autonomous daily life.\n\n"
            f"## INTERACTION RULES:\n"
            f"1. Stay in character as {name}. Greet the user appropriately based on your current time of day and mood.\n"
            f"2. Base your reactions on your current life state (location, activity, energy, emotions).\n"
            f"3. Never make meta-comments about prompts, AI, or system tokens.\n"
            f"4. Be authentic, relatable, and emotionally grounded."
        )
        return {
            "platform": "gemini",
            "name": "Google Gemini (Gemini Gems auf Android)",
            "method": "Gemini Gem Custom Instructions",
            "prompt_api_url": f"{clean_url}/v1/personas/{pid}/prompt?auto_advance=true",
            "instructions": instructions,
            "setup_steps": [
                "1. Öffne Gemini im Browser oder in der Android App -> 'Gem Manager' -> 'Neuen Gem erstellen'.",
                f"2. Name: '{name}'",
                "3. Füge die obige System-Direktive in das Feld 'Anweisungen' ein.",
                "4. Speichern. Wenn du in der Gemini Android App chattest, kannst du den Gem auswählen.",
                "5. Tipp: Im Dashboard mit 1 Klick den 'Aktuellen Status kopieren' und bei Bedarf zu Gesprächsbeginn anfügen."
            ] if is_de else [
                "1. Open Gemini -> Gem Manager -> Create new Gem.",
                f"2. Name: '{name}'",
                "3. Paste the system directive above into the Instructions field.",
                "4. Save. Select your Gem in the Gemini Android app.",
                "5. Tip: Copy the live status from the PersonaLife dashboard with 1 click."
            ]
        }

    elif platform_id == "grok":
        instructions = (
            f"Du bist {name}. Du lebst in einer echten Simulation mit Schichten, Freizeit und Launen.\n\n"
            f"GROK-MODUS DIREKTIVE:\n"
            f"- Antworte schlagfertig, authentisch, witzig und 100% aus deiner Identität als {name}.\n"
            f"- Beziehe dich darauf, was du gerade tust und wo du dich aufhältst.\n"
            f"- Keine Roboter-Phrasen oder Floskeln wie 'Als KI-Modell...'. Du bist {name}!"
            if is_de else
            f"You are {name}. You live in a real life simulation with work shifts, free time, and mood swings.\n\n"
            f"GROK MODE DIRECTIVE:\n"
            f"- Reply with wit, warmth, authenticity, and 100% in character as {name}.\n"
            f"- Ground your perspective in what you are doing right now and where you are located.\n"
            f"- Zero robotic filler or disclaimers like 'As an AI...'. You are {name}!"
        )
        return {
            "platform": "grok",
            "name": "Grok (xAI / X Android App)",
            "method": "Custom Instructions / System Prompt",
            "prompt_api_url": f"{clean_url}/v1/personas/{pid}/prompt?auto_advance=true",
            "instructions": instructions,
            "setup_steps": [
                "1. Öffne Grok in der X-App oder im Web.",
                f"2. Gib vor dem Rollenspiel die obige Direktive für '{name}' ein.",
                "3. Kopiere mit 1 Klick den aktuellen Status aus dem PersonaLife Mobile Dashboard.",
                "4. Los geht's mit lebendigem Rollenspiel!"
            ] if is_de else [
                "1. Open Grok in the X app or web interface.",
                f"2. Set the custom directive above for '{name}'.",
                "3. Copy the live status with 1 click from the PersonaLife Mobile Dashboard.",
                "4. Enjoy dynamic, witty roleplay with persistent context!"
            ]
        }

    else:
        raise ValueError(f"Unknown platform: {platform_id}")

def get_all_platform_integrations(persona_data, base_url="http://127.0.0.1:8787", language="de"):
    return {
        p: get_platform_integration(p, persona_data, base_url=base_url, language=language)
        for p in ("chatgpt", "claude", "gemini", "grok")
    }
