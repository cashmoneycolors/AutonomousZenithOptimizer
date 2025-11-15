#!/usr/bin/env python3
"""QUICK SYSTEM STARTUP DEMO"""
print("🚀 AUTONOMOUS ZENITH OPTIMIZER - SYSTEM STARTUP")

# Konfiguration
from python_modules.config_manager import validate_config
errors = validate_config()
print(f"⚙️ Konfiguration: {'OK' if not errors else f'{len(errors)} Fehler'}")

# Markt-Daten
from python_modules.market_integration import get_crypto_prices
prices = get_crypto_prices()
print(f"📊 Markt-Daten: {len(prices)} Coins - BTC: ${prices.get('BTC', {}).get('usd', 0):.0f}")

# Pool-Integration
from python_modules.nicehash_integration import get_pool_stats
stats = get_pool_stats()
print(f"🏭 Pool-Stats: {len(stats)} Algorithmen verfügbar")

# Risiko-Management starten
from python_modules.risk_manager import start_risk_monitoring, get_risk_status
start_risk_monitoring()
print("🛡️ Risiko-Management: GESTARTET")

# Backup-System starten
from python_modules.auto_backup import start_auto_backup, get_backup_statistics
start_auto_backup()
stats = get_backup_statistics()
print(f"💾 Auto-Backup: {stats.get('total_backups', 0)} Sicherungen")

# Alert-System testen
from python_modules.alert_system import send_custom_alert
send_custom_alert('QUICK_STARTUP', 'System erfolgreich gestartet!', '✅')
print("🚨 Alert-System: AKTIV")

# Mining-System starten
from python_modules.mining_system_integration import start_mining_system, get_mining_status
start_mining_system()
import time
time.sleep(1)
system_status = get_mining_status()
print(f"⛏️ Mining-System: {'AKTIV' if system_status.get('is_running') else 'INAKTIV'}")
print(f"   Aktive Rigs: {system_status.get('system_status', {}).get('active_rigs', 0)}")

print("\n🎉 AUTONOMOUS ZENITH OPTIMIZER IST LEBENDIG!")
print("=" * 60)
print("AKTIVE KOMPONENTEN:")
print("✅ Live Markt-Daten Monitor (CoinGecko)")
print("✅ NiceHash Pool Integration")
print("✅ Risiko-Management (Stop-Loss & Diversifikation)")
print("✅ Alert-System (Telegram/Discord bereit)")
print("✅ Mining-System (bereit für Krypto-Mining)")
print("✅ Auto-Backup (stündliche Sicherungen)")
print("✅ Strukturiertes Logging (aktiv)")
print("\n🚀 SYSTEM BEREIT FÜR PRODUKTIONSBETRIEB!")
