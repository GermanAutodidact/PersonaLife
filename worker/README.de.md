# PersonaLife Edge Gateway (Cloudflare Worker)

Dieser Cloudflare Worker dient als globales, hochverfügbares **Edge-Gateway** für PersonaLife. Er verbindet Smartphones und KI-Apps (wie die **ChatGPT Android APK**, Claude, Gemini und Grok) sicher und mit minimaler Latenz mit deiner lokalen Lebenssimulations-Engine.

---

## 🚀 Funktionen des Workers

1. **Globales OpenAPI 3.1 & Schema-Hosting:**
   - Liefert unter `/openapi.json` das Schema für ChatGPT Custom Actions aus.
   - Hochverfügbar auf dem Cloudflare Edge CDN, selbst wenn der heimische PC kurz neustartet.
2. **Sicherer Reverse-Proxy & Token-Injektion:**
   - Leitet Anfragen (`/v1/*`, `/dashboard`) direkt über deinen Cloudflare Tunnel an deinen lokalen PersonaLife-Server (`127.0.0.1:8787`) weiter.
   - Kann das `PERSONALIFE_API_TOKEN` automatisch auf Edge-Ebene injizieren.
3. **Intelligenter Offline-Schlafmodus:**
   - Falls der Heim-PC oder der Tunnel offline ist, gibt der Worker keinen Fehlercode zurück, sondern versetzt den Charakter in einen passenden Offline-/Schlafzustand (*„Jenna schläft tief und fest oder ist gerade nicht am Handy erreichbar...“*).
4. **Zero-Configuration CORS:**
   - Alle Anfragen (inkl. `OPTIONS`-Preflight) werden mit sauberen CORS-Headern versehen.

---

## 📦 Deployment auf Cloudflare (mit 1 Befehl)

### 1. Einmaliger Login (falls noch nicht geschehen)
```powershell
npx wrangler login
```
*Oder über die Umgebungsvariable `CLOUDFLARE_API_TOKEN`:*
```powershell
$env:CLOUDFLARE_API_TOKEN="dein-token"
```

### 2. Tunnel-Adresse konfigurieren
Öffne `wrangler.jsonc` und trage bei `ORIGIN_URL` deine bestehende Cloudflare Tunnel Domain ein:
```jsonc
"vars": {
  "ORIGIN_URL": "https://persona.deine-domain.com",
  "PERSONA_ID": "jenna",
  "FALLBACK_LANGUAGE": "de"
}
```

### 3. Deployen
```powershell
cd worker
npx wrangler deploy
```

Nach wenigen Sekunden ist dein Worker weltweit online unter:
`https://personalife-edge-gateway.<dein-subdomain>.workers.dev`

---

## 📱 Einbindung in die ChatGPT Android APK
- **Action-URL:** `https://personalife-edge-gateway.<dein-subdomain>.workers.dev/openapi.json`
- ChatGPT greift nun weltweit und stabil über das Cloudflare Edge-Netzwerk auf deine Persona zu!
