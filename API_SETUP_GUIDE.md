# 🚀 API SETUP GUIDE - Autonomous Zenith Optimizer

## Übersicht
Dieser Guide zeigt dir, wie du echte API-Keys für NiceHash Mining Pool Integration und Telegram/Discord Alerts konfigurierst.

## 1. NiceHash API Setup

### Schritt 1: NiceHash Account erstellen
1. Gehe zu: https://www.nicehash.com/
2. Erstelle einen kostenlosen Account
3. Verifiziere deine E-Mail und Telefonnummer
4. Aktiviere 2FA für extra Sicherheit

### Schritt 2: API Keys generieren
1. Gehe zu: https://www.nicehash.com/settings/keys
2. Klicke auf "New API Key"
3. Gib einen Namen ein (z.B. "AZO Mining Bot")
4. Aktiviere die Berechtigungen:
   - `Read Info` - Lesen von Account-Informationen
   - `Withdraw` - Automatische Auszahlungen (optional)
   - `Trading` - Pool Mining Berechtigungen

### Schritt 3: Organization ID finden
1. Gehe zu: https://www.nicehash.com/my/settings/organization
2. Kopiere deine Organization ID (beginnt mit "org-")

### Schritt 4: .env aktualisieren
```
POOLS_NICEHASH_API_KEY=dein_api_key_hier
POOLS_NICEHASH_API_SECRET=dein_api_secret_hier
POOLS_NICEHASH_ORG_ID=deine_org_id_hier
```

### Schritt 5: NiceHash in settings.json aktivieren
```json
{
  "Pools": {
    "NiceHash": {
      "Enabled": true,
      "ApiKey": "${POOLS_NICEHASH_API_KEY}",
      "ApiSecret": "${POOLS_NICEHASH_API_SECRET}",
      "OrganizationId": "${POOLS_NICEHASH_ORG_ID}"
    }
  }
}
```

## 2. Telegram Alert Setup

### Schritt 1: Telegram Bot erstellen
1. Starte einen Chat mit @BotFather in Telegram
2. Sende: `/newbot`
3. Gib einen Bot-Namen ein (z.B. "AZO Mining Alert Bot")
4. Gib einen Username ein (z.B. "azo_mining_bot")
5. Speichere den Bot Token

### Schritt 2: Chat ID bekommen
1. Starte einen Chat mit deinem neuen Bot
2. Sende eine Nachricht
3. Gehe zu: `https://api.telegram.org/bot<YourBOTToken>/getUpdates`
4. Suche nach `"chat":{"id":xxxxx` - das ist deine Chat ID

### Schritt 3: .env aktualisieren
```
TELEGRAM_BOT_TOKEN=dein_bot_token_hier
TELEGRAM_CHAT_ID=deine_chat_id_hier
```

## 3. Discord Alert Setup

### Schritt 1: Discord Server und Webhook erstellen
1. Öffne Discord und erstelle einen Server (oder verwende einen bestehenden)
2. Gehe zu Server Settings > Integrations > Webhooks
3. Erstelle einen neuen Webhook mit Namen "AZO Mining Alerts"
4. Kopiere die Webhook URL

### Schritt 2: .env aktualisieren
```
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_id/your_webhook_token
```

## 4. System Test

Nachdem du die Keys konfiguriert hast:

```bash
cd "C:\Users\Laptop\Desktop\Autonomous Zenith Optimizer"
python quick_start.py
```

Du solltest sehen:
- ✅ NiceHash: "API konfiguriert - Echte Integration aktiv"
- ✅ Telegram: Test-Alert gesendet
- ✅ Discord: Test-Alert gesendet

## 5. Troubleshooting

### API-Fehler?
- Überprüfe deine Keys auf Korrektheit
- Stelle sicher, dass NiceHash API-Limits nicht überschritten sind
- Bot Token und Chat ID müssen korrekt sein

### Keine Alerts?
- Überprüfe Netzwerkverbindung
- Stelle sicher, dass Bots/Webhooks aktiv sind
- Prüfe Logs in `logs/mining_errors.log`

## 6. Sicherheitshinweise

- ✅ Verwende starke, einzigartige Passwörter
- ✅ Aktiviere 2FA überall
- ✅ Teile deine API-Keys NIEMALS öffentlich
- ✅ Nutze Umgebungsvariablen statt harte Kodierung
- ✅ Rotiere Keys regelmäßig

## Support

Bei Problemen schau in die Logs:
- `logs/mining_all.log` - Alle System-Events
- `logs/mining_errors.log` - Fehler und Warnungen

Das System läuft auch ohne API-Keys im Demo-Modus!
