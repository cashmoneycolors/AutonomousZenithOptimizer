#!/usr/bin/env python3
"""
TEST SCRIPT - INTEGRATED QUANTUM MINING SYSTEM
Testet die Kombination aus Quantum Live Data und DeepSeek Mining Brain
"""

import time
import sys
import os

# Pfad zu den Modulen hinzufügen
sys.path.append(os.path.join(os.path.dirname(__file__), 'python_modules'))

try:
    from deepseek_mining_brain import IntegratedMiningSystem
    print("[OK] Module erfolgreich importiert")
except ImportError as e:
    print(f"[ERROR] Import-Fehler: {e}")
    sys.exit(1)

def test_integrated_system():
    """Teste das integrierte System"""
    print("STARTING INTEGRATED SYSTEM TEST")
    print("=" * 50)

    # Erstelle System
    system = IntegratedMiningSystem()

    try:
        # Starte System
        system.start_integrated_system()

        # Teste für 60 Sekunden
        print("Testing für 60 Sekunden...")
        start_time = time.time()

        while time.time() - start_time < 60:
            status = system.get_system_status()
            metrics = status['quantum_data']
            brain = status['brain_status']

            # Zeige Status
            print(f"\rHR: {metrics['current_hashrate']:.1f} | PW: {metrics['current_power']:.1f} | TMP: {metrics['current_temp']:.1f} | QFLUX: {metrics['quantum_flux']:.3f} | EFF: {metrics['current_efficiency']:.3f} | DECISIONS: {brain['decisions_made']}", end="", flush=True)

            time.sleep(1.0)

        print("\n\nTest erfolgreich abgeschlossen!")

        # Zeige finale Statistiken
        final_status = system.get_system_status()
        final_metrics = final_status['quantum_data']
        final_brain = final_status['brain_status']

        print("\nFINALE STATISTIKEN:")
        print(f"   Hashrate: {final_metrics['current_hashrate']:.1f} MH/s")
        print(f"   Power: {final_metrics['current_power']:.1f} W")
        print(f"   Temperature: {final_metrics['current_temp']:.1f} °C")
        print(f"   Efficiency: {final_metrics['current_efficiency']:.3f}")
        print(f"   Quantum Flux: {final_metrics['quantum_flux']:.3f}")
        print(f"   KI-Entscheidungen: {final_brain['decisions_made']}")

        if final_brain['decisions_made'] > 0:
            print(f"   Letzte Entscheidung: {final_brain['last_decision']['reasoning'][:50]}...")

    except KeyboardInterrupt:
        print("\n\nTest durch Benutzer abgebrochen")
    except Exception as e:
        print(f"\nTest-Fehler: {e}")
        return False
    finally:
        # System herunterfahren
        system.stop_integrated_system()

    return True

def performance_analysis():
    """Führe Performance-Analyse durch"""
    print("\nPERFORMANCE ANALYSIS")
    print("=" * 30)

    system = IntegratedMiningSystem()
    system.start_integrated_system()

    try:
        # Sammle Daten für 10 Sekunden
        efficiencies = []
        hashrates = []
        powers = []

        print("Sammle Performance-Daten...")
        for i in range(10):
            status = system.get_system_status()
            metrics = status['quantum_data']

            efficiencies.append(metrics['current_efficiency'])
            hashrates.append(metrics['current_hashrate'])
            powers.append(metrics['current_power'])

            time.sleep(1.0)

        # Berechne Statistiken
        avg_efficiency = sum(efficiencies) / len(efficiencies)
        avg_hashrate = sum(hashrates) / len(hashrates)
        avg_power = sum(powers) / len(powers)

        print("PERFORMANCE METRICS:")
        print(f"   Durchschnittliche Effizienz: {avg_efficiency:.3f}")
        print(f"   Durchschnittliche Hashrate: {avg_hashrate:.1f} MH/s")
        print(f"   Durchschnittliche Leistung: {avg_power:.1f} W")
        print(f"   Effizienz-Variabilität: {max(efficiencies) - min(efficiencies):.3f}")

        # Bewertung
        if avg_efficiency > 0.4:
            print("EXZELLENTE PERFORMANCE - Quantum Optimization aktiv!")
        elif avg_efficiency > 0.35:
            print("GUTE PERFORMANCE - Optimierung funktioniert")
        else:
            print("PERFORMANCE KANN VERBESSERT WERDEN")

    finally:
        system.stop_integrated_system()

if __name__ == "__main__":
    print("INTEGRATED QUANTUM MINING SYSTEM TEST SUITE")
    print("=" * 60)

    # Führe Tests durch
    success = test_integrated_system()

    if success:
        performance_analysis()
        print("\nALLE TESTS ERFOLGREICH - SYSTEM BEREIT FÜR PRODUKTION!")
    else:
        print("\nTESTS FEHLGESCHLAGEN - DEBUGGING ERFORDERLICH")