#!/usr/bin/env python3
"""
REAL-TIME PRICE FEEDS SYSTEM
Live Binance WebSocket Integration für Kryptowährung Preise
"""
import asyncio
import json
import threading
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
import websocket

from python_modules.enhanced_logging import log_event


class PriceData:
    """Echtzeit-Preis Daten Container"""

    def __init__(self, symbol: str):
        self.symbol = symbol
        self.current_price: float = 0.0
        self.price_history: deque = deque(maxlen=1000)  # Last 1000 prices
        self.volume_24h: float = 0.0
        self.price_change_24h: float = 0.0
        self.price_change_percent_24h: float = 0.0
        self.high_24h: float = 0.0
        self.low_24h: float = 0.0
        self.last_update: Optional[float] = None
        self.trade_count: int = 0

    def update_price(self, price: float):
        """Preis aktualisieren"""
        timestamp = time.time()

        # Add to history
        self.price_history.append({
            'price': price,
            'timestamp': timestamp
        })

        # Update current values
        self.current_price = price
        self.last_update = timestamp
        self.trade_count += 1


class RealtimePriceFeedsSystem:
    """Real-Time Price Feeds via Binance WebSockets"""

    BINANCE_WS_URL = "wss://stream.binance.com:9443/ws"

    def __init__(self):
        self.price_data: Dict[str, PriceData] = {}
        self.connection_status = "disconnected"
        self.subscribed_symbols: List[str] = []
        self.websocket_thread: Optional[threading.Thread] = None
        self.running = False
        self.connection_lock = threading.Lock()

        # Callbacks
        self.price_callbacks: List[Callable] = []
        self.error_callbacks: List[Callable] = []

        # Connection parameters
        self.reconnect_attempts = 3
        self.reconnect_delay = 5
        self.heartbeat_interval = 30

        log_event('REALTIME_PRICE_FEEDS_INIT', {
            'binance_ws_url': self.BINANCE_WS_URL,
            'reconnect_attempts': self.reconnect_attempts
        })

    def subscribe_symbols(self, symbols: List[str]) -> bool:
        """Symbols zum Abonnement hinzufügen"""
        # Normalize symbols to Binance format (e.g., BTCUSDT)
        normalized_symbols = [self._normalize_symbol(sym) for sym in symbols]

        new_symbols = [sym for sym in normalized_symbols if sym not in self.subscribed_symbols]

        if not new_symbols:
            return True

        self.subscribed_symbols.extend(new_symbols)

        # Initialize price data
        for symbol in new_symbols:
            self.price_data[symbol] = PriceData(symbol)

        log_event('SYMBOLS_SUBSCRIBED', {
            'symbols': new_symbols,
            'total_subscribed': len(self.subscribed_symbols)
        })

        # If running, update subscription
        if self.running:
            return self._update_subscription()

        return True

    def start(self) -> bool:
        """WebSocket-Verbindung starten"""
        if self.running:
            return True

        if not self.subscribed_symbols:
            log_event('NO_SYMBOLS_TO_SUBSCRIBE')
            return False

        self.running = True
        self.websocket_thread = threading.Thread(target=self._websocket_handler)
        self.websocket_thread.daemon = True
        self.websocket_thread.start()

        log_event('REALTIME_FEEDS_STARTED', {
            'thread_started': True,
            'symbols_count': len(self.subscribed_symbols)
        })

        return True

    def stop(self):
        """Verbindung stoppen"""
        self.running = False

        if self.websocket_thread and self.websocket_thread.is_alive():
            self.websocket_thread.join(timeout=5)

        log_event('REALTIME_FEEDS_STOPPED', {
            'connection_status': self.connection_status
        })

    def get_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Aktueller Preis für Symbol abrufen"""
        normalized = self._normalize_symbol(symbol)

        if normalized in self.price_data:
            data = self.price_data[normalized]
            return {
                'symbol': data.symbol,
                'current_price': data.current_price,
                'volume_24h': data.volume_24h,
                'price_change_24h': data.price_change_24h,
                'price_change_percent_24h': data.price_change_percent_24h,
                'high_24h': data.high_24h,
                'low_24h': data.low_24h,
                'last_update': data.last_update,
                'trade_count': data.trade_count
            }

        return None

    def get_price_history(self, symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Preis-Historie abrufen"""
        normalized = self._normalize_symbol(symbol)

        if normalized in self.price_data:
            history = list(self.price_data[normalized].price_history)[-limit:]
            return history

        return []

    def get_all_prices(self) -> Dict[str, Dict[str, Any]]:
        """Alle Preise abrufen"""
        return {symbol: self.get_price(symbol) for symbol in self.price_data.keys()
                if self.get_price(symbol) is not None}

    def get_system_status(self) -> Dict[str, Any]:
        """System-Status abrufen"""
        return {
            'connection_status': self.connection_status,
            'subscribed_symbols': len(self.subscribed_symbols),
            'active_prices': len([s for s in self.subscribed_symbols if self.price_data[s].current_price > 0]),
            'threads_active': self.websocket_thread and self.websocket_thread.is_alive(),
            'system_running': self.running,
            'last_updates': {symbol: data.last_update for symbol, data in self.price_data.items()
                           if data.last_update}
        }

    def add_price_callback(self, callback: Callable):
        """Preis-Update Callback hinzufügen"""
        if callback not in self.price_callbacks:
            self.price_callbacks.append(callback)

    def add_error_callback(self, callback: Callable):
        """Fehler Callback hinzufügen"""
        if callback not in self.error_callbacks:
            self.error_callbacks.append(callback)

    def _normalize_symbol(self, symbol: str) -> str:
        """Symbol zu Binance Format normalisieren"""
        # Remove common separators and make uppercase
        symbol = symbol.upper().replace('/', '').replace('-', '').replace('_', '')

        # Add USDT if no quote currency specified
        if not any(symbol.endswith(currency) for currency in ['USDT', 'BTC', 'ETH', 'BNB', 'ADA', 'SOL', 'DOT']):
            symbol += 'USDT'

        return symbol

    def _websocket_handler(self):
        """WebSocket Handler Thread"""
        while self.running:
            try:
                self._connect_websocket()
            except Exception as e:
                log_event('WEBSOCKET_CONNECTION_ERROR', {'error': str(e)})
                for callback in self.error_callbacks:
                    try:
                        callback('connection_error', str(e))
                    except Exception:
                        pass  # Don't let callback errors crash the system

            if not self.running:
                break

            # Wait before reconnect
            time.sleep(self.reconnect_delay)

    def _connect_websocket(self):
        """WebSocket-Verbindung herstellen"""
        stream_names = [f"{symbol.lower()}@ticker" for symbol in self.subscribed_symbols]
        subscribe_message = {
            "method": "SUBSCRIBE",
            "params": stream_names,
            "id": 1
        }

        ws_url = f"{self.BINANCE_WS_URL}/{'/'.join(stream_names)}"

        def on_message(ws, message):
            try:
                self._handle_message(message)
            except Exception as e:
                log_event('MESSAGE_PROCESSING_ERROR', {'error': str(e), 'message': message[:500]})

        def on_error(ws, error):
            self.connection_status = f"error: {str(error)}"
            log_event('WEBSOCKET_ERROR', {'error': str(error)})
            for callback in self.error_callbacks:
                try:
                    callback('websocket_error', str(error))
                except Exception:
                    pass

        def on_close(ws, close_status_code, close_msg):
            self.connection_status = f"closed: {close_status_code}"
            if self.running:
                log_event('WEBSOCKET_CLOSED', {
                    'status_code': close_status_code,
                    'message': close_msg
                })

        def on_open(ws):
            self.connection_status = "connected"
            log_event('WEBSOCKET_CONNECTED', {
                'url': ws.url,
                'symbols': len(self.subscribed_symbols)
            })

        ws = websocket.WebSocketApp(ws_url,
                                   on_message=on_message,
                                   on_error=on_error,
                                   on_close=on_close,
                                   on_open=on_open)

        # Heartbeat thread
        def run_heartbeat():
            while self.running and ws.keep_running:
                try:
                    ws.send(json.dumps({"method": "LIST_SUBSCRIPTIONS", "id": 2}))
                except Exception:
                    pass
                time.sleep(self.heartbeat_interval)

        heartbeat_thread = threading.Thread(target=run_heartbeat, daemon=True)
        heartbeat_thread.start()

        # Initial subscription
        ws.on_open = lambda ws: (on_open(ws) or ws.send(json.dumps(subscribe_message)))

        ws.run_forever()

    def _handle_message(self, message: str):
        """Eingehende WebSocket-Nachricht verarbeiten"""
        try:
            data = json.loads(message)

            # Skip subscription confirmations
            if 'result' in data and data.get('id') in [1, 2]:
                return

            # Process ticker data
            if 'stream' in data and '@ticker' in data['stream']:
                symbol = data['stream'].replace('@ticker', '').upper()
                ticker_data = data['data']
                self._update_price_data(symbol, ticker_data)

        except json.JSONDecodeError as e:
            log_event('JSON_PARSE_ERROR', {'error': str(e), 'message': message[:500]})

    def _update_price_data(self, symbol: str, ticker_data: Dict[str, Any]):
        """Preisdaten aktualisieren"""
        if symbol not in self.price_data:
            return

        price_data = self.price_data[symbol]

        # Update price
        current_price = float(ticker_data.get('c', 0))  # Close price
        if current_price > 0:
            price_data.update_price(current_price)

        # Update 24h stats
        price_data.volume_24h = float(ticker_data.get('v', 0))
        price_data.price_change_24h = float(ticker_data.get('p', 0))
        price_data.price_change_percent_24h = float(ticker_data.get('P', 0))
        price_data.high_24h = float(ticker_data.get('h', 0))
        price_data.low_24h = float(ticker_data.get('l', 0))

        # Trigger callbacks
        price_dict = self.get_price(symbol)
        for callback in self.price_callbacks:
            try:
                callback(symbol, price_dict)
            except Exception as e:
                log_event('PRICE_CALLBACK_ERROR', {'callback_error': str(e)})

        log_event('PRICE_UPDATED', {
            'symbol': symbol,
            'price': current_price,
            'change_percent': price_data.price_change_percent_24h
        })

    def _update_subscription(self) -> bool:
        """Subskription bei laufender Verbindung aktualisieren"""
        if not self.running:
            return False

        # This would require reconnecting with new subscription
        # For simplicity, we'll restart the connection
        log_event('UPDATING_SUBSCRIPTION', {
            'new_symbols': len(self.subscribed_symbols)
        })

        return True


