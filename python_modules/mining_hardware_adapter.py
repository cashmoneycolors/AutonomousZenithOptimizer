#!/usr/bin/env python3
"""
CASH MONEY COLORS ORIGINAL (R) - MINING HARDWARE ADAPTER
Echte Hardware-Steuerung für NVIDIA GPUs mit nvidia-smi
"""
import subprocess
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

class MiningHardwareAdapter:
    """
    Echter Hardware-Adapter für Mining-Rig Steuerung
    Unterstützt NVIDIA GPUs via nvidia-smi
    """
    
    def __init__(self, log_file: str = "mining_hardware.log"):
        self.log_file = log_file
        self.setup_logging()
        self.available_gpus = []
        self.detect_gpus()
        
        print("⚡ MINING HARDWARE ADAPTER INITIALISIERT")
        print(f"   Gefundene GPUs: {len(self.available_gpus)}")
        
    def setup_logging(self):
        """Richtet Logging ein"""
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def detect_gpus(self) -> List[Dict[str, Any]]:
        """
        Erkennt alle verfügbaren NVIDIA GPUs
        Returns: Liste von GPU-Infos mit Index, Name, etc.
        """
        self.available_gpus = []
        
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=index,name,memory.total,power.limit,power.default_limit,fan.speed,temperature.gpu',
                 '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        parts = [p.strip() for p in line.split(',')]
                        if len(parts) >= 5:
                            gpu_info = {
                                'index': int(parts[0]),
                                'name': parts[1],
                                'memory_mb': float(parts[2]),
                                'current_power_limit': float(parts[3]) if parts[3] != '[N/A]' else None,
                                'default_power_limit': float(parts[4]) if parts[4] != '[N/A]' else None,
                                'fan_speed': int(parts[5]) if parts[5] != '[N/A]' else None,
                                'temperature': int(parts[6]) if parts[6] != '[N/A]' else None,
                                'vendor': 'NVIDIA'
                            }
                            self.available_gpus.append(gpu_info)
                            logging.info(f"GPU erkannt: {gpu_info['name']} (Index {gpu_info['index']})")
                            
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logging.error(f"GPU-Erkennung fehlgeschlagen: {e}")
            print(f"⚠️  nvidia-smi nicht verfügbar oder Timeout")
            
        return self.available_gpus
    
    def set_power_limit(self, gpu_index: int, power_watts: int) -> bool:
        """
        Setzt Power Limit für eine GPU
        
        Args:
            gpu_index: GPU Index (0, 1, 2, ...)
            power_watts: Power Limit in Watt (z.B. 200)
            
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        try:
            result = subprocess.run(
                ['nvidia-smi', '-i', str(gpu_index), '-pl', str(power_watts)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logging.info(f"GPU {gpu_index}: Power Limit auf {power_watts}W gesetzt")
                print(f"✅ GPU {gpu_index}: Power Limit → {power_watts}W")
                return True
            else:
                logging.error(f"GPU {gpu_index}: Power Limit Fehler - {result.stderr}")
                print(f"❌ GPU {gpu_index}: Power Limit fehlgeschlagen")
                return False
                
        except Exception as e:
            logging.error(f"GPU {gpu_index}: Power Limit Exception - {e}")
            print(f"❌ GPU {gpu_index}: Exception beim Setzen des Power Limits")
            return False
    
    def set_fan_speed(self, gpu_index: int, fan_speed_percent: int) -> bool:
        """
        Setzt Lüftergeschwindigkeit für eine GPU (benötigt nvidia-settings)
        
        Args:
            gpu_index: GPU Index (0, 1, 2, ...)
            fan_speed_percent: Lüftergeschwindigkeit in % (30-100)
            
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        # Validierung
        fan_speed_percent = max(30, min(100, fan_speed_percent))
        
        try:
            # Erst Fan Control aktivieren
            result1 = subprocess.run(
                ['nvidia-settings', '-a', f'[gpu:{gpu_index}]/GPUFanControlState=1'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result1.returncode == 0:
                # Dann Fan Speed setzen
                result2 = subprocess.run(
                    ['nvidia-settings', '-a', f'[fan:{gpu_index}]/GPUTargetFanSpeed={fan_speed_percent}'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result2.returncode == 0:
                    logging.info(f"GPU {gpu_index}: Lüfter auf {fan_speed_percent}% gesetzt")
                    print(f"✅ GPU {gpu_index}: Lüfter → {fan_speed_percent}%")
                    return True
                    
            logging.warning(f"GPU {gpu_index}: nvidia-settings nicht verfügbar oder fehlgeschlagen")
            print(f"⚠️  GPU {gpu_index}: nvidia-settings benötigt für Fan Control")
            return False
            
        except FileNotFoundError:
            logging.warning(f"nvidia-settings nicht installiert")
            print(f"⚠️  nvidia-settings nicht installiert (optional für Fan Control)")
            return False
        except Exception as e:
            logging.error(f"GPU {gpu_index}: Fan Speed Exception - {e}")
            return False
    
    def get_gpu_stats(self, gpu_index: int) -> Optional[Dict[str, Any]]:
        """
        Liest aktuelle GPU-Statistiken
        
        Args:
            gpu_index: GPU Index
            
        Returns:
            Dict mit aktuellen Stats oder None bei Fehler
        """
        try:
            result = subprocess.run(
                ['nvidia-smi', '-i', str(gpu_index),
                 '--query-gpu=index,temperature.gpu,power.draw,fan.speed,utilization.gpu,memory.used,memory.total',
                 '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                parts = [p.strip() for p in result.stdout.strip().split(',')]
                if len(parts) >= 7:
                    stats = {
                        'index': int(parts[0]),
                        'temperature': int(parts[1]) if parts[1] != '[N/A]' else None,
                        'power_draw': float(parts[2]) if parts[2] != '[N/A]' else None,
                        'fan_speed': int(parts[3]) if parts[3] != '[N/A]' else None,
                        'utilization': int(parts[4]) if parts[4] != '[N/A]' else None,
                        'memory_used_mb': float(parts[5]) if parts[5] != '[N/A]' else None,
                        'memory_total_mb': float(parts[6]) if parts[6] != '[N/A]' else None,
                        'timestamp': datetime.now().isoformat()
                    }
                    return stats
                    
        except Exception as e:
            logging.error(f"GPU {gpu_index}: Stats-Abfrage fehlgeschlagen - {e}")
            
        return None
    
    def get_all_gpu_stats(self) -> List[Dict[str, Any]]:
        """Liest Stats für alle GPUs"""
        all_stats = []
        for gpu in self.available_gpus:
            stats = self.get_gpu_stats(gpu['index'])
            if stats:
                all_stats.append(stats)
        return all_stats
    
    def optimize_for_temperature(self, gpu_index: int, target_temp: int = 70) -> Dict[str, Any]:
        """
        Optimiert GPU basierend auf Temperatur
        
        Args:
            gpu_index: GPU Index
            target_temp: Zieltemperatur in °C (default: 70)
            
        Returns:
            Dict mit durchgeführten Aktionen
        """
        stats = self.get_gpu_stats(gpu_index)
        if not stats or stats['temperature'] is None:
            return {'success': False, 'reason': 'Keine Stats verfügbar'}
        
        current_temp = stats['temperature']
        actions = []
        
        # Zu heiß - Power Limit reduzieren
        if current_temp > target_temp + 5:
            # Reduziere Power Limit um 10W
            if stats.get('power_draw'):
                new_limit = int(stats['power_draw'] - 10)
                if self.set_power_limit(gpu_index, new_limit):
                    actions.append(f"Power Limit reduziert auf {new_limit}W")
            
            # Erhöhe Lüftergeschwindigkeit
            if stats.get('fan_speed') and stats['fan_speed'] < 90:
                new_fan = min(100, stats['fan_speed'] + 10)
                if self.set_fan_speed(gpu_index, new_fan):
                    actions.append(f"Lüfter erhöht auf {new_fan}%")
        
        # Zu kalt - kann mehr Power nutzen
        elif current_temp < target_temp - 10:
            # Erhöhe Power Limit um 10W
            gpu_info = next((g for g in self.available_gpus if g['index'] == gpu_index), None)
            if gpu_info and gpu_info.get('default_power_limit'):
                new_limit = int(stats.get('power_draw', 0) + 10)
                max_limit = int(gpu_info['default_power_limit'])
                new_limit = min(new_limit, max_limit)
                if self.set_power_limit(gpu_index, new_limit):
                    actions.append(f"Power Limit erhöht auf {new_limit}W")
        
        return {
            'success': True,
            'gpu_index': gpu_index,
            'current_temp': current_temp,
            'target_temp': target_temp,
            'actions': actions
        }
    
    def apply_mining_profile(self, gpu_index: int, profile: str = "balanced") -> bool:
        """
        Wendet vordefinierte Mining-Profile an
        
        Profiles:
        - "efficiency": Niedriger Verbrauch, moderate Performance
        - "balanced": Ausgewogen (default)
        - "performance": Maximum Performance
        
        Args:
            gpu_index: GPU Index
            profile: Profil-Name
            
        Returns:
            True wenn erfolgreich
        """
        gpu_info = next((g for g in self.available_gpus if g['index'] == gpu_index), None)
        if not gpu_info or not gpu_info.get('default_power_limit'):
            return False
        
        default_pl = gpu_info['default_power_limit']
        
        profiles = {
            'efficiency': {
                'power_limit': int(default_pl * 0.65),  # 65% Power
                'fan_speed': 60
            },
            'balanced': {
                'power_limit': int(default_pl * 0.80),  # 80% Power
                'fan_speed': 70
            },
            'performance': {
                'power_limit': int(default_pl * 0.95),  # 95% Power
                'fan_speed': 85
            }
        }
        
        if profile not in profiles:
            profile = 'balanced'
        
        settings = profiles[profile]
        success = True
        
        # Setze Power Limit
        if not self.set_power_limit(gpu_index, settings['power_limit']):
            success = False
        
        # Setze Fan Speed
        self.set_fan_speed(gpu_index, settings['fan_speed'])  # Optional, daher kein Fehler
        
        if success:
            logging.info(f"GPU {gpu_index}: Profil '{profile}' angewendet")
            print(f"✅ GPU {gpu_index}: Profil '{profile}' aktiviert")
        
        return success
    
    def export_config(self, filename: str = "mining_hardware_config.json") -> bool:
        """Exportiert aktuelle Hardware-Konfiguration"""
        try:
            config = {
                'timestamp': datetime.now().isoformat(),
                'gpus': self.get_all_gpu_stats()
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            print(f"✅ Konfiguration exportiert nach {filename}")
            return True
            
        except Exception as e:
            logging.error(f"Export fehlgeschlagen: {e}")
            return False


# Globale Instanz
hardware_adapter = None

def get_hardware_adapter() -> MiningHardwareAdapter:
    """Gibt die globale Hardware-Adapter Instanz zurück"""
    global hardware_adapter
    if hardware_adapter is None:
        hardware_adapter = MiningHardwareAdapter()
    return hardware_adapter


# Convenience-Funktionen
def set_gpu_power_limit(gpu_index: int, power_watts: int) -> bool:
    """Setzt Power Limit für eine GPU"""
    adapter = get_hardware_adapter()
    return adapter.set_power_limit(gpu_index, power_watts)

def set_gpu_fan_speed(gpu_index: int, fan_percent: int) -> bool:
    """Setzt Lüftergeschwindigkeit für eine GPU"""
    adapter = get_hardware_adapter()
    return adapter.set_fan_speed(gpu_index, fan_percent)

def get_gpu_statistics(gpu_index: int) -> Optional[Dict[str, Any]]:
    """Liest GPU-Statistiken"""
    adapter = get_hardware_adapter()
    return adapter.get_gpu_stats(gpu_index)

def optimize_gpu_temperature(gpu_index: int, target_temp: int = 70) -> Dict[str, Any]:
    """Optimiert GPU für Zieltemperatur"""
    adapter = get_hardware_adapter()
    return adapter.optimize_for_temperature(gpu_index, target_temp)

def apply_gpu_profile(gpu_index: int, profile: str = "balanced") -> bool:
    """Wendet Mining-Profil an"""
    adapter = get_hardware_adapter()
    return adapter.apply_mining_profile(gpu_index, profile)


if __name__ == "__main__":
    print("=" * 60)
    print("CASH MONEY COLORS - MINING HARDWARE ADAPTER TEST")
    print("=" * 60)
    
    # Initialisiere Adapter
    adapter = MiningHardwareAdapter()
    
    if len(adapter.available_gpus) == 0:
        print("\n⚠️  Keine NVIDIA GPUs gefunden!")
        print("   nvidia-smi muss installiert sein und GPUs erkennen.")
    else:
        print(f"\n✅ {len(adapter.available_gpus)} GPU(s) gefunden:\n")
        
        for gpu in adapter.available_gpus:
            print(f"   GPU {gpu['index']}: {gpu['name']}")
            print(f"      Memory: {gpu['memory_mb']:.0f} MB")
            print(f"      Power Limit: {gpu['current_power_limit']}W (Default: {gpu['default_power_limit']}W)")
            print()
        
        # Test mit erster GPU
        if len(adapter.available_gpus) > 0:
            test_gpu = adapter.available_gpus[0]['index']
            
            print(f"\n🧪 TESTE GPU {test_gpu}:")
            print("-" * 40)
            
            # Aktuelle Stats
            stats = adapter.get_gpu_stats(test_gpu)
            if stats:
                print(f"   Temperatur: {stats['temperature']}°C")
                print(f"   Power Draw: {stats['power_draw']}W")
                print(f"   Auslastung: {stats['utilization']}%")
                print(f"   Lüfter: {stats['fan_speed']}%")
            
            # Wende Balanced-Profil an
            print(f"\n⚙️  Wende 'balanced' Profil an...")
            adapter.apply_mining_profile(test_gpu, "balanced")
            
            # Export
            print(f"\n💾 Exportiere Konfiguration...")
            adapter.export_config()
    
    print("\n" + "=" * 60)
    print("TEST ABGESCHLOSSEN")
    print("=" * 60)
