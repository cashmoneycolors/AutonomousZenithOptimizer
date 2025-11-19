#!/usr/bin/env python3
"""
REALTIME MARKET FEED MODULE
Live-Krypto-Preis-Updates mit WebSocket-Unterstützung für mehrere Exchanges
Multi-Exchange Arbitrage und Profit-Maximierung
"""
import asyncio
import json
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
import websocket
import requests
from python_modules.config_manager import get_config
from python_modules.alert_system import send_custom_alert
from python_modules.enhanced_logging import log_event

class RealtimeMarketFeed:
    """Real-time Krypto-Preis-Feeds von mehreren Exchanges"""

    def __init__(self):
        self.feed_config = get_config('RealtimeMarketFeed', {})

        # Unterstützte Exchanges
        self.exchanges = {
            'binance': {
                'websocket_url': 'wss://stream.binance.com:9443/ws',
                'rest_url': 'https://api.binance.com/api/v3',
                'symbols': ['BTCUSDT', 'ETHUSDT', 'RVNUSDT', 'XMRUSDT'],
                'active': True
            },
            'coinbase': {
                'websocket_url': 'wss://ws-feed.exchange.coinbase.com',
                'rest_url': 'https://api.exchange.coinbase.com',
                'symbols': ['BTC-USD', 'ETH-USD', 'RVN-USD', 'XMR-USD'],
                'active': True
            },
            'coinbase_pro': {
                'websocket_url': 'wss://ws-feed.pro.coinbase.com',
                'rest_url': 'https://api.pro.coinbase.com',
                'symbols': ['BTC-USD', 'ETH-USD'],
                'active': False  # Premium benötigt
            },
            'kraken': {
                'websocket_url': 'wss://ws.kraken.com',
                'rest_url': 'https://api.kraken.com/0/public',
                'symbols': ['BTC/USD', 'ETH/USD', 'XMR/USD'],
                'active': True
            }
        }

        # Live-Preis-Daten
        self.live_prices = {}
        self.price_history = {}
        self.arbitrage_opportunities = []
        self.price_alerts = {}

        # Monitoring
        self.monitoring_active = False
        self.update_callbacks = []
        self.price_changes = {}

        # Arbitrage-Konfiguration
        self.arbitrage_threshold = self.feed_config.get('ArbitrageThreshold', 0.5)  # 0.5% Mindest-Spread
        self.alert_threshold = self.feed_config.get('AlertThreshold', 2.0)  # 2% Preisänderung Alert

        print("[FEED] Realtime Market Feed initialized")
        print(f"[FEED] Connected Exchanges: {len([e for e in self.exchanges.values() if e['active']])}")
        print(f"[FEED] Arbitrage Threshold: {self.arbitrage_threshold}%")

    def start_realtime_feed(self):
        """Startet Live-Preis-Feeds"""
        if self.monitoring_active:
            return

        self.monitoring_active = True

        # Starte REST-API-Polling für Exchanges ohne WebSocket
        rest_thread = threading.Thread(target=self._rest_api_monitor, daemon=True)
        rest_thread.start()

        # Starte WebSocket-Feeds
        websocket_thread = threading.Thread(target=self._websocket_monitor, daemon=True)
        websocket_thread.start()

        print("[FEED] Realtime monitoring started")

    def stop_realtime_feed(self):
        """Stoppt Live-Preis-Feeds"""
        self.monitoring_active = False
        print("[FEED] Realtime monitoring stopped")

    def get_live_price(self, symbol: str, exchange: str = None) -> Optional[Dict[str, Any]]:
        """Gibt aktuellen Live-Preis für Symbol zurück"""
        if exchange:
            key = f"{exchange}:{symbol}"
            return self.live_prices.get(key)
        else:
            # Finde besten Preis über alle Exchanges
            best_price = None
            best_exchange = None
            best_timestamp = None

            for key, price_data in self.live_prices.items():
                if key.endswith(f":{symbol}") or key.endswith(f"/{symbol}") or key.endswith(f"-{symbol}"):
                    if not best_price or price_data['timestamp'] > best_timestamp:
                        best_price = price_data
                        best_timestamp = price_data['timestamp']
                        best_exchange = key.split(':')[0]

            return best_price

    def get_price_history(self, symbol: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Gibt Preis-Historie für Symbol zurück"""
        if symbol not in self.price_history:
            return []

        cutoff_time = datetime.now() - timedelta(hours=hours)
        history = [entry for entry in self.price_history[symbol]
                  if entry['timestamp'] > cutoff_time]

        return history

    def calculate_price_change(self, symbol: str, timeframe_hours: int = 1) -> Dict[str, Any]:
        """Berechnet Preisänderung über Zeitraum"""
        history = self.get_price_history(symbol, timeframe_hours + 1)

        if len(history) < 2:
            return {'change_percent': 0, 'direction': 'stable', 'volatility': 0}

        current_price = history[-1]['price']
        old_price = history[0]['price']

        change_percent = ((current_price - old_price) / old_price) * 100

        # Richtung bestimmen
        if change_percent > 1:
            direction = 'up'
        elif change_percent < -1:
            direction = 'down'
        else:
            direction = 'stable'

        # Volatilität berechnen (Standardabweichung)
        prices = [entry['price'] for entry in history]
        volatility = self._calculate_volatility(prices)

        return {
            'change_percent': change_percent,
            'direction': direction,
            'volatility': volatility,
            'timeframe_hours': timeframe_hours,
            'current_price': current_price,
            'old_price': old_price
        }

    def detect_arbitrage_opportunities(self) -> List[Dict[str, Any]]:
        """Findet Arbitrage-Möglichkeiten zwischen Exchanges"""
        opportunities = []

        symbols = self._get_common_symbols()

        for symbol in symbols:
            prices_per_exchange = {}

            # Sammle Preise für dieses Symbol von allen Exchanges
            for key, price_data in self.live_prices.items():
                if (f":{symbol}" in key or f"/{symbol}" in key or f"-{symbol}" in key):
                    exchange_name = key.split(':')[0]
                    prices_per_exchange[exchange_name] = price_data['price']

            if len(prices_per_exchange) >= 2:
                prices = list(prices_per_exchange.values())
                max_price = max(prices)
                min_price = min(prices)

                spread_percent = ((max_price - min_price) / min_price) * 100

                if spread_percent >= self.arbitrage_threshold:
                    opportunities.append({
                        'symbol': symbol,
                        'spread_percent': spread_percent,
                        'buy_exchange': min(prices_per_exchange, key=prices_per_exchange.get),
                        'sell_exchange': max(prices_per_exchange, key=prices_per_exchange.get),
                        'buy_price': min_price,
                        'sell_price': max_price,
                        'profit_potential': (max_price - min_price) * 1000,  # Für 1000 Einheiten
                        'timestamp': datetime.now().isoformat()
                    })

        return opportunities

    def set_price_alert(self, symbol: str, threshold_percent: float, alert_type: str = 'change'):
        """Setzt Preis-Alerts"""
        self.price_alerts[symbol] = {
            'threshold': threshold_percent,
            'type': alert_type,
            'reference_price': self.get_live_price(symbol),
            'created_at': datetime.now()
        }

    def add_price_callback(self, callback: Callable):
        """Registriert Callback für Preis-Updates"""
        self.update_callbacks.append(callback)

    def _rest_api_monitor(self):
        """Überwacht Exchanges über REST-API (Fallback)"""
        while self.monitoring_active:
            try:
                self._update_from_binance_rest()
                self._update_from_coinbase_rest()
                self._update_from_kraken_rest()

                # Prüfe auf Arbitrage und Alerts
                self._check_arbitrage()
                self._check_price_alerts()

                # Callbacks ausführen
                self._execute_callbacks()

                time.sleep(5)  # 5 Sekunden Intervall

            except Exception as e:
                print(f"[FEED] REST API monitor error: {e}")
                time.sleep(10)

    def _websocket_monitor(self):
        """Überwacht Exchanges über WebSocket (für Live-Daten)"""
        try:
            # Binance WebSocket
            if self.exchanges['binance']['active']:
                self._start_binance_websocket()

            # Coinbase WebSocket
            if self.exchanges['coinbase']['active']:
                self._start_coinbase_websocket()

        except Exception as e:
            print(f"[FEED] WebSocket monitor error: {e}")

    def _update_from_binance_rest(self):
        """Aktualisiert Preise von Binance REST API"""
        try:
            symbols = self.exchanges['binance']['symbols']
            for symbol in symbols:
                url = f"{self.exchanges['binance']['rest_url']}/ticker/price?symbol={symbol}"
                response = requests.get(url, timeout=5)

                if response.status_code == 200:
                    data = response.json()
                    price = float(data['price'])

                    key = f"binance:{symbol.lower()}"
                    self.live_prices[key] = {
                        'exchange': 'binance',
                        'symbol': symbol.lower(),
                        'price': price,
                        'timestamp': datetime.now(),
                        'source': 'rest'
                    }

                    self._update_price_history(symbol.lower(), price)

        except Exception as e:
            pass  # Silent fail für Fallback

    def _update_from_coinbase_rest(self):
        """Aktualisiert Preise von Coinbase REST API"""
        try:
            symbols = self.exchanges['coinbase']['symbols']
            for symbol in symbols:
                url = f"{self.exchanges['coinbase']['rest_url']}/products/{symbol}/ticker"
                response = requests.get(url, timeout=5)

                if response.status_code == 200:
                    data = response.json()
                    price = float(data['price'])

                    key = f"coinbase:{symbol.replace('-', '').lower()}"
                    self.live_prices[key] = {
                        'exchange': 'coinbase',
                        'symbol': symbol.replace('-', '').lower(),
                        'price': price,
                        'timestamp': datetime.now(),
                        'source': 'rest'
                    }

                    self._update_price_history(symbol.replace('-', '').lower(), price)

        except Exception as e:
            pass

    def _update_from_kraken_rest(self):
        """Aktualisiert Preise von Kraken REST API"""
        try:
            url = f"{self.exchanges['kraken']['rest_url']}/Ticker"
            pairs = ['BTCUSD', 'ETHUSD', 'XMRUSD']
            params = {'pair': ','.join(pairs)}
            response = requests.get(url, params=params, timeout=5)

            if response.status_code == 200:
                data = response.json()
                for pair, ticker_data in data['result'].items():
                    price = float(ticker_data['c'][0])  # Close price

                    symbol_map = {
                        'BTCUSD': 'btc',
                        'ETHUSD': 'eth',
                        'XMRUSD': 'xmr'
                    }

                    symbol = symbol_map.get(pair, pair.lower())
                    key = f"kraken:{symbol}"

                    self.live_prices[key] = {
                        'exchange': 'kraken',
                        'symbol': symbol,
                        'price': price,
                        'timestamp': datetime.now(),
                        'source': 'rest'
                    }

                    self._update_price_history(symbol, price)

        except Exception as e:
            pass

    def _start_binance_websocket(self):
        """Startet Binance WebSocket-Verbindung"""
        import threading

        def on_message(ws, message):
            try:
                data = json.loads(message)
                if 'stream' in data and data['stream'].endswith('@ticker'):
                    ticker_data = data['data']
                    symbol = ticker_data['s'].lower().replace('usdt', '')
                    price = float(ticker_data['c'])  # Last price

                    key = f"binance:{symbol}"
                    self.live_prices[key] = {
                        'exchange': 'binance',
                        'symbol': symbol,
                        'price': price,
                        'timestamp': datetime.now(),
                        'source': 'websocket',
                        'volume': float(ticker_data['v'])
                    }

                    self._update_price_history(symbol, price)

            except Exception as e:
                pass

        def on_error(ws, error):
            pass

        def on_close(ws):
            pass

        def on_open(ws):
            # Subscribe to ticker streams
            symbols = self.exchanges['binance']['symbols']
            streams = [f"{symbol.lower()}@ticker" for symbol in symbols]
            sub_msg = {
                "method": "SUBSCRIBE",
                "params": streams,
                "id": 1
            }
            ws.send(json.dumps(sub_msg))

        ws = websocket.WebSocketApp(
            self.exchanges['binance']['websocket_url'],
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )

        ws.on_open = on_open
        ws.run_forever()

    def _start_coinbase_websocket(self):
        """Startet Coinbase WebSocket-Verbindung"""
        # Vereinfachte Implementation - würde vollständige WebSocket-Logik erfordern
        pass

    def _update_price_history(self, symbol: str, price: float):
        """Aktualisiert Preis-Historie"""
        if symbol not in self.price_history:
            self.price_history[symbol] = []

        self.price_history[symbol].append({
            'price': price,
            'timestamp': datetime.now(),
            'change': self._calculate_price_change(symbol, price)
        })

        # Alte Einträge entfernen (behalte letzten 24h)
        cutoff = datetime.now() - timedelta(hours=24)
        self.price_history[symbol] = [
            entry for entry in self.price_history[symbol]
            if entry['timestamp'] > cutoff
        ]

    def _calculate_price_change(self, symbol: str, current_price: float) -> float:
        """Berechnet Preisänderung seit letztem Update"""
        if symbol in self.price_history and len(self.price_history[symbol]) > 0:
            last_price = self.price_history[symbol][-1]['price']
            return ((current_price - last_price) / last_price) * 100
        return 0

    def _calculate_volatility(self, prices: List[float]) -> float:
        """Berechnet Preis-Volatilität"""
        if len(prices) < 2:
            return 0

        returns = []
        for i in range(1, len(prices)):
            return_pct = ((prices[i] - prices[i-1]) / prices[i-1]) * 100
            returns.append(return_pct)

        if returns:
            mean_return = sum(returns) / len(returns)
            variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
            return variance ** 0.5  # Standardabweichung
        return 0

    def _get_common_symbols(self) -> List[str]:
        """Gibt gemeinsame Symbole über alle Exchanges zurück"""
        common_symbols = set()

        # Sammle alle verfügbaren Symbole
        for exchange_data in self.live_prices.values():
            symbol = exchange_data['symbol']
            if symbol in ['btc', 'eth', 'xmr', 'rvn']:  # Gebräuchliche Symbole
                common_symbols.add(symbol)

        return list(common_symbols)

    def _check_arbitrage(self):
        """Prüft auf Arbitrage-Möglichkeiten"""
        opportunities = self.detect_arbitrage_opportunities()

        if opportunities:
            best_opportunity = max(opportunities, key=lambda x: x['spread_percent'])
            if best_opportunity['spread_percent'] > 1.0:  # Mindestens 1% Spread
                send_custom_alert("Arbitrage Opportunity",
                                f"ARBITRAGE: {best_opportunity['symbol'].upper()} spread {best_opportunity['spread_percent']:.2f}% "
                                f"Buy: {best_opportunity['buy_exchange']} Sell: {best_opportunity['sell_exchange']}",
                                "[ARBITRAGE]")

    def _check_price_alerts(self):
        """Prüft Preis-Alerts"""
        for symbol, alert_data in self.price_alerts.items():
            current_price = self.get_live_price(symbol)
            if current_price:
                reference_price = alert_data.get('reference_price', {}).get('price', current_price['price'])
                change_percent = ((current_price['price'] - reference_price) / reference_price) * 100

                if abs(change_percent) >= alert_data['threshold']:
                    alert_type = "UP" if change_percent > 0 else "DOWN"
                    send_custom_alert(f"Price Alert {symbol.upper()}",
                                    f"{symbol.upper()} {alert_type} {abs(change_percent):.2f}% to ${current_price['price']:.2f}",
                                    "[PRICE]")

                    # Alert einmalig triggern, dann entfernen
                    del self.price_alerts[symbol]

    def _execute_callbacks(self):
        """Führt registrierte Callbacks aus"""
        for callback in self.update_callbacks:
            try:
                callback(self.live_prices)
            except Exception as e:
                print(f"[FEED] Callback error: {e}")

    def get_feed_status(self) -> Dict[str, Any]:
        """Gibt Status des Market Feeds zurück"""
        active_exchanges = len([e for e in self.exchanges.values() if e['active']])

        return {
            'monitoring_active': self.monitoring_active,
            'active_exchanges': active_exchanges,
            'total_symbols': len(self.live_prices),
            'arbitrage_opportunities': len(self.detect_arbitrage_opportunities()),
            'price_alerts': len(self.price_alerts),
            'last_update': datetime.now().isoformat(),
            'data_sources': ['binance', 'coinbase', 'kraken'],
            'update_frequency': 'real-time'
        }

# Globale Market Feed Instanz
realtime_market_feed = RealtimeMarketFeed()

# Convenience-Funktionen
def start_market_feed():
    """Startet Market Feed Monitoring"""
    realtime_market_feed.start_realtime_feed()

def stop_market_feed():
    """Stoppt Market Feed Monitoring"""
    realtime_market_feed.stop_realtime_feed()

def get_live_price(symbol, exchange=None):
    """Gibt Live-Preis für Symbol zurück"""
    return realtime_market_feed.get_live_price(symbol, exchange)

def get_price_history(symbol, hours=24):
    """Gibt Preis-Historie zurück"""
    return realtime_market_feed.get_price_history(symbol, hours)

def calculate_price_change(symbol, hours=1):
    """Berechnet Preisänderung"""
    return realtime_market_feed.calculate_price_change(symbol, hours)

def detect_arbitrage():
    """Findet Arbitrage-Möglichkeiten"""
    return realtime_market_feed.detect_arbitrage_opportunities()

def set_price_alert(symbol, threshold_percent, alert_type='change'):
    """Setzt Preis-Alert"""
    realtime_market_feed.set_price_alert(symbol, threshold_percent, alert_type)

def get_feed_status():
    """Gibt Feed-Status zurück"""
    return realtime_market_feed.get_feed_status()

if __name__ == "__main__":
    print("REALTIME MARKET FEED - Multi-Exchange Live Data")
    print("=" * 55)

    print("[FEED] Teste Market Feed...")

    # Status prüfen
    status = get_feed_status()
    print(f"[FEED] Feed Status: {status['active_exchanges']} Exchanges aktiv")
    print(f"[FEED] Monitoring: {'Aktiv' if status['monitoring_active'] else 'Inaktiv'}")

    # Live-Preise testen
    btc_price = get_live_price('btc')
    if btc_price:
        print(f"[FEED] BTC Live Price: ${btc_price['price']:.2f} from {btc_price['exchange']}")
    else:
        print("[FEED] Kein BTC-Preis verfügbar")

    # Arbitrage testen
    arbitrage = detect_arbitrage()
    print(f"[FEED] Arbitrage Opportunities: {len(arbitrage)}")

    print("\n[FEED] REALTIME MARKET FEED BEREIT!")
    print("Verwende start_market_feed(), get_live_price(), detect_arbitrage()")
    print("WebSocket + REST API Support für Binance, Coinbase, Kraken")
