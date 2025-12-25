import json
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

from python_modules.optimization_summary import OptimizationSummaryAggregator


class OptimizationSummaryAggregatorTests(unittest.TestCase):
    def test_collect_summary_compiles_multi_domain_view(self):
        rig = {
            'id': 'RIG-1',
            'type': 'RTX 4090',
            'temperature': 72.0,
            'hash_rate': 120.0,
            'power_consumption': 450,
            'algorithm': 'ethash',
        }

        health_snapshot = {
            'current_temperature': 72.0,
            'current_hashrate': 120.0,
            'temperature_status': 'warning',
            'hashrate_status': 'normal',
            'recommendations': ['Check airflow'],
            'temperature_optimization': {'actions_taken': ['fan_speed_70%']},
        }

        prediction = {
            'overall_risk_level': 'high',
            'predictions': [
                {
                    'component': 'Temperature System',
                    'recommendations': ['Improve cooling']
                }
            ],
        }

        with ExitStack() as stack:
            stack.enter_context(patch('python_modules.optimization_summary.get_rigs_config', return_value=[rig]))
            stack.enter_context(patch('python_modules.optimization_summary._analyze_rig_health', return_value=health_snapshot))
            stack.enter_context(patch('python_modules.optimization_summary._predict_rig_failures', return_value=prediction))
            stack.enter_context(patch('python_modules.optimization_summary.evaluate_all_rigs', return_value={'RIG-1': {'efficiency_mhs_per_watt': 0.27, 'status': 'normal'}}))
            stack.enter_context(patch('python_modules.optimization_summary.get_maintenance_status', return_value={'monitoring_active': True}))
            stack.enter_context(patch('python_modules.optimization_summary.get_thermal_status', return_value={'optimization_active': True}))
            stack.enter_context(patch('python_modules.optimization_summary.get_thermal_efficiency_report', return_value={'average_thermal_efficiency': 84.0, 'overheating_rigs': 1, 'thermal_optimal_rigs': 0}))
            stack.enter_context(patch('python_modules.optimization_summary._get_algorithm_analytics', return_value={'current_algorithm': 'ethash', 'best_algorithm': 'kheavyhash'}))
            stack.enter_context(patch('python_modules.optimization_summary._electricity_monitor', return_value={'current_cost_per_kwh': 0.32, 'recommendations': ['Use night tariff'], 'alerts_active': True}))
            stack.enter_context(patch('python_modules.optimization_summary._electricity_overview', return_value={'daily_projection': {'profit_margin_percent': 38.5}}))
            stack.enter_context(patch('python_modules.optimization_summary.log_event'))

            aggregator = OptimizationSummaryAggregator(export_dir=tempfile.mkdtemp())
            summary = aggregator.collect_summary()

        self.assertEqual(summary['summary_metrics']['high_risk_count'], 1)
        self.assertEqual(summary['kpi_summary']['fleet_health'], 'high')
        self.assertIn('Use night tariff', summary['recommendations'])
        self.assertIn('RIG-1: fan_speed_70%', summary['recommendations'])
        self.assertEqual(summary['rig_snapshots'][0]['status_flags'], ['THERMAL_WARNING', 'MAINTENANCE_REQUIRED'])

        dashboard = aggregator.render_dashboard(summary)
        self.assertIn('Fleet Health: high', dashboard)
        self.assertIn('Algorithms: ethash (best kheavyhash)', dashboard)

    def test_export_summary_writes_json_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            aggregator = OptimizationSummaryAggregator(export_dir=tmp_dir)
            summary = {'status': 'ok'}
            export_path = aggregator.export_summary(summary, filename='summary.json')

            exported_file = Path(export_path)
            self.assertTrue(exported_file.exists())
            with exported_file.open('r', encoding='utf-8') as handle:
                data = json.load(handle)

        self.assertEqual(data['status'], 'ok')


if __name__ == '__main__':
    unittest.main()
