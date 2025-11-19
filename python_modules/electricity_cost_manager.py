#!/usr/bin/env python3
"""
ELECTRICITY COST MANAGER MODULE
Stromkosten-Berechnung pro Region und dynamische Mining-Optimierung
Deutschlandweit optimiert für Strompreise 2025
"""
import json
from datetime import datetime, time
from typing import Dict, List, Any, Optional
from python_modules.config_manager import get_config
from python_modules.alert_system import send_custom_alert
from python_modules.enhanced_logging import log_event

class ElectricityCostManager:
    """Verwaltet Stromkosten für optimale Mining-Zeiten"""

    def __init__(self):
        self.cost_config = get_config('ElectricityCostManager', {})

        # Schweizer Strompreis-Datenbank (Stand 2025)
        self.peak_prices = {
            'schweiz': {
                'winter': {'daily_avg': 0.25, 'night_tariff': 0.18, 'peak_tariff': 0.32},
                'summer': {'daily_avg': 0.22, 'night_tariff': 0.15, 'peak_tariff': 0.28}
            },
            'zuerich': {
                'winter': {'daily_avg': 0.27, 'night_tariff': 0.19, 'peak_tariff': 0.34},
                'summer': {'daily_avg': 0.24, 'night_tariff': 0.16, 'peak_tariff': 0.30}
            },
            'genf': {
                'winter': {'daily_avg': 0.26, 'night_tariff': 0.18, 'peak_tariff': 0.33},
                'summer': {'daily_avg': 0.23, 'night_tariff': 0.15, 'peak_tariff': 0.29}
            },
            'basel': {
                'winter': {'daily_avg': 0.26, 'night_tariff': 0.18, 'peak_tariff': 0.33},
                'summer': {'daily_avg': 0.23, 'night_tariff': 0.15, 'peak_tariff': 0.29}
            },
            'bern': {
                'winter': {'daily_avg': 0.24, 'night_tariff': 0.17, 'peak_tariff': 0.31},
                'summer': {'daily_avg': 0.21, 'night_tariff': 0.14, 'peak_tariff': 0.27}
            },
            'wallis': {
                'winter': {'daily_avg': 0.23, 'night_tariff': 0.16, 'peak_tariff': 0.30},
                'summer': {'daily_avg': 0.20, 'night_tariff': 0.13, 'peak_tariff': 0.26}
            },
            'graubuenden': {
                'winter': {'daily_avg': 0.22, 'night_tariff': 0.15, 'peak_tariff': 0.29},
                'summer': {'daily_avg': 0.19, 'night_tariff': 0.12, 'peak_tariff': 0.25}
            },
            'luzern': {
                'winter': {'daily_avg': 0.25, 'night_tariff': 0.17, 'peak_tariff': 0.32},
                'summer': {'daily_avg': 0.22, 'night_tariff': 0.14, 'peak_tariff': 0.28}
            },
            'thurgau': {
                'winter': {'daily_avg': 0.24, 'night_tariff': 0.17, 'peak_tariff': 0.31},
                'summer': {'daily_avg': 0.21, 'night_tariff': 0.14, 'peak_tariff': 0.27}
            }
        }

        # Zeitgesteuerte Tarife (Standard in Deutschland)
        self.time_tariffs = {
            'night_tariff_start': time(22, 0),     # 22:00 Uhr
            'night_tariff_end': time(6, 0),        # 06:00 Uhr
            'peak_tariff_start': time(7, 0),       # 07:00 Uhr
            'peak_tariff_end': time(20, 0)         # 20:00 Uhr
        }

        # Aktuelle Preise speichern
        self.current_region = 'schweiz'
        self.current_season = 'winter'  # Oder 'summer'

        print("[POWER] Electricity Cost Manager initialized")
        print(f"[POWER] Current region: {self.current_region}")
        print(f"[POWER] Current season: {self.current_season}")

    def get_current_electricity_cost(self, region: str = None, time_override: datetime = None) -> float:
        """Gibt aktuellen Strompreis basierend auf Region und Zeit zurück"""
        if region is None:
            region = self.current_region

        current_time = time_override or datetime.now()
        season = self.get_season(current_time)
        tariff_type = self.get_tariff_type(current_time)

        if region not in self.peak_prices:
            region = 'deutschland'

        regional_prices = self.peak_prices[region][season]

        if tariff_type == 'night':
            cost = regional_prices['night_tariff']
        elif tariff_type == 'peak':
            cost = regional_prices['peak_tariff']
        else:  # standard
            cost = regional_prices['daily_avg']

        return cost

    def calculate_mining_profit_hourly(self, hash_rate: float, power_consumption: float,
                                      hours: int = 24, region: str = None) -> Dict[str, Any]:
        """Berechnet Mining-Profit über Zeitraum mit dynamischen Stromkosten"""
        if region is None:
            region = self.current_region

        total_hash_processed = hash_rate * hours
        total_electricity_cost = 0
        revenue_by_hour = []
        cost_by_hour = []

        for hour in range(hours):
            # Simuliere Zeit für diese Stunde
            current_hour_time = datetime.now().replace(hour=hour % 24)

            # Aktueller Strompreis für diese Stunde
            cost_per_kwh = self.get_current_electricity_cost(region, current_hour_time)

            # Stromkosten für diese Stunde
            hourly_cost = (power_consumption / 1000) * cost_per_kwh  # kWh * Preis/kWh
            total_electricity_cost += hourly_cost

            # Annahme: Hashrate bringt täglich ca. CHF 45 (Beispielwert)
            # In Realität würde das von Mining-API kommen
            hourly_revenue = (hash_rate / 24) * 1.875  # CHF pro MH/s pro Tag
            revenue_by_hour.append(hourly_revenue)
            cost_by_hour.append(hourly_cost)

        total_revenue = sum(revenue_by_hour)
        net_profit = total_revenue - total_electricity_cost
        roi_hours = hours if net_profit > 0 else float('inf')

        return {
            'total_revenue': total_revenue,
            'total_electricity_cost': total_electricity_cost,
            'net_profit': net_profit,
            'profit_margin_percent': (net_profit / total_revenue * 100) if total_revenue > 0 else 0,
            'break_even_hours': roi_hours,
            'average_cost_per_kwh': total_electricity_cost / (power_consumption * hours / 1000),
            'hourly_breakdown': {
                'revenue': revenue_by_hour,
                'cost': cost_by_hour
            },
            'region': region,
            'power_consumption_w': power_consumption
        }

    def find_optimal_mining_hours(self, power_consumption: float, region: str = None,
                                 required_profit: float = 50) -> Dict[str, Any]:
        """Findet optimale Mining-Stunden mit höchstem Profit"""
        if region is None:
            region = self.current_region

        optimal_hours = []
        total_profit_best = float('-inf')

        # Teste alle 24 Stunden-Patterns
        for start_hour in range(24):
            # Simuliere Mining für 8 Stunden ab start_hour
            hours_mined = 8
            hash_rate = 100  # Beispiel MH/s - würde aus Rig-Konfig kommen

            profit_calc = self.calculate_mining_profit_hourly(
                hash_rate, power_consumption, hours_mined, region
            )

            net_profit = profit_calc['net_profit']

            if net_profit > required_profit and net_profit > total_profit_best:
                total_profit_best = net_profit
                optimal_hours = {
                    'start_hour': start_hour,
                    'end_hour': (start_hour + hours_mined) % 24,
                    'hours_mined': hours_mined,
                    'net_profit': net_profit,
                    'profit_margin': profit_calc['profit_margin_percent'],
                    'electricity_cost': profit_calc['total_electricity_cost']
                }

        return optimal_hours if optimal_hours else {'error': 'No profitable hours found'}

    def optimize_power_consumption(self, current_power: float, target_efficiency: float = 0.85) -> Dict[str, Any]:
        """Optimiert Stromverbrauch für maximale Efficiency"""
        # Annahme: Beste Efficiency bei 80-90% Last
        optimal_power_range = (current_power * 0.8, current_power * 0.95)

        recommendation = {
            'current_power': current_power,
            'optimal_range': optimal_power_range,
            'target_efficiency': target_efficiency,
            'recommended_power': current_power * target_efficiency,
            'power_savings_percent': (1 - target_efficiency) * 100 if current_power > optimal_power_range[0] else 0,
            'efficiency_gain_percent': 10  # Geschätzt
        }

        return recommendation

    def get_season(self, date: datetime) -> str:
        """Bestimmt Jahreszeit für Strompreis-Kalkulation"""
        month = date.month
        if month in [11, 12, 1, 2, 3]:  # Winter: Nov-Mar
            return 'winter'
        else:  # Sommer: Apr-Okt
            return 'summer'

    def get_tariff_type(self, current_time: datetime) -> str:
        """Bestimmt aktuellen Stromtarif-Typ"""
        current_time_only = current_time.time()

        night_start = self.time_tariffs['night_tariff_start']
        night_end = self.time_tariffs['night_tariff_end']

        # Nacht-Tarif (22:00 - 06:00)
        if current_time_only >= night_start or current_time_only <= night_end:
            return 'night'

        # Peak-Tarif (07:00 - 20:00)
        peak_start = self.time_tariffs['peak_tariff_start']
        peak_end = self.time_tariffs['peak_tariff_end']

        if peak_start <= current_time_only <= peak_end:
            return 'peak'

        return 'standard'  # Standard-Tarif (06:00 - 07:00, 20:00 - 22:00)

    def set_region(self, region: str) -> bool:
        """Setzt Strompreis-Region"""
        if region in self.peak_prices:
            self.current_region = region
            send_custom_alert("Electricity Region",
                            f"Electricity cost region changed to {region}",
                            "[POWER]")
            log_event('ELECTRICITY_REGION_CHANGE', {'region': region})
            return True

        return False

    def get_cost_analysis(self, rig_specs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Gibt umfassende Kostenanalyse für Rig-Flotte"""
        total_power_consumption = sum(rig.get('power_consumption', 0) for rig in rig_specs)
        total_hash_rate = sum(rig.get('hash_rate', 0) for rig in rig_specs)

        current_cost_per_kwh = self.get_current_electricity_cost()

        # Tagesanalyse
        daily_analysis = self.calculate_mining_profit_hourly(
            total_hash_rate, total_power_consumption, 24
        )

        # Wochentliche Analyse (mit optimalen Stunden)
        optimal_schedule = self.find_optimal_mining_hours(total_power_consumption)

        return {
            'fleet_analysis': {
                'total_rigs': len(rig_specs),
                'total_power_consumption_w': total_power_consumption,
                'total_hash_rate_mh': total_hash_rate,
                'power_efficiency_mh_per_w': total_hash_rate / total_power_consumption if total_power_consumption > 0 else 0
            },
            'current_costs': {
                'cost_per_kwh': current_cost_per_kwh,
                'current_tariff': self.get_tariff_type(datetime.now()),
                'region': self.current_region,
                'season': self.get_season(datetime.now())
            },
            'daily_projection': daily_analysis,
            'optimal_schedule': optimal_schedule,
            'savings_potential': {
                'switch_to_cheap_tariffs': f"CHF {(daily_analysis['total_electricity_cost'] * 0.3):.2f}/day",
                'optimize_operation_hours': f"CHF {(daily_analysis['net_profit'] * 0.2):.2f}/day potential increase"
            }
        }

    def monitor_electricity_costs(self) -> Dict[str, Any]:
        """Überwacht Stromkosten kontinuierlich"""
        current_cost = self.get_current_electricity_cost()
        tariff = self.get_tariff_type(datetime.now())

        # Empfehlungen basierend auf aktueller Situation
        recommendations = []

        if tariff == 'peak':
            recommendations.append("Consider reducing mining intensity during peak hours")
        elif tariff == 'night':
            recommendations.append("Optimal time for maximum mining operations")

        if current_cost > 0.45:  # Hoher Preis
            recommendations.append("High electricity costs detected - monitor closely")
        elif current_cost < 0.25:  # Sehr günstig
            recommendations.append("Very low electricity costs - maximize mining operations")

        return {
            'current_cost_per_kwh': current_cost,
            'current_tariff': tariff,
            'recommendations': recommendations,
            'cost_trend': 'stable',  # Would track historical trends
            'alerts_active': len(recommendations) > 0
        }


# Zusätzliche Utility-Funktionen laut Spezifikation

def get_cost_for_rig(rig: Dict[str, Any], region: str | None = None) -> Dict[str, Any]:
    """Berechnet Stromkosten pro Stunde für ein einzelnes Rig."""
    power_w = float(rig.get('power_consumption', 0) or 0)
    cost_per_kwh = electricity_cost_manager.get_current_electricity_cost(region)
    kwh_per_hour = power_w / 1000.0
    return {
        'rig_id': rig.get('id', 'unknown'),
        'cost_per_hour': kwh_per_hour * cost_per_kwh,
        'kwh_per_hour': kwh_per_hour,
        'cost_per_kwh': cost_per_kwh,
        'region': region or electricity_cost_manager.current_region,
    }


def calculate_net_profit(rig: Dict[str, Any], hours: int = 24, region: str | None = None) -> Dict[str, Any]:
    """Berechnet Nettoprofit eines Rigs (Einnahmen - Stromkosten). Sendet Alert bei negativem Profit."""
    power_w = float(rig.get('power_consumption', 0) or 0)
    # Einnahmen-Schätzung: bevorzugt profit_per_day, sonst einfache Hashrate-Schätzung
    profit_per_day = rig.get('profit_per_day')
    if profit_per_day is None:
        hashrate = float(rig.get('hash_rate', 0) or 0)
        # sehr konservative Faustformel (CHF) – Platzhalter bis echte API-Daten genutzt werden
        profit_per_day = hashrate * 0.015
    revenue = float(profit_per_day) * (hours / 24.0)

    cost_snapshot = get_cost_for_rig(rig, region)
    electricity_cost = cost_snapshot['cost_per_hour'] * hours
    net = revenue - electricity_cost

    result = {
        'rig_id': rig.get('id', 'unknown'),
        'hours': hours,
        'revenue': revenue,
        'electricity_cost': electricity_cost,
        'net_profit': net,
        'region': cost_snapshot['region'],
        'cost_per_kwh': cost_snapshot['cost_per_kwh'],
    }

    if net < 0:
        try:
            send_custom_alert(
                'Negative Net Profit',
                f"Rig {result['rig_id']} Nettoprofit negativ: CHF {net:.2f} in {hours}h",
                '[POWER]'
            )
        except Exception:
            pass

    return result

# Globale Electricity Cost Manager Instanz
electricity_cost_manager = ElectricityCostManager()

# Convenience-Funktionen
def get_current_electricity_cost(region=None):
    """Gibt aktuellen Strompreis zurück"""
    return electricity_cost_manager.get_current_electricity_cost(region)

def calculate_electricity_profit(hash_rate, power_consumption, hours=24, region=None):
    """Berechnet Stromkosten-basierten Profit"""
    return electricity_cost_manager.calculate_mining_profit_hourly(hash_rate, power_consumption, hours, region)

def find_optimal_mining_hours(power_consumption, region=None, required_profit=50):
    """Findet optimale Mining-Stunden"""
    return electricity_cost_manager.find_optimal_mining_hours(power_consumption, region, required_profit)

def get_electricity_cost_analysis():
    """Gibt Kostenanalyse zurück"""
    return electricity_cost_manager.get_cost_analysis([])

def set_electricity_region(region):
    """Setzt Strompreis-Region"""
    return electricity_cost_manager.set_region(region)

if __name__ == "__main__":
    print("ELECTRICITY COST MANAGER - Deutschland Strompreis-Optimierung")
    print("=" * 65)

    print("[POWER] Teste Stromkosten-Manager...")

    # Aktueller Preis
    current_cost = get_current_electricity_cost()
    print(f"[POWER] Aktueller Strompreis: {current_cost:.3f} CHF/kWh")
    print(f"[POWER] Aktuelle Zeit-Tarif: {electricity_cost_manager.get_tariff_type(datetime.now())}")

    # Profit-Berechnung
    profit_calc = calculate_electricity_profit(hash_rate=120, power_consumption=450, hours=24)
    print(f"[POWER] Tages-Profit: CHF {profit_calc['net_profit']:.2f}")
    print(f"[POWER] Stromkosten: CHF {profit_calc['total_electricity_cost']:.2f}")
    print(f"[POWER] Profit-Marge: {profit_calc['profit_margin_percent']:.1f}%")

    # Optimale Mining-Stunden
    optimal = find_optimal_mining_hours(power_consumption=450)
    if isinstance(optimal, dict) and 'error' not in optimal:
        print(f"[POWER] Optimale Mining-Zeit: {optimal['start_hour']:02d}:00 - {optimal['end_hour']:02d}:00 Uhr")
        print(f"[POWER] Maximale Tages-Profit: CHF {optimal['net_profit']:.2f}")
    else:
        print("[POWER] Keine optimalen Mining-Stunden gefunden")

    print("\n[POWER] ELECTRICITY COST MANAGER BEREIT!")
    print("Verwende get_current_electricity_cost(), calculate_electricity_profit(), find_optimal_mining_hours()")
    print("Region setzen mit set_electricity_region('bayern') etc.")
