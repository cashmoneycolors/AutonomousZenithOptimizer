"""
Echtzeit-Marktfeed Modul
WebSocket-basierte Live-Preisfeeds von mehreren Exchanges
"""

import asyncio
import websockets
import json
import logging
from typing import Dict, List, Callable, Optional
from datetime import datetime
from collections import deque
import aiohttp

class RealtimeMarketFeed:
    """Echtzeit-Marktdaten von mehreren Börsen via WebSocket"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_connections = {}
        self.price_callbacks = []
        self.price_history = {}  # Symbol -> deque of prices
        self.max_history = 1000
        
    async def connect_binance(self, symbols: List[str]):
        """Verbindung zu Binance WebSocket für Live-Preise"""
        streams = '/'.join([f"{symbol.lower()}@ticker" for symbol in symbols])
        uri = f"wss://stream.binance.com:9443/stream?streams={streams}"
        
        try:
            async with websockets.connect(uri) as websocket:
                self.active_connections['binance'] = websocket
                self.logger.info(f"✅ Binance WebSocket verbunden: {symbols}")
                
                async for message in websocket:
                    data = json.loads(message)
                    if 'data' in data:
                        await self._process_binance_ticker(data['data'])
        except Exception as e:
            self.logger.error(f"❌ Binance WebSocket Fehler: {e}")
            
    async def connect_coinbase(self, symbols: List[str]):
        """Verbindung zu Coinbase Pro WebSocket"""
        uri = "wss://ws-feed.exchange.coinbase.com"
        
        subscribe_message = {
            "type": "subscribe",
            "product_ids": symbols,
            "channels": ["ticker"]
        }
        
        try:
            async with websockets.connect(uri) as websocket:
                await websocket.send(json.dumps(subscribe_message))
                self.active_connections['coinbase'] = websocket
                self.logger.info(f"✅ Coinbase WebSocket verbunden: {symbols}")
                
                async for message in websocket:
                    data = json.loads(message)
                    if data.get('type') == 'ticker':
                        await self._process_coinbase_ticker(data)
        except Exception as e:
            self.logger.error(f"❌ Coinbase WebSocket Fehler: {e}")
    
    async def connect_kraken(self, symbols: List[str]):
        """Verbindung zu Kraken WebSocket"""
        uri = "wss://ws.kraken.com"
        
        subscribe_message = {
            "event": "subscribe",
            "pair": symbols,
            "subscription": {"name": "ticker"}
        }
        
        try:
            async with websockets.connect(uri) as websocket:
                await websocket.send(json.dumps(subscribe_message))
                self.active_connections['kraken'] = websocket
                self.logger.info(f"✅ Kraken WebSocket verbunden: {symbols}")
                
                async for message in websocket:
                    data = json.loads(message)
                    if isinstance(data, list) and len(data) > 1:
                        await self._process_kraken_ticker(data)
        except Exception as e:
            self.logger.error(f"❌ Kraken WebSocket Fehler: {e}")
            
    async def _process_binance_ticker(self, data: dict):
        """Verarbeite Binance Ticker-Daten"""
        symbol = data.get('s')  # z.B. BTCUSDT
        price = float(data.get('c', 0))  # Last price
        volume_24h = float(data.get('v', 0))
        price_change_pct = float(data.get('P', 0))
        
        price_data = {
            'exchange': 'binance',
            'symbol': symbol,
            'price': price,
            'volume_24h': volume_24h,
            'change_24h_pct': price_change_pct,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await self._update_price_history(symbol, price)
        await self._notify_callbacks(price_data)
        
    async def _process_coinbase_ticker(self, data: dict):
        """Verarbeite Coinbase Ticker-Daten"""
        symbol = data.get('product_id')  # z.B. BTC-USD
        price = float(data.get('price', 0))
        volume_24h = float(data.get('volume_24h', 0))
        
        price_data = {
            'exchange': 'coinbase',
            'symbol': symbol,
            'price': price,
            'volume_24h': volume_24h,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await self._update_price_history(symbol, price)
        await self._notify_callbacks(price_data)
        
    async def _process_kraken_ticker(self, data: list):
        """Verarbeite Kraken Ticker-Daten"""
        if len(data) < 2:
            return
            
        ticker_data = data[1]
        if not isinstance(ticker_data, dict):
            return
            
        symbol = data[3] if len(data) > 3 else 'UNKNOWN'
        
        # Kraken sendet Last trade price in 'c' array
        last_price = ticker_data.get('c', [0])[0] if 'c' in ticker_data else 0
        price = float(last_price)
        
        volume_24h = float(ticker_data.get('v', [0])[1]) if 'v' in ticker_data else 0
        
        price_data = {
            'exchange': 'kraken',
            'symbol': symbol,
            'price': price,
            'volume_24h': volume_24h,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await self._update_price_history(symbol, price)
        await self._notify_callbacks(price_data)
        
    async def _update_price_history(self, symbol: str, price: float):
        """Aktualisiere Preisverlauf für Symbol"""
        if symbol not in self.price_history:
            self.price_history[symbol] = deque(maxlen=self.max_history)
        
        self.price_history[symbol].append({
            'price': price,
            'timestamp': datetime.utcnow()
        })
        
    async def _notify_callbacks(self, price_data: dict):
        """Benachrichtige alle registrierten Callbacks"""
        for callback in self.price_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(price_data)
                else:
                    callback(price_data)
            except Exception as e:
                self.logger.error(f"Callback-Fehler: {e}")
                
    def register_callback(self, callback: Callable):
        """Registriere Callback für Preis-Updates"""
        self.price_callbacks.append(callback)
        self.logger.info(f"✅ Callback registriert: {callback.__name__}")
        
    def get_price_history(self, symbol: str, limit: int = 100) -> List[dict]:
        """Hole Preisverlauf für Symbol"""
        if symbol not in self.price_history:
            return []
        
        history = list(self.price_history[symbol])
        return history[-limit:]
        
    def get_current_prices(self) -> Dict[str, float]:
        """Hole aktuelle Preise aller Symbols"""
        prices = {}
        for symbol, history in self.price_history.items():
            if history:
                prices[symbol] = history[-1]['price']
        return prices
        
    async def detect_arbitrage(self, symbol: str, min_profit_pct: float = 0.5) -> Optional[dict]:
        """Erkenne Arbitrage-Möglichkeiten zwischen Börsen"""
        # Sammle Preise von allen Börsen für das Symbol
        exchange_prices = {}
        
        for exchange in ['binance', 'coinbase', 'kraken']:
            # Normalisiere Symbol-Namen
            normalized_symbol = self._normalize_symbol(symbol, exchange)
            if normalized_symbol in self.price_history:
                history = self.price_history[normalized_symbol]
                if history:
                    exchange_prices[exchange] = history[-1]['price']
        
        if len(exchange_prices) < 2:
            return None
            
        # Finde Min/Max Preise
        min_exchange = min(exchange_prices, key=exchange_prices.get)
        max_exchange = max(exchange_prices, key=exchange_prices.get)
        
        min_price = exchange_prices[min_exchange]
        max_price = exchange_prices[max_exchange]
        
        profit_pct = ((max_price - min_price) / min_price) * 100
        
        if profit_pct >= min_profit_pct:
            return {
                'symbol': symbol,
                'buy_exchange': min_exchange,
                'buy_price': min_price,
                'sell_exchange': max_exchange,
                'sell_price': max_price,
                'profit_pct': profit_pct,
                'timestamp': datetime.utcnow().isoformat()
            }
        
        return None
        
    def _normalize_symbol(self, symbol: str, exchange: str) -> str:
        """Normalisiere Symbol-Namen für verschiedene Börsen"""
        # Entferne Trennzeichen
        base_symbol = symbol.replace('-', '').replace('_', '').upper()
        
        if exchange == 'binance':
            return base_symbol  # z.B. BTCUSDT
        elif exchange == 'coinbase':
            # Coinbase nutzt BTC-USD Format
            if 'USDT' in base_symbol:
                base = base_symbol.replace('USDT', '')
                return f"{base}-USD"
            return symbol
        elif exchange == 'kraken':
            # Kraken nutzt XBT statt BTC
            if base_symbol.startswith('BTC'):
                base_symbol = base_symbol.replace('BTC', 'XBT')
            return base_symbol
        
        return symbol
        
    async def start_multi_exchange_feed(self, symbols: Dict[str, List[str]]):
        """Starte Feeds von mehreren Börsen parallel
        
        Args:
            symbols: Dict mit exchange -> symbol list
                    z.B. {'binance': ['BTCUSDT', 'ETHUSDT'],
                          'coinbase': ['BTC-USD', 'ETH-USD']}
        """
        tasks = []
        
        if 'binance' in symbols:
            tasks.append(self.connect_binance(symbols['binance']))
        
        if 'coinbase' in symbols:
            tasks.append(self.connect_coinbase(symbols['coinbase']))
            
        if 'kraken' in symbols:
            tasks.append(self.connect_kraken(symbols['kraken']))
        
        self.logger.info(f"🚀 Starte {len(tasks)} WebSocket-Verbindungen...")
        await asyncio.gather(*tasks, return_exceptions=True)


class ArbitrageDetector:
    """Spezialisierte Arbitrage-Erkennung mit Benachrichtigungen"""
    
    def __init__(self, market_feed: RealtimeMarketFeed, min_profit_pct: float = 0.5):
        self.market_feed = market_feed
        self.min_profit_pct = min_profit_pct
        self.logger = logging.getLogger(__name__)
        self.opportunities = []
        
    async def monitor_arbitrage(self, symbols: List[str], check_interval: int = 5):
        """Überwache Arbitrage-Möglichkeiten kontinuierlich"""
        while True:
            for symbol in symbols:
                opportunity = await self.market_feed.detect_arbitrage(
                    symbol, 
                    self.min_profit_pct
                )
                
                if opportunity:
                    self.opportunities.append(opportunity)
                    self.logger.info(
                        f"🎯 ARBITRAGE GEFUNDEN! {symbol}: "
                        f"Kaufe @ {opportunity['buy_exchange']} "
                        f"({opportunity['buy_price']:.2f}), "
                        f"Verkaufe @ {opportunity['sell_exchange']} "
                        f"({opportunity['sell_price']:.2f}) = "
                        f"+{opportunity['profit_pct']:.2f}%"
                    )
            
            await asyncio.sleep(check_interval)
            
    def get_opportunities(self, limit: int = 10) -> List[dict]:
        """Hole letzte Arbitrage-Möglichkeiten"""
        return self.opportunities[-limit:]


# CLI-Nutzung
async def main():
    """Demo: Echtzeit-Marktfeed"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    feed = RealtimeMarketFeed()
    
    # Callback für Preis-Updates
    def on_price_update(data):
        print(f"💰 {data['exchange']:10} | {data['symbol']:12} | ${data['price']:>10.2f}")
    
    feed.register_callback(on_price_update)
    
    # Starte Multi-Exchange Feed
    symbols = {
        'binance': ['btcusdt', 'ethusdt', 'bnbusdt'],
        'coinbase': ['BTC-USD', 'ETH-USD'],
        'kraken': ['XBT/USD', 'ETH/USD']
    }
    
    print("🚀 Starte Echtzeit-Marktfeed von Binance, Coinbase & Kraken...")
    print("=" * 70)
    
    # Starte Arbitrage-Überwachung parallel
    arbitrage = ArbitrageDetector(feed, min_profit_pct=0.3)
    
    await asyncio.gather(
        feed.start_multi_exchange_feed(symbols),
        arbitrage.monitor_arbitrage(['BTC', 'ETH', 'BNB'])
    )


if __name__ == "__main__":
    asyncio.run(main())