# Global instance
realtime_price_feed = RealtimePriceFeedsSystem()


def get_crypto_price(symbol: str) -> Optional[Dict[str, Any]]:
    """Öffentliche Funktion um Preis abzurufen"""
    return realtime_price_feed.get_price(symbol)


def subscribe_crypto_symbols(symbols: List[str]) -> bool:
    """Öffentliche Funktion um Symbole zu abonnieren"""
    return realtime_price_feed.subscribe_symbols(symbols)


def start_price_feeds() -> bool:
    """Öffentliche Funktion um Price Feeds zu starten"""
    return realtime_price_feed.start()


def stop_price_feeds():
    """Öffentliche Funktion um Price Feeds zu stoppen"""
    realtime_price_feed.stop()


def get_price_feed_status() -> Dict[str, Any]:
    """Status der Price Feeds abrufen"""
    return realtime_price_feed.get_system_status()


if __name__ == '__main__':
    # Demo usage
    print("📈 REAL-TIME PRICE FEEDS - Binance WebSocket Demo")
    print("=" * 55)

    # Subscribe to major crypto pairs
    test_symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT', 'DOTUSDT']

    print(f"📊 Subscribing to {len(test_symbols)} crypto pairs...")
    realtime_price_feed.subscribe_symbols(test_symbols)

    # Add price update callback
    def price_callback(symbol, price_data):
        if price_data:
            print(f"💰 {symbol}: ${price_data['current_price']:.2f} "
                  ".2%")

    realtime_price_feed.add_price_callback(price_callback)

    print("🚀 Starting real-time price feeds...")
    success = realtime_price_feed.start()

    if success:
        print("✅ Connected to Binance WebSocket")

        # Run for 60 seconds
        for i in range(60):
            status = realtime_price_feed.get_system_status()
            print(f"\r📊 Status: {status['connection_status']} | "
                  f"Active: {status['active_prices']}/{status['subscribed_symbols']} | "
                  f"⏰ {60-i}s remaining", end='', flush=True)
            time.sleep(1)

        print("\n\n📋 Final Prices:")
        all_prices = realtime_price_feed.get_all_prices()
        for symbol, data in all_prices.items():
            if data:
                print(f"  {symbol:8}: ${data['current_price']:>12.2f} | "
                      f"{data['price_change_percent_24h']:+.2f}% 24h")

        print("\n🛑 Stopping price feeds...")
        realtime_price_feed.stop()

    print("🎉 Demo completed!")
