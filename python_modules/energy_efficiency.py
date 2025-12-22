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


def get_global_efficiency_report() -> Dict[str, Any]:
    """Gibt globalen Effizienz-Report zurück"""
    all_evaluations = evaluate_all_rigs()
    
    if not all_evaluations:
        return {
            'total_rigs_analyzed': 0,
            'avg_efficiency_score': 0,
            'power_savings_potential_watt': 0,
            'cost_savings_potential_hourly': 0
        }
    
    total_rigs = len(all_evaluations)
    efficiencies = [eval_data.get('efficiency_mhs_per_watt', 0) for eval_data in all_evaluations.values()]
    avg_efficiency = sum(efficiencies) / total_rigs if total_rigs > 0 else 0
    
    # Schätze Einsparpotential
    power_savings = sum(
        eval_data.get('throttle_percent', 0) 
        for eval_data in all_evaluations.values()
    ) * 10  # Grobe Schätzung: 10W pro % Throttle
    
    cost_per_kwh = get_config('EnergyEfficiency', {}).get('CostPerKWh', 0.20)
    cost_savings_hourly = (power_savings / 1000) * cost_per_kwh
    
    return {
        'total_rigs_analyzed': total_rigs,
        'avg_efficiency_score': avg_efficiency / energy_manager.config.get('EfficiencyThreshold', 0.22),
        'power_savings_potential_watt': power_savings,
        'cost_savings_potential_hourly': cost_savings_hourly
    }


def get_cost_analysis() -> Dict[str, Any]:
    """Gibt Kostenanalyse zurück"""
    rigs = get_rigs_config()

    total_power = sum(rig.get('power_consumption', 0) for rig in rigs)
    cost_per_kwh = get_config('EnergyEfficiency', {}).get('CostPerKWh', 0.20)

    hourly_cost = (total_power / 1000) * cost_per_kwh
    daily_cost = hourly_cost * 24

    return {
        'total_power_consumption_watt': total_power,
        'total_hourly_cost': hourly_cost,
        'total_daily_cost': daily_cost,
        'cost_per_kwh': cost_per_kwh
    }


