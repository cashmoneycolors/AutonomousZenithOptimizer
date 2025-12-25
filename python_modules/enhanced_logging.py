#!/usr/bin/env python3
"""
CASH MONEY COLORS ORIGINAL (R) - ENHANCED LOGGING SYSTEM
Strukturiertes Logging mit Log-Leveln für Mining-System
"""
import logging
import logging.handlers
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional


class MiningFormatter(logging.Formatter):
    """Spezialisierter Formatter für Mining-Logs"""

    def format(self, record):
        # Basis-Format
        base_format = super().format(record)

        # Mining-spezifische Felder hinzufügen
        if hasattr(record, "mining_data"):
            mining_info = f" | MINING_DATA: {record.mining_data}"
            base_format += mining_info

        if hasattr(record, "profit_info"):
            profit_info = f" | PROFIT: {record.profit_info}"
            base_format += profit_info

        if hasattr(record, "rig_info"):
            rig_info = f" | RIG: {record.rig_info}"
            base_format += rig_info

        return base_format


class MiningLogger:
    """Erweitertes Logging-System für Mining-Operationen"""

    def __init__(
        self,
        log_dir: str = "logs",
        max_bytes: int = 10 * 1024 * 1024,
        backup_count: int = 5,
    ):
        self.log_dir = log_dir
        self.max_bytes = max_bytes
        self.backup_count = backup_count

        # Log-Verzeichnis erstellen
        os.makedirs(log_dir, exist_ok=True)

        # Logger erstellen
        self.logger = logging.getLogger("MiningSystem")
        self.logger.setLevel(logging.DEBUG)

        # Bestehende Handler entfernen
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # Formatter
        self.formatter = MiningFormatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Console Handler
        self.console_handler = logging.StreamHandler()
        self.console_handler.setLevel(logging.INFO)
        self.console_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.console_handler)

        # File Handler für alle Logs
        self.all_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, "mining_all.log"),
            maxBytes=max_bytes,
            backupCount=backup_count,
        )
        self.all_handler.setLevel(logging.DEBUG)
        self.all_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.all_handler)

        # File Handler für Fehler
        self.error_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, "mining_errors.log"),
            maxBytes=max_bytes,
            backupCount=backup_count,
        )
        self.error_handler.setLevel(logging.ERROR)
        self.error_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.error_handler)

        # File Handler für Mining-Operationen
        self.mining_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, "mining_operations.log"),
            maxBytes=max_bytes,
            backupCount=backup_count,
        )
        self.mining_handler.setLevel(logging.INFO)
        self.mining_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.mining_handler)

        print("ENHANCED LOGGING SYSTEM INITIALIZED")
        print(f"Log-Verzeichnis: {log_dir}")
        print("Log-Rotation: Aktiviert")

    def log_mining_cycle(self, cycle_data: Dict[str, Any]):
        """Loggt Mining-Zyklus-Daten"""
        extra = {
            "mining_data": f"Cycle_{cycle_data.get('cycle', 'N/A')} | Capital: {cycle_data.get('capital_after', 0):.2f} CHF | Profit: {cycle_data.get('cycle_profit', 0):.2f} CHF"
        }
        self.logger.info(f"MINING_CYCLE_COMPLETED", extra=extra)

    def log_profit_calculation(self, profit_data: Dict[str, Any]):
        """Loggt Profit-Berechnungen"""
        extra = {
            "profit_info": f"Algorithm: {profit_data.get('algorithm', 'N/A')} | Expected: {profit_data.get('expected_profit_chf', 0):.2f} CHF/day"
        }
        self.logger.info(
            f"PROFIT_CALCULATION | {profit_data.get('best_coin', 'N/A')}", extra=extra
        )

    def log_rig_status(self, rig_data: Dict[str, Any]):
        """Loggt Rig-Status"""
        status = "ACTIVE" if rig_data.get("status") == "ACTIVE" else "INACTIVE"
        extra = {
            "rig_info": f"{rig_data.get('id', 'N/A')} | {rig_data.get('type', 'N/A')} | Temp: {rig_data.get('temperature', 0)}°C | Status: {status}"
        }
        self.logger.info(f"RIG_STATUS_UPDATE", extra=extra)

    def log_system_event(self, event_type: str, event_data: Dict[str, Any]):
        """Loggt System-Events"""
        if event_type == "STARTUP":
            self.logger.info(
                f"SYSTEM_STARTUP | Version: {event_data.get('version', 'N/A')}"
            )
        elif event_type == "SHUTDOWN":
            self.logger.info(
                f"SYSTEM_SHUTDOWN | Uptime: {event_data.get('uptime', 'N/A')}"
            )
        elif event_type == "OPTIMIZATION":
            self.logger.info(
                f"OPTIMIZATION_EXECUTED | Type: {event_data.get('optimization_type', 'N/A')}"
            )
        elif event_type == "ERROR":
            self.logger.error(
                f"SYSTEM_ERROR | {event_data.get('error_message', 'Unknown error')}"
            )
        elif event_type == "WARNING":
            self.logger.warning(
                f"SYSTEM_WARNING | {event_data.get('warning_message', 'Unknown warning')}"
            )
        else:
            self.logger.info(f"EVENT_{event_type} | {json.dumps(event_data)}")

    def log_market_data(self, market_data: Dict[str, Any]):
        """Loggt Markt-Daten"""
        coins_logged = len(market_data)
        self.logger.info(f"MARKET_DATA_UPDATED | {coins_logged} coins refreshed")

        # Detaillierte Logs für wichtige Coins
        important_coins = ["BTC", "ETH", "RVN", "XMR"]
        for coin in important_coins:
            if coin in market_data:
                data = market_data[coin]
                self.logger.debug(
                    f"MARKET_{coin} | USD: ${data.get('usd', 0):.2f} | CHF: CHF {data.get('chf', 0):.2f} | Change: {data.get('change_24h', 0):+.1f}%"
                )

    def log_backup_operation(self, operation: str, backup_data: Dict[str, Any]):
        """Loggt Backup-Operationen"""
        if operation == "CREATED":
            self.logger.info(
                f"BACKUP_CREATED | {backup_data.get('filename', 'N/A')} | Size: {backup_data.get('size_mb', 0):.2f} MB"
            )
        elif operation == "RESTORED":
            self.logger.info(f"BACKUP_RESTORED | {backup_data.get('filename', 'N/A')}")
        elif operation == "DELETED":
            self.logger.info(
                f"BACKUP_DELETED | {backup_data.get('filename', 'N/A')} (old backup cleanup)"
            )

    def get_log_stats(self) -> Dict[str, Any]:
        """Gibt Logging-Statistiken zurück"""
        stats = {"log_directory": self.log_dir, "log_files": [], "total_size_mb": 0}

        if os.path.exists(self.log_dir):
            for file in os.listdir(self.log_dir):
                if file.endswith(".log"):
                    file_path = os.path.join(self.log_dir, file)
                    file_size = os.path.getsize(file_path)
                    modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))

                    stats["log_files"].append(
                        {
                            "filename": file,
                            "size_mb": file_size / (1024 * 1024),
                            "modified": modified_time,
                        }
                    )
                    stats["total_size_mb"] += file_size / (1024 * 1024)

        return stats

    def cleanup_old_logs(self, days_to_keep: int = 30):
        """Räumt alte Log-Dateien auf"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)

        if os.path.exists(self.log_dir):
            for file in os.listdir(self.log_dir):
                if file.endswith(".log"):
                    file_path = os.path.join(self.log_dir, file)
                    modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))

                    if modified_time < cutoff_date:
                        try:
                            os.remove(file_path)
                            self.logger.info(
                                f"OLD_LOG_DELETED | {file} (older than {days_to_keep} days)"
                            )
                        except Exception as e:
                            self.logger.error(
                                f"LOG_CLEANUP_ERROR | Failed to delete {file}: {e}"
                            )


# Globale Logger-Instanz
mining_logger = MiningLogger()


# Convenience-Funktionen
def log_cycle(cycle_data):
    """Loggt Mining-Zyklus"""
    mining_logger.log_mining_cycle(cycle_data)


def log_profit(profit_data):
    """Loggt Profit-Berechnung"""
    mining_logger.log_profit_calculation(profit_data)


def log_rig(rig_data):
    """Loggt Rig-Status"""
    mining_logger.log_rig_status(rig_data)


def log_event(event_type, event_data=None):
    """Loggt System-Event"""
    if event_data is None:
        event_data = {}
    mining_logger.log_system_event(event_type, event_data)


def log_market(market_data):
    """Loggt Markt-Daten"""
    mining_logger.log_market_data(market_data)


def log_backup(operation, backup_data):
    """Loggt Backup-Operation"""
    mining_logger.log_backup_operation(operation, backup_data)


def get_logging_stats():
    """Gibt Logging-Statistiken"""
    return mining_logger.get_log_stats()


if __name__ == "__main__":
    print("CASH MONEY COLORS ORIGINAL (R) - ENHANCED LOGGING SYSTEM")
    print("=" * 70)

    # Test des Logging-Systems
    print("🧪 Teste Enhanced Logging System...")

    # System-Events loggen
    log_event("STARTUP", {"version": "2.0", "timestamp": datetime.now().isoformat()})

    # Mining-Zyklus simulieren
    cycle_data = {
        "cycle": 1,
        "capital_before": 100.0,
        "capital_after": 130.08,
        "cycle_profit": 30.08,
    }
    log_cycle(cycle_data)

    # Profit-Berechnung loggen
    profit_data = {
        "algorithm": "ethash",
        "best_coin": "ETH",
        "expected_profit_chf": 3440.03,
    }
    log_profit(profit_data)

    # Rig-Status loggen
    rig_data = {
        "id": "GPU_1",
        "type": "RTX 4090",
        "temperature": 72,
        "status": "ACTIVE",
    }
    log_rig(rig_data)

    # Markt-Daten simulieren
    market_data = {
        "BTC": {"usd": 95000, "chf": 89000, "change_24h": -2.5},
        "ETH": {"usd": 2800, "chf": 2620, "change_24h": 1.2},
    }
    log_market(market_data)

    # Backup-Operation loggen
    backup_data = {"filename": "test_backup.json", "size_mb": 2.5}
    log_backup("CREATED", backup_data)

    # Statistiken anzeigen
    stats = get_logging_stats()
    print(f"📊 Logging-Statistiken:")
    print(f"   Log-Verzeichnis: {stats['log_directory']}")
    print(f"   Log-Dateien: {len(stats['log_files'])}")
    print(f"   Gesamt-Größe: {stats['total_size_mb']:.2f} MB")

    print("\n✅ ENHANCED LOGGING SYSTEM BEREIT!")
    print(
        "Verwende log_cycle(), log_profit(), log_rig(), log_event() für strukturiertes Logging"
    )
