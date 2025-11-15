"""
Stromkosten-Modul
Regionale Strompreis-Datenbank und dynamische Profit-Berechnung
"""

import json
import logging
from typing import Dict, Optional, List
from datetime import datetime, time
from pathlib import Path

class ElectricityCostManager:
    """Verwaltung regionaler Stromkosten und Tarifoptimierung"""
    
    # Regionale Durchschnittsstrompreise (USD pro kWh)
    REGIONAL_RATES = {
        'DE': {  # Deutschland
            'standard': 0.35,
            'night': 0.22,  # Nachtstrom 22:00 - 6:00
            'industrial': 0.18,
            'renewable': 0.28
        },
        'US': {  # USA (Durchschnitt)
            'standard': 0.13,
            'night': 0.09,
            'industrial': 0.07,
            'renewable': 0.11
        },
        'CN': {  # China
            'standard': 0.08,
            'night': 0.05,
            'industrial': 0.06,
            'renewable': 0.07
        },
        'IS': {  # Island (günstig, viel Geothermie)
            'standard': 0.06,
            'night': 0.04,
            'industrial': 0.03,
            'renewable': 0.05
        },
        'NO': {  # Norwegen (viel Wasserkraft)
            'standard': 0.09,
            'night': 0.06,
            'industrial': 0.05,
            'renewable': 0.07
        },
        'CA': {  # Kanada
            'standard': 0.12,
            'night': 0.08,
            'industrial': 0.06,
            'renewable': 0.10
        },
        'RU': {  # Russland
            'standard': 0.05,
            'night': 0.03,
            'industrial': 0.04,
            'renewable': 0.04
        },
        'KZ': {  # Kasachstan
            'standard': 0.04,
            'night': 0.02,
            'industrial': 0.03,
            'renewable': 0.03
        }
    }
    
    def __init__(self, region: str = 'DE', tariff_type: str = 'standard'):
        self.logger = logging.getLogger(__name__)
        self.region = region.upper()
        self.tariff_type = tariff_type
        self.custom_rates_file = Path('electricity_custom_rates.json')
        self.load_custom_rates()
        
    def load_custom_rates(self):
        """Lade benutzerdefinierte Tarife"""
        if self.custom_rates_file.exists():
            try:
                with open(self.custom_rates_file, 'r') as f:
                    custom_rates = json.load(f)
                    # Merge mit Standard-Raten
                    for region, rates in custom_rates.items():
                        if region in self.REGIONAL_RATES:
                            self.REGIONAL_RATES[region].update(rates)
                        else:
                            self.REGIONAL_RATES[region] = rates
                self.logger.info(f"✅ Custom rates geladen: {self.custom_rates_file}")
            except Exception as e:
                self.logger.error(f"❌ Fehler beim Laden custom rates: {e}")
                
    def save_custom_rate(self, region: str, tariff_type: str, rate: float):
        """Speichere benutzerdefinierten Tarif"""
        custom_rates = {}
        if self.custom_rates_file.exists():
            with open(self.custom_rates_file, 'r') as f:
                custom_rates = json.load(f)
        
        if region not in custom_rates:
            custom_rates[region] = {}
        
        custom_rates[region][tariff_type] = rate
        
        with open(self.custom_rates_file, 'w') as f:
            json.dump(custom_rates, f, indent=2)
        
        self.logger.info(f"✅ Custom rate gespeichert: {region}/{tariff_type} = ${rate}/kWh")
        
    def get_rate(self, hour: Optional[int] = None) -> float:
        """Hole aktuellen Strompreis pro kWh
        
        Args:
            hour: Stunde des Tages (0-23), None = current hour
        """
        if hour is None:
            hour = datetime.now().hour
        
        # Prüfe ob Nachttarif gilt (22:00 - 6:00)
        if 22 <= hour or hour < 6:
            tariff = 'night'
        else:
            tariff = self.tariff_type
        
        if self.region not in self.REGIONAL_RATES:
            self.logger.warning(f"⚠️ Region {self.region} nicht gefunden, nutze DE")
            self.region = 'DE'
        
        rate = self.REGIONAL_RATES[self.region].get(tariff, 
                                                      self.REGIONAL_RATES[self.region]['standard'])
        
        return rate
        
    def calculate_daily_cost(self, power_watts: float, hours: float = 24) -> Dict[str, float]:
        """Berechne Tagesstromkosten
        
        Args:
            power_watts: Leistungsaufnahme in Watt
            hours: Betriebsstunden pro Tag
            
        Returns:
            Dict mit Kostendetails
        """
        kwh_per_day = (power_watts / 1000) * hours
        
        # Berechne für verschiedene Stunden
        cost_by_hour = {}
        total_cost = 0
        
        for h in range(24):
            if h < hours:
                rate = self.get_rate(h)
                hourly_kwh = power_watts / 1000
                hourly_cost = hourly_kwh * rate
                cost_by_hour[h] = {
                    'rate': rate,
                    'kwh': hourly_kwh,
                    'cost': hourly_cost
                }
                total_cost += hourly_cost
        
        avg_rate = total_cost / kwh_per_day if kwh_per_day > 0 else 0
        
        return {
            'daily_kwh': kwh_per_day,
            'daily_cost_usd': total_cost,
            'monthly_cost_usd': total_cost * 30,
            'yearly_cost_usd': total_cost * 365,
            'avg_rate_per_kwh': avg_rate,
            'by_hour': cost_by_hour
        }
        
    def calculate_mining_profit(self, 
                                hashrate: float,
                                power_watts: float,
                                coin_revenue_per_day: float,
                                hours: float = 24) -> Dict[str, float]:
        """Berechne Mining-Profit nach Stromkosten
        
        Args:
            hashrate: Hashrate (MH/s oder GH/s)
            power_watts: Leistungsaufnahme in Watt
            coin_revenue_per_day: Einnahmen pro Tag in USD
            hours: Betriebsstunden pro Tag
            
        Returns:
            Dict mit Profit-Details
        """
        electricity = self.calculate_daily_cost(power_watts, hours)
        
        daily_profit = coin_revenue_per_day - electricity['daily_cost_usd']
        monthly_profit = daily_profit * 30
        yearly_profit = daily_profit * 365
        
        profit_margin = (daily_profit / coin_revenue_per_day * 100) if coin_revenue_per_day > 0 else 0
        
        return {
            'hashrate': hashrate,
            'power_watts': power_watts,
            'daily_revenue_usd': coin_revenue_per_day,
            'daily_electricity_cost_usd': electricity['daily_cost_usd'],
            'daily_profit_usd': daily_profit,
            'monthly_profit_usd': monthly_profit,
            'yearly_profit_usd': yearly_profit,
            'profit_margin_pct': profit_margin,
            'electricity_details': electricity,
            'is_profitable': daily_profit > 0
        }
        
    def find_optimal_mining_hours(self, 
                                  power_watts: float,
                                  revenue_per_hour: float) -> List[int]:
        """Finde die profitabelsten Stunden zum Minen
        
        Args:
            power_watts: Leistungsaufnahme in Watt
            revenue_per_hour: Einnahmen pro Stunde in USD
            
        Returns:
            Liste der profitabelsten Stunden (0-23)
        """
        hourly_analysis = []
        
        for hour in range(24):
            rate = self.get_rate(hour)
            kwh = power_watts / 1000
            cost = kwh * rate
            profit = revenue_per_hour - cost
            
            hourly_analysis.append({
                'hour': hour,
                'rate': rate,
                'cost': cost,
                'profit': profit
            })
        
        # Sortiere nach Profit (absteigend)
        hourly_analysis.sort(key=lambda x: x['profit'], reverse=True)
        
        # Nur profitable Stunden
        profitable_hours = [h['hour'] for h in hourly_analysis if h['profit'] > 0]
        
        return profitable_hours
        
    def compare_regions(self, power_watts: float, hours: float = 24) -> List[Dict]:
        """Vergleiche Stromkosten zwischen Regionen
        
        Args:
            power_watts: Leistungsaufnahme in Watt
            hours: Betriebsstunden pro Tag
            
        Returns:
            Liste der Regionen sortiert nach Kosten (günstigste zuerst)
        """
        comparisons = []
        
        for region in self.REGIONAL_RATES.keys():
            # Temporär Region wechseln für Berechnung
            original_region = self.region
            self.region = region
            
            costs = self.calculate_daily_cost(power_watts, hours)
            
            comparisons.append({
                'region': region,
                'daily_cost_usd': costs['daily_cost_usd'],
                'monthly_cost_usd': costs['monthly_cost_usd'],
                'yearly_cost_usd': costs['yearly_cost_usd'],
                'avg_rate': costs['avg_rate_per_kwh']
            })
            
            self.region = original_region
        
        # Sortiere nach Tageskosten
        comparisons.sort(key=lambda x: x['daily_cost_usd'])
        
        return comparisons
        
    def get_best_region(self, power_watts: float, hours: float = 24) -> Dict:
        """Finde die günstigste Region für Mining
        
        Args:
            power_watts: Leistungsaufnahme in Watt
            hours: Betriebsstunden pro Tag
            
        Returns:
            Dict mit bester Region und Einsparungen
        """
        comparisons = self.compare_regions(power_watts, hours)
        
        if not comparisons:
            return {}
        
        best = comparisons[0]
        current = next((c for c in comparisons if c['region'] == self.region), None)
        
        if current:
            savings_daily = current['daily_cost_usd'] - best['daily_cost_usd']
            savings_yearly = current['yearly_cost_usd'] - best['yearly_cost_usd']
            savings_pct = (savings_daily / current['daily_cost_usd'] * 100) if current['daily_cost_usd'] > 0 else 0
        else:
            savings_daily = 0
            savings_yearly = 0
            savings_pct = 0
        
        return {
            'best_region': best['region'],
            'best_daily_cost': best['daily_cost_usd'],
            'best_yearly_cost': best['yearly_cost_usd'],
            'current_region': self.region,
            'current_daily_cost': current['daily_cost_usd'] if current else 0,
            'savings_daily_usd': savings_daily,
            'savings_yearly_usd': savings_yearly,
            'savings_pct': savings_pct,
            'all_regions': comparisons
        }