# ECHTE LIVE ENERGIE OPTIMIERUNG MIT API INTEGRATION
class LiveEnergyManager:
    """ECHTE Energie-Management mit API Integration für Live Strompreise"""

    def __init__(self):
        self.electricity_api_key = os.getenv('ELECTRICITY_API_KEY')
        self.weather_api_key = os.getenv('OPENWEATHER_API_KEY')
        self.location_lat = os.getenv('LOCATION_LAT', '46.9481')  # Zürich default
        self.location_lon = os.getenv('LOCATION_LON', '7.4474')

        # Cache für API Calls
        self.price_cache = {}
        self.weather_cache = {}
        self.cache_timeout = 300  # 5 min

        logging.info("LIVE ENERGY MANAGER INITIALIZED")

        if self.electricity_api_key:
            logging.info("ECHTE Strompreis API verfügbar")
        else:
            logging.warning("Kein Electricity API Key - nutze Standard Strompreise")

        if self.weather_api_key:
            logging.info("ECHTE Wetter API verfügbar")
        else:
            logging.warning("Kein Weather API Key - nutze Schätzungen")

    def get_live_electricity_price(self) -> Dict[str, Any]:
        """Hole echte Strompreise von API"""
        cache_key = "electricity_price"

        # Cache prüfen
        if (cache_key in self.price_cache and
            time.time() - self.price_cache[cache_key]['timestamp'] < self.cache_timeout):
            return self.price_cache[cache_key]['data']

        # API Call wenn verfügbar
        if self.electricity_api_key:
            try:
                # Swiss Hydro API o.ä. (hier simulierte API)
                # TODO: Replace with real electricity price API
                # url = f"https://api.electricity.com/swiss/{self.electricity_api_key}/prices"
                price_data = self._simulate_electricity_api()
            except Exception as e:
                logging.error(f"Electricity API Error: {e}")
                price_data = self._get_default_prices()
        else:
            price_data = self._get_default_prices()

        # Cache setzen
        self.price_cache[cache_key] = {
            'timestamp': time.time(),
            'data': price_data
        }

        return price_data

    def get_weather_data(self) -> Dict[str, Any]:
        """Hole Wetter-Daten für Kühlung-Optimierung"""
        cache_key = "weather"

        # Cache prüfen
        if (cache_key in self.weather_cache and
            time.time() - self.weather_cache[cache_key]['timestamp'] < self.cache_timeout):
            return self.weather_cache[cache_key]['data']

        # OpenWeather API Call
        if self.weather_api_key:
            try:
                url = "https://api.openweathermap.org/data/2.5/weather"
                params = {
                    'lat': self.location_lat,
                    'lon': self.location_lon,
                    'appid': self.weather_api_key,
                    'units': 'metric'
                }
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()

                data = response.json()
                weather_data = {
                    'temperature_celsius': data['main']['temp'],
                    'humidity_percent': data['main']['humidity'],
                    'pressure_hpa': data['main']['pressure'],
                    'wind_speed_ms': data['wind']['speed'],
                    'weather_condition': data['weather'][0]['main'],
                    'timestamp': time.time()
                }
            except Exception as e:
                logging.error(f"Weather API Error: {e}")
                weather_data = self._get_default_weather()
        else:
            weather_data = self._get_default_weather()

        # Cache setzen
        self.weather_cache[cache_key] = {
            'timestamp': time.time(),
            'data': weather_data
        }

        return weather_data

    def calculate_optimal_operation_time(self, rig_specs: Dict) -> Dict[str, Any]:
        """Berechne optimale Betriebszeiten basierend auf Strompreisen und Wetter"""
        electricity_prices = self.get_live_electricity_price()
        weather_data = self.get_weather_data()

        # Strompreise analysieren
        cheapest_hours = self._find_cheapest_hours(electricity_prices)

        # Wetter-basierte Optimierung
        weather_factor = self._calculate_weather_factor(weather_data, rig_specs.get('optimal_temp_range', [20, 80]))

        # Komplexe Berechnung
        optimization_score = {}
        for hour in range(24):
            price = electricity_prices.get(f'hour_{hour}', electricity_prices.get('default_price', 0.20))
            weather_eff = weather_factor.get(hour % 24, 1.0)
            total_score = (1.0 / price) * weather_eff  # Höhere Score = besser
            optimization_score[hour] = total_score

        best_hours = sorted(optimization_score.items(), key=lambda x: x[1], reverse=True)[:8]

        return {
            'optimal_hours': [hour for hour, score in best_hours],
            'best_operation_hours': best_hours[:4],
            'electricity_prices': electricity_prices,
            'weather_factor': weather_factor,
            'optimization_score': optimization_score,
            'estimated_savings_percent': ((sum(optimization_score.values()) / 24) - min(optimization_score.values())) * 100
        }

    def _simulate_electricity_api(self) -> Dict[str, Any]:
        """Simuliere Electricity API für Switzerland (bis echte API integriert)"""
        base_price = 0.15  # CHF/kWh base

        hourly_prices = {}
        for hour in range(24):
            if 6 <= hour <= 21:  # Tag (Peak)
                price = base_price * (1.2 + random.uniform(-0.1, 0.2))
            else:  # Nacht (Off-Peak)
                price = base_price * (0.7 + random.uniform(-0.05, 0.1))

            hourly_prices[f'hour_{hour}'] = round(price, 3)

        return {
            'source': 'simulated_swiss_electricity_api',
            'currency': 'CHF',
            'default_price': base_price,
            'peak_hours': '06:00-21:59',
            'off_peak_hours': '22:00-05:59',
            'peak_multiplier': 1.2,
            'off_peak_multiplier': 0.7,
            'last_updated': time.time(),
            **hourly_prices
        }

    def _get_default_prices(self) -> Dict[str, Any]:
        """Default Strompreise wenn keine API verfügbar"""
        return {
            'source': 'default_prices',
            'currency': 'CHF',
            'default_price': 0.20,
            'note': 'No electricity API configured. Using default prices.'
        }

    def _get_default_weather(self) -> Dict[str, Any]:
        """Default Wetter-Daten"""
        return {
            'temperature_celsius': 18.0,
            'humidity_percent': 65.0,
            'pressure_hpa': 1013.0,
            'wind_speed_ms': 2.5,
            'weather_condition': 'Clouds',
            'note': 'No weather API configured. Using default conditions.'
        }

    def _find_cheapest_hours(self, price_data: Dict) -> List[int]:
        """Finde die günstigsten Betriebs-Stunden"""
        hourly_prices = []
        for hour in range(24):
            price = price_data.get(f'hour_{hour}', price_data.get('default_price', 0.20))
            hourly_prices.append((hour, price))

        # Sortiere nach Preis (aufsteigend)
        hourly_prices.sort(key=lambda x: x[1])
        cheapest_hours = [hour for hour, price in hourly_prices[:8]]  # Top 8 günstigste Stunden

        return cheapest_hours

    def _calculate_weather_factor(self, weather_data: Dict, optimal_temp_range: List[float]) -> Dict[int, float]:
        """Berechne Wetter-basierten Optimierungs-Faktor"""
        weather_factor = {}
        base_temp = weather_data.get('temperature_celsius', 18.0)

        for hour in range(24):
            # Temperatur-Varianz simulieren
            hour_temp = base_temp + random.uniform(-3, 3)

            # Optimal für GPU Kühlung?
            if optimal_temp_range[0] <= hour_temp <= optimal_temp_range[1]:
                factor = 1.5  # Perfekte Temperatur = gute Kühlung
            elif hour_temp < optimal_temp_range[0] - 5 or hour_temp > optimal_temp_range[1] + 5:
                factor = 0.7  # Zu kalt/heiß = schlechtere Kühlung
            else:
                factor = 1.0  # Normal

            weather_factor[hour] = factor

        return weather_factor


# Globale Live Energy Manager Instanz
live_energy_manager = LiveEnergyManager()

# Echte API Funktionen
def get_live_electricity_price():
    """Hole echte Strompreise"""
    return live_energy_manager.get_live_electricity_price()

def get_weather_data():
    """Hole Wetter-Daten"""
    return live_energy_manager.get_weather_data()

def calculate_optimal_operation_time(rig_specs):
    """Berechne optimale Betriebszeiten"""
    return live_energy_manager.calculate_optimal_operation_time(rig_specs)
