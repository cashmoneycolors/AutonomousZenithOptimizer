#!/usr/bin/env python3
"""
CASH MONEY COLORS ORIGINAL (R) - CONFIG MANAGER
Zentrale Konfigurationsverwaltung für alle Systemparameter
"""
import json
import os
import re
from pathlib import Path
from typing import Dict, Any, Optional, List


class ConfigManager:
    """Zentrale Konfigurationsverwaltung"""

    def __init__(self, config_file: str = "settings.json"):
        self.config_file = config_file
        self.config = {}
        self.env_vars = {}

        # Lokale .env (optional) laden, ohne echte ENV zu überschreiben
        self._load_dotenv()

        # Umgebungsvariablen sammeln
        self._load_env_vars()

        # Konfiguration laden
        self.load_config()

        print("CONFIG MANAGER INITIALIZED")
        print(f"Config File: {config_file}")
        print(f"Loaded {len(self.config)} configuration sections")

    def _load_env_vars(self):
        """Läd alle relevanten Umgebungsvariablen"""
        env_mapping = {
            "OPENROUTER_API_KEY": "OPENROUTER_API_KEY",
            "GEMINI_API_KEY": "GEMINI_API_KEY",
            "XAI_API_KEY": "XAI_API_KEY",
            "BLACKBOX_API_KEY": "BLACKBOX_API_KEY",
            "PAYPAL_CLIENT_ID": "PAYPAL_CLIENT_ID",
            "PAYPAL_CLIENT_SECRET": "PAYPAL_CLIENT_SECRET",
            "DEEPSEEK_MINING_KEY": "DEEPSEEK_MINING_KEY",
            "COINBASE_API_KEY": "COINBASE_API_KEY",
            "BINANCE_API_KEY": "BINANCE_API_KEY",
            "COINMARKETCAP_API_KEY": "COINMARKETCAP_API_KEY",
            "TELEGRAM_BOT_TOKEN": "TELEGRAM_BOT_TOKEN",
            "TELEGRAM_CHAT_ID": "TELEGRAM_CHAT_ID",
            "DISCORD_WEBHOOK_URL": "DISCORD_WEBHOOK_URL",
            "NICEHASH_API_KEY": "NICEHASH_API_KEY",
            "NICEHASH_API_SECRET": "NICEHASH_API_SECRET",
            "NICEHASH_ORG_ID": "NICEHASH_ORG_ID",
            "POOLS_NICEHASH_API_KEY": "POOLS_NICEHASH_API_KEY",
            "POOLS_NICEHASH_API_SECRET": "POOLS_NICEHASH_API_SECRET",
            "POOLS_NICEHASH_ORG_ID": "POOLS_NICEHASH_ORG_ID",
            "MININGPOOLHUB_API_KEY": "MININGPOOLHUB_API_KEY",
            "MINING_WALLET_ADDRESS": "MINING_WALLET_ADDRESS",
            "AZURE_SUBSCRIPTION_ID": "AZURE_SUBSCRIPTION_ID",
        }

        for key, env_var in env_mapping.items():
            value = os.getenv(env_var)
            if value:
                self.env_vars[key] = value

        print(f"[API] Loaded {len(self.env_vars)} environment variables")

    def _load_dotenv(self):
        """Lädt einfache KEY=VALUE Paare aus einer lokalen .env Datei.

        - Überschreibt keine bereits gesetzten ENV-Variablen.
        - Unterstützt Kommentare (#) und leere Zeilen.
        """

        candidates = []
        try:
            candidates.append(Path(self.config_file).resolve().parent / ".env")
        except Exception:
            pass

        candidates.append(Path.cwd() / ".env")

        dotenv_path = next((p for p in candidates if p.exists()), None)
        if not dotenv_path:
            return

        loaded = 0
        try:
            for raw_line in dotenv_path.read_text(
                encoding="utf-8"
            ).splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue

                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")

                if not key:
                    continue
                if key in os.environ:
                    continue

                os.environ[key] = value
                loaded += 1

            if loaded:
                print(f"[ENV] Loaded {loaded} values from {dotenv_path}")
        except Exception as e:
            print(f"[ENV] Failed to load .env: {e}")

    def load_config(self):
        """Lädt Konfiguration aus JSON-Datei"""
        if not os.path.exists(self.config_file):
            print(
                f"WARNING: Config file {self.config_file} not found, "
                "creating default config"
            )
            self._create_default_config()
            return

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                raw_config = json.load(f)

            # Umgebungsvariablen ersetzen
            self.config = self._resolve_env_vars(raw_config)

            print(f"Config loaded from {self.config_file}")

        except Exception as e:
            print(f"Error loading config: {e}")
            self._create_default_config()

    def _resolve_env_vars(self, config: Any) -> Any:
        """Ersetzt ${VAR} Platzhalter mit Umgebungsvariablen.

        Unterstützt sowohl reine Platzhalter-Strings ("${VAR}") als auch
        eingebettete Platzhalter in Strings ("prefix-${VAR}-suffix").
        """

        if isinstance(config, dict):
            resolved: Dict[str, Any] = {}
            for key, value in config.items():
                resolved[key] = self._resolve_env_vars(value)
            return resolved

        if isinstance(config, list):
            return [self._resolve_env_vars(item) for item in config]

        if isinstance(config, str):
            # Schnellpfad: kein Platzhalter enthalten
            if "${" not in config:
                return config

            # Ersetze alle ${VAR} Vorkommen im String
            pattern = re.compile(r"\$\{([A-Z0-9_]+)\}")

            def repl(match: re.Match[str]) -> str:
                var_name = match.group(1)
                return self.env_vars.get(var_name) or os.getenv(var_name, "")

            return pattern.sub(repl, config)

        return config

    def _try_get_env_override(self, key_path: str) -> Optional[str]:
        """Erlaubt ENV-Overrides ohne config-Datei-Anpassung."""
        overrides = {
            # Mining
            "Mining.WalletAddress": ["MINING_WALLET_ADDRESS"],
            # NiceHash (beide Namensschemata unterstützen)
            "Pools.NiceHash.ApiKey": [
                "POOLS_NICEHASH_API_KEY",
                "NICEHASH_API_KEY",
            ],
            "Pools.NiceHash.ApiSecret": [
                "POOLS_NICEHASH_API_SECRET",
                "NICEHASH_API_SECRET",
            ],
            "Pools.NiceHash.OrganizationId": [
                "POOLS_NICEHASH_ORG_ID",
                "NICEHASH_ORG_ID",
            ],
            # Alerts
            "Alerts.Telegram.BotToken": ["TELEGRAM_BOT_TOKEN"],
            "Alerts.Telegram.ChatId": ["TELEGRAM_CHAT_ID"],
            "Alerts.Discord.WebhookUrl": ["DISCORD_WEBHOOK_URL"],
        }

        for env_var in overrides.get(key_path, []):
            value = os.getenv(env_var)
            if value:
                return value
        return None

    def _create_default_config(self):
        """Erstellt Standardkonfiguration"""
        self.config = {
            "System": {
                "Name": "Autonomous Zenith Optimizer",
                "Version": "2.0.0",
                "Environment": "development",
                "LogLevel": "INFO",
            },
            "Mining": {
                "DefaultAlgorithm": "ethash",
                "DefaultCoin": "ETH",
                "TargetProfitPerMonth": 5000.0,
                "ElectricityCostPerKwh": 0.15,
                "MaxTemperature": 85.0,
                "MinTemperature": 40.0,
            },
            "Rigs": [],
            "Market": {
                "PrimaryApi": "coingecko",
                "CacheDurationMinutes": 5,
                "FallbackEnabled": True,
            },
            "Backup": {"Enabled": True, "IntervalHours": 1},
            "Logging": {"Enabled": True, "LogDir": "logs"},
        }

        # Speichere Standardkonfig
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
            print(f"Default config saved to {self.config_file}")
        except Exception as e:
            print(f"Error saving default config: {e}")

    def save_config(self):
        """Speichert aktuelle Konfiguration"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
            print(f"Config saved to {self.config_file}")
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key_path: str, default=None):
        """Holt Wert aus Konfiguration mit Punkt-Notation"""
        env_override = self._try_get_env_override(key_path)
        if env_override is not None:
            return env_override

        keys = key_path.split(".")
        value = self.config

        try:
            for key in keys:
                if isinstance(value, dict):
                    value = value[key]
                elif isinstance(value, list) and key.isdigit():
                    value = value[int(key)]
                else:
                    return default
            return value
        except (KeyError, IndexError, TypeError):
            return default

    def set(self, key_path: str, value: Any):
        """Setzt Wert in Konfiguration mit Punkt-Notation"""
        keys = key_path.split(".")
        config = self.config

        # Navigiere zur vorletzten Ebene
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        # Setze Wert
        config[keys[-1]] = value
        self.save_config()

    def get_section(self, section: str) -> Dict[str, Any]:
        """Holt gesamte Konfigurationssektion"""
        return self.config.get(section, {})

    def get_rigs_config(self) -> List[Dict[str, Any]]:
        """Holt Rig-Konfiguration"""
        rigs = self.get("Rigs", [])
        if not isinstance(rigs, list):
            return []
        return [rig for rig in rigs if isinstance(rig, dict)]

    def get_mining_config(self) -> Dict[str, Any]:
        """Holt Mining-Konfiguration"""
        return self.get_section("Mining")

    def get_market_config(self) -> Dict[str, Any]:
        """Holt Markt-Konfiguration"""
        return self.get_section("Market")

    def get_backup_config(self) -> Dict[str, Any]:
        """Holt Backup-Konfiguration"""
        return self.get_section("Backup")

    def get_logging_config(self) -> Dict[str, Any]:
        """Holt Logging-Konfiguration"""
        return self.get_section("Logging")

    def get_api_config(self, service: Optional[str] = None) -> Dict[str, Any]:
        """Holt API-Konfiguration"""
        api_config = self.get_section("API")
        if service:
            return api_config.get(service, {})
        return api_config

    def validate_config(self) -> List[str]:
        """Validiert Konfiguration und gibt Fehler zurück"""
        errors = []

        # System validation
        if not self.get("System.Name"):
            errors.append("System.Name is required")

        # Mining validation
        mining = self.get_mining_config()
        if mining.get("ElectricityCostPerKwh", 0) <= 0:
            errors.append("Mining.ElectricityCostPerKwh must be positive")

        # Rigs validation
        rigs = self.get_rigs_config()
        for i, rig in enumerate(rigs):
            if not rig.get("id"):
                errors.append(f"Rig[{i}].id is required")
            if rig.get("hash_rate", 0) <= 0:
                errors.append(f"Rig[{i}].hash_rate must be positive")

        # API validation - check if keys are provided
        required_apis = ["OpenRouter", "Gemini"]
        for api in required_apis:
            api_config = self.get_api_config(api)
            if api_config.get("Enabled", False) and not api_config.get("Key"):
                errors.append(f"API.{api}.Key is required when enabled")

        return errors

    def reload_config(self):
        """Lädt Konfiguration neu"""
        self._load_env_vars()
        self.load_config()

    def get_config_summary(self) -> Dict[str, Any]:
        """Gibt Konfigurationszusammenfassung"""
        return {
            "config_file": self.config_file,
            "sections_count": len(self.config),
            "env_vars_loaded": len(self.env_vars),
            "rigs_count": len(self.get_rigs_config()),
            "validation_errors": self.validate_config(),
            "last_loaded": None,  # Could add timestamp
        }


# Globale Instanz
config_manager = ConfigManager()


# Convenience-Funktionen
def get_config(key_path: str, default=None):
    """Holt Konfiguration-Wert"""
    return config_manager.get(key_path, default)


def set_config(key_path: str, value):
    """Setzt Konfiguration-Wert"""
    config_manager.set(key_path, value)


def get_rigs_config():
    """Holt Rig-Konfiguration"""
    return config_manager.get_rigs_config()


def get_mining_config():
    """Holt Mining-Konfiguration"""
    return config_manager.get_mining_config()


def validate_config():
    """Validiert Konfiguration"""
    return config_manager.validate_config()


if __name__ == "__main__":
    print("CASH MONEY COLORS ORIGINAL (R) - CONFIG MANAGER")
    print("=" * 55)

    # Test des Config Managers
    print("Teste Config Manager...")

    # Konfiguration validieren
    errors = validate_config()
    if errors:
        print(f"Konfigurationsfehler gefunden ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Konfiguration ist gueltig")

    # Zusammenfassung anzeigen
    summary = config_manager.get_config_summary()
    print("\nKonfigurations-Zusammenfassung:")
    print(f"   Config-Datei: {summary['config_file']}")
    print(f"   Sektionen: {summary['sections_count']}")
    print(f"   Umgebungsvariablen: {summary['env_vars_loaded']}")
    print(f"   Konfigurierte Rigs: {summary['rigs_count']}")

    # Beispiel-Konfiguration lesen
    print("\nBeispiel-Werte:")
    print(f"   System Name: {get_config('System.Name')}")
    print(f"   Mining Algorithm: {get_config('Mining.DefaultAlgorithm')}")
    print(
        f"   Electricity Cost: {get_config('Mining.ElectricityCostPerKwh')} "
        "CHF/kWh"
    )

    rigs = get_rigs_config()
    if rigs:
        print("\nBeispiel Rig:")
        sample_rig = rigs[0]
        print(
            f"   {sample_rig.get('id', 'N/A')}: "
            f"{sample_rig.get('type', 'N/A')} "
            f"({sample_rig.get('algorithm', 'N/A')})"
        )

    print("\nCONFIG MANAGER BEREIT!")
    print("Verwende get_config(), set_config(), validate_config()")
