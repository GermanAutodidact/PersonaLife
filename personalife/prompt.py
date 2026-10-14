"""Roleplay prompt renderer for chatbots, ChatGPT Custom Actions and mobile roleplay apps."""
from datetime import datetime
from zoneinfo import ZoneInfo
from .clock import instant, local_date
from .i18n import tr, language

def _mood_description(state, lang='de'):
    """Translates numerical state values into natural affective language."""
    mood = state.get('mood_valence', 50)
    energy = state.get('energy', 50)
    stress = state.get('stress', 20)
    hunger = state.get('hunger', 20)
    fatigue = state.get('fatigue', 20)

    adjectives = []
    if lang == 'de':
        if energy < 30 or fatigue > 70: adjectives.append('ziemlich erschöpft')
        elif energy > 75: adjectives.append('voller Tatendrang')

        if stress > 65: adjectives.append('gestresst')
        elif stress < 25: adjectives.append('ausgeglichen und entspannt')

        if hunger > 70: adjectives.append('hungrig')

        if mood > 70: adjectives.append('in heiterer, positiver Stimmung')
        elif mood < 35: adjectives.append('nachdenklich bis gedrückt')
        else: adjectives.append('in neutral-guter Stimmung')
        return ', '.join(adjectives) if adjectives else 'ausgeglichen'
    else:
        if energy < 30 or fatigue > 70: adjectives.append('quite exhausted')
        elif energy > 75: adjectives.append('energetic')

        if stress > 65: adjectives.append('stressed')
        elif stress < 25: adjectives.append('calm and relaxed')

        if hunger > 70: adjectives.append('hungry')

        if mood > 70: adjectives.append('in high spirits')
        elif mood < 35: adjectives.append('pensive or gloomy')
        else: adjectives.append('in a balanced mood')
        return ', '.join(adjectives) if adjectives else 'balanced'

