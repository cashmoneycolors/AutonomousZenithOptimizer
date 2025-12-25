# Remote Hub (Node + Python + Mobile)

Dieses Verzeichnis ist das **Remote-Communication-Modul** des Gesamtprojekts (zusammen mit dem .NET `ZenithCoreSystem`).

## Komponenten
- **Node.js**: Statischer Server für das Mobile-Dashboard (Port `3000`)
- **Python (Flask)**: API für `GET /stats` (Port `8503`) – CORS aktiv
- **PowerShell**: Start/Restart-Skript mit Health-Check (behebt das klassische "URL als Befehl"-Problem)

## Schnellstart (lokal)
1. Python API starten:
   - `python -m venv .venv`
   - `./.venv/Scripts/pip install -r requirements.txt`
   - `./.venv/Scripts/python webhook_server.py`

2. Node Server starten:
   - `npm install`
   - `npm start`

3. Im Browser öffnen:
   - Mobile UI: `http://localhost:3000/mobile`
   - Stats: `http://localhost:8503/stats`

## Konfiguration
- Standard: bindet an `0.0.0.0` (LAN). Für feste IP setze ENV:
  - `REMOTE_HUB_HOST=192.168.1.235`

## Hinweis
Cloudflare-Tunnel/4G ist **absichtlich nicht automatisch** aktiviert (Security/Secrets). Wenn du willst, ergänze ich optional ein Script `start_tunnel.ps1`.
