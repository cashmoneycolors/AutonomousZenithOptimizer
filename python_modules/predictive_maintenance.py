#!/usr/bin/env python3
"""
CASH MONEY COLORS ORIGINAL (R) - PREDICTIVE MAINTENANCE
KI-basierte Vorhersage von Hardware-Problemen bei Mining-Rigs
"""
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import threading
import statistics
import math
try:
    from python_modules.config_manager import get_config, get_rigs_config
    from python_modules.alert_system import send_system_alert, send_custom_alert
    from python_modules.enhanced_logging import log_event
    from python_modules.energy_efficiency import evaluate_rig_efficiency
    from python_modules.temperature_optimizer import optimize_rig_temperature, get_thermal_efficiency_report
except ModuleNotFoundError:
    # Direktimport wenn als Standalone ausgeführt
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from python_modules.config_manager import get_config, get_rigs_config
    from alert_system import send_system_alert, send_custom_alert
    from enhanced_logging import log_event

class PredictiveMaintenance:
    """Predictive Maintenance für Mining-Hardware"""

    def __init__(self):
        self.maintenance_config = get_config('PredictiveMaintenance', {})
        self.monitoring_active = False
        self.historical_data = {}
        self.failure_patterns = {}
        self.prediction_models = {}

        # Default-Konfiguration
        if not self.maintenance_config:
            self.maintenance_config = {
                'Enabled': True,
                'MonitorIntervalMinutes': 30,
                'PredictionThresholdHours': 168,  # 7 Tage im Voraus warnen
                'TemperatureThreshold': 80.0,
                'HashrateDropThreshold': 10.0,  # 10% Drop = Warning
                'HistoricalDataDays': 30,
                'AutoMaintenanceScheduling': True
            }

        self.temperature_data = {}
        self.hashrate_data = {}
        self.power_data = {}
        self.error_counts = {}

        print("PREDICTIVE MAINTENANCE INITIALIZED")
        print(f"   Monitoring Enabled: {self.maintenance_config.get('Enabled', True)}")
        print(f"   Prediction Horizon: {self.maintenance_config.get('PredictionThresholdHours', 168)} hours")

    def start_predictive_monitoring(self):
        """Startet Predictive Maintenance Monitoring"""
        if self.monitoring_active or not self.maintenance_config.get('Enabled', True):
            return

        self.monitoring_active = True
        monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        monitor_thread.start()

        print("INFO: Predictive Monitoring gestartet")

    def stop_predictive_monitoring(self):
        """Stoppt Predictive Maintenance Monitoring"""
        self.monitoring_active = False
        print("INFO: Predictive Monitoring gestoppt")

    def analyze_rig_health(self, rig_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analysiert den Gesundheitszustand eines Rigs"""
        rig_id = rig_data.get('id', 'unknown')
        current_temp = rig_data.get('temperature', 0)
        current_hashrate = rig_data.get('hash_rate', 0)
        current_power = rig_data.get('power_consumption', 0)

        # Historische Daten sammeln
        if rig_id not in self.temperature_data:
            self.temperature_data[rig_id] = []
            self.hashrate_data[rig_id] = []
            self.power_data[rig_id] = []
            self.error_counts[rig_id] = 0

        # Neue Messungen hinzufügen
        timestamp = datetime.now()
        self.temperature_data[rig_id].append((timestamp, current_temp))
        self.hashrate_data[rig_id].append((timestamp, current_hashrate))
        self.power_data[rig_id].append((timestamp, current_power))

        # Alte Daten bereinigen (nur letzte 30 Tage)
        cutoff_date = datetime.now() - timedelta(days=self.maintenance_config.get('HistoricalDataDays', 30))
        self.temperature_data[rig_id] = [d for d in self.temperature_data[rig_id] if d[0] > cutoff_date]
        self.hashrate_data[rig_id] = [d for d in self.hashrate_data[rig_id] if d[0] > cutoff_date]
        self.power_data[rig_id] = [d for d in self.power_data[rig_id] if d[0] > cutoff_date]

        # Analyse durchführen
        analysis = self._perform_health_analysis(rig_id, rig_data)

        return analysis

    def predict_failures(self, rig_id: str) -> Dict[str, Any]:
        """Vorhersagt potenzielle Hardware-Ausfälle"""
        if rig_id not in self.temperature_data or not self.temperature_data[rig_id]:
            return {'predictions': [], 'risk_level': 'unknown'}

        temp_data = self.temperature_data[rig_id]
        hashrate_data = self.hashrate_data[rig_id]

        predictions = []

        # Temperatur-Trend-Analyse
        temp_trend = self._analyze_temperature_trend(temp_data)
        if temp_trend['risk_level'] != 'low':
            predictions.append({
                'component': 'Temperature System',
                'failure_probability': temp_trend['failure_probability'],
                'predicted_failure_hours': temp_trend['predicted_hours'],
                'risk_level': temp_trend['risk_level'],
                'recommendations': temp_trend['recommendations']
            })

        # Hashrate-Stabilität-Analyse
        hashrate_trend = self._analyze_hashrate_stability(hashrate_data)
        if hashrate_trend['risk_level'] != 'low':
            predictions.append({
                'component': 'Hashrate Performance',
                'failure_probability': hashrate_trend['failure_probability'],
                'predicted_failure_hours': hashrate_trend['predicted_hours'],
                'risk_level': hashrate_trend['risk_level'],
                'recommendations': hashrate_trend['recommendations']
            })

        # Komplexe Vorhersage mit Machine Learning-ähnlichen Algorithmen
        if len(temp_data) >= 24 and len(hashrate_data) >= 24:  # Mindestens 24h Daten
            complex_prediction = self._complex_failure_prediction(rig_id)
            if complex_prediction:
                predictions.append(complex_prediction)

        # Gesamtrisiko bestimmen
        risk_levels = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        overall_risk = max([risk_levels.get(p['risk_level'], 1) for p in predictions], default=1)
        risk_labels = {4: 'critical', 3: 'high', 2: 'medium', 1: 'low'}

        return {
            'rig_id': rig_id,
            'predictions': predictions,
            'overall_risk_level': risk_labels.get(overall_risk, 'low'),
            'immediate_actions_required': any(p['predicted_failure_hours'] < 24 for p in predictions),
            'next_maintenance_due_hours': self._calculate_maintenance_schedule(rig_id)
        }

    def schedule_maintenance(self, predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Plant vorbeugende Wartung basierend auf Vorhersagen"""
        urgent_maintenance = []
        scheduled_maintenance = []
        preventive_actions = []

        for prediction in predictions:
            hours_until_failure = prediction.get('predicted_failure_hours', 168)
            risk_level = prediction.get('risk_level', 'low')

            if hours_until_failure < 24 or risk_level == 'critical':
                # Dringende Wartung
                urgent_maintenance.append({
                    'component': prediction['component'],
                    'priority': 'IMMEDIATE',
                    'estimated_time': '2-4 hours',
                    'cost_estimate': 'Medium',
                    'downtime_estimate': '4-8 hours'
                })
            elif hours_until_failure < 168:  # < 7 Tage
                # Geplante Wartung
                scheduled_maintenance.append({
                    'component': prediction['component'],
                    'priority': 'HIGH',
                    'schedule_within_days': max(1, int(hours_until_failure / 24)),
                    'estimated_time': '1-2 hours',
                    'cost_estimate': 'Low-Medium',
                    'downtime_estimate': '2-4 hours'
                })
            else:
                # Präventive Maßnahmen
                preventive_actions.append({
                    'component': prediction['component'],
                    'action': self._get_preventive_actions(prediction['component']),
                    'schedule_days': 30,
                    'estimated_time': '30 minutes',
                    'cost_estimate': 'Very Low'
                })

        return {
            'urgent_maintenance': urgent_maintenance,
            'scheduled_maintenance': scheduled_maintenance,
            'preventive_actions': preventive_actions,
            'estimated_cost_range': self._estimate_maintenance_cost(urgent_maintenance + scheduled_maintenance),
            'total_downtime_estimate': self._estimate_downtime(urgent_maintenance + scheduled_maintenance)
        }

    def _perform_health_analysis(self, rig_id: str, rig_data: Dict[str, Any]) -> Dict[str, Any]:
        """Führt detaillierte Gesundheitsanalyse durch"""
        current_temp = rig_data.get('temperature', 0)
        current_hashrate = rig_data.get('hash_rate', 0)
        max_temp_threshold = self.maintenance_config.get('TemperatureThreshold', 80.0)
        hashrate_drop_threshold = self.maintenance_config.get('HashrateDropThreshold', 10.0)

        analysis = {
            'rig_id': rig_id,
            'timestamp': datetime.now().isoformat(),
            'current_temperature': current_temp,
            'current_hashrate': current_hashrate,
            'temperature_status': 'normal' if current_temp < max_temp_threshold else 'warning',
            'hashrate_status': 'normal'
        }

        # Hashrate-Vergleich mit Baseline
        if len(self.hashrate_data[rig_id]) >= 24:  # Mindestens 24h Daten
            baseline_hashrate = self._calculate_baseline_hashrate(rig_id)
            if baseline_hashrate > 0:
                hashrate_drop = ((baseline_hashrate - current_hashrate) / baseline_hashrate) * 100
                analysis['hashrate_drop_percent'] = hashrate_drop
                analysis['hashrate_status'] = 'warning' if hashrate_drop > hashrate_drop_threshold * 0.5 else 'normal'
                analysis['hashrate_status'] = 'critical' if hashrate_drop > hashrate_drop_threshold else analysis['hashrate_status']

        # Efficiency-Analyse
        power_consumption = rig_data.get('power_consumption', 0)
        if power_consumption > 0 and current_hashrate > 0:
            efficiency = current_hashrate / power_consumption
            analysis['efficiency'] = efficiency

            # Vergleich mit erwarteter Efficiency
            expected_efficiency = self._get_expected_efficiency(rig_data.get('type', ''))
            if expected_efficiency > 0:
                efficiency_drop = ((expected_efficiency - efficiency) / expected_efficiency) * 100
                analysis['efficiency_drop_percent'] = efficiency_drop

        efficiency_summary = evaluate_rig_efficiency(rig_data)
        analysis['efficiency_summary'] = efficiency_summary
        if efficiency_summary.get('recommendations'):
            analysis.setdefault('recommendations', []).extend(efficiency_summary['recommendations'])

        temp_optimization = optimize_rig_temperature(rig_data)
        analysis['temperature_optimization'] = temp_optimization
        if temp_optimization.get('actions_taken'):
            log_event('TEMPERATURE_OPTIMIZATION_DECISION', {
                'rig_id': rig_id,
                'actions': temp_optimization['actions_taken'],
                'efficiency_gain': temp_optimization.get('efficiency_gain', 0),
                'temperature': temp_optimization.get('original_temperature'),
                'hash_rate': temp_optimization.get('original_hashrate')
            })

        analysis.setdefault('recommendations', []).extend([
            action for action in temp_optimization.get('actions_taken', [])
            if action not in analysis.get('recommendations', [])
        ])

        analysis['thermal_report'] = get_thermal_efficiency_report()

        return analysis

    def _analyze_temperature_trend(self, temp_data: List[Tuple[datetime, float]]) -> Dict[str, Any]:
        """Analysiert Temperatur-Trends"""
        if len(temp_data) < 24:  # Mindestens 24h Daten
            return {'risk_level': 'low', 'failure_probability': 0.05, 'predicted_hours': 999, 'recommendations': []}

        # Letzte 24h Temperaturen
        recent_temps = [temp for _, temp in temp_data[-24:]]
        avg_temp = sum(recent_temps) / len(recent_temps)
        max_temp = max(recent_temps)
        min_temp = min(recent_temps)
        temp_variance = statistics.variance(recent_temps) if len(recent_temps) > 1 else 0

        # Trend-Berechnung (lineare Regression)
        x_values = list(range(len(recent_temps)))
        slope = self._calculate_linear_trend(recent_temps)

        # Risiko-Bewertung
        risk_score = 0

        # Hohe Durchschnittstemperatur
        if avg_temp > 70:
            risk_score += 2
        elif avg_temp > 60:
            risk_score += 1

        # Hohe maximale Temperatur
        if max_temp > 85:
            risk_score += 2
        elif max_temp > 80:
            risk_score += 1

        # Steigender Trend
        if slope > 0.5:
            risk_score += 1

        # Hohe Varianz (= instabil)
        if temp_variance > 25:
            risk_score += 1

        # Risiko-Level bestimmen
        if risk_score >= 5:
            risk_level = 'critical'
            failure_prob = 0.8
            predicted_hours = 48
        elif risk_score >= 3:
            risk_level = 'high'
            failure_prob = 0.6
            predicted_hours = 168
        elif risk_score >= 2:
            risk_level = 'medium'
            failure_prob = 0.3
            predicted_hours = 336
        else:
            risk_level = 'low'
            failure_prob = 0.1
            predicted_hours = 999

        recommendations = []
        if risk_level != 'low':
            recommendations.append("Kühlung überprüfen und verbessern")
        if slope > 0.2:
            recommendations.append("Dust-Filter reinigen")
        if temp_variance > 20:
            recommendations.append("Lüfter und Thermopaste überprüfen")

        return {
            'risk_level': risk_level,
            'failure_probability': failure_prob,
            'predicted_hours': predicted_hours,
            'recommendations': recommendations,
            'avg_temperature': avg_temp,
            'max_temperature': max_temp,
            'temperature_trend': slope
        }

    def _analyze_hashrate_stability(self, hashrate_data: List[Tuple[datetime, float]]) -> Dict[str, Any]:
        """Analysiert Hashrate-Stabilität"""
        if len(hashrate_data) < 24:
            return {'risk_level': 'low', 'failure_probability': 0.05, 'predicted_hours': 999, 'recommendations': []}

        # Letzte 24h Hashrates
        recent_hashrates = [hr for _, hr in hashrate_data[-24:]]
        avg_hashrate = sum(recent_hashrates) / len(recent_hashrates)
        hashrate_variance = statistics.variance(recent_hashrates) if len(recent_hashrates) > 1 else 0

        # Trend-Berechnung
        slope = self._calculate_linear_trend(recent_hashrates)

        # Prüfe auf plötzliche Drops in letzten Stunden
        last_6h = recent_hashrates[-6:]  # Letzte 6h
        max_recent_drop = 0

        for i in range(1, len(last_6h)):
            if last_6h[i-1] > 0:
                drop = ((last_6h[i-1] - last_6h[i]) / last_6h[i-1]) * 100
                max_recent_drop = max(max_recent_drop, drop)

        # Risiko-Bewertung
        risk_score = 0

        # Negativer Trend (fallende Hashrate)
        if slope < -0.1:
            risk_score += 2
        elif slope < 0:
            risk_score += 1

        # Hohe Varianz
        std_dev = math.sqrt(hashrate_variance) if hashrate_variance > 0 else 0
        if std_dev > avg_hashrate * 0.1:  # > 10% Standardabweichung
            risk_score += 1

        # Plötzliche Drops
        if max_recent_drop > 15:
            risk_score += 2
        elif max_recent_drop > 10:
            risk_score += 1

        # Risiko-Level bestimmen
        if risk_score >= 4:
            risk_level = 'critical'
            failure_prob = 0.8
            predicted_hours = 72
        elif risk_score >= 3:
            risk_level = 'high'
            failure_prob = 0.6
            predicted_hours = 168
        elif risk_score >= 2:
            risk_level = 'medium'
            failure_prob = 0.4
            predicted_hours = 336
        else:
            risk_level = 'low'
            failure_prob = 0.15
            predicted_hours = 999

        recommendations = []
        if risk_level != 'low':
            recommendations.append("GPU-Treiber und Overclocking überprüfen")
        if max_recent_drop > 10:
            recommendations.append("VRAM und GPU-Kerne auf Fehler überprüfen")
        if hashrate_variance > 1000:
            recommendations.append("Netzteil und PCIe-Verbindungen prüfen")

        return {
            'risk_level': risk_level,
            'failure_probability': failure_prob,
            'predicted_hours': predicted_hours,
            'recommendations': recommendations,
            'avg_hashrate': avg_hashrate,
            'hashrate_variance': hashrate_variance,
            'hashrate_trend': slope,
            'max_recent_drop': max_recent_drop
        }

    def _complex_failure_prediction(self, rig_id: str) -> Optional[Dict[str, Any]]:
        """Komplexe Vorhersage mit Multi-Faktor-Analyse"""
        if (len(self.temperature_data[rig_id]) < 72 or  # 72h Daten
            len(self.hashrate_data[rig_id]) < 72 or
            len(self.power_data[rig_id]) < 72):
            return None

        # Korrelation zwischen Temperatur und Hashrate analysieren
        temp_values = [temp for _, temp in self.temperature_data[rig_id][-72:]]
        hashrate_values = [hr for _, hr in self.hashrate_data[rig_id][-72:]]

        # Korrelationskoeffizient berechnen
        if len(temp_values) == len(hashrate_values):
            correlation = self._calculate_correlation(temp_values, hashrate_values)

            # Wenn hohe Temperaturen starke Hashrate-Drops verursachen
            if correlation < -0.7:  # Starke negative Korrelation
                return {
                    'component': 'Thermal-Performance Correlation',
                    'failure_probability': 0.7,
                    'predicted_failure_hours': 96,
                    'risk_level': 'high',
                    'recommendations': [
                        'Erweiterte Kühlung implementieren',
                        'Temperatur-Limits anpassen',
                        'Performance-Monitoring verbessern'
                    ]
                }

        return None

    def _calculate_linear_trend(self, data: List[float]) -> float:
        """Berechnet linearen Trend (Steigung)"""
        if len(data) < 2:
            return 0.0

        n = len(data)
        x_sum = sum(range(n))
        y_sum = sum(data)
        xy_sum = sum(i * data[i] for i in range(n))
        x_squared_sum = sum(i * i for i in range(n))

        slope = ((n * xy_sum) - (x_sum * y_sum)) / ((n * x_squared_sum) - (x_sum * x_sum))
        return slope

    def _calculate_correlation(self, x_data: List[float], y_data: List[float]) -> float:
        """Berechnet Pearson-Korrelationskoeffizient"""
        if len(x_data) != len(y_data) or len(x_data) < 2:
            return 0.0

        n = len(x_data)
        x_mean = sum(x_data) / n
        y_mean = sum(y_data) / n

        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_data, y_data))
        x_std = math.sqrt(sum((x - x_mean) ** 2 for x in x_data) / n)
        y_std = math.sqrt(sum((y - y_mean) ** 2 for y in y_data) / n)

        denominator = n * x_std * y_std

        return numerator / denominator if denominator != 0 else 0.0

    def _calculate_baseline_hashrate(self, rig_id: str) -> float:
        """Berechnet Baseline-Hashrate aus historischen Daten"""
        hashrate_data = self.hashrate_data[rig_id]

        if len(hashrate_data) < 168:  # Weniger als 7 Tage Daten
            return 0.0

        # Letzte 7 Tage, aber nur "normale" Werte (keine plötzlichen Drops)
        recent_data = [hr for _, hr in hashrate_data[-168:]]
        recent_data.sort()

        # Oberste 80% als stabil betrachten (entferne Ausreißer)
        cut_index = int(len(recent_data) * 0.2)
        stable_data = recent_data[cut_index:]

        return sum(stable_data) / len(stable_data) if stable_data else 0.0

    def _get_expected_efficiency(self, rig_type: str) -> float:
        """Gibt erwartete Hashrate-Efficiency für Rig-Typ"""
        efficiency_map = {
            'RTX 4090': 120 / 450,  # MH/s per Watt
            'RTX 3090': 100 / 350,
            'Antminer S19 Pro': 110 / 3250,
            'Whatsminer M50': 118 / 3300
        }

        return efficiency_map.get(rig_type, 0.2)  # Default efficiency

    def _get_preventive_actions(self, component: str) -> str:
        """Gibt präventive Aktionen für Komponente"""
        actions = {
            'Temperature System': 'Lüfter reinigen und Thermopaste erneuern',
            'Hashrate Performance': 'Overclocking überprüfen und reduzieren',
            'Thermal-Performance Correlation': 'Kühlkörper und Lüfter upgraden'
        }

        return actions.get(component, 'Regelmäßige Inspektion durchführen')

    def _calculate_maintenance_schedule(self, rig_id: str) -> int:
        """Berechnet nächste geplante Wartung in Stunden"""
        # Basis: Alle 30 Tage Wartung
        base_schedule = 30 * 24

        # Anpassung basierend auf aktueller Performance
        if rig_id in self.error_counts:
            error_count = self.error_counts[rig_id]
            if error_count > 10:
                base_schedule = 14 * 24  # Alle 2 Wochen
            elif error_count > 5:
                base_schedule = 21 * 24  # Alle 3 Wochen

        return base_schedule

    def _estimate_maintenance_cost(self, tasks: List[Dict[str, Any]]) -> str:
        """Schätzt Wartungskosten"""
        base_cost = 0

        for task in tasks:
            cost_level = task.get('cost_estimate', 'Low')
            if cost_level == 'High':
                base_cost += 500
            elif cost_level == 'Medium':
                base_cost += 200
            else:  # Low/Very Low
                base_cost += 50

        if base_cost > 1000:
            return "High (CHF 1,000+)"
        elif base_cost > 500:
            return "Medium (CHF 500-1,000)"
        else:
            return "Low (CHF 500-)"

    def _estimate_downtime(self, tasks: List[Dict[str, Any]]) -> str:
        """Schätzt Ausfallzeit"""
        total_downtime = 0

        for task in tasks:
            downtime_est = task.get('downtime_estimate', '2 hours')

            if '8 hours' in downtime_est:
                total_downtime += 8
            elif '4 hours' in downtime_est:
                total_downtime += 4
            else:
                total_downtime += 2

        if total_downtime > 24:
            return "Critical (24+ hours)"
        elif total_downtime > 8:
            return "High (8-24 hours)"
        else:
            return "Low (8- hours)"

    def _monitoring_loop(self):
        """Hauptschleife für kontinuierliches Monitoring"""
        monitor_interval = self.maintenance_config.get('MonitorIntervalMinutes', 30) * 60

        while self.monitoring_active:
            try:
                # Alle Rigs scannen
                rigs = get_rigs_config()

                critical_alerts = []

                for rig in rigs:
                    rig_id = rig.get('id', 'unknown')

                    # Gesundheitsanalyse
                    health_analysis = self.analyze_rig_health(rig)

                    # Vorhersage
                    failure_predictions = self.predict_failures(rig_id)

                    # Kritische Warnungen prüfen
                    immediate_risk = failure_predictions.get('immediate_actions_required', False)
                    overall_risk = failure_predictions.get('overall_risk_level', 'low')

                    if immediate_risk or overall_risk in ['critical', 'high']:
                        critical_alerts.append({
                            'rig_id': rig_id,
                            'risk_level': overall_risk,
                            'immediate_action': immediate_risk,
                            'predictions': failure_predictions['predictions']
                        })

                # Alerts senden für kritische Fälle
                for alert in critical_alerts:
                    if alert['risk_level'] == 'critical':
                        send_system_alert("CRITICAL_MAINTENANCE_ALERT",
                                         f"Laufzeit: {datetime.now().strftime('%d.%m.%Y %H:%M')} | Rig: {alert['rig_id']} | Risiko: KRITISCH!",
                                         {'rig_id': alert['rig_id'], 'predictions': alert['predictions']})
                    elif alert['risk_level'] == 'high' or alert['immediate_action']:
                        send_custom_alert("Maintenance Warning",
                                         f"Mining-Rig {alert['rig_id']} benötigt dringend Wartung (Risiko: {alert['risk_level'].upper()})",
                                         "[WARN]")

                time.sleep(monitor_interval)

            except Exception as e:
                print(f"Predictive Maintenance Fehler: {e}")
                send_custom_alert("Predictive Maintenance Error",
                                 f"Fehler im Predictive Maintenance System: {e}",
                                 "[ERROR]")
                time.sleep(300)  # Bei Fehler 5 Minuten warten

    def get_maintenance_status(self) -> Dict[str, Any]:
        """Gibt Wartungsstatus zurück"""
        return {
            'monitoring_active': self.monitoring_active,
            'rigs_monitored': len(self.temperature_data),
            'total_data_points': sum(len(data) for data in self.temperature_data.values()),
            'last_monitoring_cycle': datetime.now().isoformat(),
            'maintenance_config': self.maintenance_config
        }

