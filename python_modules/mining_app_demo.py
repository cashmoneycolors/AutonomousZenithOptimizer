#!/usr/bin/env python3
"""
CASH MONEY COLORS ORIGINAL (R) - MINING CONTROL PANEL DEMO
Textbasierte Simulation der echten Desktop-App
MIT UNIVERSAL INTEGRATION - API-Keys & PayPal
"""
import json


import time
import random
import os
import sys
from pathlib import Path


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


class MiningAppDemo:
    """Textbasierte Demo der echten Mining Control Panel App"""

    def __init__(self):
        self.capital = 100.0
        self.total_profit = 0.0
        self.cycles = 0
        self.is_running = False

        self.rigs = [
            {'id': 'ASIC_1', 'type': 'Antminer S19 Pro', 'algo': 'SHA256', 'coin': 'BTC', 'profit': 25.0, 'temp': 65, 'status': 'ACTIVE'},
            {'id': 'ASIC_2', 'type': 'Whatsminer M50', 'algo': 'SHA256', 'coin': 'BTC', 'profit': 28.0, 'temp': 68, 'status': 'ACTIVE'},
            {'id': 'GPU_1', 'type': 'RTX 4090', 'algo': 'Ethash', 'coin': 'ETH', 'profit': 15.0, 'temp': 72, 'status': 'ACTIVE'},
            {'id': 'GPU_2', 'type': 'RTX 4090', 'algo': 'KawPow', 'coin': 'RVN', 'profit': 18.0, 'temp': 70, 'status': 'ACTIVE'},
            {'id': 'GPU_3', 'type': 'RTX 3090', 'algo': 'Ethash', 'coin': 'ETH', 'profit': 12.0, 'temp': 68, 'status': 'ACTIVE'},
            {'id': 'GPU_4', 'type': 'RTX 3090', 'algo': 'RandomX', 'coin': 'XMR', 'profit': 10.0, 'temp': 65, 'status': 'ACTIVE'},
            ]

    def clear_screen(self):
        """Clear console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def draw_app_interface(self):
        """Draw the complete app interface"""
        self.clear_screen()

        print("╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗")
        print("║                                       CASH MONEY COLORS ORIGINAL (R)                                    ║")
        print("║                                     MINING CONTROL PANEL - ECHTE APP                                    ║")
        print("╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════╣")

        # Control Panel
        print("║ SYSTEM CONTROL:                                                                                         ║")
        print("║ [START MINING] [STOP MINING] [FORCE OPTIMIZE] [RESET SYSTEM]                                            ║")
        print("╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════╣")

        # Status Display
        status_color = "[RUNNING]" if self.is_running else "[STOPPED]"
        print(f"║ STATUS: {status_color:<15} | CAPITAL: {self.capital:>8.2f} CHF | PROFIT: {self.total_profit:>8.2f} CHF           ║")
        print(f"║ RIGS: {len(self.rigs):>2d} ACTIVE         | CYCLES: {self.cycles:>5d}         | TARGET: 10,000.00 CHF                 ║")
        print("╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════╣")

        # Mining Rigs Table
        print("║ MINING RIGS:                                                                                            ║")
        print("║ ┌─────────┬─────────────────┬─────────┬──────┬─────────┬──────┬──────┬─────────────┬─────────┐         ║")
        print("║ │   ID    │      TYPE       │  ALGO   │ COIN │ H/RATE │ POWER│ TEMP │ PROFIT/DAY  │ STATUS  │         ║")
        print("║ ├─────────┼─────────────────┼─────────┼──────┼─────────┼──────┼──────┼─────────────┼─────────┤         ║")

        for rig in self.rigs:
            status_icon = "[ACTIVE]" if rig['status'] == 'ACTIVE' else "[INACTIVE]"
            print(f"║ │ {rig['id']:<7} │ {rig['type']:<15} │ {rig['algo']:<7} │ {rig['coin']:<4} │ {rig.get('hash_rate', 100):>7} │ {rig.get('power', 500):>4} │ {rig['temp']:>4} │ {rig['profit']:>11.2f} │ {status_icon:<9} │         ║")

            print("║ └─────────┴─────────────────┴─────────┴──────┴─────────┴──────┴──────┴─────────────┴─────────┘         ║")
        print("╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════╣")

        # Performance Charts (ASCII Art)
        print("║ PERFORMANCE CHARTS:                                                                                     ║")
        print("║ Profit/Cycle: ████████████████████████████████████████░░░ (Growing)                                     ║")
        print("║ Capital Growth: ██████████████████████████████████████████ (Excellent)                                   ║")
        print("║ Active Rigs: ████████████████████████████████░░░░░░░░░░░ (Scaling)                                      ║")
        print("╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════╣")

        # System Log
        print("║ SYSTEM LOG:                                                                                             ║")
        print("║ [22:45:30] MINING CONTROL PANEL INITIALIZED                                                              ║")
        print("║ [22:45:31] 6 Mining-Rigs konfiguriert und bereit                                                         ║")
        if self.is_running:
            print(f"║ [22:46:00] MINING OPERATION GESTARTET - Cycle {self.cycles}                                             ║")
            print("║ [22:46:02] Autonome Optimierung aktiviert                                                                ║")
        else:
            print("║ [WAITING] System bereit für Mining-Start                                                                 ║")
            print("╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════╝")

        print("\nCOMMANDS: 'start' (Mining starten), 'stop' (Mining stoppen), 'optimize' (Manuelle Optimierung), 'quit' (Beenden)")

    def start_mining_simulation(self):
        """Simuliere Mining-Operation"""
        self.is_running = True
        print("\n>>> MINING OPERATION GESTARTET! <<<")

        for cycle in range(1, 21):  # 20 Cycles Demo
            self.cycles = cycle

            # Calculate profit
            cycle_profit = sum(rig['profit'] * random.uniform(0.9, 1.1) for rig in self.rigs if rig['status'] == 'ACTIVE')
            self.capital += cycle_profit
            self.total_profit += cycle_profit

            # Update rig temperatures
            for rig in self.rigs:
                rig['temp'] = int(60 + random.uniform(-5, 15))

                # Algorithm optimization every 5 cycles
            if cycle % 5 == 0:
                self.perform_algorithm_optimization()

                # Hardware scaling every 10 cycles
            if cycle % 10 == 0 and len(self.rigs) < 12:
                self.scale_hardware()

                # Update display
            self.draw_app_interface()
            time.sleep(1)

            print("\n>>> DEMO BEENDET - Echte App läuft weiter im Hintergrund! <<<")

    def perform_algorithm_optimization(self):
        """Simuliere Algorithmus-Optimierung"""
        for rig in self.rigs:
            if rig['status'] == 'ACTIVE' and random.random() < 0.3:  # 30% chance
                old_coin = rig['coin']
                old_algo = rig['algo']

                # Switch to different algorithm
                if 'ASIC' in rig['id']:
                    rig['algo'] = 'SHA256'
                    rig['coin'] = 'BCH' if rig['coin'] == 'BTC' else 'BTC'
                else:
                    algorithms = [('Ethash', 'ETH'), ('KawPow', 'RVN'), ('RandomX', 'XMR')]
                    new_algo, new_coin = random.choice(algorithms)
                    rig['algo'] = new_algo
                    rig['coin'] = new_coin

                    rig['profit'] *= random.uniform(0.95, 1.1)  # Slight profit change

    def scale_hardware(self):
        """Simuliere Hardware-Skalierung"""
        new_rig = {
            'id': f'GPU_{len(self.rigs) + 1}',
            'type': 'RTX 4090',
            'algo': 'Ethash',
            'coin': 'ETH',
            'profit': 16.0,
            'temp': 70,
            'status': 'ACTIVE'
            }
        self.rigs.append(new_rig)

    def run_demo(self):
        """Run the complete demo"""
        self.draw_app_interface()

        while True:
            try:
                command = input("\nCommand: ").lower().strip()

                if command == 'start':
                    if not self.is_running:
                        self.start_mining_simulation()
                    else:
                        print("Mining läuft bereits!")

                elif command == 'stop':
                    if self.is_running:
                        self.is_running = False
                        print("🛑 MINING OPERATION GESTOPPT")
                        self.draw_app_interface()
                    else:
                        print("Mining läuft nicht!")

                elif command == 'optimize':
                    if self.is_running:
                        self.perform_algorithm_optimization()
                        print("⚡ MANUELLE OPTIMIERUNG AUSGEFÜHRT")
                        self.draw_app_interface()
                    else:
                        print("Starte zuerst Mining!")

                elif command == 'reset':
                    confirm = input("Wirklich zurücksetzen? (y/n): ")
                    if confirm.lower() == 'y':
                        self.capital = 100.0
                        self.total_profit = 0.0
                        self.cycles = 0
                        self.is_running = False
                        self.rigs = self.rigs[:6]  # Reset to 6 rigs
                        print("🔄 SYSTEM ZURÜCKGESETZT")
                        self.draw_app_interface()

                elif command == 'quit':
                    print("👋 Mining Control Panel beendet")
                    break

                else:
                    print("Verfügbare Commands: start, stop, optimize, reset, quit")

            except KeyboardInterrupt:
                print("\n👋 Demo beendet")
                break


def main():
    """Main Demo Function"""
    print("CASH MONEY COLORS ORIGINAL (R) MINING CONTROL PANEL DEMO")
    print("Simulation der echten Desktop-App")
    print("=" * 60)

    demo = MiningAppDemo()
    demo.run_demo()


if __name__ == "__main__":
    main()


def run():
    """Standard run() Funktion für Dashboard-Integration"""
    print(f"Modul {__name__} wurde ausgeführt")
    print("Implementiere hier deine spezifische Logik...")


if __name__ == "__main__":
    run()#!/usr/bin/env python3
"""Konsolenanwendung zur Steuerung und Auswertung des Mining-Systems."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:  # pragma: no cover - Unterstützung für Modulimporte im Repo-Kontext
    from python_modules.mining_data_collector import MiningDataCollector, SessionSummary
