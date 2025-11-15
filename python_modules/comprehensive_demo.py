#!/usr/bin/env python3
"""Umfassende Demo des verbesserten Mining-Systems."""

import logging
import time
from mining_system_integration import IntegratedMiningSystem, SystemConfig

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s [%(threadName)s] %(name)s: %(message)s'
)

logger = logging.getLogger(__name__)


def demo_basic_operation():
    """Demo: Grundlegende System-Operation."""
    print("\n" + "=" * 70)
    print("DEMO 1: Grundlegende System-Operation")
    print("=" * 70)
    
    config = SystemConfig(
        monitoring_interval=0.5,
        collection_interval=1.0,
        analysis_interval=1.5,
        enable_auto_optimization=True,
        log_performance_metrics=True,
    )
    
    with IntegratedMiningSystem(config=config) as system:
        print(f"\nSystem gestartet: {system.system_name} v{system.version}")
        print(f"Anzahl Rigs: {len(system.mining_rigs)}")
        
        print("\nLasse System 5 Sekunden laufen...")
        time.sleep(5)
        
        health = system.evaluate_operational_health()
        print(f"\nOperational Health:")
        print(f"  Risk Level: {health['risk_level']}")
        print(f"  Active Rigs: {health['active_rigs']}")
        print(f"  Daily Profit: CHF {health['daily_profit']:.2f}")
        print(f"  Total Profit: CHF {health['total_profit']:.2f}")
        
        if health['performance_metrics']:
            metrics = health['performance_metrics']
            print(f"\nPerformance Metrics:")
            print(f"  Monitoring Cycles: {metrics['monitoring_cycles']}")
            print(f"  Collection Cycles: {metrics['collection_cycles']}")
            print(f"  Analysis Cycles: {metrics['analysis_cycles']}")
            print(f"  Optimization Calls: {metrics['optimization_calls']}")
    
    print("\nSystem gestoppt (automatisch via Context Manager)")


def demo_overheating_scenario():
    """Demo: Überhitzungs-Szenario und automatische Optimierung."""
    print("\n" + "=" * 70)
    print("DEMO 2: Überhitzungs-Szenario")
    print("=" * 70)
    
    config = SystemConfig(
        monitoring_interval=0.5,
        collection_interval=1.0,
        analysis_interval=1.0,
        enable_auto_optimization=False,  # Manuell steuern
    )
    
    system = IntegratedMiningSystem(config=config)
    system.initialize_components()
    
    # Überhitzung simulieren
    print("\nSimuliere Überhitzung bei GPU_1 und GPU_2...")
    system.mining_rigs[0]["temperature"] = 92.0
    system.mining_rigs[1]["temperature"] = 88.0
    
    print("\nZustand vor Optimierung:")
    for rig in system.mining_rigs:
        print(f"  {rig['id']}: {rig['temperature']:.1f}°C, {rig['hash_rate']:.1f} MH/s, Status: {rig['status']}")
    
    # Risikobewertung durchführen
    assessment = system._perform_risk_assessment()
    print(f"\nRisikobewertung:")
    print(f"  Level: {assessment.level}")
    print(f"  Score: {assessment.score}")
    print(f"  Recommendation: {assessment.recommendation}")
    if assessment.issues:
        print(f"  Issues:")
        for issue in assessment.issues:
            print(f"    - {issue}")
    
    # Optimierung durchführen
    print("\nFühre Optimierung durch...")
    system.optimize_mining_strategy()
    
    print("\nZustand nach Optimierung:")
    for rig in system.mining_rigs:
        print(f"  {rig['id']}: {rig['temperature']:.1f}°C, {rig['hash_rate']:.1f} MH/s, Status: {rig['status']}")
    
    # Neue Risikobewertung
    assessment = system._perform_risk_assessment()
    print(f"\nNeue Risikobewertung:")
    print(f"  Level: {assessment.level}")
    print(f"  Score: {assessment.score}")


def demo_scaling():
    """Demo: Skalierung der Mining-Operation."""
    print("\n" + "=" * 70)
    print("DEMO 3: Skalierung")
    print("=" * 70)
    
    system = IntegratedMiningSystem()
    system.initialize_components()
    
    print(f"\nInitial: {len(system.mining_rigs)} Rigs")
    
    print("\nSkaliere hoch auf 10 Rigs...")
    system.scale_mining_operation(10)
    print(f"Anzahl Rigs: {len(system.mining_rigs)}")
    
    system.step_once()
    health = system.evaluate_operational_health()
    print(f"Daily Profit (10 Rigs): CHF {health['daily_profit']:.2f}")
    
    print("\nSkaliere runter auf 2 Rigs...")
    system.scale_mining_operation(2)
    print(f"Anzahl Rigs: {len(system.mining_rigs)}")
    
    system.step_once()
    health = system.evaluate_operational_health()
    print(f"Daily Profit (2 Rigs): CHF {health['daily_profit']:.2f}")


