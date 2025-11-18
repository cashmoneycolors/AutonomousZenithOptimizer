#!/usr/bin/env python3
"""
REGIONAL ELECTRICITY COST CALCULATOR
GeoIP-basierte Stromkosten-Berechnung mit dynamischen Tarifen
"""
import json
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from python_modules.enhanced_logging import log_event


class Region(Enum):
    """Bekannte Regionen für Stromkosten"""
    EUROPE_WEST = "europe_west"       # Deutschland, Frankreich, Benelux
    EUROPE_EAST = "europe_east"       # Osteuropa
    EUROPE_NORTH = "europe_north"     # Skandinavien
    EUROPE_SOUTH = "europe_south"     # Südeuropa
    UK = "uk"                        # Großbritannien
    US_EAST = "us_east"              # Ostküste USA
    US_WEST = "us_west"              # Westküste USA
    US_CENTRAL = "us_central"         # Zentral USA
    ASIA_EAST = "asia_east"         # Ostasien (Japan, Korea)
    ASIA_SOUTH = "asia_south"        # Südostasien
    CANADA = "canada"                # Kanada
    AUSTRALIA = "australia"          # Australien
    MIDDLE_EAST = "middle_east"      # Naher Osten
    UNKNOWN = "unknown"


@dataclass
class ElectricityTariff:
    """Stromkosten-Tarif für eine Region"""
    region: Region
    base_rate_usd_per_kwh: float
    peak_multiplier: float = 1.0
    off_peak_multiplier: float = 0.8
    tax_rate_percent: float = 0.0
    currency: str = "USD"
    source: str = "estimated"
    last_updated: Optional[float] = None

    def get_current_rate(self, timestamp: Optional[float] = None) -> float:
        """Aktueller Strompreis (mit Peak/Off-Peak-Logik)"""
        if timestamp is None:
            timestamp = time.time()

        # Einfache Peak/Off-Peak Logik (7-23 Uhr Peak)
        hour = datetime.fromtimestamp(timestamp).hour
        is_peak = 7 <= hour <= 23

        multiplier = self.peak_multiplier if is_peak else self.off_peak_multiplier
        rate_with_peak = self.base_rate_usd_per_kwh * multiplier

        # Steuern hinzufügen
        tax_amount = rate_with_peak * (self.tax_rate_percent / 100.0)

        return rate_with_peak + tax_amount