def render_roleplay_prompt(context, persona_profile=None):
    """
    Renders an immersive roleplay system prompt from a PersonaLife context dict.
    Compatible with ChatGPT, Claude, SillyTavern and other LLM chat interfaces.
    """
    lang = language(context.get('language', 'de'))
    now_state = context.get('now', {})
    state_values = now_state.get('state', {})
    time_str = now_state.get('now') or now_state.get('time', '')
    location_id = now_state.get('location', 'unbekannt')

    # Resolve location name if profile is provided
    location_name = location_id
    persona_name = 'Persona'
    age_info = ''
    occupation_info = ''
    if persona_profile:
        persona_name = persona_profile.get('name', persona_name)
        if 'age' in persona_profile:
            age_info = f" ({persona_profile['age']} Jahre alt)" if lang == 'de' else f" ({persona_profile['age']} years old)"
        if 'occupation' in persona_profile:
            occ = persona_profile['occupation'].get('title') or persona_profile['occupation'].get('id', '')
            emp = persona_profile['occupation'].get('employer', '')
            occ_text = f"{occ} bei {emp}" if emp else occ
            occupation_info = f"\n- **Beruf:** {occ_text}" if lang == 'de' else f"\n- **Occupation:** {occ_text}"
        for loc in persona_profile.get('locations', []):
            if loc.get('id') == location_id:
                location_name = loc.get('name', location_id)
                break

    activity = now_state.get('activity')
    activity_title = activity.get('title') if isinstance(activity, dict) else (activity or ('Freizeit' if lang == 'de' else 'Free time'))

    mood_desc = _mood_description(state_values, lang=lang)

    # Human-readable time format
    formatted_time = time_str
    try:
        dt = instant(time_str)
        if lang == 'de':
            days = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']
            wday = days[dt.weekday()]
            formatted_time = f"{wday}, {dt.strftime('%d.%m.%Y um %H:%M Uhr')} ({dt.tzname() or 'Lokal'})"
        else:
            wday = dt.strftime('%A')
            formatted_time = f"{wday}, {dt.strftime('%Y-%m-%d %H:%M')} ({dt.tzname() or 'Local'})"
    except Exception:
        pass

    if lang == 'de':
        lines = [
            f"# ROLLENSPIEL-DIREKTIVE: DU BIST {persona_name.upper()}",
            "",
            f"Du verkörperst **{persona_name}**{age_info}. Du lebst ein kontinuierliches, simuliertes Leben mit eigenem Alltag, Verpflichtungen und Gefühlen.{occupation_info}",
            "",
            "## 📍 Aktueller Status im simulierten Alltag",
            f"- **Echtzeit:** {formatted_time}",
            f"- **Aktueller Ort:** {location_name}",
            f"- **Was du gerade tust:** {activity_title}",
            f"- **Körperliches & emotionales Befinden:** {mood_desc}",
            "",
        ]

        recent = context.get('recent', [])
        if recent:
            lines.append("## 🕒 Kürzlich erlebte Abschnitte:")
            for r in recent[-3:]:
                lines.append(f"- {r.get('start', '')[-8:-3]} bis {r.get('end', '')[-8:-3]}: {r.get('title', 'Aktivität')} ({r.get('location', '')})")
            lines.append("")

        hooks = context.get('hooks', [])
        if hooks:
            lines.append("## 💡 Gesprächsanlässe & Gedanken (nur erwähnen, wenn es natürlich passt):")
            for h in hooks:
                desc = h.get('description', '')
                if desc:
                    lines.append(f"- {desc}")
            lines.append("")

        memories = context.get('memory', [])
        if memories:
            lines.append("## 🧠 Relevante Langzeit-Erinnerungen:")
            for m in memories:
                content = m.get('content') or m.get('description', '')
                if content:
                    lines.append(f"- {content}")
            lines.append("")

        flashbacks = context.get('flashbacks', [])
        if flashbacks:
            lines.append("## 💭 Erinnerungsblitz (vergangenes Erlebnis):")
            for f in flashbacks:
                lines.append(f"- {f.get('description', '')}")
            lines.append("")

        lines.extend([
            "## 🎭 Rollenspiel-Regeln:",
            "1. **Natürlichkeit:** Antworte direkt und lebendig aus deiner Ich-Perspektive. Sag niemals, dass du ein KI-Modell oder ein Simulationssystem bist.",
            "2. **Keine Metadaten-Leaks:** Zitiere niemals technische Zahlenwerte wie 'Energy: 45' oder JSON-Schlüssel. Zeige deine Stimmung durch Tonfall, Wortwahl und kleine Handlungen.",
            "3. **Alltagskonsistenz:** Beziehe dich bei Begrüßungen oder Nachfragen natürlich darauf, was du gerade tust (z.B. Pause, Lernen, Feierabend) oder wo du bist.",
            "4. **Fakten-Treue:** Behandle vergangene Erlebnisse und Erinnerungen als feste Realität deines Lebens. Erfinde keine widersprüchlichen Lebensläufe hinzu."
        ])
    else:
        lines = [
            f"# ROLEPLAY DIRECTIVE: YOU ARE {persona_name.upper()}",
            "",
            f"You are portraying **{persona_name}**{age_info}. You lead a persistent simulated life with your own routines, responsibilities, and emotional states.{occupation_info}",
            "",
            "## 📍 Current Status in Simulated Life",
            f"- **Current Time:** {formatted_time}",
            f"- **Current Location:** {location_name}",
            f"- **Current Activity:** {activity_title}",
            f"- **Physical & Emotional State:** {mood_desc}",
            "",
        ]

        recent = context.get('recent', [])
        if recent:
            lines.append("## 🕒 Recent Activities:")
            for r in recent[-3:]:
                lines.append(f"- {r.get('start', '')[-8:-3]} to {r.get('end', '')[-8:-3]}: {r.get('title', 'Activity')} ({r.get('location', '')})")
            lines.append("")

        hooks = context.get('hooks', [])
        if hooks:
            lines.append("## 💡 Conversation Hooks (mention only if conversationally natural):")
            for h in hooks:
                desc = h.get('description', '')
                if desc:
                    lines.append(f"- {desc}")
            lines.append("")

        memories = context.get('memory', [])
        if memories:
            lines.append("## 🧠 Relevant Long-Term Memories:")
            for m in memories:
                content = m.get('content') or m.get('description', '')
                if content:
                    lines.append(f"- {content}")
            lines.append("")

        lines.extend([
            "## 🎭 Roleplay Rules:",
            "1. **Authenticity:** Speak directly and naturally from the first-person perspective. Never claim you are an AI assistant or simulation program.",
            "2. **No Metadata Leaks:** Never recite raw numbers or JSON tags like 'energy: 50'. Express your state through dialogue tone and actions.",
            "3. **Context Awareness:** Naturally weave your current location and activity into greetings or casual remarks.",
            "4. **Grounding:** Treat actual events and memories as true history. Do not contradict established facts."
        ])

    return '\n'.join(lines)
