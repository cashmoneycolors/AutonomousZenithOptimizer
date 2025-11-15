#!/usr/bin/env python3
"""
CASH MONEY COLORS ORIGINAL (R) - DYNAMIC ALGORITHM SWITCHER
Marktbasierte intelligente Algorithmus-Wechsel für maximale Profite
"""
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import threading
from python_modules.config_manager import get_config, get_rigs_config
from python_modules.market_integration import get_crypto_prices, calculate_mining_profit
from python_modules.nicehash_integration import get_pool_stats, calculate_profit_comparison
from python_modules.alert_system import send_custom_alert
from python_modules.enhanced_logging import log_event

class AlgorithmSwitcher:
    """Intelligenter Algorithmus-Wechsler für optimale Profite"""

    def __init__(self):
        self.switch_config = get_config('AlgorithmSwitch', {})
        self.monitoring_active = False
        self.switch_history = []
        self.performance_history = {}
        self.current_algorithm = "ethash"
        self.best_algorithm = "ethash"

        # Default-Konfiguration
        if not self.switch_config:
            self.switch_config = {
                'Enabled': True,
                'SwitchThreshold': 15.0,  # 15% besser = wechseln
                'MinSwitchIntervalMinutes': 60,  # Nicht öfter als alle Stunde
                'AnalysisWindowHours': 24,  # 24h historische Daten
                'RiskTolerance': 'medium',  # conservative/medium/aggressive
                'VolatilityMultiplier': 1.0,  # Marktrisiko-Anpassung
                'PoolBias': 0.9  # Bevorzuge Pool-Mining um 10%
            }

        # Algorithmus-Mapping
        self.algorithms = {
            'ethash': {'coins': ['ETH', 'ETC'], 'difficulty_multiplier': 1.0},
            'kawpow': {'coins': ['RVN'], 'difficulty_multiplier': 0.8},
            'randomx': {'coins': ['XMR'], 'difficulty_multiplier': 0.6},
            'autolykos': {'coins': ['ERG'], 'difficulty_multiplier': 0.7},
            'octopus': {'coins': ['CFX'], 'difficulty_multiplier': 0.9},
            'kheavyhash': {'coins': ['KAS'], 'difficulty_multiplier': 0.5},
            'sha256': {'coins': ['BTC', 'BCH'], 'difficulty_multiplier': 1.2}
        }

        print("🧠 ALGORITHM SWITCHER INITIALIZED")
        print(f"   Switching Enabled: {self.switch_config.get('Enabled', True)}")
        print(f"   Risk Tolerance: {self.switch_config.get('RiskTolerance', 'medium')}")

    def start_algorithm_monitoring(self):
        """Startet kontinuierliches Algorithmus-Monitoring"""
        if self.monitoring_active or not self.switch_config.get('Enabled', True):
            return

        self.monitoring_active = True
        monitor_thread = threading.Thread(target=self._algorithm_monitor_loop, daemon=True)
        monitor_thread.start()

        print("🔄 Algorithm Monitoring gestartet")

    def stop_algorithm_monitoring(self):
        """Stoppt Algorithmus-Monitoring"""
        self.monitoring_active = False
        print("⏹️ Algorithm Monitoring gestoppt")

    def analyze_algorithm_performance(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Analysiert Performance aller Algorithmen über Zeitfenster"""
        market_data = get_crypto_prices()
        pool_stats = get_pool_stats()
        rigs = get_rigs_config()

        analysis_results = {}
        total_rigs_power = sum(rig.get('power_consumption', 0) for rig in rigs)

        for algo_name, algo_config in self.algorithms.items():
            if algo_name not in pool_stats:
                continue

            # Hole Pool-Statistiken
            pool_data = pool_stats.get(algo_name, {})
            nh_paying = pool_data.get('paying_usd', 0)

            # Lokale Berechnung (vereinfacht für Alle Rigs)
            rig_count = len(rigs)
            avg_power_per_rig = total_rigs_power / max(rig_count, 1)
            estimated_local_profit = rig_count * nh_paying * 100  # Rough estimate

            # Markt-Volatilität für Risiko-Bewertung
            coin_volatility = 0
            coin_count = 0

            for coin in algo_config['coins']:
                if coin in market_data:
                    coin_count += 1
                    coin_volatility += abs(market_data[coin].get('change_24h', 0))

            avg_volatility = coin_volatility / max(coin_count, 1)

            # Risiko-Adjustierung
            risk_factor = self._calculate_risk_factor(avg_volatility, algo_config['difficulty_multiplier'])

            # Endgültige Bewertung
            adjusted_profit = estimated_local_profit * risk_factor
            pool_bias = self.switch_config.get('PoolBias', 1.0)
            final_score = adjusted_profit * pool_bias

            analysis_results[algo_name] = {
                'algorithm': algo_name,
                'pool_profit_per_day': nh_paying,
                'estimated_local_profit': estimated_local_profit,
                'adjusted_profit': adjusted_profit,
                'final_score': final_score,
                'volatility': avg_volatility,
                'difficulty_multiplier': algo_config['difficulty_multiplier'],
                'risk_factor': risk_factor,
                'supported_coins': algo_config['coins'],
                'timestamp': datetime.now().isoformat()
            }

        return analysis_results

    def get_optimal_algorithm(self) -> Tuple[str, Dict[str, Any]]:
        """Findet den optimalen Algorithmus für aktuelle Marktbedingungen"""
        performance_analysis = self.analyze_algorithm_performance()

        if not performance_analysis:
            return self.current_algorithm, {'error': 'Keine Analyse-Daten verfügbar'}

        # Sortiere nach final_score (höchster zuerst)
        sorted_algos = sorted(
            performance_analysis.items(),
            key=lambda x: x[1]['final_score'],
            reverse=True
        )

        best_algorithm = sorted_algos[0][0]
        best_data = sorted_algos[0][1]

        # Überprüfe Switch-Threshold
        current_algo_data = performance_analysis.get(self.current_algorithm, {})
        current_score = current_algo_data.get('final_score', 0)

        switch_threshold = self.switch_config.get('SwitchThreshold', 15.0) / 100.0
        improvement_percentage = ((best_data['final_score'] - current_score) / max(current_score, 0.01)) * 100

        # Prüfe Zeit seit letztem Switch
        can_switch = self._can_switch_algorithm(best_algorithm, improvement_percentage)

        recommendation = {
            'recommended_algorithm': best_algorithm,
            'current_algorithm': self.current_algorithm,
            'improvement_percentage': improvement_percentage,
            'can_switch': can_switch,
            'switch_threshold': switch_threshold * 100,
            'time_until_next_switch': self._get_time_until_next_switch_minutes(),
            'analysis_data': best_data,
            'all_algorithms': sorted_algos[:5]  # Top 5 zeigen
        }

        return best_algorithm if can_switch else self.current_algorithm, recommendation

    def switch_to_best_algorithm(self) -> Dict[str, Any]:
        """Führt Algorithmus-Wechsel zur besten Option durch"""
        optimal_algo, recommendation = self.get_optimal_algorithm()

        if not recommendation.get('can_switch', False):
            return {
                'switched': False,
                'reason': 'Switch nicht möglich (Threshold/Zeit)',
                'recommendation': recommendation
            }

        if optimal_algo == self.current_algorithm:
            return {
                'switched': False,
                'reason': 'Bereits optimaler Algorithmus',
                'recommendation': recommendation
            }

        # Führe Switch durch
        result = self._execute_algorithm_switch(optimal_algo, recommendation)

        if result['success']:
            self.current_algorithm = optimal_algo
            self.best_algorithm = optimal_algo

            # Logge Switch
            switch_event = {
                'from_algorithm': recommendation['current_algorithm'],
                'to_algorithm': optimal_algo,
                'improvement': recommendation['improvement_percentage'],
                'timestamp': datetime.now().isoformat(),
                'reason': 'market_optimization'
            }
            self.switch_history.append(switch_event)

            # Alert
            send_custom_alert("Algorithmus Switch",
                            f"Automatischer Switch: {recommendation['current_algorithm']} → {optimal_algo} (+{recommendation['improvement_percentage']:.1f}%)",
                            "🧠")

            log_event('ALGORITHM_SWITCH', switch_event)

        return result

    def _algorithm_monitor_loop(self):
        """Hauptschleife für Algorithmus-Monitoring"""
        check_interval = self.switch_config.get('AnalysisWindowHours', 24) * 3600 / 24  # Alle 1 Stunde

        while self.monitoring_active:
            try:
                # Automatischer Switch prüfen
                self.switch_to_best_algorithm()

                time.sleep(check_interval)

            except Exception as e:
                print(f"Algorithm Monitor Fehler: {e}")
                send_custom_alert("Algorithm Monitor Error", f"Fehler im Algorithmus-Monitoring: {e}")
                time.sleep(300)  # 5 Minuten warten bei Fehler

    def _calculate_risk_factor(self, volatility: float, difficulty_multiplier: float) -> float:
        """Berechnet Risiko-Faktor basierend auf Marktbedingungen"""
        risk_tolerance = self.switch_config.get('RiskTolerance', 'medium')

        risk_factors = {
            'conservative': 0.7,
            'medium': 1.0,
            'aggressive': 1.3
        }

        base_risk = risk_factors.get(risk_tolerance, 1.0)

        # Volatilitäts-Adjustment
        volatility_multiplier = self.switch_config.get('VolatilityMultiplier', 1.0)
        if volatility > 20:
            base_risk *= (1.0 - volatility_multiplier * 0.2)
        elif volatility < 5:
            base_risk *= (1.0 + volatility_multiplier * 0.1)

        # Difficulty Adjustment
        base_risk *= difficulty_multiplier

        return max(0.1, min(2.0, base_risk))  # Clamp zwischen 0.1 und 2.0

    def _can_switch_algorithm(self, new_algorithm: str, improvement_percentage: float) -> bool:
        """Prüft ob Algorithmus gewechselt werden kann"""
        if improvement_percentage < self.switch_config.get('SwitchThreshold', 15.0):
            return False

        # Zeit seit letztem Switch prüfen
        min_interval_minutes = self.switch_config.get('MinSwitchIntervalMinutes', 60)

        if self.switch_history:
            last_switch = self.switch_history[-1]
            last_switch_time = datetime.fromisoformat(last_switch['timestamp'])
            time_since_last_switch = (datetime.now() - last_switch_time).total_seconds() / 60

            if time_since_last_switch < min_interval_minutes:
                return False

        return True

    def _get_time_until_next_switch_minutes(self) -> int:
        """Berechnet Minuten bis nächsten möglichen Switch"""
        min_interval_minutes = self.switch_config.get('MinSwitchIntervalMinutes', 60)

        if not self.switch_history:
            return 0

        last_switch_time = datetime.fromisoformat(self.switch_history[-1]['timestamp'])
        time_since_last_switch = (datetime.now() - last_switch_time).total_seconds() / 60

        return max(0, int(min_interval_minutes - time_since_last_switch))

    def _execute_algorithm_switch(self, new_algorithm: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Führt Algorithmus-Wechsel durch"""
        try:
            # Hier würde die eigentliche Hardware-Konfiguration erfolgen
            # Für Mining-Rigs: GPU-Treiber neu laden, Pool-URLs ändern, etc.

            # Simuliert Switch-Delay
            time.sleep(2)

            return {
                'success': True,
                'message': f'Algorithmus gewechselt zu {new_algorithm}',
                'analysis': analysis_data
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Switch-Fehler: {e}',
                'error': str(e)
            }

    def get_algorithm_analytics(self) -> Dict[str, Any]:
        """Gibt Algorithmus-Analytics zurück"""
        return {
            'current_algorithm': self.current_algorithm,
            'best_algorithm': self.best_algorithm,
            'total_switches': len(self.switch_history),
            'last_switch': self.switch_history[-1] if self.switch_history else None,
            'monitoring_active': self.monitoring_active,
            'analysis_window_hours': self.switch_config.get('AnalysisWindowHours', 24),
            'risk_tolerance': self.switch_config.get('RiskTolerance', 'medium'),
            'performance_data': self.analyze_algorithm_performance()
        }

# Globale Algorithmus-Switcher Instanz
algorithm_switcher = AlgorithmSwitcher()

# Convenience-Funktionen
def start_algorithm_monitoring():
    """Startet Algorithmus-Monitoring"""
    algorithm_switcher.start_algorithm_monitoring()

def stop_algorithm_monitoring():
    """Stoppt Algorithmus-Monitoring"""
    algorithm_switcher.stop_algorithm_monitoring()

def analyze_algorithms():
    """Analysiert alle Algorithmen"""
    return algorithm_switcher.analyze_algorithm_performance()

def switch_to_best_algorithm():
    """Wechselt zu bestem Algorithmus"""
    return algorithm_switcher.switch_to_best_algorithm()

def get_algorithm_analytics():
    """Holt Analytics-Daten"""
    return algorithm_switcher.get_algorithm_analytics()

if __name__ == "__main__":
    print("CASH MONEY COLORS ORIGINAL (R) - ALGORITHM SWITCHER")
    print("=" * 60)

    print("🧪 Teste Algorithm Switcher...")

    # Performance-Analyse
    analysis = analyze_algorithms()
    print(f"✅ {len(analysis)} Algorithmen analysiert")

    if analysis:
        # Sortiere nach Score
        sorted_algos = sorted(analysis.items(), key=lambda x: x[1]['final_score'], reverse=True)
        best_algo = sorted_algos[0]

        print(f"\n🏆 Bester Algorithmus: {best_algo[0].upper()}")
        print(f"   Pool Profit/Day: ${best_algo[1]['pool_profit_per_day']:.4f}")
        print(f"   Geschätzter Profit: ${best_algo[1]['adjusted_profit']:.2f}")
        print(f"   Risiko-Faktor: {best_algo[1]['risk_factor']:.1f}")

        # Test Switch (ohne echte Ausführung)
        optimal, rec = algorithm_switcher.get_optimal_algorithm()
        if rec.get('can_switch'):
            print(f"\n🔄 Switch möglich zu: {optimal.upper()}")
            print(f"   Verbesserung: {rec['improvement_percentage']:.1f}%")
        else:
            reason = "Threshold nicht erreicht" if rec['improvement_percentage'] < rec['switch_threshold'] else "Zeit-Intervall aktiv"
            print(f"Not Switch verfügbar")
            print(f"Grund: {reason}")

    print("\n✅ ALGORITHM SWITCHER BEREIT!")
    print("Verwende start_algorithm_monitoring() für kontinuierliche Optimierung")
    print(f"   Aktueller Algorithmus: {algorithm_switcher.current_algorithm.upper()}")
    print(f"   Risiko-Toleranz: {algorithm_switcher.switch_config.get('RiskTolerance', 'medium')}")
