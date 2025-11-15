import time
import unittest

from python_modules.mining_system_integration import IntegratedMiningSystem


class IntegratedMiningSystemTests(unittest.TestCase):
    def setUp(self) -> None:
        self.system = IntegratedMiningSystem(
            monitoring_interval=0.1,
            collection_interval=0.2,
            analysis_interval=0.3,
        )
        self.system.initialize_components()

    def tearDown(self) -> None:
        try:
            self.system.stop_integrated_mining()
        finally:
            # Sicherstellen, dass keine Threads mehr laufen
            time.sleep(0.05)

    def test_risk_assessment_detects_overheating(self):
        with self.system._lock:
            self.system.mining_rigs[0]['temperature'] = 92.0
            self.system.mining_rigs[0]['status'] = 'OVERHEATING'

        self.system._perform_risk_assessment()
        assessment = self.system.system_status['last_risk_assessment']

        self.assertEqual('high', assessment['level'])
        self.assertGreaterEqual(assessment['score'], 60)
        self.assertTrue(
            any('überhitzt' in issue.lower() for issue in assessment['issues'])
        )

    def test_optimize_mining_strategy_reduces_hashrate_on_high_risk(self):
        with self.system._lock:
            rig = self.system.mining_rigs[0]
            rig['temperature'] = 90.0
            rig['status'] = 'OVERHEATING'
            rig['hash_rate'] = 100.0
            rig['profit_per_day'] = 20.0
            self.system.system_status['daily_profit'] = 8.0

        self.system._perform_risk_assessment()
        original_hash_rate = self.system.mining_rigs[0]['hash_rate']

        self.system.optimize_mining_strategy()

        optimized_rig = self.system.mining_rigs[0]
        self.assertLess(optimized_rig['hash_rate'], original_hash_rate)
        self.assertLessEqual(optimized_rig['temperature'], 84.0)
        self.assertTrue(self.system.system_status['advisories'])

    def test_context_manager_starts_and_stops_cleanly(self):
        with IntegratedMiningSystem(
            monitoring_interval=0.1,
            collection_interval=0.2,
            analysis_interval=0.3,
        ) as running_system:
            time.sleep(0.2)
            self.assertTrue(running_system.is_running)

        self.assertFalse(running_system.is_running)

    def test_evaluate_operational_health_reports_metrics(self):
        self.system.step_once(include_collection=False, include_analysis=True)
        health = self.system.evaluate_operational_health()

        self.assertIn('risk_level', health)
        self.assertIn('average_efficiency', health)
        self.assertIsInstance(health['advisories'], list)


if __name__ == '__main__':
    unittest.main()