# Globale Predictive Maintenance Instanz
predictive_maintenance = PredictiveMaintenance()

# Convenience-Funktionen
def start_predictive_monitoring():
    """Startet Predictive Maintenance Monitoring"""
    predictive_maintenance.start_predictive_monitoring()

def stop_predictive_monitoring():
    """Stoppt Predictive Maintenance Monitoring"""
    predictive_maintenance.stop_predictive_monitoring()

def analyze_rig_health(rig_data):
    """Analysiert Rig-Gesundheit"""
    return predictive_maintenance.analyze_rig_health(rig_data)

def predict_rig_failures(rig_id):
    """Vorhersagt Rig-Ausfälle"""
    return predictive_maintenance.predict_failures(rig_id)

def get_maintenance_status():
    """Gibt Wartungsstatus"""
    return predictive_maintenance.get_maintenance_status()

if __name__ == "__main__":
    print("CASH MONEY COLORS ORIGINAL (R) - PREDICTIVE MAINTENANCE")
    print("=" * 65)

    print("Teste Predictive Maintenance...")

    # Beispiel-Rig Daten
    test_rig = {
        'id': 'GPU_1',
        'type': 'RTX 4090',
        'temperature': 78.5,
        'hash_rate': 115.0,
        'power_consumption': 440,
        'algorithm': 'ethash'
    }

    # Gesundheitsanalyse
    health = analyze_rig_health(test_rig)
    print(f"[OK] Gesundheitsanalyse für {test_rig['id']}:")
    print(f"   Temperatur-Status: {health.get('temperature_status', 'Unknown')}")
    print(f"   Hashrate-Status: {health.get('hashrate_status', 'Unknown')}")

    # Ausfall-Vorhersage (mit vorhandenen Daten)
    prediction = predict_rig_failures(test_rig['id'])
    print(f"\n🔮 Vorhersage für {test_rig['id']}:")
    print(f"   Gesamtrisiko: {prediction.get('overall_risk_level', 'Unknown').upper()}")
    print(f"   Sofortige Maßnahmen: {prediction.get('immediate_actions_required', False)}")

    print("\n[OK] PREDICTIVE MAINTENANCE BEREIT!")
    print("Verwende start_predictive_monitoring() für kontinuierliche Hardware-Überwachung")
