#!/usr/bin/env python3
"""
CASH MONEY COLORS ORIGINAL (R) - ALERT SYSTEM
Telegram/Discord Integration für Live-Benachrichtigungen
"""
import requests
from datetime import datetime
from typing import Dict, List, Any
import os
from python_modules.config_manager import get_config


class AlertSystem:
    """Vereinheitlichtes Alert-System für alle Benachrichtigungen"""

    def __init__(self):
        self.telegram_config = get_config("Alerts.Telegram", {})
        self.discord_config = get_config("Alerts.Discord", {})
        self.enabled_alerts = []
        self.alert_history = []

        # Aktiviere verfügbare Services
        if self.telegram_config.get("Enabled", False):
            self.enabled_alerts.append("telegram")
            print("📱 Telegram Alerts aktiviert")
        if self.discord_config.get("Enabled", False):
            self.enabled_alerts.append("discord")
            print("🎮 Discord Alerts aktiviert")

        if not self.enabled_alerts:
            print(
                "⚠️ Keine Alert-Services aktiviert. Konfiguriere Telegram oder Discord in settings.json"
            )

        print("🚨 ALERT SYSTEM INITIALIZED")

    def send_profit_alert(self, profit_data: Dict[str, Any]):
        """Benachrichtigung bei Profit-Milestones"""
        current_profit = profit_data.get("current_total_profit", 0)
        daily_profit = profit_data.get("daily_profit", 0)
        min_alert = float(
            self.telegram_config.get("MinProfitAlert", 50)
            or self.discord_config.get("MinProfitAlert", 50)
        )

        if daily_profit >= min_alert:
            message = f"💰 PROFIT ALERT!\n💵 Tagesprofit: {daily_profit:.2f} CHF\n💎 Gesamtprofit: {current_profit:.2f} CHF\n⏰ {datetime.now().strftime('%H:%M:%S')}"

            self._send_alert(message, "PROFIT")
            self._log_alert("PROFIT", message, profit_data)

    def send_temperature_alert(self, rig_data: Dict[str, Any]):
        """Benachrichtigung bei Temperatur-Problemen"""
        temp = rig_data.get("temperature", 0)
        max_temp = float(
            self.telegram_config.get("TemperatureThreshold", 85)
            or self.discord_config.get("TemperatureThreshold", 85)
        )

        if temp >= max_temp:
            message = f"🔥 TEMPERATUR ALERT!\n🔌 Rig: {rig_data.get('id', 'Unknown')}\n🌡️ Temperatur: {temp:.1f}°C\n⚠️ MAX: {max_temp}°C\n⏰ {datetime.now().strftime('%H:%M:%S')}"

            self._send_alert(message, "TEMPERATURE")
            self._log_alert("TEMPERATURE", message, rig_data)

    def send_rig_failure_alert(self, rig_data: Dict[str, Any]):
        """Benachrichtigung bei Rig-Ausfällen"""
        message = f"❌ RIG FAILURE ALERT!\n🔌 Rig: {rig_data.get('id', 'Unknown')}\n⚙️ Status: {rig_data.get('status', 'FAILED')}\n🔄 Hashrate: {rig_data.get('hash_rate', 0)} MH/s\n⏰ {datetime.now().strftime('%H:%M:%S')}"

        self._send_alert(message, "RIG_FAILURE")
        self._log_alert("RIG_FAILURE", message, rig_data)

    def send_market_alert(self, market_data: Dict[str, Any]):
        """Benachrichtigung bei Markt-Änderungen"""
        price_changes = []
        for coin, data in market_data.items():
            change_24h = data.get("change_24h", 0)
            if abs(change_24h) >= 5.0:  # 5% Schwelle
                price_changes.append(
                    f"{coin}: {change_24h:+.1f}% (${data.get('usd', 0):.2f})"
                )

        if price_changes:
            message = (
                "📈 MARKET ALERT!\n"
                + "\n".join(price_changes)
                + f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"
            )

            self._send_alert(message, "MARKET")
            self._log_alert("MARKET", message, market_data)

    def send_system_alert(
        self, alert_type: str, message: str, data: Dict[str, Any] = None
    ):
        """Benachrichtigung bei System-Events"""
        formatted_message = f"⚙️ SYSTEM ALERT - {alert_type.upper()}\n{message}\n⏰ {datetime.now().strftime('%H:%M:%S')}"

        self._send_alert(formatted_message, alert_type.upper())
        self._log_alert(alert_type.upper(), formatted_message, data or {})

    def send_custom_alert(self, title: str, message: str, emoji: str = "ℹ️"):
        """Benutzerdefinierte Benachrichtigung"""
        formatted_message = f"{emoji} {title.upper()}\n{message}\n⏰ {datetime.now().strftime('%H:%M:%S')}"

        self._send_alert(formatted_message, "CUSTOM")
        self._log_alert("CUSTOM", formatted_message, {"title": title, "emoji": emoji})

    def _send_telegram_alert(self, message: str):
        """Sendet Alert via Telegram"""
        if "telegram" not in self.enabled_alerts:
            return

        bot_token = os.getenv("TELEGRAM_BOT_TOKEN") or self.telegram_config.get(
            "BotToken", ""
        )
        chat_id = os.getenv("TELEGRAM_CHAT_ID") or self.telegram_config.get(
            "ChatId", ""
        )

        if not bot_token or not chat_id:
            print("⚠️ Telegram-Bot nicht konfiguriert")
            return

        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}

            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                print("📱 Telegram Alert gesendet")
            else:
                print(f"❌ Telegram Fehler: {response.status_code}")

        except Exception as e:
            print(f"❌ Telegram Exception: {e}")

    def _send_discord_alert(self, message: str):
        """Sendet Alert via Discord Webhook"""
        if "discord" not in self.enabled_alerts:
            return

        webhook_url = os.getenv("DISCORD_WEBHOOK_URL") or self.discord_config.get(
            "WebhookUrl", ""
        )

        if not webhook_url:
            print("⚠️ Discord-Webhook nicht konfiguriert")
            return

        try:
            payload = {
                "content": message,
                "username": "AZO Mining Bot",
                "avatar_url": "https://i.imgur.com/4M34hi2.png",
            }

            response = requests.post(webhook_url, json=payload, timeout=10)
            if response.status_code == 204:
                print("🎮 Discord Alert gesendet")
            else:
                print(f"❌ Discord Fehler: {response.status_code}")

        except Exception as e:
            print(f"❌ Discord Exception: {e}")

    def _send_alert(self, message: str, alert_type: str):
        """Sendet Alert an alle aktivierten Services"""
        if self.telegram_config.get(
            "Enabled", False
        ) and alert_type in self.telegram_config.get("AlertTypes", ["all"]):
            self._send_telegram_alert(message)

        if self.discord_config.get(
            "Enabled", False
        ) and alert_type in self.discord_config.get("AlertTypes", ["all"]):
            self._send_discord_alert(message)

    def _log_alert(self, alert_type: str, message: str, data: Dict[str, Any]):
        """Loggt Alert intern"""
        alert_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": alert_type,
            "message": message,
            "data": data,
        }
        self.alert_history.append(alert_entry)

        # Behalte nur die letzten 100 Alerts
        if len(self.alert_history) > 100:
            self.alert_history.pop(0)

        print(f"🚨 ALERT LOGGED: {alert_type}")

    def get_alert_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Gibt Alert-Historie zurück"""
        return self.alert_history[-limit:]

    def test_alert(self, service: str = "all"):
        """Test-Funktion für Alerts"""
        test_message = f"🧪 TEST ALERT\nAlert-System funktioniert!\nService: {service}\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        if service in ["telegram", "all"]:
            self._send_telegram_alert(test_message)
        if service in ["discord", "all"]:
            self._send_discord_alert(test_message)

        print(f"🧪 Test-Alert gesendet an: {service}")


# Globale Alert-Instanz
alert_system = AlertSystem()


# Convenience-Funktionen
def send_profit_alert(profit_data):
    """Profit-Benachrichtigung"""
    alert_system.send_profit_alert(profit_data)


def send_temperature_alert(rig_data):
    """Temperatur-Benachrichtigung"""
    alert_system.send_temperature_alert(rig_data)


def send_rig_failure_alert(rig_data):
    """Rig-Ausfall Benachrichtigung"""
    alert_system.send_rig_failure_alert(rig_data)


def send_market_alert(market_data):
    """Markt-Benachrichtigung"""
    alert_system.send_market_alert(market_data)


def send_system_alert(alert_type, message, data=None):
    """System-Benachrichtigung"""
    alert_system.send_system_alert(alert_type, message, data or {})


def send_custom_alert(title, message, emoji="ℹ️"):
    """Benutzerdefinierte Benachrichtigung"""
    alert_system.send_custom_alert(title, message, emoji)


def test_alert(service="all"):
    """Test-Benachrichtigung"""
    alert_system.test_alert(service)


def get_alert_history(limit=20):
    """Alert-Historie"""
    return alert_system.get_alert_history(limit)


if __name__ == "__main__":
    print("CASH MONEY COLORS ORIGINAL (R) - ALERT SYSTEM")
    print("=" * 50)

    print("🧪 Teste Alert-System...")

    # Test-Profite Alert
    test_profit_data = {"current_total_profit": 1250.50, "daily_profit": 75.30}
    send_profit_alert(test_profit_data)

    # Test-Temperatur Alert
    test_rig_data = {"id": "GPU_1", "temperature": 89.5, "status": "OVERHEATING"}
    send_temperature_alert(test_rig_data)

    # Test-Markt Alert
    test_market_data = {
        "BTC": {"usd": 95000, "change_24h": -7.5},
        "ETH": {"usd": 3800, "change_24h": 12.3},
    }
    send_market_alert(test_market_data)

    print("\n✅ ALERT SYSTEM BEREIT!")
    print(
        "Verwende send_profit_alert(), send_temperature_alert(), send_market_alert(), etc."
    )
    print("Konfiguriere Telegram/Discord in settings.json für echte Benachrichtigungen")
