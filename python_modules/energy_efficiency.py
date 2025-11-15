#!/usr/bin/env python3
"""
CASH MONEY COLORS ORIGINAL (R) - ENERGY EFFICIENCY MANAGER
Analysiert Hashrate vs. Leistungsaufnahme und gibt Optimierungsanweisungen.
"""
from __future__ import annotations

from typing import Dict, Any

from python_modules.config_manager import get_config, get_rigs_config
from python_modules.enhanced_logging import log_event


class EnergyEfficiencyManager:
    """Verantwortlich für energieeffiziente Entscheidungen"""

    def __init__(self) -> None:
        self.config = get_config('EnergyEfficiency', {
            'Enabled': True,
            'EfficiencyThreshold': 0.22,  # Hashrate (MH/s) per Watt
            'CriticalTemperature': 85.0,  # °C
            'ThrottleStepPercent': 5,
            'MinEfficiencyTarget': 0.25,
            'EvaluationWindowMinutes': 15,
        })
        self.power_history: Dict[str, list[Dict[str, Any]]] = {}

    def evaluate_rig(self, rig_data: Dict[str, Any]) -> Dict[str, Any]:
        """Berechnet Energieeffizienz-Indikatoren für ein einzelnes Rig"""
        rig_id = rig_data.get('id', 'unknown')
        hashrate = rig_data.get('hash_rate', 0.0)
        power = max(rig_data.get('power_consumption', 0.0), 1.0)
        temperature = rig_data.get('temperature', 0.0)

        efficiency = hashrate / power if power else 0.0
        target = self.config.get('EfficiencyThreshold', 0.22)
        min_target = self.config.get('MinEfficiencyTarget', 0.25)
        temperature_limit = self.config.get('CriticalTemperature', 85.0)

        recommendations = []
        action_required = False
        throttle_percent = 0

        if efficiency < target:
            action_required = True
            throttle_percent = self.config.get('ThrottleStepPercent', 5)
            recommendations.append(
                f"EFFICIENCY_WARNING: {efficiency:.2f} MH/s/W (Ziel ≥ {target:.2f})"
            )

        if efficiency < min_target:
            recommendations.append("Senkung der Spannung und feinere Takt-Drosselung empfohlen")

        if temperature > temperature_limit:
            action_required = True
            throttle_percent = max(throttle_percent, self.config.get('ThrottleStepPercent', 5))
            recommendations.append(
                f"HIGH_TEMPERATURE: {temperature:.1f}°C > {temperature_limit:.1f}°C -> sofort drosseln"
            )

        status = "normal"
        if action_required:
            status = "throttle"

        result = {
            'rig_id': rig_id,
            'efficiency_mhs_per_watt': round(efficiency, 4),
            'target_mhs_per_watt': target,
            'throttle_percent': throttle_percent,
            'temperature': temperature,
            'status': status,
            'recommendations': recommendations,
        }

        if action_required and self.config.get('Enabled', True):
            log_event('ENERGY_EFFICIENCY_ALERT', {
                'rig_id': rig_id,
                'efficiency': result['efficiency_mhs_per_watt'],
                'temperature': temperature,
                'throttle_percent': throttle_percent,
            })

        return result

    def evaluate_all_rigs(self) -> Dict[str, Dict[str, Any]]:
        """Bewertet alle konfigurierten Rigs"""
        rigs = get_rigs_config()
        return {rig.get('id', f"rig_{i}"): self.evaluate_rig(rig) for i, rig in enumerate(rigs, start=1)}


# Globale Instanz
energy_manager = EnergyEfficiencyManager()


def evaluate_rig_efficiency(rig_data: Dict[str, Any]) -> Dict[str, Any]:
    return energy_manager.evaluate_rig(rig_data)


def evaluate_all_rigs() -> Dict[str, Dict[str, Any]]:
    return energy_manager.evaluate_all_rigs()