def demo_config_management():
    """Demo: Konfigurations-Management."""
    print("\n" + "=" * 70)
    print("DEMO 4: Konfigurations-Management")
    print("=" * 70)
    
    import tempfile
    from pathlib import Path
    
    # Erstelle Custom Config
    config = SystemConfig(
        monitoring_interval=2.0,
        collection_interval=5.0,
        analysis_interval=10.0,
        shutdown_timeout=3.0,
        enable_auto_optimization=False,
        log_performance_metrics=True,
    )
    
    print("\nCustom Config erstellt:")
    print(f"  Monitoring Interval: {config.monitoring_interval}s")
    print(f"  Collection Interval: {config.collection_interval}s")
    print(f"  Analysis Interval: {config.analysis_interval}s")
    print(f"  Auto Optimization: {config.enable_auto_optimization}")
    
    # Speichern
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_path = f.name
    
    try:
        config.save_to_file(config_path)
        print(f"\nConfig gespeichert nach: {config_path}")
        
        # Laden
        loaded_config = SystemConfig.from_file(config_path)
        print(f"\nConfig geladen von: {config_path}")
        print(f"  Monitoring Interval: {loaded_config.monitoring_interval}s")
        print(f"  Collection Interval: {loaded_config.collection_interval}s")
        print(f"  Auto Optimization: {loaded_config.enable_auto_optimization}")
        
        # System mit geladener Config starten
        print("\nStarte System mit geladener Config...")
        system = IntegratedMiningSystem(config=loaded_config)
        print(f"  System Monitoring Interval: {system.monitoring_interval}s")
        
    finally:
        Path(config_path).unlink(missing_ok=True)


def demo_system_report():
    """Demo: System-Report."""
    print("\n" + "=" * 70)
    print("DEMO 5: System-Report")
    print("=" * 70)
    
    config = SystemConfig(
        monitoring_interval=0.5,
        collection_interval=1.0,
        analysis_interval=1.5,
    )
    
    system = IntegratedMiningSystem(config=config)
    system.start_integrated_mining()
    
    print("\nLasse System 3 Sekunden laufen...")
    time.sleep(3)
    
    print("\n" + system.generate_system_report())
    
    system.stop_integrated_mining()


def demo_continuous_monitoring():
    """Demo: Kontinuierliches Monitoring."""
    print("\n" + "=" * 70)
    print("DEMO 6: Kontinuierliches Monitoring")
    print("=" * 70)
    
    config = SystemConfig(
        monitoring_interval=0.5,
        collection_interval=1.0,
        analysis_interval=1.0,
        enable_auto_optimization=True,
    )
    
    with IntegratedMiningSystem(config=config) as system:
        print("\nMonitoring für 10 Sekunden...")
        print("(Das System passt sich automatisch an)")
        
        for i in range(10):
            time.sleep(1)
            status = system.get_system_status()
            sys_status = status["system_status"]
            
            print(f"\nSekunde {i+1}:")
            print(f"  Active Rigs: {sys_status.get('active_rigs', 0)}")
            print(f"  Total Profit: CHF {sys_status.get('total_profit', 0.0):.4f}")
            
            assessment = sys_status.get('last_risk_assessment', {})
            print(f"  Risk Level: {assessment.get('level', 'unknown')}")
            
            # Zeige heißeste Rigs
            temps = [(r['id'], r['temperature']) for r in system.mining_rigs]
            temps.sort(key=lambda x: x[1], reverse=True)
            print(f"  Hottest Rig: {temps[0][0]} @ {temps[0][1]:.1f}°C")


def main():
    """Führt alle Demos aus."""
    print("\n" + "=" * 70)
    print("MINING SYSTEM - COMPREHENSIVE DEMO")
    print("=" * 70)
    
    demos = [
        ("Basic Operation", demo_basic_operation),
        ("Overheating Scenario", demo_overheating_scenario),
        ("Scaling", demo_scaling),
        ("Config Management", demo_config_management),
        ("System Report", demo_system_report),
        ("Continuous Monitoring", demo_continuous_monitoring),
    ]
    
    for name, demo_func in demos:
        try:
            demo_func()
        except KeyboardInterrupt:
            print("\n\nDemo abgebrochen durch Benutzer")
            break
        except Exception as e:
            logger.exception(f"Fehler in Demo '{name}': {e}")
        
        if demo_func != demos[-1][1]:  # Nicht bei letzter Demo
            input("\n[Enter drücken für nächste Demo...]")
    
    print("\n" + "=" * 70)
    print("ALLE DEMOS ABGESCHLOSSEN")
    print("=" * 70)


if __name__ == "__main__":
    main()
