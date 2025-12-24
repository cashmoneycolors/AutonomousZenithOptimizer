#!/usr/bin/env python3
"""
CASH MONEY COLORS ORIGINAL (R) - HARDWARE INTEGRATION
Integration des Hardware-Adapters mit dem Temperature Optimizer
"""
from typing import Dict, List, Any, Optional
try:
    from mining_hardware_adapter import (
        get_hardware_adapter,
        set_gpu_power_limit,
        set_gpu_fan_speed,
        get_gpu_statistics,
        optimize_gpu_temperature,
        apply_gpu_profile
    )
    from rig_gpu_mapper import get_rig_mapper, get_gpu_index_for_rig
except ImportError:
    # Wenn direkt ausgeführt, versuche relativen Import
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from mining_hardware_adapter import (
        get_hardware_adapter,
        set_gpu_power_limit,
        set_gpu_fan_speed,
        get_gpu_statistics,
        optimize_gpu_temperature,
        apply_gpu_profile
    )
    from rig_gpu_mapper import get_rig_mapper, get_gpu_index_for_rig

class HardwareIntegration:
    """
    Verbindet den MiningHardwareAdapter mit dem bestehenden System
    Ermöglicht echte Hardware-Steuerung aus dem Temperature Optimizer
    """
    
    def __init__(self):
        self.adapter = get_hardware_adapter()
        self.mapper = get_rig_mapper()
        self.enabled = len(self.adapter.available_gpus) > 0
        
        if self.enabled:
            print(f"✅ Hardware-Integration aktiv: {len(self.adapter.available_gpus)} GPU(s)")
        else:
            print(f"⚠️  Hardware-Integration im Simulations-Modus (keine GPUs gefunden)")
    
    def _get_gpu_index(self, rig_data: Dict[str, Any]) -> int:
        """
        Ermittelt GPU-Index für ein Rig
        
        Args:
            rig_data: Rig-Informationen mit 'id' und optional 'gpu_index'
            
        Returns:
            GPU-Index
        """
        # Priorität 1: Explizit angegebener gpu_index
        if 'gpu_index' in rig_data and rig_data['gpu_index'] is not None:
            return rig_data['gpu_index']
        
        # Priorität 2: Mapping via rig_id
        rig_id = rig_data.get('id', 'UNKNOWN')
        return get_gpu_index_for_rig(rig_id)
    
    def apply_power_limit_to_rig(self, rig_data: Dict[str, Any], power_limit_watts: int) -> bool:
        """
        Wendet Power Limit auf ein Mining-Rig an
        
        Args:
            rig_data: Rig-Informationen mit 'id' und optional 'gpu_index'
            power_limit_watts: Power Limit in Watt
            
        Returns:
            True wenn erfolgreich
        """
        if not self.enabled:
            print(f"[SIM] Rig {rig_data.get('id')}: Power Limit → {power_limit_watts}W")
            return False
        
        gpu_index = self._get_gpu_index(rig_data)
        return set_gpu_power_limit(gpu_index, power_limit_watts)
    
    def apply_fan_speed_to_rig(self, rig_data: Dict[str, Any], fan_speed_percent: int) -> bool:
        """
        Setzt Lüftergeschwindigkeit für ein Rig
        
        Args:
            rig_data: Rig-Informationen mit 'id' und optional 'gpu_index'
            fan_speed_percent: Lüftergeschwindigkeit 30-100%
            
        Returns:
            True wenn erfolgreich
        """
        if not self.enabled:
            print(f"[SIM] Rig {rig_data.get('id')}: Lüfter → {fan_speed_percent}%")
            return False
        
        gpu_index = self._get_gpu_index(rig_data)
        return set_gpu_fan_speed(gpu_index, fan_speed_percent)
    
    def get_rig_temperature(self, rig_data: Dict[str, Any]) -> Optional[int]:
        """
        Liest echte Temperatur von Hardware
        
        Args:
            rig_data: Rig-Informationen mit 'id' und optional 'gpu_index'
            
        Returns:
            Temperatur in °C oder None
        """
        if not self.enabled:
            return None
        
        gpu_index = self._get_gpu_index(rig_data)
        stats = get_gpu_statistics(gpu_index)
        
        if stats and stats.get('temperature'):
            return stats['temperature']
        return None
    
    def optimize_rig(self, rig_data: Dict[str, Any], target_temp: int = 70) -> Dict[str, Any]:
        """
        Optimiert ein Rig für Zieltemperatur
        
        Args:
            rig_data: Rig-Informationen mit 'id' und optional 'gpu_index'
            target_temp: Zieltemperatur in °C
            
        Returns:
            Dict mit Optimierungsergebnissen
        """
        if not self.enabled:
            return {
                'success': False,
                'mode': 'simulation',
                'message': 'Hardware-Integration nicht verfügbar'
            }
        
        gpu_index = self._get_gpu_index(rig_data)
        return optimize_gpu_temperature(gpu_index, target_temp)
    
    def apply_profile_to_rig(self, rig_data: Dict[str, Any], profile: str = "balanced") -> bool:
        """
        Wendet Mining-Profil auf Rig an
        
        Profiles: "efficiency", "balanced", "performance"
        
        Args:
            rig_data: Rig-Informationen mit 'id' und optional 'gpu_index'
            profile: Profil-Name
            
        Returns:
            True wenn erfolgreich
        """
        if not self.enabled:
            print(f"[SIM] Rig {rig_data.get('id')}: Profil '{profile}' angewendet")
            return False
        
        gpu_index = self._get_gpu_index(rig_data)
        return apply_gpu_profile(gpu_index, profile)
    
    def get_all_rig_stats(self) -> List[Dict[str, Any]]:
        """Liest Stats für alle verfügbaren Rigs/GPUs"""
        if not self.enabled:
            return []
        
        return self.adapter.get_all_gpu_stats()
    
    def handle_temperature_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Behandelt Temperatur-Events vom Temperature Optimizer
        
        Args:
            event_data: Event mit 'rig_id', 'temperature', 'action', optional 'gpu_index'
            
        Returns:
            Dict mit durchgeführten Aktionen
        """
        rig_id = event_data.get('rig_id')
        current_temp = event_data.get('temperature')
        action = event_data.get('action')
        
        result = {
            'rig_id': rig_id,
            'event_handled': False,
            'actions': []
        }
        
        if not self.enabled:
            result['mode'] = 'simulation'
            return result
        
        # Erstelle Rig-Daten mit korrektem Mapping
        rig_data = {
            'id': rig_id,
            'gpu_index': event_data.get('gpu_index')  # Optional, wird via Mapping ermittelt falls None
        }
        gpu_index = self._get_gpu_index(rig_data)
        
        # Behandle verschiedene Actions
        if action == 'reduce_power':
            power_reduction = event_data.get('power_reduction_watts', 10)
            stats = get_gpu_statistics(gpu_index)
            if stats and stats.get('power_draw'):
                new_limit = int(stats['power_draw'] - power_reduction)
                if self.apply_power_limit_to_rig(rig_data, new_limit):
                    result['actions'].append(f'Power Limit reduziert auf {new_limit}W')
                    result['event_handled'] = True
        
        elif action == 'increase_fan':
            fan_increase = event_data.get('fan_increase_percent', 10)
            stats = get_gpu_statistics(gpu_index)
            if stats and stats.get('fan_speed'):
                new_fan = min(100, stats['fan_speed'] + fan_increase)
                if self.apply_fan_speed_to_rig(rig_data, new_fan):
                    result['actions'].append(f'Lüfter erhöht auf {new_fan}%')
                    result['event_handled'] = True
        
        elif action == 'optimize':
            target = event_data.get('target_temperature', 70)
            opt_result = self.optimize_rig(rig_data, target)
            if opt_result.get('success'):
                result['actions'] = opt_result.get('actions', [])
                result['event_handled'] = True
        
        return result


# Globale Instanz
hardware_integration = None

def get_hardware_integration() -> HardwareIntegration:
    """Gibt die globale Hardware-Integration Instanz zurück"""
    global hardware_integration
    if hardware_integration is None:
        hardware_integration = HardwareIntegration()
    return hardware_integration


# Convenience-Funktionen für Temperature Optimizer
def handle_mining_power_limit_event(rig_id: str, temperature: float, power_limit: int, gpu_index: Optional[int] = None) -> Dict[str, Any]:
    """
    Behandelt MINING_POWER_LIMIT Event
    
    Args:
        rig_id: Rig ID
        temperature: Aktuelle Temperatur
        power_limit: Neues Power Limit in Watt
        gpu_index: Optional expliziter GPU-Index (überschreibt Mapping)
        
    Returns:
        Dict mit Ergebnis
    """
    integration = get_hardware_integration()
    rig_data = {'id': rig_id, 'gpu_index': gpu_index}
    
    success = integration.apply_power_limit_to_rig(rig_data, power_limit)
    
    return {
        'rig_id': rig_id,
        'temperature': temperature,
        'power_limit': power_limit,
        'success': success,
        'hardware_mode': integration.enabled
    }


def handle_fan_speed_event(rig_id: str, temperature: float, fan_speed: int, gpu_index: Optional[int] = None) -> Dict[str, Any]:
    """
    Behandelt Fan Speed Event
    
    Args:
        rig_id: Rig ID
        temperature: Aktuelle Temperatur
        fan_speed: Neue Lüftergeschwindigkeit in %
        gpu_index: Optional expliziter GPU-Index (überschreibt Mapping)
        
    Returns:
        Dict mit Ergebnis
    """
    integration = get_hardware_integration()
    rig_data = {'id': rig_id, 'gpu_index': gpu_index}
    
    success = integration.apply_fan_speed_to_rig(rig_data, fan_speed)
    
    return {
        'rig_id': rig_id,
        'temperature': temperature,
        'fan_speed': fan_speed,
        'success': success,
        'hardware_mode': integration.enabled
    }


if __name__ == "__main__":
    print("=" * 60)
    print("HARDWARE INTEGRATION TEST")
    print("=" * 60)
    
    # Initialisiere Integration
    integration = HardwareIntegration()
    
    print(f"\nModus: {'Hardware' if integration.enabled else 'Simulation'}")
    
    # Test Events
    print("\n🧪 TESTE EVENTS:")
    print("-" * 40)
    
    # Power Limit Event
    result1 = handle_mining_power_limit_event("RIG_001", 75.0, 180)
    print(f"Power Limit Event: {result1}")
    
    # Fan Speed Event
    result2 = handle_fan_speed_event("RIG_001", 75.0, 80)
    print(f"Fan Speed Event: {result2}")
    
    # Stats abrufen
    if integration.enabled:
        print("\n📊 GPU STATISTIKEN:")
        print("-" * 40)
        stats = integration.get_all_rig_stats()
        for stat in stats:
            print(f"GPU {stat['index']}: {stat['temperature']}°C, {stat['power_draw']}W, {stat['utilization']}%")
    
    print("\n" + "=" * 60)
    print("TEST ABGESCHLOSSEN")
    print("=" * 60)