class RegionalElectricityCalculator:
    """Regionaler Stromkosten-Rechner"""

    # Bekannte GeoIP-Services
    GEOIP_SERVICES = [
        "http://ip-api.com/json/",
        "https://ipinfo.io/json"
    ]

    def __init__(self):
        self.tariffs: Dict[Region, ElectricityTariff] = {}
        self.user_location: Optional[Dict[str, Any]] = None
        self.user_region: Region = Region.UNKNOWN
        self.last_ip_check: Optional[float] = None
        self.cache_timeout = 3600  # 1 Stunde Cache

        self._load_default_tariffs()
        self._detect_user_location()

        log_event('REGIONAL_ELECTRICITY_CALCULATOR_INIT', {
            'tariffs_loaded': len(self.tariffs),
            'user_region': self.user_region.value if self.user_location else 'unknown'
        })

    def _load_default_tariffs(self):
        """Lade Standard-Tarife für bekannte Regionen"""
        self.tariffs = {
            Region.EUROPE_WEST: ElectricityTariff(
                region=Region.EUROPE_WEST,
                base_rate_usd_per_kwh=0.45,
                peak_multiplier=1.2,
                off_peak_multiplier=0.8,
                tax_rate_percent=19.0,  # EU Durchschnitt
                currency="EUR",
                source="EU Energy Statistics 2025"
            ),
            Region.EUROPE_EAST: ElectricityTariff(
                region=Region.EUROPE_EAST,
                base_rate_usd_per_kwh=0.18,
                peak_multiplier=1.1,
                off_peak_multiplier=0.9,
                tax_rate_percent=15.0,
                currency="EUR",
                source="Eastern Europe Energy Market"
            ),
            Region.EUROPE_NORTH: ElectricityTariff(
                region=Region.EUROPE_NORTH,
                base_rate_usd_per_kwh=0.38,
                peak_multiplier=1.5,  # Hohe Peak-Nutzung im Winter
                off_peak_multiplier=0.7,
                tax_rate_percent=25.0,
                currency="EUR",
                source="Nordic Energy Systems"
            ),
            Region.UK: ElectricityTariff(
                region=Region.UK,
                base_rate_usd_per_kwh=0.52,
                peak_multiplier=1.3,
                off_peak_multiplier=0.6,
                tax_rate_percent=5.0,  # UK hat separate Steuern
                currency="GBP",
                source="UK National Grid"
            ),
            Region.US_EAST: ElectricityTariff(
                region=Region.US_EAST,
                base_rate_usd_per_kwh=0.15,
                peak_multiplier=2.0,  # Hohe Peaks in Ostküste
                off_peak_multiplier=0.5,
                tax_rate_percent=0.0,  # Verschiedene lokale Steuern
                currency="USD",
                source="US EIA - East Coast Average"
            ),
            Region.US_WEST: ElectricityTariff(
                region=Region.US_WEST,
                base_rate_usd_per_kwh=0.12,
                peak_multiplier=1.8,
                off_peak_multiplier=0.6,
                tax_rate_percent=0.0,
                currency="USD",
                source="Western US Power Markets"
            ),
            Region.ASIA_EAST: ElectricityTariff(
                region=Region.ASIA_EAST,
                base_rate_usd_per_kwh=0.22,
                peak_multiplier=1.4,
                off_peak_multiplier=0.8,
                tax_rate_percent=8.0,
                currency="USD",
                source="East Asia Energy Markets"
            ),
            Region.CANADA: ElectricityTariff(
                region=Region.CANADA,
                base_rate_usd_per_kwh=0.08,
                peak_multiplier=1.6,
                off_peak_multiplier=0.7,
                tax_rate_percent=13.0,  # Provinzielle Steuern
                currency="CAD",
                source="Canadian Energy Regulator"
            ),
            Region.AUSTRALIA: ElectricityTariff(
                region=Region.AUSTRALIA,
                base_rate_usd_per_kwh=0.28,
                peak_multiplier=1.7,  # Hohe Peaks im Sommer
                off_peak_multiplier=0.5,
                tax_rate_percent=10.0,
                currency="AUD",
                source="Australian Energy Market Operator"
            )
        }

        # Update timestamps
        current_time = time.time()
        for tariff in self.tariffs.values():
            tariff.last_updated = current_time

    def _detect_user_location(self) -> bool:
        """Erkenne Benutzer-Standort via GeoIP"""
        try:
            # Cache prüfen
            if (self.last_ip_check and
                time.time() - self.last_ip_check < self.cache_timeout and
                self.user_location):
                return True

            for service_url in self.GEOIP_SERVICES:
                try:
                    response = requests.get(service_url, timeout=10)
                    if response.status_code == 200:
                        self.user_location = response.json()
                        self.last_ip_check = time.time()
                        self.user_region = self._map_location_to_region(self.user_location)
                        return True
                except Exception as e:
                    log_event('GEOIP_SERVICE_FAILED', {
                        'service': service_url,
                        'error': str(e)
                    })
                    continue

            # Fallback: Verwende Default
            log_event('GEOIP_DETECTION_FAILED', {'fallback_to_default': True})
            self.user_region = Region.EUROPE_WEST  # Sensible Default
            return False

        except Exception as e:
            log_event('LOCATION_DETECTION_ERROR', {'error': str(e)})
            return False

    def _map_location_to_region(self, location_data: Dict[str, Any]) -> Region:
        """Mappe GeoIP-Daten zu Region"""
        try:
            country = location_data.get('country', '').upper()
            region = location_data.get('regionName', '').upper()
            city = location_data.get('city', '').upper()

            # Deutschland/Österreich/Schweiz/Benelux
            if country in ['DE', 'AT', 'CH', 'NL', 'BE', 'LU']:
                return Region.EUROPE_WEST

            # UK
            if country == 'GB':
                return Region.UK

            # Nordeuropa
            if country in ['SE', 'NO', 'DK', 'FI']:
                return Region.EUROPE_NORTH

            # Osteuropa
            if country in ['PL', 'CZ', 'HU', 'RO', 'UA', 'RU']:
                return Region.EUROPE_EAST

            # USA - Ostküste
            if country == 'US' and region in ['NEW YORK', 'NEW JERSEY', 'PENNSYLVANIA',
                                            'MARYLAND', 'VIRGINIA', 'DISTRICT OF COLUMBIA',
                                            'MASSACHUSETTS', 'CONNECTICUT', 'RHODE ISLAND',
                                            'VERMONT', 'NEW HAMPSHIRE', 'MAINE']:
                return Region.US_EAST

            # USA - Westküste
            if country == 'US' and region in ['CALIFORNIA', 'WASHINGTON', 'OREGON']:
                return Region.US_WEST

            # USA - Zentral
            if country == 'US':
                return Region.US_CENTRAL

            # Kanada
            if country == 'CA':
                return Region.CANADA

            # Japan/Korea
            if country in ['JP', 'KR']:
                return Region.ASIA_EAST

            # Australien
            if country == 'AU':
                return Region.AUSTRALIA

            # Default
            return Region.EUROPE_WEST

        except Exception as e:
            log_event('REGION_MAPPING_ERROR', {'error': str(e)})
            return Region.UNKNOWN

    def get_current_electricity_rate(self, timestamp: Optional[float] = None) -> Dict[str, Any]:
        """Hole aktuellen Strompreis für Benutzer-Region"""
        if self.user_region == Region.UNKNOWN:
            # Versuche erneute Erkennung
            self._detect_user_location()

        tariff = self.tariffs.get(self.user_region)

        if not tariff:
            # Fallback zu Europa West
            tariff = self.tariffs.get(Region.EUROPE_WEST)

        if not tariff:
            return {
                'error': 'no_tariff_available',
                'region': 'unknown',
                'rate_usd_per_kwh': 0.20,  # Global Durchschnitt
                'is_estimate': True
            }

        current_rate = tariff.get_current_rate(timestamp)

        return {
            'region': tariff.region.value,
            'currency': tariff.currency,
            'rate_usd_per_kwh': round(current_rate, 4),
            'base_rate': tariff.base_rate_usd_per_kwh,
            'tax_rate_percent': tariff.tax_rate_percent,
            'source': tariff.source,
            'last_updated': tariff.last_updated,
            'is_estimate': tariff.source == 'estimated',
            'peak_hours': tariff.peak_multiplier > 1.0
        }

    def calculate_mining_costs(self, rig_config: Dict[str, Any],
                              mining_hours: float = 24.0) -> Dict[str, Any]:
        """Berechne Mining-Kosten für Rigs"""
        rate_data = self.get_current_electricity_rate()
        current_rate = rate_data['rate_usd_per_kwh']

        # Rig-Analyse
        rig_wattage = rig_config.get('power_consumption_watts', 0)
        rig_hashrate = rig_config.get('hash_rate_mhs', 0)
        rig_efficiency = rig_hashrate / rig_wattage if rig_wattage > 0 else 0

        # Kostenberechnung
        daily_consumption_kwh = (rig_wattage * mining_hours) / 1000.0
        daily_cost = daily_consumption_kwh * current_rate

        weekly_cost = daily_cost * 7
        monthly_cost = daily_cost * 30

        return {
            'currency': rate_data['currency'],
            'electricity_rate_usd_per_kwh': current_rate,
            'rig_wattage': rig_wattage,
            'daily_consumption_kwh': round(daily_consumption_kwh, 2),
            'daily_cost_usd': round(daily_cost, 2),
            'weekly_cost_usd': round(weekly_cost, 2),
            'monthly_cost_usd': round(monthly_cost, 2),
            'rig_efficiency_mhs_per_watt': round(rig_efficiency, 4),
            'region': rate_data['region'],
            'is_estimate': rate_data.get('is_estimate', True)
        }

    def compare_regions(self, rig_config: Dict[str, Any]) -> Dict[str, Any]:
        """Vergleiche Stromkosten über verschiedene Regionen"""
        comparison = {}
        base_rig = self.calculate_mining_costs(rig_config, 1)  # 1 Stunde

        for region, tariff in self.tariffs.items():
            rate = tariff.get_current_rate()
            hourly_cost = (rig_config.get('power_consumption_watts', 0) / 1000.0) * rate

            comparison[region.value] = {
                'rate_usd_per_kwh': round(rate, 4),
                'hourly_cost_usd': round(hourly_cost, 4),
                'currency': tariff.currency,
                'tax_rate_percent': tariff.tax_rate_percent
            }

        # Sortiere nach günstigsten Kosten
        sorted_regions = sorted(comparison.items(),
                              key=lambda x: x[1]['hourly_cost_usd'])

        return {
            'base_rig_cost_per_hour': round(base_rig['daily_cost_usd'], 4),
            'cheapest_region': sorted_regions[0][0],
            'most_expensive_region': sorted_regions[-1][0],
            'cost_difference_percent': round(
                ((sorted_regions[-1][1]['hourly_cost_usd'] - sorted_regions[0][1]['hourly_cost_usd']) /
                 sorted_regions[0][1]['hourly_cost_usd']) * 100, 1
            ),
            'comparison': dict(sorted_regions)
        }

    def get_location_info(self) -> Dict[str, Any]:
        """Hole Standort-Informationen"""
        return {
            'location_detected': self.user_location is not None,
            'detected_region': self.user_region.value if self.user_location else 'unknown',
            'ip_check_timestamp': self.last_ip_check,
            'cache_valid': (time.time() - (self.last_ip_check or 0)) < self.cache_timeout,
            'location_data': self.user_location
        }

    def update_tariff_data(self, region: Region, new_rate: float, source: str = "manual"):
        """Aktualisiere Tarif-Daten für Region"""
        if region in self.tariffs:
            tariff = self.tariffs[region]
            tariff.base_rate_usd_per_kwh = new_rate
            tariff.last_updated = time.time()
            tariff.source = source

            log_event('TARIFF_UPDATED', {
                'region': region.value,
                'new_rate': new_rate,
                'source': source
            })

            return True
        return False

    def export_tariff_data(self, filename: Optional[str] = None) -> Path:
        """Exportiere alle Tarif-Daten als JSON"""
        export_dir = Path('reports/electricity')
        export_dir.mkdir(parents=True, exist_ok=True)

        filename = filename or f"electricity_rates_{int(time.time())}.json"

        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'user_region': self.user_region.value if self.user_location else 'unknown',
            'tariffs': {region.value: {
                'base_rate_usd_per_kwh': tariff.base_rate_usd_per_kwh,
                'peak_multiplier': tariff.peak_multiplier,
                'off_peak_multiplier': tariff.off_peak_multiplier,
                'tax_rate_percent': tariff.tax_rate_percent,
                'currency': tariff.currency,
                'source': tariff.source,
                'last_updated': tariff.last_updated
            } for region, tariff in self.tariffs.items()}
        }

        export_path = export_dir / filename
        with export_path.open('w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        return export_path


# Global instance
regional_electricity = RegionalElectricityCalculator()


def get_current_electricity_price() -> Dict[str, Any]:
    """Öffentliche Funktion: Hole aktuellen Strompreis"""
    return regional_electricity.get_current_electricity_rate()


def calculate_rig_electricity_cost(rig_config: Dict[str, Any],
                                  mining_hours: float = 24.0) -> Dict[str, Any]:
    """Öffentliche Funktion: Berechne Stromkosten für Rig"""
    return regional_electricity.calculate_mining_costs(rig_config, mining_hours)


def compare_electricity_rates(rig_config: Dict[str, Any]) -> Dict[str, Any]:
    """Öffentliche Funktion: Vergleiche verschiedene Regionen"""
    return regional_electricity.compare_regions(rig_config)


def get_location_detection_status() -> Dict[str, Any]:
    """Öffentliche Funktion: Hole Standort-Erkennungsstatus"""
    return regional_electricity.get_location_info()


if __name__ == '__main__':
    # Demo usage
    print("⚡ REGIONAL ELECTRICITY COST CALCULATOR")
    print("=" * 50)

    # Location detection
    print("📍 Detecting user location...")
    location_info = regional_electricity.get_location_info()
    print(f"   Region: {location_info['detected_region']}")
    print(f"   Detected: {location_info['location_detected']}")

    # Current electricity rate
    print("
💰 Current Electricity Rate:"    rate_info = regional_electricity.get_current_electricity_rate()
    print(f"   Region: {rate_info['region']}")
    print(f"   Rate: ${rate_info['rate_usd_per_kwh']:.4f}/kWh")
    print(f"   Currency: {rate_info['currency']}")
    print(f"   Source: {rate_info['source']}")

    # Sample rig cost calculation
    print("
🔧 Mining Rig Cost Simulation:"    sample_rig = {
        'name': 'RTX 3080 Mining Rig',
        'power_consumption_watts': 320,
        'hash_rate_mhs': 95.0
    }

    cost_calc = regional_electricity.calculate_mining_costs(sample_rig, 24)
    print(f"   Rig: {sample_rig['name']}")
    print(f"   Power: {sample_rig['power_consumption_watts']}W")
    print(f"   Daily Consumption: {cost_calc['daily_consumption_kwh']:.2f} kWh")
    print(f"   Daily Cost: ${cost_calc['daily_cost_usd']:.2f}")
    print(f"   Monthly Cost: ${cost_calc['monthly_cost_usd']:.2f}")

    # Region comparison
    print("
📊 Regional Cost Comparison:"    comparison = regional_electricity.compare_regions(sample_rig)
    print(f"   Cheapest: {comparison['cheapest_region']} (${comparison['comparison'][comparison['cheapest_region']]['hourly_cost_usd']:.4f}/h)")
    print(f"   Most Expensive: {comparison['most_expensive_region']} (${comparison['comparison'][comparison['most_expensive_region']]['hourly_cost_usd']:.4f}/h)")
    print(f"   Price Difference: {comparison['cost_difference_percent']:.1f}%")

    print("
📄 Exporting tariff data..."    exported = regional_electricity.export_tariff_data()
    print(f"   Exported to: {exported}")

    print("
✅ Regional Electricity Calculator ready!"