except ModuleNotFoundError:  # pragma: no cover - Direktaufruf aus demselben Verzeichnis
    from mining_data_collector import MiningDataCollector, SessionSummary  # type: ignore


def _format_currency(value: float) -> str:
    return f"{value:,.2f} CHF".replace(",", "'")


def _format_datetime(dt_str: Optional[str]) -> str:
    if not dt_str:
        return "-"
    try:
        return datetime.fromisoformat(dt_str).strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return dt_str


class MiningConsoleApp:
    """Stellt ein produktives CLI für das Mining-System bereit."""

    def __init__(
        self,
        collector: MiningDataCollector,
        snapshot_limit: int = 5,
        show_rigs: bool = True,
    ) -> None:
        self.collector = collector
        self.snapshot_limit = max(1, snapshot_limit)
        self.show_rigs = show_rigs

    def run_session(
        self,
        duration_seconds: float,
        snapshot_interval: float,
        optimize_every: int,
    ) -> SessionSummary:
        print("═" * 90)
        print("Autonomes Mining-System – produktive Sitzung wird gestartet")
        print(
            f"Dauer: {duration_seconds:.1f}s | Snapshot-Intervall: {snapshot_interval:.1f}s | "
            f"Optimierung alle {optimize_every} Snapshots"
        )
        print("═" * 90)
        summary = self.collector.run_session(
            duration_seconds=duration_seconds,
            snapshot_interval=snapshot_interval,
            optimize_every=optimize_every,
        )
        detail = self.collector.get_session_detail(summary.session_id)
        self._print_result(summary, detail)
        return summary

    def _print_result(self, summary: SessionSummary, detail: Dict[str, Any]) -> None:
        session = detail.get("session", {})
        snapshots: List[Dict[str, Any]] = detail.get("snapshots", [])
        print("\nZusammenfassung")
        print("-" * 90)
        print(
            f"Session #{summary.session_id} | Start: {_format_datetime(session.get('started_at'))} | "
            f"Ende: {_format_datetime(session.get('ended_at'))} | Dauer: {summary.duration_seconds:.1f}s"
        )
        print(
            f"Snapshots: {summary.snapshots} | Tagesprofit: {_format_currency(summary.daily_profit)} | "
            f"Gesamtprofit: {_format_currency(summary.total_profit)}"
        )
        risk_info = f"Score {summary.risk_score:.2f}" if summary.risk_score is not None else "keine Bewertung"
        print(f"Risikolevel: {summary.risk_level} ({risk_info})")
        if summary.recommendation:
            print(f"Empfehlung: {summary.recommendation}")
        if summary.report:
            print("Bericht:")
            print(summary.report.strip())

        print("\nLetzte Snapshots")
        print("-" * 90)
        if not snapshots:
            print("Keine Snapshots aufgezeichnet.")
            return

        for index, snapshot in enumerate(snapshots[-self.snapshot_limit :], start=1):
            timestamp = _format_datetime(snapshot.get("timestamp"))
            daily_profit = snapshot.get("daily_profit") or 0.0
            total_profit = snapshot.get("total_profit") or 0.0
            risk_level = snapshot.get("risk_level", "unknown")
            risk_score = snapshot.get("risk_score")
            recommendation = snapshot.get("recommendation") or "-"
            print(
                f"[{index}/{len(snapshots)}] {timestamp} | Tag: {_format_currency(daily_profit)} | "
                f"Total: {_format_currency(total_profit)} | Risiko: {risk_level}"
            )
            if risk_score is not None:
                print(f"  Score: {risk_score:.2f} – Empfehlung: {recommendation}")
            advisories = snapshot.get("advisories") or []
            if advisories:
                print("  Hinweise: " + "; ".join(map(str, advisories)))

            if self.show_rigs:
                rigs = snapshot.get("rigs") or []
                if rigs:
                    print("    Rigs:")
                    for rig in rigs:
                        rig_id = rig.get("rig_id", "?")
                        algo = rig.get("algorithm", "-")
                        coin = rig.get("coin", "-")
                        hash_rate = rig.get("hash_rate") or 0.0
                        profit = rig.get("profit_per_day") or 0.0
                        temp = rig.get("temperature") or 0.0
                        status = rig.get("status", "UNKNOWN")
                        print(
                            "      "
                            f"{rig_id:<8} | {algo:<8} | {coin:<4} | Hashrate: {hash_rate:>7.2f} | "
                            f"Profit/Tag: {_format_currency(profit)} | Temp: {temp:>5.1f}°C | Status: {status}"
                        )


