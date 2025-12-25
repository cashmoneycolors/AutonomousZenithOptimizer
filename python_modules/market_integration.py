#!/usr/bin/env python3
"""
CASH MONEY COLORS ORIGINAL (R) - MARKET INTEGRATION
Echte Markt-Daten für realistische Mining-Profit-Kalkulation
CoinGecko API Integration für Live-Krypto-Preise
"""
import requests
import json
from datetime import datetime
from typing import Dict, List
import os
from pathlib import Path

# Universal Integration Setup
def setup_universal_integration():
    """Richtet universelle Integration mit API-Keys und PayPal ein
    
    Note: This function loads sensitive data. Consider using environment variables
    and accessing credentials only when needed rather than storing globally.
    """

    # API-Keys aus .env laden
    env_file = Path('.env')
    api_keys = {}
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    api_keys[key.strip()] = value.strip()

                    # PayPal-Konfiguration
    paypal_config = {
        'client_id': api_keys.get('PAYPAL_CLIENT_ID'),
        'client_secret': api_keys.get('PAYPAL_CLIENT_SECRET'),
        'mode': 'sandbox',
        'currency': 'CHF'
        }

    # DeepSeek Mining Brain Integration
    mining_config = {
        'deepseek_key': api_keys.get('DEEPSEEK_MINING_KEY'),
        'auto_profit_transfer': True,
        'paypal_integration': paypal_config
        }

    return {
        'api_keys': api_keys,
        'paypal': paypal_config,
        'mining': mining_config,
        'integrated': True
        }

# Automatische Integration beim Import
# WARNING: Credentials stored in global scope - consider refactoring for production
universal_config = setup_universal_integration()

