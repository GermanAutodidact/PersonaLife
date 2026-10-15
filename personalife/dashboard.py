"""Interactive Mobile-First Visual Dashboard for PersonaLife.
Optimized for Android smartphones, Samsung DeX, split-screen, and desktop browsers.
"""

def render_dashboard_html(persona_id="jenna", base_url=""):
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>PersonaLife — Live Companion Dashboard</title>
    <style>
        :root {{
            --bg: #0b0f19;
            --surface: #141d2e;
            --surface-hover: #1b263b;
            --border: #23334d;
            --primary: #3b82f6;
            --primary-glow: rgba(59, 130, 246, 0.35);
            --accent: #8b5cf6;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --text-main: #f1f5f9;
            --text-muted: #94a3b8;
            --radius: 16px;
        }}
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            -webkit-tap-highlight-color: transparent;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}
        body {{
            background-color: var(--bg);
            color: var(--text-main);
            padding: 12px;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--surface);
            padding: 14px 18px;
            border-radius: var(--radius);
            border: 1px solid var(--border);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        }}
        .logo-area {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .pulse-indicator {{
            width: 12px;
            height: 12px;
            background-color: var(--success);
            border-radius: 50%;
            box-shadow: 0 0 10px var(--success);
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0% {{ transform: scale(0.95); opacity: 0.8; }}
            50% {{ transform: scale(1.2); opacity: 1; }}
            100% {{ transform: scale(0.95); opacity: 0.8; }}
        }}
        .logo-title {{
            font-size: 1.15rem;
            font-weight: 700;
            letter-spacing: -0.5px;
            background: linear-gradient(135deg, #60a5fa, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .live-clock {{
            font-size: 0.85rem;
            color: var(--text-muted);
            font-variant-numeric: tabular-nums;
        }}
        /* Main Persona Hero Card */
        .card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 18px;
            display: flex;
            flex-direction: column;
            gap: 14px;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
        }}
        .persona-hero {{
            display: flex;
            align-items: center;
            gap: 16px;
        }}
        .avatar {{
            width: 64px;
            height: 64px;
            border-radius: 50%;
            background: linear-gradient(135deg, #3b82f6, #8b5cf6);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.8rem;
            font-weight: 800;
            color: white;
            box-shadow: 0 0 20px var(--primary-glow);
            flex-shrink: 0;
        }}
        .persona-info {{
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}
        .persona-name {{
            font-size: 1.35rem;
            font-weight: 700;
        }}
        .persona-meta {{
            font-size: 0.85rem;
            color: var(--text-muted);
        }}
        .badges-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 4px;
        }}
        .badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid var(--border);
        }}
        .badge-loc {{
            background: rgba(59, 130, 246, 0.15);
            color: #93c5fd;
            border-color: rgba(59, 130, 246, 0.3);
        }}
        .badge-act {{
            background: rgba(139, 92, 246, 0.15);
            color: #c4b5fd;
            border-color: rgba(139, 92, 246, 0.3);
        }}
        /* Vitals Grid */
        .vitals-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }}
        @media (min-width: 600px) {{
            .vitals-grid {{
                grid-template-columns: repeat(3, 1fr);
            }}
        }}
        .vital-box {{
            background: rgba(0, 0, 0, 0.2);
            padding: 10px 12px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}
        .vital-head {{
            display: flex;
            justify-content: space-between;
            font-size: 0.75rem;
            color: var(--text-muted);
            font-weight: 600;
        }}
        .progress-track {{
            width: 100%;
            height: 6px;
            background: rgba(255, 255, 255, 0.08);
            border-radius: 4px;
            overflow: hidden;
        }}
        .progress-bar {{
            height: 100%;
            border-radius: 4px;
            transition: width 0.4s ease;
        }}
        .bar-energy {{ background: linear-gradient(90deg, #f59e0b, #10b981); }}
        .bar-mood {{ background: linear-gradient(90deg, #ec4899, #8b5cf6); }}
        .bar-stress {{ background: linear-gradient(90deg, #10b981, #ef4444); }}
        .bar-hunger {{ background: linear-gradient(90deg, #3b82f6, #f59e0b); }}
        .bar-fatigue {{ background: linear-gradient(90deg, #3b82f6, #ec4899); }}
        .bar-social {{ background: linear-gradient(90deg, #8b5cf6, #3b82f6); }}

        /* Action Buttons */
        .quick-actions {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }}
        .btn {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 14px 16px;
            border-radius: 12px;
            font-size: 0.9rem;
            font-weight: 600;
            border: none;
            cursor: pointer;
            transition: all 0.2s;
            text-decoration: none;
            text-align: center;
        }}
        .btn:active {{
            transform: scale(0.97);
        }}
        .btn-primary {{
            background: linear-gradient(135deg, #2563eb, #7c3aed);
            color: white;
            box-shadow: 0 4px 15px var(--primary-glow);
            grid-column: span 2;
            font-size: 1rem;
        }}
        .btn-secondary {{
            background: var(--surface-hover);
            color: var(--text-main);
            border: 1px solid var(--border);
        }}
        /* Platform Tabs */
        .tabs-header {{
            display: flex;
            gap: 6px;
            overflow-x: auto;
            padding-bottom: 4px;
        }}
        .tab-btn {{
            padding: 8px 14px;
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border);
            color: var(--text-muted);
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            white-space: nowrap;
        }}
        .tab-btn.active {{
            background: var(--primary);
            color: white;
            border-color: var(--primary);
            box-shadow: 0 2px 10px var(--primary-glow);
        }}
        .tab-pane {{
            display: none;
            flex-direction: column;
            gap: 12px;
            margin-top: 10px;
        }}
        .tab-pane.active {{
            display: flex;
        }}
        .code-box {{
            background: #060911;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 12px;
            font-family: monospace;
            font-size: 0.8rem;
            color: #cbd5e1;
            white-space: pre-wrap;
            word-break: break-all;
            max-height: 200px;
            overflow-y: auto;
        }}
        /* Notification Toast */
        .toast {{
            position: fixed;
            bottom: 24px;
            left: 50%;
            transform: translateX(-50%) translateY(100px);
            background: #10b981;
            color: white;
            padding: 12px 24px;
            border-radius: 30px;
            font-weight: 600;
            font-size: 0.9rem;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
            opacity: 0;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            z-index: 1000;
            pointer-events: none;
        }}
        .toast.show {{
            transform: translateX(-50%) translateY(0);
            opacity: 1;
        }}
    </style>
</head>
<body>

    <header class="header">
        <div class="logo-area">
            <div class="pulse-indicator"></div>
            <div>
                <div class="logo-title">PersonaLife Mobile</div>
                <div class="live-clock" id="clock-display">Synchronisiere...</div>
            </div>
        </div>
        <select id="persona-select" onchange="switchPersona(this.value)" style="background:var(--surface-hover); color:var(--text-main); border:1px solid var(--border); border-radius:8px; padding:6px 10px; font-size:0.85rem; outline:none;">
            <option value="{persona_id}">{persona_id.capitalize()}</option>
        </select>
    </header>

    <!-- Main Persona Status Card -->
    <main class="card">
        <div class="persona-hero">
            <div class="avatar" id="avatar-initial">J</div>
            <div class="persona-info">
                <div class="persona-name" id="name-display">{persona_id.capitalize()}</div>
                <div class="persona-meta" id="role-display">KI-Begleiterin</div>
                <div class="badges-row">
                    <span class="badge badge-loc" id="location-badge">📍 Lädt...</span>
                    <span class="badge badge-act" id="activity-badge">⏳ Aktivität</span>
                </div>
            </div>
        </div>

        <!-- Vital Bars -->
        <div class="vitals-grid">
            <div class="vital-box">
                <div class="vital-head"><span>⚡ ENERGIE</span><span id="val-energy">--%</span></div>
                <div class="progress-track"><div class="progress-bar bar-energy" id="bar-energy" style="width: 0%"></div></div>
            </div>
            <div class="vital-box">
                <div class="vital-head"><span>😊 LAUNE</span><span id="val-mood">--%</span></div>
                <div class="progress-track"><div class="progress-bar bar-mood" id="bar-mood" style="width: 0%"></div></div>
            </div>
            <div class="vital-box">
                <div class="vital-head"><span>😌 STRESS</span><span id="val-stress">--%</span></div>
                <div class="progress-track"><div class="progress-bar bar-stress" id="bar-stress" style="width: 0%"></div></div>
            </div>
            <div class="vital-box">
                <div class="vital-head"><span>🍔 HUNGER</span><span id="val-hunger">--%</span></div>
                <div class="progress-track"><div class="progress-bar bar-hunger" id="bar-hunger" style="width: 0%"></div></div>
            </div>
            <div class="vital-box">
                <div class="vital-head"><span>💤 MÜDIGKEIT</span><span id="val-fatigue">--%</span></div>
                <div class="progress-track"><div class="progress-bar bar-fatigue" id="bar-fatigue" style="width: 0%"></div></div>
            </div>
            <div class="vital-box">
                <div class="vital-head"><span>👥 SOZIAL</span><span id="val-social">--%</span></div>
                <div class="progress-track"><div class="progress-bar bar-social" id="bar-social" style="width: 0%"></div></div>
            </div>
        </div>

        <!-- Touch Actions -->
        <div class="quick-actions">
            <button class="btn btn-primary" onclick="copyRoleplayPrompt()">
                📋 Aktuellen Rollenspiel-Prompt kopieren
            </button>
            <button class="btn btn-secondary" onclick="openChatRecorder()">
                💬 Gespräch erfassen (Gemini KI)
            </button>
            <button class="btn btn-secondary" onclick="testLiveReply()">
                ✨ Live-Chat (Gemini Flash)
            </button>
            <button class="btn btn-secondary" onclick="refreshState()">
                🔄 Aktualisieren
            </button>
        </div>
    </main>

    <!-- App Connectors Section -->
    <section class="card">
        <h3 style="font-size: 1.05rem; font-weight: 700;">🚀 App-Einbindung & Konfiguration</h3>
        <p style="font-size: 0.8rem; color: var(--text-muted);">
            Wähle deine bevorzugte Android-App für fertige Anweisungen:
        </p>

        <div class="tabs-header">
            <button class="tab-btn active" onclick="showTab('chatgpt')">🟢 ChatGPT</button>
            <button class="tab-btn" onclick="showTab('claude')">🟣 Claude</button>
            <button class="tab-btn" onclick="showTab('gemini')">🔵 Gemini</button>
            <button class="tab-btn" onclick="showTab('grok')">⚫ Grok</button>
        </div>

        <!-- ChatGPT Tab -->
        <div class="tab-pane active" id="pane-chatgpt">
            <div style="font-size: 0.85rem; line-height: 1.4;">
                <strong>Android APK Action-Integration:</strong>
                Füge die folgende OpenAPI-URL in deinen Custom GPT ein:
            </div>
            <div class="code-box" id="chatgpt-openapi-url">Lädt...</div>
            <button class="btn btn-secondary" onclick="copyText('chatgpt-openapi-url', 'OpenAPI-URL kopiert!')">
                🔗 OpenAPI-URL kopieren
            </button>
            <button class="btn btn-secondary" onclick="copyText('chatgpt-instructions', 'Anweisungen kopiert!')">
                📋 Custom GPT Instructions kopieren
            </button>
            <div class="code-box" id="chatgpt-instructions" style="display:none;"></div>
        </div>

        <!-- Claude Tab -->
        <div class="tab-pane" id="pane-claude">
            <div style="font-size: 0.85rem; line-height: 1.4;">
                <strong>Claude Project & MCP:</strong>
                Kopiere die Custom Instructions für dein Claude-Projekt oder starte den MCP-Server:
            </div>
            <div class="code-box" id="claude-instructions">Lädt...</div>
            <button class="btn btn-secondary" onclick="copyText('claude-instructions', 'Claude-Instruktionen kopiert!')">
                📋 Claude Instructions kopieren
            </button>
        </div>

        <!-- Gemini Tab -->
        <div class="tab-pane" id="pane-gemini">
            <div style="font-size: 0.85rem; line-height: 1.4;">
                <strong>Gemini Gems (Android):</strong>
                Kopiere diese System-Direktive in deinen erstellten Gem:
            </div>
            <div class="code-box" id="gemini-instructions">Lädt...</div>
            <button class="btn btn-secondary" onclick="copyText('gemini-instructions', 'Gemini-Direktive kopiert!')">
                📋 Gemini Gem Instruktion kopieren
            </button>
        </div>

        <!-- Grok Tab -->
        <div class="tab-pane" id="pane-grok">
            <div style="font-size: 0.85rem; line-height: 1.4;">
                <strong>Grok / X App:</strong>
                System-Direktive für schnelles Rollenspiel in Grok:
            </div>
            <div class="code-box" id="grok-instructions">Lädt...</div>
            <button class="btn btn-secondary" onclick="copyText('grok-instructions', 'Grok-Direktive kopiert!')">
                📋 Grok Direktive kopieren
            </button>
        </div>
    </section>

    <!-- Quick Chat Modal / Sheet -->
    <div id="chat-sheet" style="display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.7); z-index: 900; align-items: flex-end; justify-content: center;">
        <div class="card" style="width: 100%; max-width: 500px; border-radius: 20px 20px 0 0; border-bottom: none; animation: slideUp 0.3s ease;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h3 style="font-size: 1.1rem; font-weight:700;">💬 Gespräch protokollieren</h3>
                <button onclick="closeChatRecorder()" style="background:none; border:none; color:var(--text-muted); font-size:1.5rem; cursor:pointer;">&times;</button>
            </div>
            <p style="font-size: 0.8rem; color: var(--text-muted);">
                Trage eine Zusammenfassung ein ODER füge den rohen Dialog aus ChatGPT, Claude, Grok oder Gemini ein – Google Gemini extrahiert automatisch Erinnerungen und berechnet emotionale Effekte!
            </p>
            <textarea id="chat-summary-input" rows="4" placeholder="Z.B.: Haben über ihren Tag geredet... ODER kopierten Chatverlauf hier einfügen!" style="background:var(--bg); color:var(--text-main); border:1px solid var(--border); border-radius:10px; padding:10px; outline:none; resize:none; font-size:0.9rem;"></textarea>
            <div style="display:flex; flex-direction:column; gap:8px;">
                <div style="display:flex; gap:10px;">
                    <button class="btn btn-primary" style="flex:1;" onclick="submitGeminiReflect()">✨ Mit Gemini KI analysieren</button>
                    <button class="btn btn-secondary" style="flex:1;" onclick="submitQuickChat()">💾 Direkt speichern</button>
                </div>
                <button class="btn btn-secondary" onclick="closeChatRecorder()">Abbrechen</button>
            </div>
        </div>
    </div>

    <div class="toast" id="toast">Aktion erfolgreich!</div>

    <script>
        let currentPersona = "{persona_id}";
        let authToken = localStorage.getItem("persona_token") || "";

        function showToast(msg) {{
            const t = document.getElementById("toast");
            t.innerText = msg;
            t.classList.add("show");
            setTimeout(() => t.classList.remove("show"), 2400);
        }}

        function showTab(platform) {{
            document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));
            event.target.classList.add("active");
            document.getElementById("pane-" + platform).classList.add("active");
        }}

        async function fetchWithAuth(url, options = {{}}) {{
            options.headers = options.headers || {{}};
            if (authToken) {{
                options.headers["Authorization"] = "Bearer " + authToken;
            }}
            options.headers["Accept-Language"] = "de";
            return fetch(url, options);
        }}

        async function refreshState() {{
            try {{
                const res = await fetchWithAuth(`/v1/personas/${{currentPersona}}/prompt?auto_advance=true`);
                if (res.status === 401) {{
                    const token = prompt("Bitte PERSONALIFE_API_TOKEN eingeben:");
                    if (token) {{
                        authToken = token;
                        localStorage.setItem("persona_token", token);
                        return refreshState();
                    }}
                }}
                const data = await res.json();
                if (data.prompt) {{
                    window.lastPrompt = data.prompt;
                }}
                if (data.location) {{
                    document.getElementById("location-badge").innerText = "📍 " + data.location;
                }}
                if (data.activity) {{
                    const actTitle = typeof data.activity === 'object' ? (data.activity.title || 'Aktivität') : data.activity;
                    document.getElementById("activity-badge").innerText = "⏳ " + actTitle;
                }}

                // Fetch detailed state
                const stateRes = await fetchWithAuth(`/v1/personas/${{currentPersona}}/state`);
                const stateData = await stateRes.json();
                if (stateData.now) {{
                    const d = new Date(stateData.now);
                    document.getElementById("clock-display").innerText = d.toLocaleDateString("de-DE", {{ weekday: 'short', hour: '2-digit', minute: '2-digit' }});
                }}
                if (stateData.state) {{
                    updateVitals(stateData.state);
                }}
            }} catch (e) {{
                console.error("State refresh error", e);
            }}
        }}

        function updateVitals(state) {{
            const updateBar = (id, val) => {{
                const elVal = document.getElementById("val-" + id);
                const elBar = document.getElementById("bar-" + id);
                if (elVal && elBar && val !== undefined) {{
                    const pct = Math.round(val);
                    elVal.innerText = pct + "%";
                    elBar.style.width = pct + "%";
                }}
            }};
            updateBar("energy", state.energy);
            updateBar("mood", state.mood_valence);
            updateBar("stress", state.stress);
            updateBar("hunger", state.hunger);
            updateBar("fatigue", state.fatigue);
            updateBar("social", state.social_energy);
        }}

        async function loadConnectors() {{
            try {{
                const origin = window.location.origin;
                document.getElementById("chatgpt-openapi-url").innerText = origin + "/openapi.json";

                const res = await fetchWithAuth(`/v1/personas/${{currentPersona}}/connectors`);
                if (res.ok) {{
                    const data = await res.json();
                    if (data.chatgpt) {{
                        document.getElementById("chatgpt-instructions").innerText = data.chatgpt.instructions;
                    }}
                    if (data.claude) {{
                        document.getElementById("claude-instructions").innerText = data.claude.instructions;
                    }}
                    if (data.gemini) {{
                        document.getElementById("gemini-instructions").innerText = data.gemini.instructions;
                    }}
                    if (data.grok) {{
                        document.getElementById("grok-instructions").innerText = data.grok.instructions;
                    }}
                }}
            }} catch (e) {{
                console.error("Connectors load error", e);
            }}
        }}

        async function copyRoleplayPrompt() {{
            await refreshState();
            if (window.lastPrompt) {{
                await navigator.clipboard.writeText(window.lastPrompt);
                showToast("📋 Rollenspiel-Prompt in Zwischenablage!");
            }} else {{
                showToast("Fehler beim Abrufen des Prompts.");
            }}
        }}

        async function copyText(elementId, successMsg) {{
            const text = document.getElementById(elementId).innerText;
            await navigator.clipboard.writeText(text);
            showToast(successMsg);
        }}

        function openChatRecorder() {{
            document.getElementById("chat-sheet").style.display = "flex";
            document.getElementById("chat-summary-input").focus();
        }}

        function closeChatRecorder() {{
            document.getElementById("chat-sheet").style.display = "none";
            document.getElementById("chat-summary-input").value = "";
        }}

        async function submitQuickChat() {{
            const summary = document.getElementById("chat-summary-input").value.trim();
            if (!summary) return;
            try {{
                const res = await fetchWithAuth(`/v1/personas/${{currentPersona}}/quick-chat`, {{
                    method: "POST",
                    headers: {{ "Content-Type": "application/json" }},
                    body: JSON.stringify({{ summary: summary, duration_minutes: 10 }})
                }});
                if (res.ok) {{
                    closeChatRecorder();
                    showToast("✅ Gespräch im Gedächtnis gespeichert!");
                    refreshState();
                }} else {{
                    showToast("Fehler beim Speichern");
                }}
            }} catch (e) {{
                showToast("Netzwerkfehler");
            }}
        }}

        async function submitGeminiReflect() {{
            const text = document.getElementById("chat-summary-input").value.trim();
            if (!text) return;
            showToast("⏳ Gemini KI analysiert Gespräch...");
            try {{
                const res = await fetchWithAuth(`/v1/personas/${{currentPersona}}/reflect`, {{
                    method: "POST",
                    headers: {{ "Content-Type": "application/json" }},
                    body: JSON.stringify({{ dialogue: text, duration_minutes: 10 }})
                }});
                if (res.ok) {{
                    closeChatRecorder();
                    showToast("✨ Erinnerungen & Vitalwerte via Gemini aktualisiert!");
                    refreshState();
                }} else {{
                    showToast("Fehler bei Gemini-Analyse");
                }}
            }} catch (e) {{
                showToast("Netzwerkfehler");
            }}
        }}

        async function testLiveReply() {{
            const msg = prompt("Nachricht an Persona (Live-Test mit Gemini Flash):", "Hallo, wie geht es dir gerade?");
            if (!msg) return;
            showToast("⏳ Persona denkt nach (Gemini Flash)...");
            try {{
                const res = await fetchWithAuth(`/v1/personas/${{currentPersona}}/chat-reply`, {{
                    method: "POST",
                    headers: {{ "Content-Type": "application/json" }},
                    body: JSON.stringify({{ message: msg, record: true }})
                }});
                if (res.ok) {{
                    const data = await res.json();
                    alert(`💬 Antwort von ${{data.persona_name || "Persona"}}:\n\n${{data.reply}}`);
                    refreshState();
                }} else {{
                    showToast("Fehler beim Abrufen der Antwort");
                }}
            }} catch (e) {{
                showToast("Netzwerkfehler");
            }}
        }}

        // Init
        refreshState();
        loadConnectors();
        setInterval(refreshState, 30000); // 30s auto-refresh
    </script>
</body>
</html>
"""
