#!/usr/bin/env python3
"""
CLOUD AUTOSCALING MODULE - Automatic Cloud Mining Rig Management
Azure & AWS Integration für dynamisches Cloud-Mining
"""
import time
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import threading
import random
from python_modules.config_manager import get_config
from python_modules.alert_system import send_custom_alert, send_system_alert
from python_modules.market_integration import get_crypto_prices

class CloudAutoscalingManager:
    """Cloud Mining Autoscaling Manager"""

    def __init__(self):
        self.cloud_config = get_config('CloudAutoscaling', {})

        # Cloud-Provider Integration
        self.cloud_providers = {
            'azure': {
                'api_base': 'https://management.azure.com',
                'regions': ['switzerlandnorth', 'switzerlandwest', 'germanywestcentral'],
                'vm_sizes': ['Standard_NC6s_v3', 'Standard_NC12s_v3', 'Standard_NC24s_v3'],  # A100 GPUs
                'max_instances': 50,
                'active': True,
                'api_key_configured': bool(self.cloud_config.get('AzureSubscriptionId'))
            },
            'aws': {
                'api_base': 'https://ec2.amazonaws.com',
                'regions': ['eu-central-1', 'eu-north-1', 'eu-west-1'],
                'instance_types': ['p3.2xlarge', 'p3.8xlarge', 'p3.16xlarge'],  # V100 GPUs
                'max_instances': 100,
                'active': True,
                'api_key_configured': bool(self.cloud_config.get('AWSAccessKeyId'))
            },
            'gcp': {
                'api_base': 'https://compute.googleapis.com',
                'regions': ['europe-west6', 'europe-west3'],
                'machine_types': ['n1-highmem-16', 'n1-highmem-32'],
                'max_instances': 25,
                'active': False,  # Noch nicht konfiguriert
                'api_key_configured': False
            }
        }

        # Cloud Mining Rigs
        self.active_cloud_rigs = {}
        self.scaling_history = []
        self.cost_tracking = {}
        self.performance_monitoring = {}

        # Autoscaling Konfiguration
        self.min_profit_threshold = self.cloud_config.get('MinProfitThreshold', 25.0)  # CHF pro Tag
        self.max_instances_per_region = self.cloud_config.get('MaxInstancesPerRegion', 10)
        self.scaling_cooldown_seconds = self.cloud_config.get('ScalingCooldown', 300)  # 5 Minuten
        self.profit_based_scaling = True

        print("[CLOUD] Cloud Autoscaling Manager Initialized")
        print("[CLOUD] Providers Available: Azure, AWS")
        print(f"[CLOUD] Min Profit Threshold: CHF {self.min_profit_threshold}/day")

    def start_cloud_autoscaling(self):
        """Startet Cloud Autoscaling Monitoring"""
        print("[CLOUD] Starting Cloud Autoscaling...")

        # Starte Monitoring Threads
        scaling_thread = threading.Thread(target=self._autoscaling_monitor, daemon=True)
        scaling_thread.start()

        cost_monitor_thread = threading.Thread(target=self._cost_monitor, daemon=True)
        cost_monitor_thread.start()

        performance_thread = threading.Thread(target=self._performance_monitor, daemon=True)
        performance_thread.start()

        # Initiale Marktanalyse
        self._analyze_market_and_scale()

        send_custom_alert("Cloud Autoscaling",
                         "Cloud Mining Autoscaling activated - monitoring market conditions",
                         "[CLOUD]")

    def create_cloud_mining_rig(self, provider: str, region: str, algorithm: str = 'ethash') -> Dict[str, Any]:
        """Erstellt neue Cloud Mining Rig"""

        if provider not in self.cloud_providers or not self.cloud_providers[provider]['active']:
            return {'status': 'FAILED', 'reason': f'Provider {provider} not available'}

        provider_config = self.cloud_providers[provider]

        # Wähle optimale Instance basierend auf Algorithmus
        instance_type = self._select_optimal_instance(provider, algorithm)
        if not instance_type:
            return {'status': 'FAILED', 'reason': 'No suitable instance available'}

        # Erstelle einzigartige Rig-ID
        rig_id = f"{provider}_{region}_{algorithm}_{int(time.time())}"

        # Simuliere Cloud-Rig Erstellung
        rig_config = {
            'rig_id': rig_id,
            'provider': provider,
            'region': region,
            'instance_type': instance_type,
            'algorithm': algorithm,
            'status': 'PROVISIONING',
            'created_at': datetime.now(),
            'expected_ready_at': datetime.now() + timedelta(minutes=10),
            'estimated_cost_per_hour': self._estimate_hourly_cost(provider, instance_type, region),
            'estimated_profit_per_hour': self._estimate_hourly_profit(algorithm, instance_type),
            'performance_tracker': {'start_time': time.time(), 'total_hashes': 0, 'total_energy': 0}
        }

        self.active_cloud_rigs[rig_id] = rig_config

        # Simuliere Provisioning-Zeit
        threading.Timer(10, self._complete_rig_provisioning, [rig_id]).start()

        send_system_alert("CLOUD_RIG_CREATED",
                         f"New cloud mining rig created: {rig_id} ({provider} {region})",
                         rig_config)

        return {
            'status': 'PROVISIONING',
            'rig_id': rig_id,
            'estimated_ready_time': '10 minutes',
            'expected_cost_hourly': rig_config['estimated_cost_per_hour']
        }

    def scale_cloud_fleet(self, target_profit: float) -> Dict[str, Any]:
        """Skaliert Cloud-Fleet basierend auf Ziel-Profit"""

        current_profit = self._calculate_total_cloud_profit()
        profit_gap = target_profit - current_profit

        if profit_gap < 0:
            # Zu viel Kapazität - skalieren runter
            return self._scale_down(abs(profit_gap))
        elif profit_gap > 10:
            # Mehr Kapazität needed
            return self._scale_up(profit_gap)
        else:
            return {'action': 'MAINTAIN_CURRENT_LEVEL', 'reason': 'Profit target met'}

    def terminate_cloud_rig(self, rig_id: str) -> Dict[str, Any]:
        """Beendet Cloud Mining Rig"""

        if rig_id not in self.active_cloud_rigs:
            return {'status': 'FAILED', 'reason': 'Rig not found'}

        rig = self.active_cloud_rigs[rig_id]
        provider = rig['provider']

        # Simuliere Termination
        rig['status'] = 'TERMINATING'
        rig['terminated_at'] = datetime.now()

        # Berechne finale Kosten
        runtime_hours = (datetime.now() - rig['created_at']).total_seconds() / 3600
        total_cost = runtime_hours * rig['estimated_cost_per_hour']
        total_profit = runtime_hours * rig['estimated_profit_per_hour']

        rig['final_cost'] = total_cost
        rig['final_profit'] = total_profit
        rig['net_return'] = total_profit - total_cost

        # Move zu Historie
        self.scaling_history.append({
            'rig_id': rig_id,
            'action': 'TERMINATED',
            'runtime_hours': runtime_hours,
            'total_cost': total_cost,
            'total_profit': total_profit,
            'net_profit': total_profit - total_cost,
            'timestamp': datetime.now().isoformat()
        })

        del self.active_cloud_rigs[rig_id]

        send_system_alert("CLOUD_RIG_TERMINATED",
                         f"Cloud rig {rig_id} terminated - Net: CHF {total_profit - total_cost:.2f}",
                         {
                             'rig_id': rig_id,
                             'provider': provider,
                             'net_profit': total_profit - total_cost
                         })

        return {
            'status': 'TERMINATED',
            'rig_id': rig_id,
            'runtime_hours': round(runtime_hours, 2),
            'total_cost': round(total_cost, 2),
            'total_profit': round(total_profit, 2),
            'net_profit': round(total_profit - total_cost, 2)
        }

    def get_cloud_fleet_status(self) -> Dict[str, Any]:
        """Gibt Cloud-Fleet Status zurück"""

        total_rigs = len(self.active_cloud_rigs)
        provisioning_rigs = len([r for r in self.active_cloud_rigs.values() if r['status'] == 'PROVISIONING'])
        active_rigs = len([r for r in self.active_cloud_rigs.values() if r['status'] == 'ACTIVE'])

        total_cost_per_hour = sum(r['estimated_cost_per_hour'] for r in self.active_cloud_rigs.values())
        total_profit_per_hour = sum(r['estimated_profit_per_hour'] for r in self.active_cloud_rigs.values())

        # Provider Breakdown
        provider_breakdown = {}
        for rig in self.active_cloud_rigs.values():
            provider = rig['provider']
            if provider not in provider_breakdown:
                provider_breakdown[provider] = {
                    'active_rigs': 0,
                    'total_cost_hourly': 0,
                    'total_profit_hourly': 0
                }
            provider_breakdown[provider]['active_rigs'] += 1
            provider_breakdown[provider]['total_cost_hourly'] += rig['estimated_cost_per_hour']
            provider_breakdown[provider]['total_profit_hourly'] += rig['estimated_profit_per_hour']

        return {
            'total_cloud_rigs': total_rigs,
            'active_rigs': active_rigs,
            'provisioning_rigs': provisioning_rigs,
            'total_cost_per_hour': round(total_cost_per_hour, 2),
            'total_profit_per_hour': round(total_profit_per_hour, 2),
            'net_profit_per_hour': round(total_profit_per_hour - total_cost_per_hour, 2),
            'daily_profit_estimation': round((total_profit_per_hour - total_cost_per_hour) * 24, 2),
            'provider_breakdown': provider_breakdown,
            'scaling_efficiency_score': self._calculate_scaling_efficiency(),
            'last_scaling_action': self._get_last_scaling_action(),
            'autoscaling_active': True
        }

    def optimize_cloud_deployment(self) -> Dict[str, Any]:
        """Optimiert Cloud-Deployment basierend auf Marktbedingungen"""

        market_data = get_crypto_prices()
        current_profit = self._calculate_total_cloud_profit()

        # Algorithmus-Analyse
        btc_price = market_data.get('bitcoin', {}).get('usd', 50000)
        eth_price = market_data.get('ethereum', {}).get('usd', 3000)

        # Entscheide beste Algorithmus-Kombination
        if btc_price > 100000:  # Bull Market
            recommended_algos = ['ethash', 'kawpow', 'randomx']
            recommended_regions = ['switzerlandnorth', 'eu-central-1']
        else:  # Bear/Normal Market
            recommended_algos = ['ethash', 'kawpow']
            recommended_regions = ['germanywestcentral', 'eu-west-1']

        optimization_result = {
            'market_condition': 'bull' if btc_price > 100000 else 'normal',
            'recommended_algorithms': recommended_algos,
            'recommended_regions': recommended_regions,
            'target_profit_per_rig': self._estimate_optimal_rig_profit(),
            'estimated_monthly_cost': round(current_profit * 30 * 0.1, 0),  # 10% der Erträge
            'optimization_actions': self._generate_optimization_actions()
        }

        return optimization_result

    def _autoscaling_monitor(self):
        """Überwacht Markt und skaliert automatisch"""
        last_scaling = 0

        while True:
            try:
                current_time = time.time()

                # Check ob Cooldown vorbei
                if current_time - last_scaling < self.scaling_cooldown_seconds:
                    time.sleep(60)
                    continue

                # Marktanalyse
                market_profit = self._analyze_market_profit_potential()

                if market_profit > self.min_profit_threshold * 1.5:  # Sehr profitabel
                    if len(self.active_cloud_rigs) < self.max_instances_per_region * 2:
                        self._scale_up_market_driven()
                        last_scaling = current_time

                elif market_profit < self.min_profit_threshold * 0.5:  # Unprofitabel
                    if len(self.active_cloud_rigs) > 2:  # Minimum 2 Rigs behalten
                        self._scale_down_market_driven()
                        last_scaling = current_time

                time.sleep(300)  # Check alle 5 Minuten

            except Exception as e:
                print(f"[CLOUD] Autoscaling monitor error: {e}")
                time.sleep(60)

    def _cost_monitor(self):
        """Überwacht Cloud-Kosten kontinuierlich"""
        while True:
            try:
                for rig_id, rig in list(self.active_cloud_rigs.items()):
                    if rig['status'] == 'ACTIVE':
                        # Update Laufzeit-Kosten
                        runtime_hours = (datetime.now() - rig['created_at']).total_seconds() / 3600
                        rig['current_cost'] = runtime_hours * rig['estimated_cost_per_hour']

                        # Profitabilitäts-Check
                        if self._calculate_rig_profitability(rig) < 0.5:  # <50% profitable
                            # Markiere für Termination
                            rig['termination_recommended'] = True

                time.sleep(3600)  # Stündliche Updates

            except Exception as e:
                print(f"[CLOUD] Cost monitor error: {e}")
                time.sleep(600)

    def _performance_monitor(self):
        """Überwacht Performance der Cloud-Rigs"""
        while True:
            try:
                for rig_id, rig in self.active_cloud_rigs.items():
                    if rig['status'] == 'ACTIVE' and 'performance_tracker' in rig:
                        tracker = rig['performance_tracker']

                        # Simuliere Performance-Updates
                        tracker['total_hashes'] += random.uniform(100, 500) * 3600  # MH/s * Stunde
                        tracker['total_energy'] += random.uniform(400, 800)  # Wh

                        # Hashrate/Auflösung berechnen
                        runtime_hours = (time.time() - tracker['start_time']) / 3600
                        rig['current_hashrate'] = tracker['total_hashes'] / max(runtime_hours, 1)
                        rig['efficiency_mh_per_w'] = rig['current_hashrate'] / (tracker['total_energy'] / max(runtime_hours, 1) / 1000)

                time.sleep(900)  # 15 Minuten Updates

            except Exception as e:
                print(f"[CLOUD] Performance monitor error: {e}")
                time.sleep(300)

    def _select_optimal_instance(self, provider: str, algorithm: str) -> Optional[str]:
        """Wählt optimale Cloud-Instance basierend auf Algorithmus"""
        provider_config = self.cloud_providers[provider]

        # Algorithmus-optimierte Instance-Auswahl
        if algorithm == 'ethash':
            return provider_config.get('vm_sizes' if provider == 'azure' else 'instance_types', [])[0]
        elif algorithm == 'kawpow':
            return provider_config.get('vm_sizes' if provider == 'azure' else 'instance_types', [])[1] if len(provider_config.get('vm_sizes' if provider == 'azure' else 'instance_types', [])) > 1 else None
        else:
            return provider_config.get('vm_sizes' if provider == 'azure' else 'instance_types', [])[0]

    def _estimate_hourly_cost(self, provider: str, instance_type: str, region: str) -> float:
        """Schätzt stündliche Cloud-Kosten"""

        # Basis-Preise (in CHF) - Deutschland/Schweiz Regionen
        pricing = {
            'azure': {
                'switzerlandnorth': {'Standard_NC6s_v3': 2.80, 'Standard_NC12s_v3': 5.60, 'Standard_NC24s_v3': 11.20},
                'germanywestcentral': {'Standard_NC6s_v3': 2.50, 'Standard_NC12s_v3': 5.00, 'Standard_NC24s_v3': 10.00}
            },
            'aws': {
                'eu-central-1': {'p3.2xlarge': 3.10, 'p3.8xlarge': 12.20, 'p3.16xlarge': 24.40},
                'eu-north-1': {'p3.2xlarge': 3.50, 'p3.8xlarge': 14.00, 'p3.16xlarge': 28.00}
            }
        }

        return pricing.get(provider, {}).get(region, {}).get(instance_type, 3.00)

    def _estimate_hourly_profit(self, algorithm: str, instance_type: str) -> float:
        """Schätzt stündlichen Mining-Profit"""

        # Basis-Profite (in CHF) für verschiedene GPUs
        gpu_profits = {
            'Standard_NC6s_v3': {'ethash': 3.50, 'kawpow': 2.80, 'randomx': 1.80},  # RTX A4000 equivalent
            'Standard_NC12s_v3': {'ethash': 6.80, 'kawpow': 5.50, 'randomx': 3.50},  # 2x RTX A4000
            'Standard_NC24s_v3': {'ethash': 13.50, 'kawpow': 11.00, 'randomx': 7.00},  # 4x RTX A4000
            'p3.2xlarge': {'ethash': 4.20, 'kawpow': 3.20, 'randomx': 2.50},  # V100
            'p3.8xlarge': {'ethash': 16.50, 'kawpow': 13.00, 'randomx': 9.50},  # 4x V100
            'p3.16xlarge': {'ethash': 33.00, 'kawpow': 26.00, 'randomx': 19.00}  # 8x V100
        }

        return gpu_profits.get(instance_type, {}).get(algorithm, 3.00)

    def _complete_rig_provisioning(self, rig_id: str):
        """Schließt Rig-Provisioning ab"""
        if rig_id in self.active_cloud_rigs:
            self.active_cloud_rigs[rig_id]['status'] = 'ACTIVE'
            self.active_cloud_rigs[rig_id]['activated_at'] = datetime.now()

            send_system_alert("CLOUD_RIG_READY",
                             f"Cloud mining rig {rig_id} is now active and mining",
                             {'rig_id': rig_id})

    def _analyze_market_and_scale(self):
        """Analysiert Markt und skaliert initial"""
        market_profit = self._analyze_market_profit_potential()

        if market_profit > self.min_profit_threshold:
            # Erstelle initiale Rigs
            self.create_cloud_mining_rig('azure', 'switzerlandnorth', 'ethash')
            if market_profit > self.min_profit_threshold * 1.2:
                self.create_cloud_mining_rig('aws', 'eu-central-1', 'kawpow')

    def _calculate_total_cloud_profit(self) -> float:
        """Berechnet totalen Cloud-Profit pro Stunde"""
        return sum(r['estimated_profit_per_hour'] for r in self.active_cloud_rigs.values()) - \
               sum(r['estimated_cost_per_hour'] for r in self.active_cloud_rigs.values())

    def _calculate_scaling_efficiency(self) -> float:
        """Berechnet Scaling-Effizienz Score"""
        if not self.scaling_history:
            return 100.0

        recent_actions = [h for h in self.scaling_history[-10:] if 'net_profit' in h]
        if not recent_actions:
            return 100.0

        profitable_actions = sum(1 for h in recent_actions if h['net_profit'] > 0)
        return (profitable_actions / len(recent_actions)) * 100

    def _get_last_scaling_action(self) -> Optional[Dict[str, Any]]:
        """Gibt letzte Scaling-Aktion zurück"""
        return self.scaling_history[-1] if self.scaling_history else None

    def _scale_up(self, profit_gap: float) -> Dict[str, Any]:
        """Skaliert Cloud-Kapazität hoch"""
        rigs_needed = max(1, int(profit_gap / 30))  # Angenommen 30 CHF/Rig/Tag

        created_rigs = []
        for i in range(min(rigs_needed, 3)):  # Max 3 Rigs gleichzeitig
            rig = self.create_cloud_mining_rig('azure', 'switzerlandnorth', 'ethash')
            if rig['status'] != 'FAILED':
                created_rigs.append(rig['rig_id'])

        return {
            'action': 'SCALED_UP',
            'rigs_created': len(created_rigs),
            'expected_profit_increase': rigs_needed * 30,  # Schätzungen
            'rigs': created_rigs
        }

    def _scale_down(self, profit_gap: float) -> Dict[str, Any]:
        """Skaliert Cloud-Kapazität runter"""
        active_rigs = [rig_id for rig_id, rig in self.active_cloud_rigs.items()
                      if rig['status'] == 'ACTIVE']

        rigs_to_terminate = min(len(active_rigs), max(1, int(profit_gap / 20)))

        terminated_rigs = []
        for rig_id in active_rigs[:rigs_to_terminate]:
            result = self.terminate_cloud_rig(rig_id)
            if result['status'] == 'TERMINATED':
                terminated_rigs.append(result)

        return {
            'action': 'SCALED_DOWN',
            'rigs_terminated': len(terminated_rigs),
            'cost_savings': sum(r['total_cost'] for r in terminated_rigs),
            'rigs': terminated_rigs
        }

    def _analyze_market_profit_potential(self) -> float:
        """Analysiert Markt-Profit-Potential"""
        market_data = get_crypto_prices()

        # Vereinfachte Marktanalyse
        btc_price = market_data.get('bitcoin', {}).get('usd', 50000)
        eth_price = market_data.get('ethereum', {}).get('usd', 3000)

        # Basis potenzial ist eine Funktion der Preise
        base_potential = (btc_price / 50000 + eth_price / 3000) / 2 * 40  # CHF

        return max(base_potential, 10)  # Minimum 10 CHF

    def _calculate_rig_profitability(self, rig: Dict[str, Any]) -> float:
        """Berechnet einzelne Rig-Profitabilität"""
        if 'current_cost' not in rig or 'estimated_profit_per_hour' not in rig:
            return 1.0

        current_cost = rig['current_cost']
        expected_profit = rig['estimated_profit_per_hour'] * ((datetime.now() - rig['created_at']).total_seconds() / 3600)

        if expected_profit == 0:
            return 0.0

        return (expected_profit - current_cost) / expected_profit

