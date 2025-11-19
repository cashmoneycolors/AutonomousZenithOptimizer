#!/usr/bin/env python3
"""
Realtime Pricefeed Wrapper
- WebSocket/Poller über bestehendes realtime_market_feed
- Abonnenten: algorithm_switcher, risk_manager, optimization_summary
- Konfiguration via settings.json (optional: RealtimePriceFeed section)
"""
from __future__ import annotations

from typing import Any, Dict, Callable, Optional
from threading import Lock

from python_modules.config_manager import get_config
from python_modules.realtime_market_feed import (
    start_market_feed,
    stop_market_feed,
    get_live_price as _get_live_price,
    get_price_history as _get_price_history,
    calculate_price_change as _calculate_price_change,
    detect_arbitrage as _detect_arbitrage,
    get_feed_status as _get_feed_status,
    realtime_market_feed as _feed
)
from python_modules.algorithm_switcher import switch_to_best_algorithm, get_algorithm_analytics
from python_modules.risk_manager import get_risk_status
from python_modules.optimization_summary import OptimizationSummaryAggregator
from python_modules.alert_system import send_custom_alert


_subscribers_lock = Lock()
_subscribers: list[Callable[[Dict[str, Any]], None]] = []


def _notify_subscribers(live_prices: Dict[str, Any]) -> None:
    with _subscribers_lock:
        for cb in list(_subscribers):
            try:
                cb(live_prices)
            except Exception:
                # Subscriber-Fehler nicht explodieren lassen
                pass


def subscribe(callback: Callable[[Dict[str, Any]], None]) -> None:
    with _subscribers_lock:
        _subscribers.append(callback)


def unsubscribe(callback: Callable[[Dict[str, Any]], None]) -> None:
    with _subscribers_lock:
        if callback in _subscribers:
            _subscribers.remove(callback)


# Intervall/Settings (falls vorhanden)
_feed_settings = get_config('RealtimePriceFeed', {}) or {}

# Hook: leite Updates an unsere lokalen Subscriber weiter
_feed.add_price_callback(_notify_subscribers)


# Default-Subscriber: Algorithm-Switcher, Risk, Optimization Summary

def _algo_subscriber(_: Dict[str, Any]) -> None:
    try:
        result = switch_to_best_algorithm()
        if result.get('switched'):
            send_custom_alert('Algorithm Switch', result.get('message', ''), '[ALGO]')
    except Exception:
        pass


def _risk_subscriber(_: Dict[str, Any]) -> None:
    try:
        _ = get_risk_status()  # Snapshot halten; Alerts erfolgen im Modul selbst
    except Exception:
        pass


_aggregator: Optional[OptimizationSummaryAggregator] = None

def _summary_subscriber(_: Dict[str, Any]) -> None:
    global _aggregator
    try:
        if _aggregator is None:
            _aggregator = OptimizationSummaryAggregator(export_dir='optimization_reports')
        # Nur metrik-snapshot, kein Export bei jedem Tick
        _ = _aggregator.collect_summary(include_rig_details=False)
    except Exception:
        pass


# Registriere Default-Subscriber
subscribe(_algo_subscriber)
subscribe(_risk_subscriber)
subscribe(_summary_subscriber)


# Public API (kompatibel und einfach)

def start() -> None:
    start_market_feed()


def stop() -> None:
    stop_market_feed()


def get_live_price(symbol: str, exchange: Optional[str] = None) -> Optional[Dict[str, Any]]:
    return _get_live_price(symbol, exchange)


def get_price_history(symbol: str, hours: int = 24):
    return _get_price_history(symbol, hours)


def calculate_price_change(symbol: str, hours: int = 1):
    return _calculate_price_change(symbol, hours)


def detect_arbitrage():
    return _detect_arbitrage()


def get_status():
    return _get_feed_status()


if __name__ == '__main__':
    start()
    status = get_status()
    print(f"Realtime Pricefeed aktiv: {status.get('monitoring_active')} | Exchanges: {status.get('active_exchanges')}")
