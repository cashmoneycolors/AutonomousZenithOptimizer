#!/usr/bin/env python3
"""
CASH MONEY COLORS ORIGINAL (R) - TEMPERATURE OPTIMIZER
Automatische Temperatur-basierte Übertaktung und Kühlungs-Optimierung
"""
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import threading
import statistics
from python_modules.config_manager import get_config, get_rigs_config
from python_modules.alert_system import send_custom_alert
from python_modules.enhanced_logging import log_event

class TemperatureOptimizer:
    """Automatischer Temperatur-Optimierer für maximale Performance"""

    def __init__(self):
        self.temp_config = get_config('TemperatureOptimization', {})
        self.monitoring_active = False
        self.optimization_active = False
        self.rig_overclocks = {}
        self.temperature_history = {}
        self.efficiency_gains = {}

        # Default-Konfiguration
        if not self.temp_config:
            self.temp_config = {
                'Enabled': True,
                'OverclockEnabled': True,
                'FanControlEnabled': True,
                'TargetTemperatureRange': [65, 75],  # Min/Max optimale Temperatur
                'OverclockIncrement': 50,  # MH/s Schritte
                'UndervoltEnabled': True,
                'FanSpeedMin': 30,
                'FanSpeedMax': 100,
                'MonitoringIntervalSeconds': 60,
                'RecoveryTimeMinutes': 10,
                'StabilityTestDurationMinutes': 5
            }

        self.current_fan_speeds = {}
        self.power_limits = {}
        self.voltage_offsets = {}

        print("🌡️ TEMPERATURE OPTIMIZER INITIALIZED")
        print(f"   Target Range: {self.temp_config.get('TargetTemperatureRange', [65, 75])}°C")
        print(f"   Overclocking: {'ENABLED' if self.temp_config.get('OverclockEnabled', True) else 'DISABLED'}")

    def start_temperature_optimization(self):
        """Startet automatische Temperatur-Optimierung"""
        if self.optimization_active:
            return

        self.optimization_active = True
        monitor_thread = threading.Thread(target=self._optimization_loop, daemon=True)
        monitor_thread.start()

        print("⚡ Temperature Optimization gestartet")

    def stop_temperature_optimization(self):
        """Stoppt Temperatur-Optimierung und setzt alles zurück"""
        if not self.optimization_active:
            return

        self.optimization_active = False
        self._reset_all_overclocks()

        print("❄️ Temperature Optimization gestoppt - Overclocks zurückgesetzt")

    def optimize_rig_temperature(self, rig_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimiert Temperatur-Performance eines einzelnen Rigs"""
        rig_id = rig_data.get('id', 'unknown')
        current_temp = rig_data.get('temperature', 0)
        current_hashrate = rig_data.get('hash_rate', 0)
        max_safe_temp = self.temp_config.get('TargetTemperatureRange', [65, 75])[1]

        optimization = {
            'rig_id': rig_id,
            'original_hashrate': current_hashrate,
            'original_temperature': current_temp,
            'actions_taken': [],
            'efficiency_gain': 0,
            'stability_rating': 'stable'
        }

        # Temperatur-basierte Entscheidungen
        if current_temp > max_safe_temp:
            # Zu heiß - Drosseln oder Kühlung verbessern
            action = self._handle_overtemperature(rig_id, rig_data, current_temp, max_safe_temp)
            optimization['actions_taken'].append(action)

        elif current_temp < max_safe_temp - 10:  # Mehr als 10° unter Maximum
            # Gute Kühlung - Overclocking versuchen
            if self.temp_config.get('OverclockEnabled', True):
                action = self._try_overclocking(rig_id, rig_data, current_temp, current_hashrate)
                if action:
                    optimization['actions_taken'].append(action)
                    optimization['efficiency_gain'] = action.get('efficiency_gain', 0)

        # Lüftergeschwindigkeit optimieren
        if self.temp_config.get('FanControlEnabled', True):
            fan_action = self._optimize_fan_speed(rig_id, rig_data)
            if fan_action:
                optimization['actions_taken'].append(fan_action)

        # Undervolting für zusätzliche Efficiency
        if self.temp_config.get('UndervoltEnabled', True) and current_temp < max_safe_temp - 5:
            undervolt_action = self._optimize_voltage(rig_id, rig_data)
            if undervolt_action:
                optimization['actions_taken'].append(undervolt_action)
                optimization['efficiency_gain'] += undervolt_action.get('power_saving', 0)

        return optimization

    def monitor_thermal_efficiency(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """Überwacht thermische Efficiency über Zeitfenster"""
        rigs = get_rigs_config()
        efficiency_report = {
            'monitoring_period_minutes': time_window_minutes,
            'rig_efficiency_scores': {},
            'thermal_optimal_rigs': 0,
            'overheating_rigs': 0,
            'underperforming_rigs': 0,
            'average_thermal_efficiency': 0,
            'power_savings_total': 0
        }

        total_efficiency = 0
        rig_count = 0

        for rig in rigs:
            rig_id = rig.get('id', 'unknown')

            # Sammle historische Daten für diesen Rig
            if rig_id not in self.temperature_history:
                continue

            recent_temps = [temp for _, temp in self.temperature_history[rig_id][-60:]]  # Letzte Stunde
            if not recent_temps:
                continue

            rig_count += 1
            avg_temp = sum(recent_temps) / len(recent_temps)

            # Efficiency Score berechnen (basierend auf idealer Temperatur)
            target_min, target_max = self.temp_config.get('TargetTemperatureRange', [65, 75])
            target_center = (target_min + target_max) / 2

            # Je näher an der optimalen Temperatur, desto höher der Score
            temp_distance = abs(avg_temp - target_center)
            temp_range = target_max - target_min

            efficiency_score = max(0, (1 - (temp_distance / (temp_range * 2))) * 100)

            # Power Efficiency basierend auf Overclocking/Voltage Optimization
            power_efficiency = self._calculate_power_efficiency(rig_id, rig)

            rig_score = {
                'average_temperature': avg_temp,
                'thermal_efficiency_score': efficiency_score,
                'power_efficiency_percentage': power_efficiency,
                'overall_efficiency_score': (efficiency_score + power_efficiency) / 2,
                'optimization_actions': len(self.rig_overclocks.get(rig_id, {}).get('history', []))
            }

            efficiency_report['rig_efficiency_scores'][rig_id] = rig_score
            total_efficiency += rig_score['overall_efficiency_score']

            # Kategorisieren
            if efficiency_score > 80:
                efficiency_report['thermal_optimal_rigs'] += 1
            elif avg_temp > target_max:
                efficiency_report['overheating_rigs'] += 1
            elif efficiency_score < 60:
                efficiency_report['underperforming_rigs'] += 1

        if rig_count > 0:
            efficiency_report['average_thermal_efficiency'] = total_efficiency / rig_count
            efficiency_report['power_savings_total'] = self._calculate_total_power_savings()

        return efficiency_report

    def _handle_overtemperature(self, rig_id: str, rig_data: Dict[str, Any],
                              current_temp: float, max_temp: float) -> Dict[str, Any]:
        """Behandelt Übertemperatur durch Drosseln oder Kühlung"""
        temp_over = current_temp - max_temp
        severity = 'critical' if temp_over > 10 else 'warning' if temp_over > 5 else 'minor'

        actions = []

        # Emergency Throttling für kritische Übertemperatur
        if severity == 'critical':
            self._emergency_throttle(rig_id, temp_over)
            actions.append('emergency_throttle')

        # Fan Speed erhöhen
        if self.temp_config.get('FanControlEnabled', True):
            fan_speed = self._calculate_fan_speed_for_temperature(current_temp, rig_id)
            self._set_fan_speed(rig_id, fan_speed)
            actions.append(f'fan_speed_{fan_speed}%')

        # Overclocking zurücknehmen
        if rig_id in self.rig_overclocks:
            self._reduce_overclock(rig_id, temp_over / 5)  # Reduziere um Temperature/5 MH/s
            actions.append('overclock_reduced')

        # Alert senden
        send_custom_alert("Temperature Alert",
                         f"Rig {rig_id}: {current_temp:.1f}°C (Max: {max_temp}°C) - {severity.upper()}",
                         "🔥")

        log_event('TEMPERATURE_OVERHEAT', {
            'rig_id': rig_id,
            'temperature': current_temp,
            'max_temp': max_temp,
            'severity': severity,
            'actions_taken': actions
        })

        return {
            'action': 'overtemperature_handling',
            'severity': severity,
            'temp_over': temp_over,
            'actions_taken': actions,
            'fan_speed': self.current_fan_speeds.get(rig_id, 'auto')
        }

    def _try_overclocking(self, rig_id: str, rig_data: Dict[str, Any],
                         current_temp: float, current_hashrate: float) -> Optional[Dict[str, Any]]:
        """Versucht Overclocking wenn Temperatur gut ist"""
        if not self.temp_config.get('OverclockEnabled', True):
            return None

        # Prüfe Stabilität der letzten Stunden
        stability_ok = self._check_stability(rig_id)
        if not stability_ok:
            return None

        # Berechne mögliches Overclocking
        temp_headroom = self.temp_config.get('TargetTemperatureRange', [65, 75])[1] - current_temp
        overclock_potential = min(temp_headroom * 10, 200)  # Max 200 MH/s basierend auf Temperatur-Headroom

        if overclock_potential < self.temp_config.get('OverclockIncrement', 50):
            return None

        # Simuliert Overclocking (in Realität würde GPU-API verwendet)
        new_hashrate = current_hashrate + overclock_potential

        # Stabilitätstest vornehmen
        stable = self._run_stability_test(rig_id, new_hashrate)
        if not stable:
            overclock_potential = overclock_potential * 0.7  # Reduziere auf 70%
            new_hashrate = current_hashrate + overclock_potential
            stable = self._run_stability_test(rig_id, new_hashrate)

        if stable:
            # Overclocking erfolgreich
            self.rig_overclocks.setdefault(rig_id, {'current': 0, 'history': []})
            self.rig_overclocks[rig_id]['current'] += overclock_potential
            self.rig_overclocks[rig_id]['history'].append({
                'timestamp': datetime.now().isoformat(),
                'overclock_mhs': overclock_potential,
                'new_hashrate': new_hashrate,
                'temperature_trigger': current_temp
            })

            send_custom_alert("Overclock Success",
                             f"Rig {rig_id}: Overclocked +{overclock_potential} MH/s ({new_hashrate} MH/s total)",
                             "⚡")

            return {
                'action': 'overclock_success',
                'overclock_amount': overclock_potential,
                'new_hashrate': new_hashrate,
                'efficiency_gain': overclock_potential / current_hashrate * 100
            }

        return None

    def _optimize_fan_speed(self, rig_id: str, rig_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Optimiert Lüftergeschwindigkeit für beste Balance"""
        if not self.temp_config.get('FanControlEnabled', True):
            return None

        current_temp = rig_data.get('temperature', 70)
        current_speed = self.current_fan_speeds.get(rig_id, 50)

        optimal_speed = self._calculate_fan_speed_for_temperature(current_temp, rig_id)

        if abs(optimal_speed - current_speed) >= 10:  # Nur ändern bei 10% Unterschied
            self._set_fan_speed(rig_id, optimal_speed)

            return {
                'action': 'fan_speed_optimization',
                'from_speed': current_speed,
                'to_speed': optimal_speed,
                'temperature': current_temp
            }

        return None

    def _optimize_voltage(self, rig_id: str, rig_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Optimiert Spannung für bessere Efficiency"""
        if not self.temp_config.get('UndervoltEnabled', True):
            return None

        current_temp = rig_data.get('temperature', 70)
        current_power = rig_data.get('power_consumption', 300)

        # Berechne optimale Spannung basierend auf Temperatur
        base_voltage = 900  # mV, rig-spezifisch anpassen
        temp_factor = max(0, (80 - current_temp) / 20)  # Stabiler bei niedrigerer Temperatur
        optimal_voltage = base_voltage - (temp_factor * 50)

        current_voltage = self.voltage_offsets.get(rig_id, base_voltage)

        if abs(optimal_voltage - current_voltage) >= 25:  # Nur ändern bei 25mV Unterschied
            self._set_voltage(rig_id, optimal_voltage)

            power_saving = (current_voltage - optimal_voltage) / base_voltage * 5  # Geschätzte 5% Savings

            return {
                'action': 'voltage_optimization',
                'from_voltage': current_voltage,
                'to_voltage': optimal_voltage,
                'power_saving': power_saving,
                'temperature': current_temp
            }

        return None

    def _calculate_fan_speed_for_temperature(self, temperature: float, rig_id: str) -> int:
        """Berechnet optimale Lüftergeschwindigkeit für Temperatur"""
        target_min, target_max = self.temp_config.get('TargetTemperatureRange', [65, 75])
        fan_min, fan_max = self.temp_config.get('FanSpeedMin', 30), self.temp_config.get('FanSpeedMax', 100)

        if temperature <= target_min - 5:
            return fan_min
        elif temperature >= target_max + 5:
            return fan_max
        else:
            # Lineare Interpolation zwischen Min und Max
            temp_range = (target_max + 5) - (target_min - 5)
            temp_pos = (temperature - (target_min - 5)) / temp_range
            return int(fan_min + (fan_max - fan_min) * temp_pos)

    def _check_stability(self, rig_id: str) -> bool:
        """Prüft ob Rig in letzten Stunden stabil war"""
        if rig_id not in self.temperature_history or len(self.temperature_history[rig_id]) < 12:
            return True  # Nicht genug Daten = annehmen stabil

        recent_temps = [temp for _, temp in self.temperature_history[rig_id][-12:]]  # Letzte 12 Messungen

        # Prüfe Temperatur-Varianz
        variance = statistics.variance(recent_temps) if len(recent_temps) > 1 else 0

        # Prüfe extreme Ausreißer
        avg_temp = sum(recent_temps) / len(recent_temps)
        max_deviation = max(abs(temp - avg_temp) for temp in recent_temps)

        # Stabil wenn Varianz < 25°C² und max Abweichung < 15°C
        return variance < 25 and max_deviation < 15

    def _run_stability_test(self, rig_id: str, test_hashrate: float) -> bool:
        """Führt Stabilitätstest für neue Overclocking-Einstellungen durch"""
        # Simuliert Stabilitätstest
        test_duration = self.temp_config.get('StabilityTestDurationMinutes', 5) * 60

        # In Realität würde hier Mining-Software für Testzeitraum gestartet
        # und System auf Stabilität geprüft

        # Pseudo-Random Test basierend auf Hashrate-Wahrscheinlichkeit
        stability_prob = max(0.1, min(1.0, (150 - (test_hashrate / 100)) / 150))

        import random
        return random.random() < stability_prob

    def _set_fan_speed(self, rig_id: str, speed: int):
        """Setzt Lüftergeschwindigkeit"""
        self.current_fan_speeds[rig_id] = speed
        # Hier würde eigentliche Hardware-Steuerung erfolgen

    def _set_voltage(self, rig_id: str, voltage_mv: float):
        """Setzt GPU-Spannung"""
        self.voltage_offsets[rig_id] = voltage_mv
        # Hier würde eigentliche Hardware-Steuerung erfolgen

    def _emergency_throttle(self, rig_id: str, temp_over: float):
        """Notfall-Drosselung bei gefährlicher Übertemperatur"""
        # Sofort Lüfter auf Maximum setzen
        self._set_fan_speed(rig_id, 100)

        # Overclocking komplett zurücknehmen
        if rig_id in self.rig_overclocks:
            self.rig_overclocks[rig_id]['current'] = 0

        send_custom_alert("EMERGENCY THROTTLE",
                         f"Rig {rig_id}: Emergency Throttle aktiviert due to {temp_over:.1f}°C overtemperature",
                         "🚨")

    def _reduce_overclock(self, rig_id: str, reduction_amount: float):
        """Reduziert Overclocking eines Rigs"""
        if rig_id in self.rig_overclocks:
            current = self.rig_overclocks[rig_id]['current']
            new_current = max(0, current - reduction_amount)
            self.rig_overclocks[rig_id]['current'] = new_current

    def _reset_all_overclocks(self):
        """Setzt alle Overclocks zurück"""
        for rig_id in self.rig_overclocks:
            self.rig_overclocks[rig_id]['current'] = 0

        # Lüfter auf Standard setzen
        standard_fan_speed = (self.temp_config.get('FanSpeedMin', 30) + self.temp_config.get('FanSpeedMax', 100)) // 2
        for rig_id in self.current_fan_speeds:
            self._set_fan_speed(rig_id, standard_fan_speed)

        send_custom_alert("Overclock Reset",
                         "Alle Rig-Overclocks wurden zur Sicherheit zurückgesetzt",
                         "🔄")

    def _calculate_power_efficiency(self, rig_id: str, rig_data: Dict[str, Any]) -> float:
        """Berechnet Power-Efficiency eines Rigs"""
        power_consumption = rig_data.get('power_consumption', 300)
        hashrate = rig_data.get('hash_rate', 100)

        if power_consumption <= 0 or hashrate <= 0:
            return 0

        # Efficiency = MH/s per Watt
        efficiency = hashrate / power_consumption

        # Vergleich mit optimaler Efficiency
        optimal_efficiency = self._get_optimal_efficiency(rig_data.get('type', ''))

        if optimal_efficiency > 0:
            efficiency_percentage = (efficiency / optimal_efficiency) * 100
            return min(100, max(0, efficiency_percentage))

        return 50  # Default wenn unbekannt

    def _get_optimal_efficiency(self, rig_type: str) -> float:
        """Gibt optimale Efficiency für Rig-Typ"""
        efficiency_map = {
            'RTX 4090': 120 / 450,  # MH/s per Watt
            'RTX 3090': 100 / 350,
            'Antminer S19 Pro': 110 / 3250,
            'Whatsminer M50': 118 / 3300
        }

        return efficiency_map.get(rig_type, 0.25)

    def _calculate_total_power_savings(self) -> float:
        """Berechnet totale Power-Einsparungen durch Optimierungen"""
        total_savings = 0

        for rig_id, overclock_data in self.rig_overclocks.items():
            current_overclock = overclock_data.get('current', 0)
            if current_overclock > 0:
                # Schätzungen: 5% Power Savings pro 50 MH/s Overclock
                total_savings += (current_overclock / 50) * 15  # 15W Savings per 50 MH/s

        return total_savings

    def _optimization_loop(self):
        """Hauptschleife für kontinuierliche Optimierung"""
        monitor_interval = self.temp_config.get('MonitoringIntervalSeconds', 60)

        while self.optimization_active:
            try:
                # Temperatur-Daten sammeln für alle Rigs
                self._collect_temperature_data()

                # Optimierung für jeden Rig durchführen
                rigs = get_rigs_config()
                for rig in rigs:
                    optimization_result = self.optimize_rig_temperature(rig)

                    if optimization_result['actions_taken']:
                        log_event('THERMAL_OPTIMIZATION', {
                            'rig_id': rig['id'],
                            'actions_taken': optimization_result['actions_taken'],
                            'efficiency_gain': optimization_result['efficiency_gain']
                        })

                time.sleep(monitor_interval)

            except Exception as e:
                print(f"Temperature Optimization Fehler: {e}")
                send_custom_alert("Temperature Optimizer Error",
                                 f"Fehler im Temperature Optimizer: {e}",
                                 "[ERROR]")
                time.sleep(300)  # Bei Fehler 5 Minuten warten

    def _collect_temperature_data(self):
        """Sammelt Temperatur-Daten von allen Rigs (simuliert)"""
        rigs = get_rigs_config()

        for rig in rigs:
            rig_id = rig.get('id', 'unknown')

            # Simulierte Temperatur mit realistischen Schwankungen
            base_temp = rig.get('temperature', 70)
            variation = (time.time() % 10) - 5  # -5 bis +5 Variation
            current_temp = base_temp + variation * 0.1

            if rig_id not in self.temperature_history:
                self.temperature_history[rig_id] = []

            self.temperature_history[rig_id].append((datetime.now(), current_temp))

            # Alte Daten bereinigen (behalte nur 24h)
            cutoff = datetime.now() - timedelta(hours=24)
            self.temperature_history[rig_id] = [(t, temp) for t, temp in self.temperature_history[rig_id] if t > cutoff]

    def get_thermal_status(self) -> Dict[str, Any]:
        """Gibt thermischen Status zurück"""
        return {
            'optimization_active': self.optimization_active,
            'rigs_optimized': len(self.rig_overclocks),
            'total_overclock_mhs': sum(data.get('current', 0) for data in self.rig_overclocks.values()),
            'temperature_data_points': sum(len(data) for data in self.temperature_history.values()),
            'power_savings_estimated': self._calculate_total_power_savings(),
            'config': self.temp_config
        }

# Globale Temperature Optimizer Instanz
temperature_optimizer = TemperatureOptimizer()

# Convenience-Funktionen
def start_temperature_optimization():
    """Startet Temperature-Optimierung"""
    temperature_optimizer.start_temperature_optimization()

def stop_temperature_optimization():
    """Stoppt Temperature-Optimierung"""
    temperature_optimizer.stop_temperature_optimization()

def optimize_rig_temperature(rig_data):
    """Optimiert einzelnen Rig"""
    return temperature_optimizer.optimize_rig_temperature(rig_data)

def get_thermal_efficiency_report():
    """Gibt thermische Efficiency-Report"""
    return temperature_optimizer.monitor_thermal_efficiency()

def get_thermal_status():
    """Gibt thermischen Status"""
    return temperature_optimizer.get_thermal_status()

if __name__ == "__main__":
    print("CASH MONEY COLORS ORIGINAL (R) - TEMPERATURE OPTIMIZER")
    print("=" * 65)

    print("🧪 Teste Temperature Optimizer...")

    # Test-Rig
    test_rig = {
        'id': 'GPU_1',
        'type': 'RTX 4090',
        'temperature': 68.5,
        'hash_rate': 120.0,
        'power_consumption': 450
    }

    # Temperature-Optimierung testen
    optimization = optimize_rig_temperature(test_rig)
    print(f"[OK] Temperature Optimization für {test_rig['id']}:")
    print(f"   Actions: {len(optimization['actions_taken'])}")
    print(f"   Efficiency Gain: {optimization['efficiency_gain']:.1f}%")

    # Thermal Status testen
    status = get_thermal_status()
    print(f"[OK] Thermal Status: {status['rigs_optimized']} Rigs per ris optimized")

    print("\n[OK] TEMPERATURE OPTIMIZER BEREIT!")
    print("Verwende start_temperature_optimization() für automatische Temperatur-Kontrolle")
    print("Optimiert Lüftergeschwindigkeiten, Overclocking und Voltage für maximale Efficiency")
