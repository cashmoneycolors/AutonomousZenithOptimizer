#!/usr/bin/env python3
"""Umfassende Tests für das Mining-System."""

import json
import logging
import os
import tempfile
import time
import unittest
from pathlib import Path

from mining_system_integration import (
    IntegratedMiningSystem,
    SystemConfig,
    OptimizationAction,
    RiskAssessment,
    DeepSeekMiningBrain,
)

logging.basicConfig(level=logging.WARNING)


class TestSystemConfig(unittest.TestCase):
    """Tests für SystemConfig."""

    def test_default_config(self):
        """Test der Standard-Konfiguration."""
        config = SystemConfig()
        self.assertEqual(config.monitoring_interval, 1.0)
        self.assertEqual(config.collection_interval, 5.0)
        self.assertEqual(config.analysis_interval, 7.0)
        self.assertEqual(config.shutdown_timeout, 5.0)
        self.assertTrue(config.enable_auto_optimization)
        self.assertTrue(config.log_performance_metrics)

    def test_from_env(self):
        """Test Laden aus Umgebungsvariablen."""
        os.environ["MINING_MONITOR_INTERVAL"] = "2.5"
        os.environ["MINING_AUTO_OPTIMIZE"] = "false"
        
        config = SystemConfig.from_env()
        self.assertEqual(config.monitoring_interval, 2.5)
        self.assertFalse(config.enable_auto_optimization)
        
        # Cleanup
        del os.environ["MINING_MONITOR_INTERVAL"]
        del os.environ["MINING_AUTO_OPTIMIZE"]

    def test_save_and_load_config(self):
        """Test Speichern und Laden von Konfigurationsdateien."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_path = f.name
        
        try:
            # Speichern
            config = SystemConfig(
                monitoring_interval=2.0,
                collection_interval=10.0,
                enable_auto_optimization=False,
            )
            config.save_to_file(config_path)
            
            # Laden
            loaded = SystemConfig.from_file(config_path)
            self.assertEqual(loaded.monitoring_interval, 2.0)
            self.assertEqual(loaded.collection_interval, 10.0)
            self.assertFalse(loaded.enable_auto_optimization)
        finally:
            Path(config_path).unlink(missing_ok=True)

    def test_load_nonexistent_file(self):
        """Test Laden einer nicht existierenden Datei."""
        config = SystemConfig.from_file("/nonexistent/path/config.json")
        # Sollte Default-Werte zurückgeben
        self.assertEqual(config.monitoring_interval, 1.0)


class TestOptimizationAction(unittest.TestCase):
    """Tests für OptimizationAction."""

    def test_create_action(self):
        """Test Erstellung einer Optimierungsaktion."""
        action = OptimizationAction(
            action="adjust_hashrate",
            rigs=("GPU_1", "GPU_2"),
            description="Test action",
            factor=0.8,
            delta_temperature=-5.0,
        )
        self.assertEqual(action.action, "adjust_hashrate")
        self.assertEqual(len(action.rigs), 2)
        self.assertEqual(action.factor, 0.8)


class TestRiskAssessment(unittest.TestCase):
    """Tests für RiskAssessment."""

    def test_risk_assessment_to_dict(self):
        """Test Konvertierung zu Dictionary."""
        assessment = RiskAssessment(
            level="high",
            score=75.5,
            recommendation="Take action",
            issues=["Issue 1", "Issue 2"],
        )
        data = assessment.to_dict()
        self.assertEqual(data["level"], "high")
        self.assertEqual(data["score"], 75.5)
        self.assertEqual(len(data["issues"]), 2)


class TestDeepSeekMiningBrain(unittest.TestCase):
    """Tests für DeepSeekMiningBrain."""

    def test_brain_initialization(self):
        """Test Brain-Initialisierung."""
        brain = DeepSeekMiningBrain()
        brain.start_brain_operations()
        brain.stop_brain_operations()

    def test_optimization_high_risk(self):
        """Test Optimierung bei hohem Risiko."""
        brain = DeepSeekMiningBrain()
        context = {
            "last_risk_assessment": {"level": "high"},
            "rigs": [
                {"id": "GPU_1", "temperature": 90.0, "status": "OVERHEATING"},
            ],
        }
        actions = brain.identify_optimization_opportunities(context)
        self.assertGreater(len(actions), 0)
        # Sollte mindestens Hashrate-Anpassung und Kühlungs-Erhöhung beinhalten
        action_types = [a.action for a in actions]
        self.assertIn("adjust_hashrate", action_types)
        self.assertIn("increase_cooling", action_types)

    def test_optimization_medium_risk(self):
        """Test Optimierung bei mittlerem Risiko."""
        brain = DeepSeekMiningBrain()
        context = {
            "last_risk_assessment": {"level": "medium"},
            "rigs": [],
        }
        actions = brain.identify_optimization_opportunities(context)
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0].action, "optimize_costs")

    def test_optimization_low_risk(self):
        """Test Optimierung bei niedrigem Risiko."""
        brain = DeepSeekMiningBrain()
        context = {
            "last_risk_assessment": {"level": "low"},
            "rigs": [],
        }
        actions = brain.identify_optimization_opportunities(context)
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0].action, "maintain")


class TestIntegratedMiningSystem(unittest.TestCase):
    """Tests für IntegratedMiningSystem."""

    def setUp(self):
        """Setup für jeden Test."""
        self.config = SystemConfig(
            monitoring_interval=0.1,
            collection_interval=0.2,
            analysis_interval=0.3,
            shutdown_timeout=2.0,
            log_performance_metrics=True,
        )

    def test_system_initialization(self):
        """Test System-Initialisierung."""
        system = IntegratedMiningSystem(config=self.config)
        self.assertEqual(system.system_name, "Integrated Mining System")
        self.assertEqual(system.version, "2024.1")
        self.assertFalse(system.is_running)
        self.assertEqual(len(system.mining_rigs), 3)

    def test_component_initialization(self):
        """Test Komponenten-Initialisierung."""
        system = IntegratedMiningSystem(config=self.config)
        system.initialize_components()
        
        self.assertIsNotNone(system.deepseek_brain)
        self.assertIsNotNone(system.control_panel)
        self.assertIsNotNone(system.data_collector)
        self.assertIsNotNone(system.data_analyzer)

    def test_start_stop_system(self):
        """Test Start und Stop des Systems."""
        system = IntegratedMiningSystem(config=self.config)
        
        # Start
        system.start_integrated_mining()
        self.assertTrue(system.is_running)
        time.sleep(0.5)  # Kurz laufen lassen
        
        # Stop
        system.stop_integrated_mining()
        self.assertFalse(system.is_running)

    def test_context_manager(self):
        """Test Context Manager."""
        with IntegratedMiningSystem(config=self.config) as system:
            self.assertTrue(system.is_running)
            time.sleep(0.3)
        # Nach dem with-Block sollte das System gestoppt sein
        self.assertFalse(system.is_running)

    def test_run_for(self):
        """Test run_for Methode."""
        system = IntegratedMiningSystem(config=self.config)
        start = time.time()
        system.run_for(0.5)
        elapsed = time.time() - start
        
        self.assertFalse(system.is_running)
        self.assertGreaterEqual(elapsed, 0.5)
        self.assertLess(elapsed, 1.0)

    def test_step_once(self):
        """Test einzelner Schritt."""
        system = IntegratedMiningSystem(config=self.config)
        system.initialize_components()
        
        initial_profit = system.system_status.get("total_profit", 0.0)
        system.step_once(include_collection=True, include_analysis=True)
        
        # Status sollte aktualisiert sein
        self.assertIsNotNone(system.system_status.get("last_update"))
        # Profit sollte gewachsen sein (minimal)
        self.assertGreaterEqual(system.system_status.get("total_profit", 0.0), initial_profit)

    def test_risk_assessment(self):
        """Test Risikobewertung."""
        system = IntegratedMiningSystem(config=self.config)
        system.initialize_components()
        
        # Normal-Fall
        assessment = system._perform_risk_assessment()
        self.assertIn(assessment.level, ["low", "medium", "high"])
        
        # Überhitzungs-Szenario simulieren
        system.mining_rigs[0]["temperature"] = 95.0
        system.mining_rigs[0]["status"] = "OVERHEATING"
        assessment = system._perform_risk_assessment()
        self.assertEqual(assessment.level, "high")
        self.assertGreater(len(assessment.issues), 0)

    def test_optimization_strategy(self):
        """Test Optimierungsstrategie."""
        system = IntegratedMiningSystem(config=self.config)
        system.initialize_components()
        
        # Überhitzung simulieren
        system.mining_rigs[0]["temperature"] = 92.0
        system.mining_rigs[0]["status"] = "OVERHEATING"
        initial_hashrate = system.mining_rigs[0]["hash_rate"]
        
        system.optimize_mining_strategy()
        
        # Hashrate sollte reduziert worden sein
        self.assertLess(system.mining_rigs[0]["hash_rate"], initial_hashrate)
        # Temperatur sollte gesunken sein
        self.assertLess(system.mining_rigs[0]["temperature"], 92.0)

    def test_scale_mining_operation(self):
        """Test Skalierung der Mining-Operation."""
        system = IntegratedMiningSystem(config=self.config)
        system.initialize_components()
        
        # Aufstocken
        system.scale_mining_operation(5)
        self.assertEqual(len(system.mining_rigs), 5)
        
        # Reduzieren
        system.scale_mining_operation(2)
        self.assertEqual(len(system.mining_rigs), 2)

    def test_operational_health(self):
        """Test Operational Health Evaluation."""
        system = IntegratedMiningSystem(config=self.config)
        system.initialize_components()
        system.step_once()
        
        health = system.evaluate_operational_health()
        
        self.assertIn("risk_level", health)
        self.assertIn("active_rigs", health)
        self.assertIn("daily_profit", health)
        self.assertIn("performance_metrics", health)
        self.assertGreater(health["active_rigs"], 0)

    def test_system_report(self):
        """Test System-Report-Generierung."""
        system = IntegratedMiningSystem(config=self.config)
        system.initialize_components()
        system.step_once()
        
        report = system.generate_system_report()
        
        self.assertIn("INTEGRATED MINING SYSTEM", report)
        self.assertIn("STATUS REPORT", report)
        self.assertIn("Active Rigs", report)
        self.assertIn("Daily Profit", report)

    def test_performance_metrics_tracking(self):
        """Test Performance-Metriken-Tracking."""
        system = IntegratedMiningSystem(config=self.config)
        system.start_integrated_mining()
        
        time.sleep(0.5)
        
        system.stop_integrated_mining()
        
        # Performance-Metriken sollten erfasst worden sein
        metrics = system._performance_metrics
        self.assertGreater(metrics["monitoring_cycles"], 0)
        self.assertGreater(metrics["collection_cycles"], 0)
        self.assertGreater(metrics["analysis_cycles"], 0)

    def test_concurrent_access(self):
        """Test gleichzeitiger Zugriff."""
        import threading
        
        system = IntegratedMiningSystem(config=self.config)
        system.start_integrated_mining()
        
        results = []
        
        def access_system():
            for _ in range(10):
                health = system.evaluate_operational_health()
                results.append(health["active_rigs"])
                time.sleep(0.01)
        
        threads = [threading.Thread(target=access_system) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        system.stop_integrated_mining()
        
        # Alle Zugriffe sollten erfolgreich gewesen sein
        self.assertEqual(len(results), 30)

    def test_double_start_prevention(self):
        """Test Verhinderung von Doppel-Start."""
        system = IntegratedMiningSystem(config=self.config)
        
        system.start_integrated_mining()
        self.assertTrue(system.is_running)
        
        # Zweiter Start sollte nichts ändern
        system.start_integrated_mining()
        self.assertTrue(system.is_running)
        
        system.stop_integrated_mining()

    def test_double_stop_safety(self):
        """Test Sicherheit bei Doppel-Stop."""
        system = IntegratedMiningSystem(config=self.config)
        
        system.start_integrated_mining()
        system.stop_integrated_mining()
        self.assertFalse(system.is_running)
        
        # Zweiter Stop sollte sicher sein
        system.stop_integrated_mining()
        self.assertFalse(system.is_running)


class TestModuleFunctions(unittest.TestCase):
    """Tests für Modul-Funktionen."""

    def test_module_functions(self):
        """Test der globalen Modul-Funktionen."""
        from mining_system_integration import (
            start_mining_system,
            stop_mining_system,
            get_mining_status,
            generate_mining_report,
            optimize_mining,
            scale_mining,
        )
        
        # Diese Funktionen sollten alle ohne Fehler ausführbar sein
        start_mining_system()
        time.sleep(0.3)
        
        status = get_mining_status()
        self.assertIn("system_name", status)
        
        report = generate_mining_report()
        self.assertIsInstance(report, str)
        
        optimize_mining()
        scale_mining(4)
        
        stop_mining_system()


def run_all_tests():
    """Führt alle Tests aus und gibt einen detaillierten Report."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(__import__(__name__))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