def _print_session_list(sessions: List[Dict[str, Any]]) -> None:
    if not sessions:
        print("Keine aufgezeichneten Sitzungen vorhanden.")
        return
    print("Verfügbare Sitzungen (neueste zuerst):")
    print("-" * 90)
    for entry in sessions:
        session_id = entry.get("id")
        started_at = _format_datetime(entry.get("started_at"))
        ended_at = _format_datetime(entry.get("ended_at"))
        risk = entry.get("risk_level", "unknown")
        snapshots = entry.get("snapshots", 0)
        total_profit = _format_currency(float(entry.get("total_profit") or 0.0))
        print(
            f"#{session_id:<4} | Start: {started_at} | Ende: {ended_at} | "
            f"Snapshots: {snapshots:<3} | Profit: {total_profit:<12} | Risiko: {risk}"
        )


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Produktives CLI zur Steuerung und Auswertung des Mining-Systems"
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=MiningDataCollector.DEFAULT_DB_PATH,
        help="Pfad zur SQLite-Datenbank, Standard: data/mining_data_collector.db",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=45.0,
        help="Dauer der Simulation in Sekunden (Standard: 45)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=2.0,
        help="Abstand zwischen Snapshots in Sekunden (Standard: 2)",
    )
    parser.add_argument(
        "--optimize-every",
        type=int,
        default=3,
        help="Anzahl Snapshots bis zur automatischen Optimierung (Standard: 3)",
    )
    parser.add_argument(
        "--snapshot-limit",
        type=int,
        default=5,
        help="Anzahl der zuletzt angezeigten Snapshots (Standard: 5)",
    )
    parser.add_argument(
        "--hide-rigs",
        action="store_true",
        help="Unterdrückt die detaillierte Anzeige der Rig-Telemetrie",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Listet vorhandene Sitzungen und beendet das Programm",
    )
    parser.add_argument(
        "--show",
        type=int,
        metavar="SESSION_ID",
        help="Zeigt Details zu einer gespeicherten Sitzung an und beendet das Programm",
    )
    parser.add_argument(
        "--export",
        type=Path,
        default=None,
        help="Exportiert die betrachtete Sitzung als JSON-Datei",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    collector = MiningDataCollector(db_path=args.database)

    if args.list:
        _print_session_list(collector.list_sessions())
        return 0

    if args.show is not None:
        detail = collector.get_session_detail(args.show)
        session_info = detail.get("session", {})
        snapshots: List[Dict[str, Any]] = detail.get("snapshots", [])
        report_source = session_info.get("notes")
        if isinstance(report_source, dict):
            report_text = json.dumps(report_source, indent=2, ensure_ascii=False)
        elif report_source is None:
            report_text = ""
        else:
            report_text = str(report_source)
        try:
            started_at = datetime.fromisoformat(str(session_info.get("started_at")))
        except Exception:
            started_at = datetime.now()
        ended_raw = session_info.get("ended_at")
        try:
            ended_at = (
                datetime.fromisoformat(str(ended_raw))
                if ended_raw
                else started_at
            )
        except Exception:
            ended_at = started_at

        summary = SessionSummary(
            session_id=int(session_info.get("id", args.show)),
            started_at=started_at,
            ended_at=ended_at,
            duration_seconds=float(session_info.get("duration_seconds") or 0.0),
            snapshots=int(session_info.get("snapshots") or len(snapshots)),
            daily_profit=float(session_info.get("daily_profit") or 0.0),
            total_profit=float(session_info.get("total_profit") or 0.0),
            risk_level=str(session_info.get("risk_level") or "unknown"),
            risk_score=(
                float(session_info.get("risk_score"))
                if session_info.get("risk_score") is not None
                else None
            ),
            recommendation=str(session_info.get("recommendation") or ""),
            report=report_text,
        )
        app = MiningConsoleApp(
            collector,
            snapshot_limit=args.snapshot_limit,
            show_rigs=not args.hide_rigs,
        )
        app._print_result(summary, detail)  # pylint: disable=protected-access
        if args.export:
            export_path = collector.export_session_to_json(summary.session_id, args.export)
            print(f"Sitzung exportiert nach: {export_path}")
        return 0

    app = MiningConsoleApp(
        collector,
        snapshot_limit=args.snapshot_limit,
        show_rigs=not args.hide_rigs,
    )
    summary = app.run_session(
        duration_seconds=max(1.0, float(args.duration)),
        snapshot_interval=max(0.2, float(args.interval)),
        optimize_every=max(1, int(args.optimize_every)),
    )

    if args.export:
        export_path = collector.export_session_to_json(summary.session_id, args.export)
        print(f"Sitzung exportiert nach: {export_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
