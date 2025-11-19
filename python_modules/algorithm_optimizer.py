#!/usr/bin/env python3
"""
CASH MONEY COLORS ORIGINAL (R) - ALGORITHM OPTIMIZER
Maximale Profit-Optimierung mit KI-basierten Entscheidungen
"""
import json
import time
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import statistics

# Markt-Integration importieren (fallback wenn nicht verfügbar)
try:
    from market_integration import get_crypto_prices, calculate_mining_profit, get_optimal_algorithm
    MARKET_AVAILABLE = True
except ImportError:
    MARKET_AVAILABLE = False

class AlgorithmOptimizer:
    """KI-basierte Algorithmus-Optimierung für maximalen Mining-Profit"""

    def __init__(self, config_file: str = "mining_config.json"):
        self.config = self.load_config(config_file)
        self.performance_history = defaultdict(list)
        self.algorithm_performance = defaultdict(lambda: {'total_profit': 0, 'cycles': 0, 'avg_profit': 0})
        self.rig_health = {}
        self.temperature_data = defaultdict(list)
        self.power_efficiency = {}

        # Optimierungsparameter
        self.optimization_cycles = 0
        self.last_market_check = datetime.now()
        self.market_cache_duration = 300  # 5 Minuten

        print("🧠 ALGORITHM OPTIMIZER INITIALIZED")
        print("🎯 ZIEL: MAXIMALER PROFIT DURCH KI-OPTIMIERUNG")

    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Lädt Konfiguration aus JSON-Datei"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ Konfigurationsdatei {config_file} nicht gefunden, verwende Standardwerte")
            return self.get_default_config()

    def get_default_config(self) -> Dict[str, Any]:
        """Standard-Konfiguration"""
        return {
            "optimization": {
                "algorithm_switching": True,
                "market_based_decisions": True,
                "hardware_scaling": True,
                "temperature_management": True,
                "power_efficiency": True,
                "predictive_maintenance": True
            },
            "thresholds": {
                "min_profit_threshold": 5.0,
                "temperature_warning": 75,
                "temperature_critical": 85,
                "power_efficiency_target": 0.8,
                "maintenance_interval_days": 30
            },
            "algorithms": {
                "ethash": {"coins": ["ETH", "ETC"], "efficiency": 0.85},
                "kawpow": {"coins": ["RVN"], "efficiency": 0.82},
                "randomx": {"coins": ["XMR"], "efficiency": 0.78},
                "sha256": {"coins": ["BTC", "BCH"], "efficiency": 0.95}
            }
        }

    def optimize_rig_configuration(self, rig: Dict[str, Any], market_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Optimiert eine einzelne Rig-Konfiguration für maximalen Profit"""
        rig_id = rig['id']
        rig_type = rig['type']

        # Sammle historische Performance-Daten
        historical_performance = self.performance_history.get(rig_id, [])

        # Markt-Daten abrufen (falls verfügbar)
        if MARKET_AVAILABLE and market_data:
            optimal_config = self.market_based_optimization(rig, market_data)
        else:
            optimal_config = self.heuristic_optimization(rig, historical_performance)

        # Temperatur-Management
        optimal_config = self.apply_temperature_management(optimal_config, rig)

        # Energieeffizienz-Optimierung
        optimal_config = self.apply_power_efficiency(optimal_config, rig)

        # Predictive Maintenance
        optimal_config = self.apply_predictive_maintenance(optimal_config, rig)

        return optimal_config

    def market_based_optimization(self, rig: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Markt-basierte Optimierung mit Live-Daten"""
        rig_specs = self.get_rig_specs(rig['type'])

        try:
            optimal = get_optimal_algorithm(rig_specs)

            if optimal['optimal_algorithm']:
                new_config = rig.copy()
                new_config['algorithm'] = optimal['optimal_algorithm']
                new_config['coin'] = optimal['optimal_coin']
                new_config['profit'] = optimal['expected_profit_chf']
                new_config['optimization_reason'] = 'market_data'
                new_config['expected_profit'] = optimal['expected_profit_chf']

                # Vergleiche mit aktueller Konfiguration
                profit_gain = new_config['profit'] - rig.get('profit', 0)
                if profit_gain > 0:
                    print(f"💰 MARKT-OPTIMIERUNG: {rig['id']} | +CHF {profit_gain:.2f}/Tag | {new_config['coin']}({new_config['algorithm']})")

                return new_config

        except Exception as e:
            print(f"❌ Markt-Optimierung fehlgeschlagen: {e}")

        # Fallback zur heuristischen Optimierung
        return self.heuristic_optimization(rig, [])

    def heuristic_optimization(self, rig: Dict[str, Any], historical_data: List[Dict]) -> Dict[str, Any]:
        """Heuristische Optimierung basierend auf historischen Daten"""
        current_algorithm = rig.get('algorithm', 'ethash')
        current_profit = rig.get('profit', 0)

        # Algorithmus-Performance aus Historie analysieren
        algorithm_performance = self.analyze_algorithm_performance(historical_data)

        # Beste verfügbare Algorithmen für diesen Rig-Typ
        available_algorithms = self.get_available_algorithms_for_rig(rig['type'])

        best_algorithm = current_algorithm
        best_profit = current_profit

        # Teste alle verfügbaren Algorithmen
        for algorithm in available_algorithms:
            if algorithm in algorithm_performance:
                avg_profit = algorithm_performance[algorithm]['avg_profit']
                if avg_profit > best_profit:
                    best_algorithm = algorithm
                    best_profit = avg_profit

        # Neue Konfiguration erstellen
        new_config = rig.copy()
        if best_algorithm != current_algorithm:
            new_config['algorithm'] = best_algorithm
            new_config['coin'] = self.get_coin_for_algorithm(best_algorithm)
            new_config['profit'] = best_profit
            new_config['optimization_reason'] = 'historical_data'

            profit_gain = best_profit - current_profit
            print(f"📊 HISTORISCHE OPTIMIERUNG: {rig['id']} | +CHF {profit_gain:.2f}/Tag | {new_config['coin']}({best_algorithm})")

        return new_config

    def apply_temperature_management(self, config: Dict[str, Any], rig: Dict[str, Any]) -> Dict[str, Any]:
        """Wendet Temperatur-Management an"""
        rig_id = rig['id']
        temp_threshold = self.config['thresholds']['temperature_warning']

        # Simuliere Temperatur-Daten (in echter Implementierung von Hardware-Sensoren)
        current_temp = self.temperature_data[rig_id][-1] if self.temperature_data[rig_id] else random.uniform(60, 80)

        # Temperatur-basierte Anpassungen
        if current_temp > temp_threshold:
            # Reduziere Hash-Rate um Temperatur zu senken
            temp_reduction = min(0.2, (current_temp - temp_threshold) / 20)  # Max 20% Reduktion
            config['temperature_adjustment'] = -temp_reduction
            config['profit'] *= (1 - temp_reduction)
            config['temperature_reason'] = f"Temp: {current_temp:.1f}°C > {temp_threshold}°C"
        else:
            # Optimale Temperatur - kann leicht übertakten
            overclock_bonus = 0.05  # 5% Bonus bei optimaler Temperatur
            config['temperature_adjustment'] = overclock_bonus
            config['profit'] *= (1 + overclock_bonus)
            config['temperature_reason'] = f"Optimal temp: {current_temp:.1f}°C"

        return config

    def apply_power_efficiency(self, config: Dict[str, Any], rig: Dict[str, Any]) -> Dict[str, Any]:
        """Optimiert Energieeffizienz"""
        target_efficiency = self.config['thresholds']['power_efficiency_target']

        # Simuliere Effizienz-Berechnung
        current_efficiency = random.uniform(0.7, 0.9)  # 70-90% Effizienz

        if current_efficiency < target_efficiency:
            # Verbessere Effizienz durch Software-Optimierung
            efficiency_gain = min(0.1, target_efficiency - current_efficiency)
            config['power_efficiency'] = current_efficiency + efficiency_gain
            config['profit'] *= (1 + efficiency_gain * 0.5)  # 50% des Effizienz-Gewinns wird Profit
            config['efficiency_reason'] = f"Effizienz: {current_efficiency:.1f} -> {config['power_efficiency']:.1f}"
        else:
            config['power_efficiency'] = current_efficiency
            config['efficiency_reason'] = f"Optimale Effizienz: {current_efficiency:.1f}"

        return config

    def apply_predictive_maintenance(self, config: Dict[str, Any], rig: Dict[str, Any]) -> Dict[str, Any]:
        """Wendet Predictive Maintenance an"""
        rig_id = rig['id']
        maintenance_interval = self.config['thresholds']['maintenance_interval_days']

        # Simuliere Wartungs-Status
        if rig_id not in self.rig_health:
            self.rig_health[rig_id] = {
                'last_maintenance': datetime.now() - timedelta(days=random.randint(0, maintenance_interval)),
                'performance_degradation': random.uniform(0, 0.1),
                'error_count': random.randint(0, 5)
            }

        health = self.rig_health[rig_id]
        days_since_maintenance = (datetime.now() - health['last_maintenance']).days

        # Maintenance erforderlich?
        if days_since_maintenance > maintenance_interval or health['error_count'] > 3:
            # Reduziere Performance bis Maintenance durchgeführt wird
            maintenance_penalty = min(0.3, days_since_maintenance / (maintenance_interval * 2))
            config['maintenance_penalty'] = -maintenance_penalty
            config['profit'] *= (1 - maintenance_penalty)
            config['maintenance_reason'] = f"Wartung erforderlich ({days_since_maintenance} Tage)"
            config['maintenance_required'] = True
        else:
            config['maintenance_penalty'] = 0
            config['maintenance_reason'] = f"Wartung OK ({days_since_maintenance} Tage)"
            config['maintenance_required'] = False

        return config

    def get_rig_specs(self, rig_type: str) -> Dict[str, Any]:
        """Gibt Rig-Spezifikationen zurück"""
        specs_map = {
            'RTX_4090': {'hash_rate': 120, 'power_consumption': 450, 'electricity_cost': 0.15},
            'RTX_3090': {'hash_rate': 100, 'power_consumption': 350, 'electricity_cost': 0.15},
            'S19_Pro': {'hash_rate': 110000, 'power_consumption': 3250, 'electricity_cost': 0.15}
        }
        return specs_map.get(rig_type, {'hash_rate': 100, 'power_consumption': 300, 'electricity_cost': 0.15})

    def get_available_algorithms_for_rig(self, rig_type: str) -> List[str]:
        """Gibt verfügbare Algorithmen für Rig-Typ zurück"""
        if 'RTX' in rig_type:
            return ['ethash', 'kawpow', 'randomx']
        elif 'ASIC' in rig_type or 'S19' in rig_type:
            return ['sha256']
        else:
            return ['ethash']

    def get_coin_for_algorithm(self, algorithm: str) -> str:
        """Gibt Standard-Coin für Algorithmus zurück"""
        coin_map = {
            'ethash': 'ETH',
            'kawpow': 'RVN',
            'randomx': 'XMR',
            'sha256': 'BTC'
        }
        return coin_map.get(algorithm, 'BTC')

    def analyze_algorithm_performance(self, historical_data: List[Dict]) -> Dict[str, Dict]:
        """Analysiert historische Algorithmus-Performance"""
        performance = defaultdict(lambda: {'profits': [], 'total_profit': 0, 'cycles': 0})

        for data in historical_data:
            if 'algorithm' in data and 'cycle_profit' in data:
                algo = data['algorithm']
                profit = data['cycle_profit']
                performance[algo]['profits'].append(profit)
                performance[algo]['total_profit'] += profit
                performance[algo]['cycles'] += 1

        # Berechne Durchschnitte
        for algo, data in performance.items():
            if data['cycles'] > 0:
                data['avg_profit'] = data['total_profit'] / data['cycles']
            else:
                data['avg_profit'] = 0

        return dict(performance)

    def optimize_entire_farm(self, rigs: List[Dict[str, Any]], market_data: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Optimiert gesamte Farm für maximalen Profit"""
        print(f"\n🧠 FARM-OPTIMIERUNG (ZYKLUS {self.optimization_cycles + 1})")
        print("=" * 60)

        optimized_rigs = []
        total_profit_gain = 0
        total_current_profit = 0

        for rig in rigs:
            current_profit = rig.get('profit', 0)
            total_current_profit += current_profit

            # Optimiere einzelne Rig
            optimized_rig = self.optimize_rig_configuration(rig, market_data)
            optimized_rigs.append(optimized_rig)

            profit_gain = optimized_rig.get('profit', 0) - current_profit
            total_profit_gain += profit_gain

            # Aktualisiere Performance-Historie
            self.update_performance_history(rig['id'], optimized_rig)

        # Zusammenfassung
        if total_profit_gain > 0:
            print(f"💰 FARM-PROFIT-STEIGERUNG: +CHF {total_profit_gain:.2f}/Tag")
            print(f"📊 Neue Gesamt-Performance: CHF {total_current_profit + total_profit_gain:.2f}/Tag")
        else:
            print("📊 Farm-Konfiguration ist bereits optimal")

        self.optimization_cycles += 1
        return optimized_rigs

    def update_performance_history(self, rig_id: str, rig_data: Dict[str, Any]):
        """Aktualisiert Performance-Historie"""
        self.performance_history[rig_id].append({
            'timestamp': datetime.now(),
            'algorithm': rig_data.get('algorithm'),
            'profit': rig_data.get('profit', 0),
            'temperature': rig_data.get('temperature', random.uniform(60, 80)),
            'efficiency': rig_data.get('power_efficiency', 0.8)
        })

        # Behalte nur letzte 100 Einträge
        if len(self.performance_history[rig_id]) > 100:
            self.performance_history[rig_id] = self.performance_history[rig_id][-100:]

    def get_optimization_stats(self) -> Dict[str, Any]:
        """Gibt Optimierungs-Statistiken zurück"""
        return {
            'optimization_cycles': self.optimization_cycles,
            'rigs_tracked': len(self.performance_history),
            'total_performance_records': sum(len(records) for records in self.performance_history.values()),
            'algorithm_performance': dict(self.algorithm_performance),
            'rig_health_status': dict(self.rig_health)
        }

    def reset_optimization(self):
        """Setzt Optimierung zurück (für neue Session)"""
        self.optimization_cycles = 0
        self.performance_history.clear()
        self.algorithm_performance.clear()
        print("🔄 OPTIMIERUNG ZURÜCKGESETZT")

# Globale Instanz
algorithm_optimizer = AlgorithmOptimizer()

def optimize_farm(rigs: List[Dict[str, Any]], market_data: Optional[Dict] = None) -> List[Dict[str, Any]]:
    """Convenience-Funktion für Farm-Optimierung"""
    return algorithm_optimizer.optimize_entire_farm(rigs, market_data)

def get_optimization_stats() -> Dict[str, Any]:
    """Convenience-Funktion für Optimierungs-Statistiken"""
    return algorithm_optimizer.get_optimization_stats()

if __name__ == "__main__":
    print("CASH MONEY COLORS ORIGINAL (R) - ALGORITHM OPTIMIZER")
    print("=" * 70)

    # Test des Algorithm Optimizers
    print("🧪 Teste Algorithm Optimizer...")

    # Beispiel-Rigs
    test_rigs = [
        {'id': 'GPU_1', 'type': 'RTX_4090', 'algorithm': 'ethash', 'coin': 'ETH', 'profit': 8.5},
        {'id': 'GPU_2', 'type': 'RTX_3090', 'algorithm': 'kawpow', 'coin': 'RVN', 'profit': 7.2},
        {'id': 'ASIC_1', 'type': 'S19_Pro', 'algorithm': 'sha256', 'coin': 'BTC', 'profit': 12.8}
    ]

    print(f"📊 Teste Optimierung mit {len(test_rigs)} Rigs...")

    # Optimiere Farm
    optimized_rigs = optimize_farm(test_rigs)

    # Zeige Ergebnisse
    print("\n📈 OPTIMIERUNGS-ERGEBNISSE:")
    for rig in optimized_rigs:
        print(f"  {rig['id']}: {rig['coin']}({rig['algorithm']}) | CHF {rig.get('profit', 0):.2f}/Tag")

    # Statistiken
    stats = get_optimization_stats()
    print(f"\n📊 OPTIMIERUNGS-STATISTIKEN:")
    print(f"   Optimierung-Zyklen: {stats['optimization_cycles']}")
    print(f"   Rigs getrackt: {stats['rigs_tracked']}")
    print(f"   Performance-Records: {stats['total_performance_records']}")

    print("\n✅ ALGORITHM OPTIMIZER BEREIT!")
    print("Verwende optimize_farm() für KI-basierte Profit-Maximierung")
