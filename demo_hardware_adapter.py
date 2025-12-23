#!/usr/bin/env python3
"""
CASH MONEY COLORS ORIGINAL (R) - HARDWARE ADAPTER DEMO
Vollständige Demo der Hardware-Steuerungsfunktionen
"""
import time
import sys
from pathlib import Path

# Import-Pfad konfigurieren
sys.path.insert(0, str(Path(__file__).parent / 'python_modules'))

from mining_hardware_adapter import get_hardware_adapter
from hardware_integration import get_hardware_integration, handle_mining_power_limit_event, handle_fan_speed_event

def print_section(title):
    """Druckt formatierte Sektion"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def demo_gpu_detection():
    """Demo: GPU-Erkennung"""
    print_section("1. GPU-ERKENNUNG")
    
    adapter = get_hardware_adapter()
    
    if len(adapter.available_gpus) == 0:
        print("\n⚠️  KEINE NVIDIA GPUs GEFUNDEN")
        print("   nvidia-smi muss installiert sein und GPUs erkennen.")
        print("   Demo läuft im Simulations-Modus weiter...\n")
        return None
    
    print(f"\n✅ {len(adapter.available_gpus)} GPU(s) erkannt:\n")
    
    for gpu in adapter.available_gpus:
        print(f"   GPU {gpu['index']}: {gpu['name']}")
        print(f"      Memory:       {gpu['memory_mb']:.0f} MB")
        print(f"      Power Limit:  {gpu['current_power_limit']}W (Default: {gpu['default_power_limit']}W)")
        print(f"      Temperatur:   {gpu['temperature']}°C")
        print(f"      Lüfter:       {gpu['fan_speed']}%")
        print()
    
    return adapter.available_gpus[0]['index'] if adapter.available_gpus else None

def demo_gpu_stats(gpu_index):
    """Demo: GPU-Statistiken abrufen"""
    print_section("2. GPU-STATISTIKEN ABRUFEN")
    
    adapter = get_hardware_adapter()
    
    if gpu_index is None:
        print("\n[SIMULATION] Würde GPU-Stats abrufen...")
        return
    
    print(f"\n📊 Aktuelle Stats für GPU {gpu_index}:\n")
    
    stats = adapter.get_gpu_stats(gpu_index)
    if stats:
        print(f"   Temperatur:        {stats['temperature']}°C")
        print(f"   Power Draw:        {stats['power_draw']:.1f}W")
        print(f"   Auslastung:        {stats['utilization']}%")
        print(f"   Lüfter:            {stats['fan_speed']}%")
        print(f"   Memory verwendet:  {stats['memory_used_mb']:.0f} MB / {stats['memory_total_mb']:.0f} MB")
        print(f"   Timestamp:         {stats['timestamp']}")
    else:
        print("   ❌ Stats konnten nicht abgerufen werden")

def demo_power_limit_control(gpu_index):
    """Demo: Power Limit Steuerung"""
    print_section("3. POWER LIMIT STEUERUNG")
    
    adapter = get_hardware_adapter()
    
    if gpu_index is None:
        print("\n[SIMULATION] Würde Power Limit setzen...")
        print("   GPU 0: Power Limit → 180W")
        return
    
    # Original Power Limit speichern
    original_stats = adapter.get_gpu_stats(gpu_index)
    original_pl = original_stats['power_draw'] if original_stats else None
    
    print(f"\n⚡ Setze Power Limit für GPU {gpu_index}...\n")
    
    # Test 1: Reduziere auf 180W
    print("   Test 1: Reduziere auf 180W")
    success = adapter.set_power_limit(gpu_index, 180)
    if success:
        time.sleep(2)
        stats = adapter.get_gpu_stats(gpu_index)
        print(f"   ✅ Aktuell: {stats['power_draw']:.1f}W bei {stats['temperature']}°C")
    
    # Test 2: Zurück zu 200W
    print("\n   Test 2: Erhöhe auf 200W")
    success = adapter.set_power_limit(gpu_index, 200)
    if success:
        time.sleep(2)
        stats = adapter.get_gpu_stats(gpu_index)
        print(f"   ✅ Aktuell: {stats['power_draw']:.1f}W bei {stats['temperature']}°C")

def demo_fan_control(gpu_index):
    """Demo: Lüfter-Steuerung"""
    print_section("4. LÜFTER-STEUERUNG")
    
    adapter = get_hardware_adapter()
    
    if gpu_index is None:
        print("\n[SIMULATION] Würde Lüftergeschwindigkeit setzen...")
        print("   GPU 0: Lüfter → 75%")
        return
    
    print(f"\n🌀 Setze Lüftergeschwindigkeit für GPU {gpu_index}...\n")
    print("   ⚠️  Benötigt nvidia-settings (optional)")
    
    # Test: Lüfter auf 75%
    success = adapter.set_fan_speed(gpu_index, 75)
    if success:
        time.sleep(2)
        stats = adapter.get_gpu_stats(gpu_index)
        print(f"   ✅ Lüfter: {stats['fan_speed']}%")
    else:
        print("   ℹ️  Fan Control benötigt nvidia-settings")

def demo_mining_profiles(gpu_index):
    """Demo: Mining-Profile"""
    print_section("5. MINING-PROFILE")
    
    adapter = get_hardware_adapter()
    
    if gpu_index is None:
        print("\n[SIMULATION] Würde Profile anwenden...")
        profiles = ["efficiency", "balanced", "performance"]
        for profile in profiles:
            print(f"   GPU 0: Profil '{profile}' angewendet")
        return
    
    print(f"\n🎯 Teste verschiedene Mining-Profile für GPU {gpu_index}:\n")
    
    profiles = [
        ("efficiency", "Niedriger Verbrauch (65% Power, 60% Lüfter)"),
        ("balanced", "Ausgewogen (80% Power, 70% Lüfter)"),
        ("performance", "Maximum Performance (95% Power, 85% Lüfter)")
    ]
    
    for profile, description in profiles:
        print(f"   {profile.upper()}:")
        print(f"      {description}")
        
        success = adapter.apply_mining_profile(gpu_index, profile)
        if success:
            time.sleep(3)
            stats = adapter.get_gpu_stats(gpu_index)
            print(f"      ✅ Power: {stats['power_draw']:.1f}W, Temp: {stats['temperature']}°C")
        else:
            print(f"      ❌ Fehler beim Anwenden")
        print()

def demo_temperature_optimization(gpu_index):
    """Demo: Temperatur-Optimierung"""
    print_section("6. TEMPERATUR-OPTIMIERUNG")
    
    adapter = get_hardware_adapter()
    
    if gpu_index is None:
        print("\n[SIMULATION] Würde Temperatur optimieren...")
        print("   GPU 0: Optimiere für 70°C Zieltemperatur")
        return
    
    print(f"\n🌡️  Automatische Temperatur-Optimierung für GPU {gpu_index}:\n")
    
    # Aktuelle Temperatur
    stats = adapter.get_gpu_stats(gpu_index)
    if stats:
        print(f"   Aktuelle Temperatur: {stats['temperature']}°C")
        print(f"   Zieltemperatur:      70°C")
        print()
        
        # Optimiere
        result = adapter.optimize_for_temperature(gpu_index, target_temp=70)
        
        if result['success']:
            print(f"   ✅ Optimierung durchgeführt:")
            for action in result['actions']:
                print(f"      - {action}")
        else:
            print(f"   ℹ️  Keine Anpassung nötig (Temperatur OK)")

def demo_event_integration():
    """Demo: Event-Integration"""
    print_section("7. EVENT-INTEGRATION")
    
    integration = get_hardware_integration()
    
    print(f"\n🔗 Integration-Modus: {'Hardware' if integration.enabled else 'Simulation'}\n")
    
    # Test Power Limit Event
    print("   Event 1: MINING_POWER_LIMIT")
    result = handle_mining_power_limit_event(
        rig_id="RIG_001",
        temperature=75.0,
        power_limit=180
    )
    print(f"      Rig:         {result['rig_id']}")
    print(f"      Temperatur:  {result['temperature']}°C")
    print(f"      Power Limit: {result['power_limit']}W")
    print(f"      Erfolg:      {result['success']}")
    print(f"      Modus:       {'Hardware' if result['hardware_mode'] else 'Simulation'}")
    
    print()
    
    # Test Fan Speed Event
    print("   Event 2: FAN_SPEED")
    result = handle_fan_speed_event(
        rig_id="RIG_001",
        temperature=75.0,
        fan_speed=80
    )
    print(f"      Rig:         {result['rig_id']}")
    print(f"      Temperatur:  {result['temperature']}°C")
    print(f"      Lüfter:      {result['fan_speed']}%")
    print(f"      Erfolg:      {result['success']}")
    print(f"      Modus:       {'Hardware' if result['hardware_mode'] else 'Simulation'}")

def demo_config_export():
    """Demo: Konfiguration exportieren"""
    print_section("8. KONFIGURATION EXPORTIEREN")
    
    adapter = get_hardware_adapter()
    
    print("\n💾 Exportiere aktuelle Hardware-Konfiguration...\n")
    
    filename = "mining_hardware_config_demo.json"
    success = adapter.export_config(filename)
    
    if success:
        print(f"   ✅ Konfiguration gespeichert: {filename}")
        
        # Zeige Inhalt
        import json
        try:
            with open(filename, 'r') as f:
                config = json.load(f)
            print(f"\n   Inhalt:")
            print(f"      Timestamp: {config['timestamp']}")
            print(f"      GPUs:      {len(config['gpus'])}")
        except:
            pass
    else:
        print(f"   ❌ Export fehlgeschlagen")

def main():
    """Hauptprogramm"""
    print("\n")
    print("=" * 70)
    print("  CASH MONEY COLORS - MINING HARDWARE ADAPTER")
    print("  Vollständige Funktionsdemo")
    print("=" * 70)
    
    # GPU-Erkennung
    gpu_index = demo_gpu_detection()
    
    if gpu_index is None:
        print("\n" + "⚠️ " * 20)
        print("HINWEIS: Demo läuft im SIMULATIONS-MODUS")
        print("Für echte Hardware-Steuerung wird nvidia-smi mit GPUs benötigt")
        print("⚠️ " * 20)
    
    input("\n👉 Drücke ENTER um fortzufahren...")
    
    # Demos durchführen
    demo_gpu_stats(gpu_index)
    input("\n👉 Drücke ENTER um fortzufahren...")
    
    demo_power_limit_control(gpu_index)
    input("\n👉 Drücke ENTER um fortzufahren...")
    
    demo_fan_control(gpu_index)
    input("\n👉 Drücke ENTER um fortzufahren...")
    
    demo_mining_profiles(gpu_index)
    input("\n👉 Drücke ENTER um fortzufahren...")
    
    demo_temperature_optimization(gpu_index)
    input("\n👉 Drücke ENTER um fortzufahren...")
    
    demo_event_integration()
    input("\n👉 Drücke ENTER um fortzufahren...")
    
    demo_config_export()
    
    # Abschluss
    print_section("DEMO ABGESCHLOSSEN")
    
    print("\n✅ Alle Features wurden demonstriert!")
    print("\nWeitere Informationen:")
    print("   - README: HARDWARE_ADAPTER_README.md")
    print("   - Code:   python_modules/mining_hardware_adapter.py")
    print("   - Integration: python_modules/hardware_integration.py")
    
    print("\n" + "=" * 70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Demo abgebrochen\n")
    except Exception as e:
        print(f"\n\n❌ Fehler: {e}\n")
        import traceback
        traceback.print_exc()