class MarketIntegration:
    """Echte Markt-Daten Integration für Mining-System"""

    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.cache_file = "market_cache.json"
        self.cache_duration = 300  # 5 Minuten Cache
        self.last_update = None
        self.market_data = {}

        # Mining-relevante Coins
        self.mining_coins = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'RVN': 'ravencoin',
            'XMR': 'monero',
            'ERG': 'ergo',
            'CFX': 'conflux-token',
            'KAS': 'kaspa',
            'ETC': 'ethereum-classic'
        }

        # Algorithmus-Mapping für Profit-Kalkulation
        self.algorithm_coins = {
            'sha256': ['BTC', 'BCH'],
            'ethash': ['ETH', 'ETC'],
            'kawpow': ['RVN'],
            'randomx': ['XMR'],
            'autolykos': ['ERG'],
            'octopus': ['CFX'],
            'kheavyhash': ['KAS']
        }

        print("[COIN] MARKET INTEGRATION INITIALIZED")
        print("[STATS] Live Crypto-Preise für realistische Mining-Kalkulation")

    def get_crypto_prices(self, coins: List[str] = None) -> Dict[str, float]:
        """Holt aktuelle Krypto-Preise von CoinGecko"""
        if coins is None:
            coins = list(self.mining_coins.keys())

        # Cache prüfen
        if self._is_cache_valid():
            return self._load_cache()

        try:
            # CoinGecko IDs sammeln
            coin_ids = [self.mining_coins.get(coin, coin.lower()) for coin in coins]
            coin_ids_str = ','.join(coin_ids)

            # API Request
            url = f"{self.base_url}/simple/price"
            params = {
                'ids': coin_ids_str,
                'vs_currencies': 'usd,chf',
                'include_24hr_change': 'true'
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Daten formatieren
            prices = {}
            for coin, coin_data in data.items():
                # Coin Symbol finden
                symbol = None
                for sym, id in self.mining_coins.items():
                    if id == coin:
                        symbol = sym
                        break
                if not symbol:
                    symbol = coin.upper()

                prices[symbol] = {
                    'usd': coin_data.get('usd', 0),
                    'chf': coin_data.get('chf', 0),
                    'change_24h': coin_data.get('usd_24h_change', 0),
                    'last_update': datetime.now().isoformat()
                }

            # Cache speichern
            self._save_cache(prices)
            self.market_data = prices
            self.last_update = datetime.now()

            print(f"[MONEY] Preise aktualisiert für {len(prices)} Coins")
            return prices

        except Exception as e:
            print(f"[ERROR] Fehler beim Laden der Markt-Daten: {e}")
            # Fallback auf Cache oder simulierte Daten
            return self._get_fallback_prices(coins)

    def calculate_mining_profit(self, algorithm: str, hash_rate: float,
                              power_consumption: float, electricity_cost: float = 0.15) -> Dict:
        """Berechnet realistischen Mining-Profit basierend auf Markt-Daten"""

        # Coins für Algorithmus finden
        coins = self.algorithm_coins.get(algorithm, [])
        if not coins:
            return {'error': f'Algorithmus {algorithm} nicht unterstützt'}

        # Markt-Daten laden
        market_data = self.get_crypto_prices(coins)

        profits = {}
        best_profit = 0
        best_coin = None

        for coin in coins:
            if coin not in market_data:
                continue

            # Vereinfachte Profit-Kalkulation (in der Realität komplexer)
            # Hier würden Mining-Pool Daten verwendet werden
            coin_data = market_data[coin]

            # Simulierte Block-Belohnung und Schwierigkeit
            if coin == 'BTC':
                block_reward = 6.25  # Historical pre-April-2024 halving value (current reward: 3.125 BTC)
                difficulty_factor = 1.0
                blocks_per_day = 144  # ca.
            elif coin == 'ETH':
                # Note: ETH mining ended in Sept 2022 with The Merge (PoS transition)
                # This is for historical/simulation purposes only
                block_reward = 2.0  # Historical pre-merge value
                difficulty_factor = 0.8
                blocks_per_day = 7200  # ca.
            elif coin == 'RVN':
                block_reward = 2500
                difficulty_factor = 0.9
                blocks_per_day = 1440
            else:
                # Generische Werte für andere Coins
                block_reward = 1.0
                difficulty_factor = 1.0
                blocks_per_day = 1000

            # Profit-Kalkulation
            daily_reward = block_reward * blocks_per_day * (hash_rate / 1000000) * difficulty_factor
            daily_value_usd = daily_reward * coin_data['usd']

            # Stromkosten abziehen
            daily_power_cost = (power_consumption * 24 * electricity_cost) / 1000  # kWh * Preis
            net_profit_usd = daily_value_usd - daily_power_cost

            # In CHF umrechnen
            net_profit_chf = net_profit_usd * coin_data['chf'] / coin_data['usd']

            profits[coin] = {
                'daily_profit_chf': net_profit_chf,
                'daily_profit_usd': net_profit_usd,
                'power_cost_chf': daily_power_cost * (coin_data['chf'] / coin_data['usd']),
                'price_usd': coin_data['usd'],
                'price_chf': coin_data['chf'],
                'change_24h': coin_data['change_24h']
            }

            if net_profit_chf > best_profit:
                best_profit = net_profit_chf
                best_coin = coin

        return {
            'algorithm': algorithm,
            'hash_rate': hash_rate,
            'power_consumption': power_consumption,
            'best_coin': best_coin,
            'best_profit_chf': best_profit,
            'all_profits': profits,
            'electricity_cost_per_kwh': electricity_cost
        }

    def get_optimal_algorithm(self, rig_specs: Dict) -> Dict:
        """Findet optimalen Algorithmus für einen Rig"""

        algorithms = ['sha256', 'ethash', 'kawpow', 'randomx', 'autolykos', 'octopus', 'kheavyhash']
        best_profit = 0
        best_algo = None
        best_coin = None

        for algo in algorithms:
            profit_data = self.calculate_mining_profit(
                algo,
                rig_specs.get('hash_rate', 100),
                rig_specs.get('power_consumption', 300),
                rig_specs.get('electricity_cost', 0.15)
            )

            if 'best_profit_chf' in profit_data and profit_data['best_profit_chf'] > best_profit:
                best_profit = profit_data['best_profit_chf']
                best_algo = algo
                best_coin = profit_data.get('best_coin')

        return {
            'optimal_algorithm': best_algo,
            'optimal_coin': best_coin,
            'expected_profit_chf': best_profit,
            'rig_specs': rig_specs
        }

    def _is_cache_valid(self) -> bool:
        """Prüft ob Cache noch gültig ist"""
        if not os.path.exists(self.cache_file):
            return False

        if self.last_update is None:
            return False

        return (datetime.now() - self.last_update).seconds < self.cache_duration

    def _load_cache(self) -> Dict:
        """Lädt Cache-Daten"""
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, IOError):
            return {}

    def _save_cache(self, data: Dict):
        """Speichert Daten im Cache"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Cache-Speicherung fehlgeschlagen: {e}")

    def _get_fallback_prices(self, coins: List[str]) -> Dict:
        """Fallback-Preise wenn API nicht verfügbar"""
        fallback_prices = {
            'BTC': {'usd': 45000, 'chf': 42000, 'change_24h': 2.5},
            'ETH': {'usd': 2800, 'chf': 2600, 'change_24h': 1.8},
            'RVN': {'usd': 0.035, 'chf': 0.032, 'change_24h': -3.2},
            'XMR': {'usd': 165, 'chf': 153, 'change_24h': 0.5},
            'ERG': {'usd': 1.85, 'chf': 1.72, 'change_24h': 4.1},
            'CFX': {'usd': 0.25, 'chf': 0.23, 'change_24h': -1.5},
            'KAS': {'usd': 0.18, 'chf': 0.17, 'change_24h': 2.8},
            'ETC': {'usd': 22, 'chf': 20, 'change_24h': -0.8}
        }

        prices = {}
        for coin in coins:
            if coin in fallback_prices:
                prices[coin] = fallback_prices[coin]
                prices[coin]['last_update'] = datetime.now().isoformat()

        print("[WARN] Fallback-Preise verwendet (API nicht verfügbar)")
        return prices

# Globale Instanz
market_integration = MarketIntegration()

# Standalone-Funktionen
def get_crypto_prices(coins=None):
    """Holt aktuelle Krypto-Preise"""
    return market_integration.get_crypto_prices(coins)

def calculate_mining_profit(algorithm, hash_rate, power_consumption, electricity_cost=0.15):
    """Berechnet Mining-Profit"""
    return market_integration.calculate_mining_profit(algorithm, hash_rate, power_consumption, electricity_cost)

def get_optimal_algorithm(rig_specs):
    """Findet optimalen Algorithmus"""
    return market_integration.get_optimal_algorithm(rig_specs)

if __name__ == "__main__":
    print("CASH MONEY COLORS ORIGINAL (R) - MARKET INTEGRATION")
    print("=" * 60)

    # Test der Markt-Integration
    print("🧪 Teste Markt-Daten Integration...")

    # Preise laden
    prices = get_crypto_prices()
    print(f"📈 Geladene Preise für {len(prices)} Coins")

    for coin, data in list(prices.items())[:3]:  # Erste 3 anzeigen
        print(f"  {coin}: ${data['usd']:.2f} | CHF {data['chf']:.2f} ({data['change_24h']:+.1f}%)")

    # Profit-Kalkulation testen
    print("\n[MONEY] Teste Profit-Kalkulation...")
    profit = calculate_mining_profit('ethash', 120, 450, 0.15)
    if 'best_coin' in profit:
        print(f"Optimal für Ethash: {profit['best_coin']} mit CHF {profit['best_profit_chf']:.2f}/Tag")

    print("\n[OK] MARKET INTEGRATION BEREIT!")
    print("Verwende get_crypto_prices(), calculate_mining_profit(), get_optimal_algorithm()")


def run():
    """Standard run() Funktion für Dashboard-Integration"""
    print(f"Modul {__name__} wurde ausgeführt")
    print("Implementiere hier deine spezifische Logik...")

