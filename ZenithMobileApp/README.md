# ZenithMobileApp (Smartphone)

Minimaler Android-Client (Kotlin) als **Smartphone-App**.

Funktion: Öffnet das bestehende Mobile-Dashboard aus diesem System per **WebView**.

## Was wird geladen?

- Standard-URL ist in `app/src/main/res/values/strings.xml` als `remote_hub_url` gesetzt.

### Emulator

- `http://10.0.2.2:3000/mobile?api=http://10.0.2.2:8503`
  - `10.0.2.2` zeigt im Android-Emulator auf den Host-PC.

### Physisches Smartphone (WLAN)

- Ersetze `10.0.2.2` durch die **LAN-IP deines PCs** (z.B. `192.168.178.20`).
- Beispiel:
  - `http://192.168.178.20:3000/mobile?api=http://192.168.178.20:8503`

## Start der Mobile-UI + Stats (auf dem PC)

Im bestehenden Repo `AutonomousZenithOptimizer`:

- Node UI: `remote_hub/server.mjs` (Port 3000)
- Flask Stats: `remote_hub/webhook_server.py` (Port 8503)
- Beides zusammen: `remote_hub/start_hub.ps1`

## Build/Run

Empfohlen: **Android Studio**

1. Ordner `ZenithMobileApp` in Android Studio öffnen.
2. Gradle Sync abwarten.
3. Run auf Emulator oder Gerät.

Wenn Android Studio nach dem Gradle Wrapper fragt, bestätige das Generieren (oder nutze im Terminal):

- `gradle wrapper`

CLI (optional):

- `./gradlew :app:assembleDebug`

Hinweis: Die App erlaubt für Entwicklung `http` (Cleartext), damit LAN-URLs funktionieren.
Für Play Store später auf `https` umstellen.
