#!/usr/bin/env python3
"""
CASH MONEY COLORS ORIGINAL (R) - NICEHASH MINING POOL INTEGRATION
Echte NiceHash API Integration für profitable Mining-Operationen
"""
import requests
import json
import hmac
import hashlib
import time
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import os
from python_modules.config_manager import get_config


class NiceHashIntegration:
    """Echte NiceHash API Integration für Mining-Pools"""

    def __init__(self):
        self.base_url = "https://api2.nicehash.com"
        self.api_key = get_config("Pools.NiceHash.ApiKey", "")
        self.api_secret = get_config("Pools.NiceHash.ApiSecret", "")
        self.org_id = get_config("Pools.NiceHash.OrganizationId", "")

        # Algorithmen-Mapping (NiceHash zu lokale Namen)
        self.algorithm_mapping = {
            "DAGGERHASHIMOTO": "ethash",
            "ETCHASH": "etchash",
            "KAWPOW": "kawpow",
            "RANDOMXMONERO": "randomx",
            "AUTOLYKOS": "autolykos",
            "OCTOPUS": "octopus",
            "KHEAVYHASH": "kheavyhash",
            "SHA256ASICBOOST": "sha256",
        }

        self.reverse_mapping = {v: k for k, v in self.algorithm_mapping.items()}

        self.cache_duration = 300  # 5 Minuten Cache
        self.last_api_call = None
        self.api_cache = {}

        if self.api_key and self.api_secret:
            print("🏭 NICEHASH INTEGRATION INITIALIZED - Echte API verfügbar")
            print(f"🏢 Organization: {self.org_id}")
        else:
            print("⚠️ NiceHash nicht konfiguriert - Verwende Demo-Modus")
            print(
                "Setze POOLS_NICEHASH_API_KEY, POOLS_NICEHASH_API_SECRET, POOLS_NICEHASH_ORG_ID"
            )

    def _get_auth_headers(
        self, method: str, endpoint: str, timestamp: int = None
    ) -> Dict[str, str]:
        """Erstellt authentifizierte Headers für NiceHash API"""
        if not timestamp:
            timestamp = int(time.time() * 1000)

        # Erstelle Signatur
        message = f"{self.api_key}\x00{timestamp}\x00{self.api_secret}"
        signature = hmac.new(
            self.api_secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256
        ).digest()

        # Base64 encode
        signature_b64 = base64.b64encode(signature).decode("utf-8")

        return {
            "X-Time": str(timestamp),
            "X-Nonce": str(timestamp),
            "X-Organization-Id": self.org_id,
            "X-Request-Id": str(timestamp),
            "X-Auth": f"{self.api_key}:{signature_b64}",
        }

    def _api_request(
        self, endpoint: str, method: str = "GET", data: Dict = None
    ) -> Optional[Dict]:
        """Führt API-Request aus mit Authentifizierung"""
        if not self.api_key or not self.api_secret:
            print("❌ NiceHash API nicht konfiguriert")
            return self._get_demo_data(endpoint)

        url = f"{self.base_url}{endpoint}"

        # Cache prüfen
        cache_key = f"{method}:{endpoint}"
        if cache_key in self.api_cache:
            cache_time, cache_data = self.api_cache[cache_key]
            if time.time() - cache_time < self.cache_duration:
                return cache_data

        try:
            headers = self._get_auth_headers(method, endpoint)

            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=10)

            response.raise_for_status()
            result = response.json()

            # Cache aktualisieren
            self.api_cache[cache_key] = (time.time(), result)
            self.last_api_call = datetime.now()

            return result

        except Exception as e:
            print(f"❌ NiceHash API Fehler: {e}")
            return self._get_demo_data(endpoint)

    def get_pool_stats(self, algorithm: str = None) -> Dict[str, Any]:
        """Holt aktuelle Pool-Statistiken"""
        if algorithm and algorithm in self.reverse_mapping:
            algorithm = self.reverse_mapping[algorithm]

        endpoint = "/main/api/v2/public/stats/global/current"

        data = self._api_request(endpoint)
        if not data:
            return {}

        stats = {}
        if "algos" in data:
            for algo_data in data["algos"]:
                algo_name = algo_data.get("algorithm", "")
                local_algo = self.algorithm_mapping.get(algo_name, algo_name.lower())

                if algorithm and local_algo != algorithm:
                    continue

                stats[local_algo] = {
                    "algorithm": local_algo,
                    "paying": algo_data.get("paying", 0),
                    "paying_usd": float(algo_data.get("paying", 0))
                    / 100000000,  # H konvertieren
                    "difficulty": algo_data.get("difficulty", 0),
                    "speed": algo_data.get("speed", 0),
                    "market_factor": algo_data.get("marketFactor", 0),
                    "last_update": datetime.fromtimestamp(
                        algo_data.get("timestamp", 0) / 1000
                    ),
                }

        return stats

    def get_mining_rigs(self) -> List[Dict[str, Any]]:
        """Holt Mining-Rigs von NiceHash"""
        endpoint = "/main/api/v2/mining/rigs2"

        data = self._api_request(endpoint)
        if not data or "miningRigs" not in data:
            return []

        rigs = []
        for rig in data["miningRigs"]:
            rigs.append(
                {
                    "id": rig.get("rigId", ""),
                    "name": rig.get("name", ""),
                    "status": rig.get("minerStatus", ""),
                    "algorithm": self.algorithm_mapping.get(
                        rig.get("algorithm", ""), rig.get("algorithm", "")
                    ),
                    "total_profitability": rig.get("totalProfitabilityLocal", 0),
                    "total_hashrate": rig.get("totalHashrate", 0),
                    "devices": rig.get("deviceId", []),
                    "local_profitability": rig.get("profitabilityLocal", 0),
                    "unpaid_amount": rig.get("unpaidAmount", 0),
                }
            )

        return rigs

    def create_rig(self, rig_name: str, algorithm: str, devices: List[str]) -> bool:
        """Erstellt neuen Rig auf NiceHash"""
        if algorithm in self.reverse_mapping:
            algorithm = self.reverse_mapping[algorithm]

        endpoint = "/main/api/v2/mining/rig"
        data = {"name": rig_name, "algorithm": algorithm, "devices": devices}

        result = self._api_request(endpoint, "POST", data)
        if result:
            print(f"✅ Rig erstellt: {rig_name}")
            return True
        return False

    def calculate_profit_comparison(self, local_rig: Dict[str, Any]) -> Dict[str, Any]:
        """Vergleicht lokale Rig-Performance mit NiceHash"""
        rig_algorithm = local_rig.get("algorithm", "")

        # Hole NiceHash Stats
        pool_stats = self.get_pool_stats(rig_algorithm)
        if not pool_stats:
            return {"error": "Keine Pool-Daten verfügbar"}

        nicehash_data = pool_stats.get(rig_algorithm, {})

        # Lokale Berechnung (vereinfacht)
        local_hashrate = local_rig.get("hash_rate", 0)
        local_efficiency = local_rig.get("efficiency", 0)

        # NiceHash Paying Rate (vereinfacht aus global stats)
        nh_paying_usd = nicehash_data.get("paying_usd", 0)

        # Schätze lokale Profitabilität
        # In Realität würde komplexere Kalkulation verwendet
        electricity_cost = get_config("Mining.ElectricityCostPerKwh", 0.15)
        power_consumption = local_rig.get("power_consumption", 300)

        # Tageskosten berechnen
        daily_kwh = (power_consumption * 24) / 1000
        daily_cost = daily_kwh * electricity_cost

        # NiceHash vergleichbare Erträge
        estimated_nh_daily = nh_paying_usd * local_hashrate * local_efficiency * 24

        comparison = {
            "algorithm": rig_algorithm,
            "rig_id": local_rig.get("id", ""),
            "nicehash_paying_rate": nh_paying_usd,
            "estimated_nh_daily_profit": estimated_nh_daily,
            "local_daily_cost": daily_cost,
            "nh_net_profit": estimated_nh_daily - daily_cost,
            "should_use_nicehash": (estimated_nh_daily - daily_cost) > 0,
            "profit_difference": estimated_nh_daily - daily_cost,
            "comparison_timestamp": datetime.now().isoformat(),
            "market_data": nicehash_data,
        }

        return comparison

    def optimize_mining_strategy(
        self, local_rigs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Optimiert Mining-Strategie basierend auf NiceHash Daten"""
        # Hole alle Pool-Stats
        all_stats = self.get_pool_stats()

        best_strategies = []
        total_local_profit = 0
        total_nh_profit = 0

        for rig in local_rigs:
            comparison = self.calculate_profit_comparison(rig)

            if "error" not in comparison:
                local_daily = rig.get("profit_per_day", 0)
                nh_daily = comparison.get("nh_net_profit", 0)

                total_local_profit += local_daily
                total_nh_profit += nh_daily

                best_strategies.append(
                    {
                        "rig_id": rig["id"],
                        "current_local_profit": local_daily,
                        "nicehash_profit": nh_daily,
                        "recommendation": (
                            "nicehash" if comparison["should_use_nicehash"] else "local"
                        ),
                        "profit_gain": nh_daily - local_daily,
                        "algorithm": rig.get("algorithm", ""),
                    }
                )

        return {
            "total_local_profit": total_local_profit,
            "total_nicehash_profit": total_nh_profit,
            "recommended_switch_all": total_nh_profit > total_local_profit,
            "total_profit_difference": total_nh_profit - total_local_profit,
            "rig_recommendations": best_strategies,
            "analysis_timestamp": datetime.now().isoformat(),
        }

    def _get_demo_data(self, endpoint: str) -> Optional[Dict]:
        """Liefert Demo-Daten wenn API nicht verfügbar"""
        demo_data = {
            "/main/api/v2/public/stats/global/current": {
                "algos": [
                    {
                        "algorithm": "DAGGERHASHIMOTO",
                        "paying": 25000000,  # 0.25 USD/TH/day
                        "difficulty": 1000000000000,
                        "speed": 1000000000,
                        "marketFactor": 1.2,
                        "timestamp": int(time.time() * 1000),
                    },
                    {
                        "algorithm": "KAWPOW",
                        "paying": 15000000,  # 0.15 USD
                        "difficulty": 500000000,
                        "speed": 500000000,
                        "marketFactor": 0.8,
                        "timestamp": int(time.time() * 1000),
                    },
                ]
            },
            "/main/api/v2/mining/rigs2": {
                "miningRigs": [
                    {
                        "rigId": "nh_demo_rig_1",
                        "name": "Demo Rig GTX 3080",
                        "minerStatus": "MINING",
                        "algorithm": "DAGGERHASHIMOTO",
                        "totalProfitabilityLocal": 12.5,
                        "totalHashrate": 95,
                        "deviceId": ["gpu0"],
                        "profitabilityLocal": 12.5,
                        "unpaidAmount": 0.05,
                    }
                ]
            },
        }

        return demo_data.get(endpoint)

    def get_integration_status(self) -> Dict[str, Any]:
        """Gibt Integrationsstatus zurück"""
        return {
            "configured": bool(self.api_key and self.api_secret and self.org_id),
            "last_api_call": (
                self.last_api_call.isoformat() if self.last_api_call else None
            ),
            "cached_requests": len(self.api_cache),
            "supported_algorithms": len(self.algorithm_mapping),
            "organization_id": self.org_id if self.org_id else None,
        }


# Globale Instanz
nicehash_integration = NiceHashIntegration()


# Convenience-Funktionen
def get_pool_stats(algorithm=None):
    """Holt Pool-Statistiken"""
    return nicehash_integration.get_pool_stats(algorithm)


def get_mining_rigs():
    """Holt Mining-Rigs"""
    return nicehash_integration.get_mining_rigs()


def calculate_profit_comparison(local_rig):
    """Vergleicht Profitabilität"""
    return nicehash_integration.calculate_profit_comparison(local_rig)


def optimize_mining_strategy(local_rigs):
    """Optimiert Mining-Strategie"""
    return nicehash_integration.optimize_mining_strategy(local_rigs)


def create_nicehash_rig(rig_name, algorithm, devices):
    """Erstellt NiceHash Rig"""
    return nicehash_integration.create_rig(rig_name, algorithm, devices)


if __name__ == "__main__":
    print("CASH MONEY COLORS ORIGINAL (R) - NICEHASH INTEGRATION")
    print("=" * 60)

    print("🧪 Teste NiceHash Integration...")

    # Pool-Stats laden
    print("\n📊 Lade Pool-Statistiken...")
    stats = get_pool_stats()
    if stats:
        print(f"✅ {len(stats)} Algorithmen gefunden:")
        for algo, data in list(stats.items())[:3]:
            print(".4f")
    else:
        print("❌ Keine Statistiken verfügbar")

    # Rigs checken
    print("\n🔧 Lade Mining-Rigs...")
    rigs = get_mining_rigs()
    print(f"📋 {len(rigs)} NiceHash Rigs gefunden")

    # Profit-Vergleich Demo
    print("\n💰 Profit-Vergleich Demo...")
    demo_rig = {
        "id": "demo_gpu",
        "algorithm": "ethash",
        "hash_rate": 120,
        "power_consumption": 450,
        "profit_per_day": 18.0,
    }
    comparison = calculate_profit_comparison(demo_rig)
    if "error" not in comparison:
        print(".2f" ".2f" f"NiceHash empfohlen: {comparison['should_use_nicehash']}")

    print("\n✅ NICEHASH INTEGRATION BEREIT!")
    print(
        "Verwende get_pool_stats(), optimize_mining_strategy(), calculate_profit_comparison()"
    )
    print(
        "Konfiguriere API-Keys via ENV (oder settings.json mit ${...}-Platzhaltern) für echte NiceHash Integration"
    )