class MiningScheduler:
    """Intelligente Mining-Zeitplanung basierend auf Strompreisen"""
    
    def __init__(self, cost_manager: ElectricityCostManager):
        self.cost_manager = cost_manager
        self.logger = logging.getLogger(__name__)
        
    def create_optimal_schedule(self, 
                               power_watts: float,
                               revenue_per_hour: float,
                               min_hours: int = 12,
                               max_hours: int = 24) -> Dict:
        """Erstelle optimalen Mining-Zeitplan
        
        Args:
            power_watts: Leistungsaufnahme in Watt
            revenue_per_hour: Einnahmen pro Stunde
            min_hours: Minimum Betriebsstunden pro Tag
            max_hours: Maximum Betriebsstunden pro Tag
            
        Returns:
            Dict mit Zeitplan
        """
        profitable_hours = self.cost_manager.find_optimal_mining_hours(
            power_watts, 
            revenue_per_hour
        )
        
        # Begrenze auf min/max
        if len(profitable_hours) < min_hours:
            self.logger.warning(f"⚠️ Nur {len(profitable_hours)} profitable Stunden gefunden")
            # Nutze beste verfügbare Stunden
            all_hours = list(range(24))
            schedule_hours = profitable_hours + all_hours[:min_hours - len(profitable_hours)]
        elif len(profitable_hours) > max_hours:
            schedule_hours = profitable_hours[:max_hours]
        else:
            schedule_hours = profitable_hours
        
        # Berechne Gesamt-Statistiken
        total_revenue = revenue_per_hour * len(schedule_hours)
        electricity = self.cost_manager.calculate_daily_cost(power_watts, len(schedule_hours))
        total_profit = total_revenue - electricity['daily_cost_usd']
        
        return {
            'mining_hours': sorted(schedule_hours),
            'hours_per_day': len(schedule_hours),
            'time_ranges': self._convert_to_time_ranges(schedule_hours),
            'daily_revenue_usd': total_revenue,
            'daily_electricity_cost_usd': electricity['daily_cost_usd'],
            'daily_profit_usd': total_profit,
            'profit_margin_pct': (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        }
        
    def _convert_to_time_ranges(self, hours: List[int]) -> List[str]:
        """Konvertiere Stunden-Liste zu Zeit-Ranges (z.B. '22:00-06:00')"""
        if not hours:
            return []
        
        hours = sorted(hours)
        ranges = []
        start = hours[0]
        end = hours[0]
        
        for i in range(1, len(hours)):
            if hours[i] == end + 1:
                end = hours[i]
            else:
                ranges.append(f"{start:02d}:00-{(end+1)%24:02d}:00")
                start = hours[i]
                end = hours[i]
        
        ranges.append(f"{start:02d}:00-{(end+1)%24:02d}:00")
        return ranges


# CLI Demo
def main():
    """Demo: Stromkosten-Analyse"""
    logging.basicConfig(level=logging.INFO)
    
    print("⚡ STROMKOSTEN-ANALYSE FÜR CRYPTO MINING")
    print("=" * 70)
    
    # Mining-Rig Specs
    rig_power = 3000  # Watt (z.B. 10x RTX 3080)
    rig_hashrate = 1000  # MH/s
    daily_revenue = 50  # USD
    
    # Deutschland
    print("\n📍 DEUTSCHLAND (Aktuell)")
    de_manager = ElectricityCostManager(region='DE', tariff_type='standard')
    de_profit = de_manager.calculate_mining_profit(rig_hashrate, rig_power, daily_revenue)
    
    print(f"  Tägliche Einnahmen:     ${de_profit['daily_revenue_usd']:.2f}")
    print(f"  Stromkosten (24h):      ${de_profit['daily_electricity_cost_usd']:.2f}")
    print(f"  Täglicher Profit:       ${de_profit['daily_profit_usd']:.2f}")
    print(f"  Gewinnmarge:            {de_profit['profit_margin_pct']:.1f}%")
    print(f"  Profitabel:             {'✅ JA' if de_profit['is_profitable'] else '❌ NEIN'}")
    
    # Regionen-Vergleich
    print("\n🌍 REGIONEN-VERGLEICH (Sortiert nach Kosten)")
    print("-" * 70)
    comparisons = de_manager.compare_regions(rig_power)
    
    for region in comparisons[:5]:
        print(f"  {region['region']:3} | "
              f"Tag: ${region['daily_cost_usd']:6.2f} | "
              f"Monat: ${region['monthly_cost_usd']:7.2f} | "
              f"Jahr: ${region['yearly_cost_usd']:9.2f}")
    
    # Beste Region
    print("\n🏆 OPTIMALE REGION")
    best = de_manager.get_best_region(rig_power)
    print(f"  Beste Region:           {best['best_region']}")
    print(f"  Ersparnis pro Tag:      ${best['savings_daily_usd']:.2f}")
    print(f"  Ersparnis pro Jahr:     ${best['savings_yearly_usd']:.2f}")
    print(f"  Ersparnis in %:         {best['savings_pct']:.1f}%")
    
    # Zeitplanung
    print("\n⏰ OPTIMALER MINING-ZEITPLAN")
    scheduler = MiningScheduler(de_manager)
    schedule = scheduler.create_optimal_schedule(rig_power, daily_revenue / 24)
    
    print(f"  Mining-Stunden:         {schedule['hours_per_day']}h/Tag")
    print(f"  Zeitfenster:            {', '.join(schedule['time_ranges'])}")
    print(f"  Optimierter Profit:     ${schedule['daily_profit_usd']:.2f}/Tag")
    print(f"  Gewinnmarge:            {schedule['profit_margin_pct']:.1f}%")


if __name__ == "__main__":
    main()