# Globale Cloud Autoscaling Instanz
cloud_autoscaling = CloudAutoscalingManager()

# Convenience-Funktionen
def start_cloud_autoscaling():
    """Startet Cloud Autoscaling"""
    return cloud_autoscaling.start_cloud_autoscaling()

def create_cloud_rig(provider, region, algorithm='ethash'):
    """Erstellt Cloud Mining Rig"""
    return cloud_autoscaling.create_cloud_mining_rig(provider, region, algorithm)

def get_cloud_status():
    """Gibt Cloud-Fleet Status zurück"""
    return cloud_autoscaling.get_cloud_fleet_status()

def terminate_cloud_rig(rig_id):
    """Beendet Cloud Rig"""
    return cloud_autoscaling.terminate_cloud_rig(rig_id)

def optimize_cloud():
    """Optimiert Cloud-Deployment"""
    return cloud_autoscaling.optimize_cloud_deployment()

if __name__ == "__main__":
    print("CLOUD AUTOSCALING MANAGER - Dynamic Cloud Mining")
    print("=" * 60)

    print("[CLOUD] Testing Cloud Autoscaling...")

    # Start Cloud Autoscaling
    start_cloud_autoscaling()

    # Erstelle Test-Rig
    rig = create_cloud_rig('azure', 'switzerlandnorth', 'ethash')
    print(f"[CLOUD] Created Rig: {rig['rig_id']}")

    # Check Status
    status = get_cloud_status()
    print(f"[CLOUD] Total Cloud Rigs: {status['total_cloud_rigs']}")
    print(f"[CLOUD] Daily Profit Estimation: CHF {status['daily_profit_estimation']}")

    # Optimization
    optimization = optimize_cloud()
    print(f"[CLOUD] Market Condition: {optimization['market_condition']}")
    print(f"[CLOUD] Recommended Algorithms: {optimization['recommended_algorithms']}")

    print("\n[CLOUD] CLOUD AUTOSCALING READY!")
    print("Azure & AWS Integration - Dynamic Scaling - Profit Maximization")
