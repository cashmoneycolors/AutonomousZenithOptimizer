#!/usr/bin/env python3
"""
CASH MONEY COLORS ORIGINAL (R) - MINING DATA COLLECTOR
Sammelt und speichert ALLE Mining-Daten persistent
ECHTE PRODUKTIONS-DATENBANK für Mining-Operationen
"""
import sys

from pathlib import Path
from auto_error_fixing import attempt_error_fix


# Universal Integration Setup
def setup_universal_integration():
    """Richtet universelle Integration mit API-Keys und PayPal ein"""

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
universal_config = setup_universal_integration()


import sqlite3
import json
import time
import random
from datetime import datetime, timedelta
import os
import threading


class MiningDataCollector:
    """Umfassendes Daten-Sammel-System für Mining-Operationen"""

    def __init__(self):
        self.db_path = "data/mining_data_collector.db"
        os.makedirs("data", exist_ok=True)

        # Initialize Datenbank
        self.init_database()

        # Daten-Sammel-Statistiken
        self.total_sessions = 0
        self.total_cycles = 0
        self.total_profit = 0.0
        self.peak_capital = 0.0
        self.best_cycle_profit = 0.0

        # Live-Daten
        self.current_session_data = []
        self.performance_history = []

        print("MINING DATA COLLECTOR INITIALIZED")
        print("=" * 50)

    def init_database(self):
        """Erstelle vollständige Datenbank-Struktur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Mining Sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mining_sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                end_time DATETIME,
                duration_seconds INTEGER,
                total_cycles INTEGER,
                total_profit REAL,
                peak_capital REAL,
                rigs_used INTEGER,
                status TEXT
                )
            ''')

        # Mining Cycles
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mining_cycles (
                cycle_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                cycle_number INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                capital_before REAL,
                capital_after REAL,
                cycle_profit REAL,
                active_rigs INTEGER,
                total_hashrate REAL,
                optimization_events TEXT,
                FOREIGN KEY (session_id) REFERENCES mining_sessions (session_id)
                )
            ''')

        # Rig Performance
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rig_performance (
                performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                cycle_id INTEGER,
                rig_id TEXT,
                rig_type TEXT,
                algorithm TEXT,
                coin TEXT,
                hash_rate REAL,
                power_consumption REAL,
                temperature REAL,
                profit_per_day REAL,
                efficiency REAL,
                status TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cycle_id) REFERENCES mining_cycles (cycle_id)
                )
            ''')

        # Algorithm Performance
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS algorithm_performance (
                algo_id INTEGER PRIMARY KEY AUTOINCREMENT,
                cycle_id INTEGER,
                algorithm TEXT,
                coin TEXT,
                rigs_using INTEGER,
                total_profit REAL,
                avg_efficiency REAL,
                market_factor REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cycle_id) REFERENCES mining_cycles (cycle_id)
                )
            ''')

        # System Events
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                event_type TEXT,
                event_description TEXT,
                event_data TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES mining_sessions (session_id)
                )
            ''')

        # Performance Analytics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_analytics (
                analytics_id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                total_sessions INTEGER,
                total_cycles INTEGER,
                total_profit REAL,
                avg_cycle_profit REAL,
                best_cycle_profit REAL,
                peak_capital REAL,
                rigs_used_avg REAL,
                optimization_events INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

        conn.commit()
        conn.close()

    def start_mining_session(self):
        """Starte neue Mining-Session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO mining_sessions (status)
            VALUES (?)
            ''', ('ACTIVE',))

        session_id = cursor.lastrowid
        conn.commit()
        conn.close()

        self.total_sessions += 1
        self.current_session_data = []

        # Log Session-Start
        self.log_system_event(session_id, 'SESSION_START', 'Mining session started', {'session_id': session_id})

        print(f"MINING SESSION {session_id} GESTARTET")
        return session_id

    def record_mining_cycle(self, session_id, cycle_data):
        """Zeichne Mining-Cycle-Daten auf"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Cycle-Daten
        cursor.execute('''
            INSERT INTO mining_cycles
            (session_id, cycle_number, capital_before, capital_after, cycle_profit,
             active_rigs, total_hashrate, optimization_events)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
            session_id,
            cycle_data['cycle_number'],
            cycle_data['capital_before'],
            cycle_data['capital_after'],
            cycle_data['cycle_profit'],
            cycle_data['active_rigs'],
            cycle_data.get('total_hashrate', 0),
            json.dumps(cycle_data.get('optimization_events', []))
            ))

        cycle_id = cursor.lastrowid

        # Rig Performance
        for rig in cycle_data.get('rigs', []):
            cursor.execute('''
                INSERT INTO rig_performance
                (cycle_id, rig_id, rig_type, algorithm, coin, hash_rate,
                 power_consumption, temperature, profit_per_day, efficiency, status)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                cycle_id,
                rig['id'],
                rig['type'],
                rig['algo'],
                rig['coin'],
                rig.get('hash_rate', 0),
                rig.get('power', 0),
                rig.get('temp', 0),
                rig['profit'],
                rig.get('efficiency', 0),
                rig['status']
                ))

        # Algorithm Performance
        for algo_data in cycle_data.get('algorithm_performance', []):
            cursor.execute('''
                INSERT INTO algorithm_performance
                (cycle_id, algorithm, coin, rigs_using, total_profit, avg_efficiency, market_factor)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                cycle_id,
                algo_data['algorithm'],
                algo_data['coin'],
                algo_data['rigs_using'],
                algo_data['total_profit'],
                algo_data['avg_efficiency'],
                algo_data['market_factor']
                ))

        conn.commit()
        conn.close()

        # Update Statistiken
        self.total_cycles += 1
        self.total_profit += cycle_data['cycle_profit']
        self.peak_capital = max(self.peak_capital, cycle_data['capital_after'])
        self.best_cycle_profit = max(self.best_cycle_profit, cycle_data['cycle_profit'])

        # Speichere in Session-Daten
        self.current_session_data.append(cycle_data)

        return cycle_id

    def end_mining_session(self, session_id):
        """Beende Mining-Session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Berechne Session-Statistiken
        session_cycles = len(self.current_session_data)
        session_profit = sum(cycle['cycle_profit'] for cycle in self.current_session_data)
        peak_capital = max((cycle['capital_after'] for cycle in self.current_session_data), default=0)

        # Update Session
        cursor.execute('''
            UPDATE mining_sessions
            SET end_time = CURRENT_TIMESTAMP,
                duration_seconds = ?,
                total_cycles = ?,
                total_profit = ?,
                peak_capital = ?,
                rigs_used = ?,
                status = ?
                WHERE session_id = ?
            ''', (
            session_cycles * 2,  # Ungefähre Dauer (2 Sekunden pro Cycle)
            session_cycles,
            session_profit,
            peak_capital,
            self.current_session_data[0]['active_rigs'] if self.current_session_data else 0,
            'COMPLETED',
            session_id
            ))

        conn.commit()
        conn.close()

        # Log Session-Ende
        self.log_system_event(session_id, 'SESSION_END', 'Mining session completed',
            {'cycles': session_cycles, 'profit': session_profit})

        print(f"MINING SESSION {session_id} BEENDET")
        print(f"Cycles: {session_cycles}, Profit: {session_profit:.2f} CHF")

    def log_system_event(self, session_id, event_type, description, event_data=None):
        """Log System-Event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO system_events (session_id, event_type, event_description, event_data)
            VALUES (?, ?, ?, ?)
            ''', (
            session_id,
            event_type,
            description,
            json.dumps(event_data) if event_data else None
            ))

        conn.commit()
        conn.close()

    def log_optimization_event(self, session_id, optimization_type, details):
        """Log Optimierung-Event"""
        self.log_system_event(session_id, 'OPTIMIZATION', f'{optimization_type} optimization performed', details)

    def log_hardware_event(self, session_id, hardware_event, details):
        """Log Hardware-Event"""
        self.log_system_event(session_id, 'HARDWARE', hardware_event, details)

    def update_daily_analytics(self):
        """Update tägliche Analytics"""
        today = datetime.now().date()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Sammle Tagesdaten
        cursor.execute('''
            SELECT COUNT(*), SUM(total_cycles), SUM(total_profit),
                AVG(total_profit/total_cycles), MAX(peak_capital)
                   FROM mining_sessions
            WHERE DATE(start_time) = ?
            ''', (today,))

        result = cursor.fetchone()

        if result and result[0] > 0:
            cursor.execute('''
                INSERT OR REPLACE INTO performance_analytics
                (date, total_sessions, total_cycles, total_profit, avg_cycle_profit,
                 best_cycle_profit, peak_capital, rigs_used_avg, optimization_events)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                today,
                result[0],  # total_sessions
                result[1] or 0,  # total_cycles
                result[2] or 0,  # total_profit
                result[3] or 0,  # avg_cycle_profit
                self.best_cycle_profit,
                result[4] or 0,  # peak_capital
                6,  # Durchschnittliche Rigs (kann verbessert werden)
                0   # optimization_events (kann verbessert werden)
                ))

            conn.commit()
        conn.close()

    def get_session_summary(self, session_id):
        """Hole Session-Zusammenfassung"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM mining_sessions WHERE session_id = ?
            ''', (session_id,))

        session = cursor.fetchone()
        conn.close()

        if session:
            return {
                'session_id': session[0],
                'start_time': session[1],
                'end_time': session[2],
                'duration_seconds': session[3],
                'total_cycles': session[4],
                'total_profit': session[5],
                'peak_capital': session[6],
                'rigs_used': session[7],
                'status': session[8]
                }
            return None

    def get_performance_report(self, days=7):
        """Hole Performance-Report für letzte X Tage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT date, total_sessions, total_cycles, total_profit,
                avg_cycle_profit, peak_capital
                   FROM performance_analytics
            WHERE date >= date('now', '-{} days')
            ORDER BY date DESC
            '''.format(days))

        reports = cursor.fetchall()
        conn.close()

        return [{
            'date': row[0],
            'sessions': row[1],
            'cycles': row[2],
            'profit': row[3],
            'avg_cycle_profit': row[4],
            'peak_capital': row[5]
            } for row in reports]

    def export_all_data(self, filename="mining_data_export.json"):
        """Exportiere alle Daten als JSON"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'summary': {
                'total_sessions': self.total_sessions,
                'total_cycles': self.total_cycles,
                'total_profit': self.total_profit,
                'peak_capital': self.peak_capital,
                'best_cycle_profit': self.best_cycle_profit
                },
            'sessions': [],
            'cycles': [],
            'rig_performance': [],
            'algorithm_performance': [],
            'system_events': [],
            'analytics': []
            }

        # Export all tables
        tables = ['mining_sessions', 'mining_cycles', 'rig_performance',
            'algorithm_performance', 'system_events', 'performance_analytics']

        for table in tables:
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()

            export_data[table.replace('mining_', '').replace('performance_', '').replace('_', '')] = [
                dict(row) for row in rows
                ]

            conn.close()

        # Save to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)

            print(f"ALLE DATEN EXPORTIERT NACH: {filename}")
        return filename

    def get_database_stats(self):
        """Hole Datenbank-Statistiken"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {}

        # Count records in each table
        tables = ['mining_sessions', 'mining_cycles', 'rig_performance',
            'algorithm_performance', 'system_events', 'performance_analytics']

        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            stats[table] = cursor.fetchone()[0]

        # Database file size
        stats['database_size_mb'] = os.path.getsize(self.db_path) / (1024 * 1024)

        conn.close()

        return stats


# Demo-Daten-Sammler für Live-Demo
class LiveDataCollector:
    """Sammelt Live-Daten aus der Mining-Demo"""

    def __init__(self):
        self.data_collector = MiningDataCollector()
        self.current_session_id = None
        self.is_collecting = False

    def start_collection(self):
        """Starte Daten-Sammlung"""
        self.current_session_id = self.data_collector.start_mining_session()
        self.is_collecting = True
        print("LIVE DATA COLLECTION GESTARTET")

    def collect_cycle_data(self, capital_before, capital_after, cycle_profit, active_rigs, rigs_data):
        """Sammle Cycle-Daten"""
        if not self.is_collecting or not self.current_session_id:
            return

            cycle_data = {
            'cycle_number': len(self.data_collector.current_session_data) + 1,
            'capital_before': capital_before,
            'capital_after': capital_after,
            'cycle_profit': cycle_profit,
            'active_rigs': active_rigs,
            'total_hashrate': sum(rig.get('hash_rate', 100) for rig in rigs_data),
            'optimization_events': [],
            'rigs': rigs_data,
            'algorithm_performance': self.calculate_algorithm_performance(rigs_data)
            }

        self.data_collector.record_mining_cycle(self.current_session_id, cycle_data)

    def collect_optimization_event(self, event_type, details):
        """Sammle Optimierung-Event"""
        if self.is_collecting and self.current_session_id:
            self.data_collector.log_optimization_event(self.current_session_id, event_type, details)

    def collect_hardware_event(self, event_type, details):
        """Sammle Hardware-Event"""
        if self.is_collecting and self.current_session_id:
            self.data_collector.log_hardware_event(self.current_session_id, event_type, details)

    def calculate_algorithm_performance(self, rigs_data):
        """Berechne Algorithmus-Performance"""
        algo_stats = {}

        for rig in rigs_data:
            algo = rig['algo']
            coin = rig['coin']

            if algo not in algo_stats:
                algo_stats[algo] = {
                    'algorithm': algo,
                    'coin': coin,
                    'rigs_using': 0,
                    'total_profit': 0.0,
                    'avg_efficiency': 0.0,
                    'market_factor': random.uniform(0.9, 1.1)
                    }

                algo_stats[algo]['rigs_using'] += 1
            algo_stats[algo]['total_profit'] += rig['profit']

        # Calculate averages
        for algo_data in algo_stats.values():
            if algo_data['rigs_using'] > 0:
                algo_data['avg_efficiency'] = algo_data['total_profit'] / algo_data['rigs_using']

                return list(algo_stats.values())

    def stop_collection(self):
        """Stoppe Daten-Sammlung"""
        if self.is_collecting and self.current_session_id:
            self.data_collector.end_mining_session(self.current_session_id)
            self.data_collector.update_daily_analytics()
            self.is_collecting = False
            print("LIVE DATA COLLECTION GESTOPPT")

    def export_session_data(self):
        """Exportiere Session-Daten"""
        if self.current_session_id:
            filename = f"mining_session_{self.current_session_id}_export.json"
            return self.data_collector.export_all_data(filename)
            return None

    def get_collection_stats(self):
        """Hole Sammel-Statistiken"""
        return {
            'current_session': self.current_session_id,
            'is_collecting': self.is_collecting,
            'session_cycles': len(self.data_collector.current_session_data),
            'database_stats': self.data_collector.get_database_stats(),
            'performance_report': self.data_collector.get_performance_report(7)
            }


# Standalone Demo mit Daten-Sammlung
def run_demo_with_data_collection():
    """Demo mit vollständiger Daten-Sammlung"""

    # Initialize Data Collector
    data_collector = LiveDataCollector()

    # Demo Rigs
    rigs = [
        {'id': 'ASIC_1', 'type': 'S19_Pro', 'algo': 'SHA256', 'coin': 'BTC', 'profit': 25.0, 'status': 'ACTIVE'},
        {'id': 'ASIC_2', 'type': 'M50', 'algo': 'SHA256', 'coin': 'BTC', 'profit': 28.0, 'status': 'ACTIVE'},
        {'id': 'GPU_1', 'type': 'RTX_4090', 'algo': 'Ethash', 'coin': 'ETH', 'profit': 15.0, 'status': 'ACTIVE'},
        {'id': 'GPU_2', 'type': 'RTX_4090', 'algo': 'KawPow', 'coin': 'RVN', 'profit': 18.0, 'status': 'ACTIVE'},
        {'id': 'GPU_3', 'type': 'RTX_3090', 'algo': 'Ethash', 'coin': 'ETH', 'profit': 12.0, 'status': 'ACTIVE'},
        {'id': 'GPU_4', 'type': 'RTX_3090', 'algo': 'RandomX', 'coin': 'XMR', 'profit': 10.0, 'status': 'ACTIVE'},
        ]

    print("CASH MONEY COLORS ORIGINAL (R) - MINING DATA COLLECTOR DEMO")
    print("=" * 70)
    print("SAMMELT ALLE MINING-DATEN IN ECHTER PRODUKTIONS-DATENBANK")
    print("=" * 70)

    # Start Data Collection
    data_collector.start_collection()

    capital = 100.0
    total_profit = 0.0

    print(f"STARTKAPITAL: {capital:.2f} CHF")
    print("STARTE MINING MIT LIVE-DATEN-SAMMLUNG...")
    print()

    for cycle in range(1, 16):
        capital_before = capital

        # Calculate profit
        cycle_profit = sum(rig['profit'] * random.uniform(0.9, 1.1) for rig in rigs)
        capital += cycle_profit
        total_profit += cycle_profit

        # Update rig temperatures
        for rig in rigs:
            rig['temp'] = int(60 + random.uniform(-5, 15))

        # Collect cycle data
        data_collector.collect_cycle_data(capital_before, capital, cycle_profit, len(rigs), rigs)

        print(f"Cycle {cycle}: +{cycle_profit:.2f} CHF -> Total: {capital:.2f} CHF")

        # Algorithm optimization every 5 cycles
        if cycle % 5 == 0:
            # Simulate optimization
            for rig in rigs:
                if random.random() < 0.4:
                    old_coin = rig['coin']
                    if 'ASIC' in rig['id']:
                        rig['coin'] = 'BCH' if rig['coin'] == 'BTC' else 'BTC'
                    else:
                        algorithms = [('Ethash', 'ETH'), ('KawPow', 'RVN'), ('RandomX', 'XMR')]
                        new_algo, new_coin = random.choice(algorithms)
                        rig['algo'] = new_algo
                        rig['coin'] = new_coin

                        rig['profit'] *= random.uniform(0.95, 1.05)

                    data_collector.collect_optimization_event('ALGORITHM_SWITCH', {'cycle': cycle})
            print(">>> ALGORITHM OPTIMIZATION COMPLETED <<<")

        # Hardware scaling every 10 cycles
        if cycle % 10 == 0:
            new_rig = {
                'id': f'GPU_{len(rigs) + 1}',
                'type': 'RTX_4090',
                'algo': 'Ethash',
                'coin': 'ETH',
                'profit': 16.0,
                'status': 'ACTIVE'
                }
            rigs.append(new_rig)
            data_collector.collect_hardware_event('HARDWARE_SCALING', {'new_rig': new_rig['id']})
            print(">>> HARDWARE SCALING COMPLETED <<<")

            time.sleep(0.5)

    # Stop collection and export
    data_collector.stop_collection()

    print("\n" + "=" * 70)
    print("DEMO BEENDET - ALLE DATEN GESAMMELT UND GESPEICHERT")
    print("=" * 70)
    print(f"FINALES KAPITAL: {capital:.2f} CHF")
    print(f"GESAMTGEWINN: {total_profit:.2f} CHF")
    print(f"ZYKLEN: {len(data_collector.data_collector.current_session_data)}")

    # Export data
    export_file = data_collector.export_session_data()
    if export_file:
        print(f"DATEN EXPORTIERT: {export_file}")

    # Show database stats
    stats = data_collector.get_collection_stats()
    print("\nDATENBANK-STATISTIKEN:")
    for key, value in stats['database_stats'].items():
        print(f"  {key}: {value}")

    print("\n>>> ALLE MINING-DATEN WURDEN ERFOLGREICH GESAMMELT UND GESPEICHERT <<<")


if __name__ == "__main__":
    run_demo_with_data_collection()


def run():
    """Standard run() Funktion für Dashboard-Integration"""
    print(f"Modul {__name__} wurde ausgeführt")
    print("Implementiere hier deine spezifische Logik...")


if __name__ == "__main__":
    run()#!/usr/bin/env python3
"""Produktive Datenerfassung für das autonome Mining-System."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:  # pragma: no cover - Fallback für Direktaufruf
    from python_modules.mining_system_integration import IntegratedMiningSystem
except ModuleNotFoundError:  # pragma: no cover - Unterstützung für Namespace-Pakete
    from mining_system_integration import IntegratedMiningSystem  # type: ignore

from python_modules.algorithm_switcher import switch_to_best_algorithm
from python_modules.enhanced_logging import log_event


@dataclass(slots=True)
class SessionSummary:
    """Aggregierte Informationen einer aufgezeichneten Sitzung."""

    session_id: int
    started_at: datetime
    ended_at: datetime
    duration_seconds: float
    snapshots: int
    daily_profit: float
    total_profit: float
    risk_level: str
    risk_score: Optional[float]
    recommendation: str
    report: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat(),
            "duration_seconds": round(self.duration_seconds, 3),
            "snapshots": self.snapshots,
            "daily_profit": round(self.daily_profit, 4),
            "total_profit": round(self.total_profit, 4),
            "risk_level": self.risk_level,
            "risk_score": None if self.risk_score is None else round(self.risk_score, 2),
            "recommendation": self.recommendation,
            "report": self.report,
        }


class MiningDataCollector:
    """Persistente Datenerfassung für das Integrated Mining System."""

    DEFAULT_DB_PATH = Path("data") / "mining_data_collector.db"

    def __init__(self, db_path: Optional[str | Path] = None) -> None:
        self.db_path = Path(db_path) if db_path is not None else self.DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _ensure_schema(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    started_at TEXT NOT NULL,
                    ended_at TEXT,
                    duration_seconds REAL,
                    snapshots INTEGER DEFAULT 0,
                    total_profit REAL,
                    daily_profit REAL,
                    risk_level TEXT,
                    risk_score REAL,
                    recommendation TEXT,
                    notes TEXT
                );

                CREATE TABLE IF NOT EXISTS snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    daily_profit REAL,
                    total_profit REAL,
                    active_rigs INTEGER,
                    risk_level TEXT,
                    risk_score REAL,
                    recommendation TEXT,
                    advisories TEXT,
                    FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS rig_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    snapshot_id INTEGER NOT NULL,
                    rig_id TEXT NOT NULL,
                    rig_type TEXT,
                    algorithm TEXT,
                    coin TEXT,
                    hash_rate REAL,
                    power_consumption REAL,
                    profit_per_day REAL,
                    temperature REAL,
                    efficiency REAL,
                    status TEXT,
                    FOREIGN KEY(snapshot_id) REFERENCES snapshots(id) ON DELETE CASCADE
                );
                """
            )

    def _begin_session(self, started_at: datetime) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO sessions (started_at) VALUES (?)",
                (started_at.isoformat(),),
            )
            return int(cursor.lastrowid)

    def _store_snapshot(self, session_id: int, status: Dict[str, Any]) -> None:
        timestamp = datetime.now(timezone.utc)
        system_status: Dict[str, Any] = status.get("system_status", {})
        assessment: Dict[str, Any] = system_status.get("last_risk_assessment", {})
        advisories: List[str] = list(system_status.get("advisories", []))

        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO snapshots (
                    session_id, timestamp, daily_profit, total_profit,
                    active_rigs, risk_level, risk_score, recommendation, advisories
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    timestamp.isoformat(),
                    float(system_status.get("daily_profit", 0.0) or 0.0),
                    float(system_status.get("total_profit", 0.0) or 0.0),
                    int(system_status.get("active_rigs", 0) or 0),
                    str(assessment.get("level", "unknown")),
                    float(assessment.get("score", 0.0) or 0.0),
                    str(assessment.get("recommendation", "")),
                    json.dumps(advisories[-10:], ensure_ascii=False),
                ),
            )
            snapshot_id = int(cursor.lastrowid)

            for rig in status.get("mining_rigs", []):
                conn.execute(
                    """
                    INSERT INTO rig_snapshots (
                        snapshot_id, rig_id, rig_type, algorithm, coin,
                        hash_rate, power_consumption, profit_per_day,
                        temperature, efficiency, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        snapshot_id,
                        str(rig.get("id")),
                        str(rig.get("type")),
                        str(rig.get("algorithm")),
                        str(rig.get("coin")),
                        float(rig.get("hash_rate", 0.0) or 0.0),
                        float(rig.get("power_consumption", 0.0) or 0.0),
                        float(rig.get("profit_per_day", 0.0) or 0.0),
                        float(rig.get("temperature", 0.0) or 0.0),
                        float(rig.get("efficiency", 0.0) or 0.0),
                        str(rig.get("status", "UNKNOWN")),
                    ),
                )

    def _finalize_session(
        self,
        session_id: int,
        started_at: datetime,
        ended_at: datetime,
        snapshots: int,
        status: Dict[str, Any],
        report: str,
    ) -> SessionSummary:
        duration = max(0.0, (ended_at - started_at).total_seconds())
        system_status: Dict[str, Any] = status.get("system_status", {})
        assessment: Dict[str, Any] = system_status.get("last_risk_assessment", {})

        daily_profit = float(system_status.get("daily_profit", 0.0) or 0.0)
        total_profit = float(system_status.get("total_profit", 0.0) or 0.0)
        risk_score = float(assessment.get("score")) if assessment.get("score") is not None else None

        with self._connect() as conn:
            conn.execute(
                """
                UPDATE sessions
                SET ended_at = ?,
                    duration_seconds = ?,
                    snapshots = ?,
                    total_profit = ?,
                    daily_profit = ?,
                    risk_level = ?,
                    risk_score = ?,
                    recommendation = ?,
                    notes = ?
                WHERE id = ?
                """,
                (
                    ended_at.isoformat(),
                    duration,
                    snapshots,
                    total_profit,
                    daily_profit,
                    str(assessment.get("level", "unknown")),
                    risk_score,
                    str(assessment.get("recommendation", "")),
                    json.dumps(system_status.get("analysis_summary", {}), ensure_ascii=False)
                    if system_status.get("analysis_summary")
                    else None,
                    session_id,
                ),
            )

        return SessionSummary(
            session_id=session_id,
            started_at=started_at,
            ended_at=ended_at,
            duration_seconds=duration,
            snapshots=snapshots,
            daily_profit=daily_profit,
            total_profit=total_profit,
            risk_level=str(assessment.get("level", "unknown")),
            risk_score=risk_score,
            recommendation=str(assessment.get("recommendation", "")),
            report=report,
        )

    def _mark_session_failed(
        self,
        session_id: int,
        started_at: datetime,
        ended_at: datetime,
        snapshots: int,
        error_message: str,
    ) -> None:
        duration = max(0.0, (ended_at - started_at).total_seconds())
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE sessions
                SET ended_at = ?,
                    duration_seconds = ?,
                    snapshots = ?,
                    risk_level = 'error',
                    recommendation = ?,
                    notes = ?
                WHERE id = ?
                """,
                (
                    ended_at.isoformat(),
                    duration,
                    snapshots,
                    "Sitzung aufgrund eines Fehlers beendet",
                    error_message,
                    session_id,
                ),
            )

    def _evaluate_market_algorithm_switch(self) -> Optional[Dict[str, Any]]:
        try:
            result = switch_to_best_algorithm()
        except Exception as exc:
            log_event('MARKET_ALGO_SWITCH_ERROR', {'error': str(exc), 'timestamp': datetime.now().isoformat()})
            return None

        if result.get('success'):
            analysis = result.get('analysis', {})
            log_event('MARKET_ALGO_SWITCH_COMPLETED', {
                'algorithm': analysis.get('algorithm', 'unknown'),
                'improvement': analysis.get('improvement', 0),
                'risk_factor': analysis.get('risk_factor', 0),
                'timestamp': datetime.now().isoformat(),
            })

        return result

    def run_session(
        self,
        duration_seconds: float = 60.0,
        snapshot_interval: float = 5.0,
        optimize_every: int = 3,
    ) -> SessionSummary:
        duration_seconds = max(0.5, float(duration_seconds))
        snapshot_interval = max(0.1, float(snapshot_interval))
        optimize_every = max(1, int(optimize_every))

        started_at = datetime.now(timezone.utc)
        session_id = self._begin_session(started_at)

        system = IntegratedMiningSystem(
            monitoring_interval=snapshot_interval,
            collection_interval=snapshot_interval,
            analysis_interval=snapshot_interval,
        )
        system.start_integrated_mining()

        snapshots = 0
        last_status: Dict[str, Any] = {}
        try:
            end_time = time.monotonic() + duration_seconds
            while time.monotonic() < end_time:
                system.step_once(include_collection=True, include_analysis=True)
                current_status = system.get_system_status()
                self._store_snapshot(session_id, current_status)
                last_status = current_status
                snapshots += 1

                if snapshots % optimize_every == 0:
                    system.optimize_mining_strategy()
                    self._evaluate_market_algorithm_switch()

                time.sleep(snapshot_interval)
        except Exception as exc:  # pragma: no cover - rethrow nach Logging
            ended_at = datetime.now(timezone.utc)
            self._mark_session_failed(session_id, started_at, ended_at, snapshots, str(exc))
            raise
        finally:
            system.stop_integrated_mining()

        ended_at = datetime.now(timezone.utc)
        if not last_status:
            last_status = system.get_system_status()
        report = system.generate_system_report()
        return self._finalize_session(session_id, started_at, ended_at, snapshots, last_status, report)

    def list_sessions(self) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, started_at, ended_at, snapshots, total_profit, daily_profit, risk_level
                FROM sessions
                ORDER BY id DESC
                """
            ).fetchall()
        sessions: List[Dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            if item.get("started_at"):
                item["started_at"] = str(item["started_at"])
            if item.get("ended_at"):
                item["ended_at"] = str(item["ended_at"])
            sessions.append(item)
        return sessions

    def get_session_detail(self, session_id: int) -> Dict[str, Any]:
        with self._connect() as conn:
            session = conn.execute(
                "SELECT * FROM sessions WHERE id = ?",
                (session_id,),
            ).fetchone()
            if session is None:
                raise ValueError(f"Unbekannte Session-ID: {session_id}")

            snapshot_rows = conn.execute(
                "SELECT * FROM snapshots WHERE session_id = ? ORDER BY id",
                (session_id,),
            ).fetchall()

            if snapshot_rows:
                placeholder = ",".join("?" for _ in snapshot_rows)
                ids = [row["id"] for row in snapshot_rows]
                rig_rows = conn.execute(
                    f"SELECT * FROM rig_snapshots WHERE snapshot_id IN ({placeholder}) ORDER BY snapshot_id, rig_id",
                    ids,
                ).fetchall()
            else:
                rig_rows = []

        session_dict = dict(session)
        for key in ("started_at", "ended_at"):
            if session_dict.get(key):
                session_dict[key] = str(session_dict[key])
        if session_dict.get("notes"):
            try:
                session_dict["notes"] = json.loads(session_dict["notes"])
            except json.JSONDecodeError:
                pass

        rig_map: Dict[int, List[Dict[str, Any]]] = {}
        for rig in rig_rows:
            rig_entry = dict(rig)
            rid = rig_entry.pop("snapshot_id")
            rig_map.setdefault(rid, []).append(rig_entry)

        snapshots: List[Dict[str, Any]] = []
        for row in snapshot_rows:
            entry = dict(row)
            entry_id = entry.pop("id")
            entry["timestamp"] = str(entry["timestamp"])
            if entry.get("advisories"):
                try:
                    entry["advisories"] = json.loads(entry["advisories"])
                except json.JSONDecodeError:
                    entry["advisories"] = [entry["advisories"]]
            entry["rigs"] = rig_map.get(entry_id, [])
            snapshots.append(entry)

        return {"session": session_dict, "snapshots": snapshots}

    def export_session_to_json(self, session_id: int, output_path: str | Path) -> Path:
        detail = self.get_session_detail(session_id)
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(detail, indent=2, ensure_ascii=False), encoding="utf-8")
        return output


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Persistente Datenerfassung für das Integrated Mining System")
    parser.add_argument("--database", type=Path, default=MiningDataCollector.DEFAULT_DB_PATH,
                        help="Pfad zur SQLite-Datenbank (Standard: data/mining_data_collector.db)")
    parser.add_argument("--duration", type=float, default=30.0,
                        help="Aufzeichnungsdauer in Sekunden (Standard: 30)")
    parser.add_argument("--interval", type=float, default=2.0,
                        help="Abstand zwischen Snapshots in Sekunden (Standard: 2)")
    parser.add_argument("--optimize-every", type=int, default=3,
                        help="Anzahl Snapshots bis zur automatischen Optimierung")
    parser.add_argument("--list", action="store_true", dest="list_sessions",
                        help="Vorhandene Sitzungen statt einer neuen Aufzeichnung anzeigen")
    parser.add_argument("--export", type=Path, default=None,
                        help="Exportiert die letzte aufgezeichnete Sitzung als JSON an den angegebenen Pfad")
    parser.add_argument("--session", type=int, default=None,
                        help="Explizite Session-ID für den Export oder die Detailanzeige")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    collector = MiningDataCollector(db_path=args.database)

    if args.list_sessions:
        sessions = collector.list_sessions()
        if not sessions:
            print("Keine gespeicherten Sitzungen vorhanden.")
            return 0
        print("Verfügbare Sitzungen:")
        for entry in sessions:
            started = entry.get("started_at", "?")
            ended = entry.get("ended_at") or "laufend" if entry.get("ended_at") else "-"
            print(f"  #{entry['id']}: {started} -> {ended}, Snapshots={entry['snapshots']}, Risiko={entry['risk_level']}")
        return 0

    summary = collector.run_session(
        duration_seconds=args.duration,
        snapshot_interval=args.interval,
        optimize_every=args.optimize_every,
    )

    print("Sitzung abgeschlossen:")
    print(json.dumps(summary.to_dict(), indent=2, ensure_ascii=False))

    session_id = summary.session_id if args.session is None else args.session
    if args.export:
        export_path = collector.export_session_to_json(session_id, args.export)
        print(f"Sitzung als JSON exportiert: {export_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
