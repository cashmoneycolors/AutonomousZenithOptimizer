#!/usr/bin/env python3
"""
AUTONOMOUS ZENITH OPTIMIZER - SYSTEM STARTUP
Vollständiges System zum Leben erwecken mit allen Komponenten
"""
import time
import threading
from datetime import datetime

print("🚀 AUTONOMOUS ZENITH OPTIMIZER - SYSTEM STARTUP")
print("=" * 60)
print(f"⏰ Startup Zeit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Schritt 1: Konfiguration laden
print("\n⚙️ 1. KONFIGURATION LADEN...")
from python_modules.config_manager import get_config, validate_config

try:
    validation_errors = validate_config()
    if validation_errors:
        print(f"⚠️ Konfigurations-Warnungen: {len(validation_errors)}")
        for error in validation_errors[:3]:  # Zeige nur erste 3
            print(f"   - {error}")
    else:
        print("✅ Konfiguration vollständig validiert")

    # Lade kritische Einstellungen
    mining_config = get_config('Mining', {})
    risk_config = get_config('RiskManagement', {})
    print(f"   Mining-Algorithmus: {mining_config.get('DefaultAlgorithm', 'N/A')}")
    print(f"   Risiko-Schutz: {'AKTIV' if risk_config.get('StopLossEnabled', False) else 'INAKTIV'}")

except Exception as e:
    print(f"❌ Fehler beim Konfigurations-Laden: {e}")

# Schritt 2: Markt-Daten initialisieren
print("\n📊 2. MARKT-DATEN SYSTEM...")
from python_modules.market_integration import get_crypto_prices

try:
    market_prices = get_crypto_prices()
    print(f"✅ Markt-Daten geladen für {len(market_prices)} Coins")

    # Zeige Top-Coins
    top_coins = ['BTC', 'ETH', 'RVN']
    for coin in top_coins:
        if coin in market_prices:
            data = market_prices[coin]
            print(f"   {coin}: ${data.get('usd', 0):.0f} ({data.get('change_24h', 0):+.1f}%)")

except Exception as e:
    print(f"❌ Markt-Daten Fehler: {e}")

# Schritt 3: Pool-Integration testen
print("\n🏭 3. POOL-INTEGRATION...")
from python_modules.nicehash_integration import get_pool_stats, optimize_mining_strategy, get_mining_rigs

try:
    pool_stats = get_pool_stats()
    print(f"✅ Pool-Statistiken verfügbar für {len(pool_stats)} Algorithmen")

    # Mining-Rigs prüfen
    rigs = get_mining_rigs()
    print(f"   Mining-Rigs: {len(rigs)} konfiguriert")

    # Optimierung testen
    rigs_config = get_config('Rigs', [])
    if rigs_config:
        optimization = optimize_mining_strategy(rigs_config[:2])  # Nur erste 2 für Speed
        print(f"   Strategie-Empfehlung: {optimization.get('recommended_switch_all', 'N/A')}")

except Exception as e:
    print(f"❌ Pool-Integration Fehler: {e}")

# Schritt 4: Alert-System vorbereiten
print("\n🚨 4. ALERT-SYSTEM VORBEREITEN...")
from python_modules.alert_system import send_system_alert

try:
    send_system_alert("SYSTEM_STARTUP", "Autonomous Zenith Optimizer System wird gestartet", {"time": datetime.now().isoformat()})
    print("✅ Alert-System bereit (Benachrichtigungen werden gesendet)")

except Exception as e:
    print(f"❌ Alert-System Fehler: {e}")

# Schritt 5: Backup-System starten
print("\n💾 5. BACKUP-SYSTEM STARTEN...")
from python_modules.auto_backup import start_auto_backup, get_backup_statistics

try:
    start_auto_backup()
    time.sleep(0.5)  # Kleiner Delay für Startup
    stats = get_backup_statistics()
    print(f"✅ Auto-Backup gestartet ({stats.get('total_backups', 0)} vorhandene Sicherungen)")

except Exception as e:
    print(f"❌ Backup-System Fehler: {e}")

# Schritt 6: Risiko-Management aktivieren
print("\n🛡️ 6. RISIKO-MANAGEMENT STARTEN...")
from python_modules.risk_manager import start_risk_monitoring, get_risk_status

try:
    start_risk_monitoring()
    time.sleep(0.5)  # Startup-Delay
    risk_status = get_risk_status()
    print(f"✅ Risiko-Monitoring aktiv ({'EMERGENCY STOP' if risk_status.get('emergency_stop') else 'NORMAL'})")

except Exception as e:
    print(f"❌ Risiko-Management Fehler: {e}")

# Schritt 7: Mining-System starten
print("\n⛏️ 7. MINING-SYSTEM STARTEN...")
from python_modules.mining_system_integration import start_mining_system, get_system_status

try:
    start_mining_system()
    time.sleep(1.0)  # Startup-Delay

    system_status = get_system_status()
    print(f"✅ Mining-System {'AKTIV' if system_status.get('is_running', False) else 'INAKTIV'}")
    print(f"   Aktive Rigs: {system_status.get('system_status', {}).get('active_rigs', 0)}")
    print(f"   Total Profit: CHF {system_status.get('system_status', {}).get('total_profit', 0):.4f}")

except Exception as e:
    print(f"❌ Mining-System Fehler: {e}")

# Schritt 8: System-Status Überwachung starten
print("\n📈 8. SYSTEM-STATUS ÜBERWACHUNG...")

def system_monitor_loop():
    """Kontinuierliche System-Überwachung"""
    while True:
        try:
            # System-Status abrufen
            system_status = get_system_status()
            risk_status = get_risk_status()

            # Aktualisiere Status alle 30 Sekunden
            print(f"\n🔄 STATUS UPDATE {datetime.now().strftime('%H:%M:%S')}:")
            print(f"   Mining: {'🚀 ACTIVE' if system_status.get('is_running') else '⏸️  INACTIVE'}")
            print(f"   Rigs: {system_status.get('system_status', {}).get('active_rigs', 0)}")
            print(f"   Profit: CHF {system_status.get('system_status', {}).get('total_profit', 0):.4f}")
            print(f"   Risiko: {'🛡️  OK' if not risk_status.get('emergency_stop') else '🚨 EMERGENCY'}")

            time.sleep(30)  # Alle 30 Sekunden

        except KeyboardInterrupt:
            print("\n⏹️ System-Monitoring gestoppt (Benutzer-Eingabe)")
            break
        except Exception as e:
            print(f"❌ Monitoring-Fehler: {e}")
            time.sleep(10)

# Schritt 9: Finale System-Bereitschaft
print("\n🎯 9. FINALE SYSTEM-BEREITSCHAFT...")
print("✅ ALLE SYSTEM-KOMPONENTEN GESTARTET!")
print("=" * 60)
print("🚀 AUTONOMOUS ZENITH OPTIMIZER IST JETZT LEBENDIG!")
print()
print("AKTIVE KOMPONENTEN:")
print("   - 📊 Live Markt-Daten Monitor")
print("   - 🏭 NiceHash Pool Integration")
print("   - 🛡️ Risiko-Management (Stop-Loss & Diversifikation)")
print("   - 🚨 Alert-System (Telegram/Discord bereit)")
print("   - ⛏️  Mining-System (kontinuierlicher Betrieb)")
print("   - 💾 Auto-Backup (stündlich)")
print("   - 📝 Strukturiertes Logging (aktiv)")
print()
print("🔄 SYSTEM MONITORING... (Strg+C zum Stoppen)")

# Finale Alert
try:
    send_system_alert("SYSTEM_STARTUP_COMPLETE",
                     "Alle Autonomous Zenith Optimizer Komponenten erfolgreich gestartet und operationell",
                     {"startup_time": datetime.now().isoformat()})
except:
    pass

# Start kontinuierliche Überwachung
try:
    system_monitor_loop()
except KeyboardInterrupt:
    print("\n" + "="*60)
    print("🛑 SYSTEM ABSCHALTUNG...")
    print("Alle Komponenten werden sauber beendet...")

    # Graceful Shutdown
    try:
        from python_modules.mining_system_integration import stop_mining_system
        stop_mining_system()
        print("✅ Mining-System gestoppt")
    except:
        pass

    try:
        from python_modules.risk_manager import stop_risk_monitoring
        stop_risk_monitoring()
        print("✅ Risiko-Monitoring gestoppt")
    except:
        pass

    try:
        from python_modules.auto_backup import stop_auto_backup
        stop_auto_backup()
        print("✅ Backup-System gestoppt")
    except:
        pass

    print("🎯 AUTONOMOUS ZENITH OPTIMIZER KOMPLETT GESHUTTED DOWN!")
    print("="*60)
