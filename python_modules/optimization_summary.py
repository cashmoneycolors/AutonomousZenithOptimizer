#!/usr/bin/env python3
"""
OPTIMIZATION SUMMARY MODULE v5.0
Systemweite Zusammenfassung aller Optimierungen - VEREINFACHT UND ROBUST
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, cast
import os

# Import required functions from other modules
from python_modules.predictive_maintenance import analyze_rig_health, predict_rig_failures
from python_modules.algorithm_switcher import get_algorithm_analytics
from python_modules.electricity_cost_manager import electricity_cost_manager
from python_modules.energy_efficiency import evaluate_all_rigs
from python_modules.temperature_optimizer import get_thermal_status, get_thermal_efficiency_report
from python_modules.config_manager import get_rigs_config
from python_modules.main_integration_module import get_maintenance_status
from python_modules.enhanced_logging import log_event


AnalyzeRigHealthFn = Callable[[Dict[str, Any]], Dict[str, Any]]
PredictRigFailuresFn = Callable[[str], Dict[str, Any]]
AlgorithmAnalyticsFn = Callable[[], Dict[str, Any]]
ElectricityMonitorFn = Callable[[], Dict[str, Any]]
ElectricityCostOverviewFn = Callable[[List[Dict[str, Any]]], Dict[str, Any]]

_analyze_rig_health: AnalyzeRigHealthFn = analyze_rig_health
_predict_rig_failures: PredictRigFailuresFn = predict_rig_failures
_get_algorithm_analytics: AlgorithmAnalyticsFn = get_algorithm_analytics
_electricity_monitor: ElectricityMonitorFn = electricity_cost_manager.monitor_electricity_costs
_electricity_overview: ElectricityCostOverviewFn = electricity_cost_manager.get_cost_analysis


RISK_LEVEL_ORDER: Dict[str, int] = {
    'critical': 4,
    'high': 3,
    'medium': 2,
    'low': 1,
    'unknown': 0,
}


class OptimizationSummaryAggregator:
    """Stellt eine systemweite Zusammenfassung der Optimierungsbereiche bereit."""

    def __init__(self, export_dir: str = 'reports/optimization'):
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def collect_summary(self, include_rig_details: bool = True) -> Dict[str, Any]:
        """Fasst alle Optimierungs-Domänen zu einem konsolidierten Report zusammen."""
        timestamp = datetime.now(timezone.utc).isoformat()
        rigs = get_rigs_config()

        maintenance = get_maintenance_status()
        thermal_status = get_thermal_status()
        thermal_report = get_thermal_efficiency_report()
        energy_efficiency = evaluate_all_rigs()
        algorithm_status = cast(Dict[str, Any], self._safe_call(_get_algorithm_analytics, default={}))
        electricity_snapshot = cast(
            Dict[str, Any],
            self._safe_call(
                _electricity_monitor,
                default={},
            ),
        )
        electricity_overview = cast(
            Dict[str, Any],
            self._safe_call(
                _electricity_overview,
                rigs,
                default={},
            ),
        )

        rig_snapshots: List[Dict[str, Any]] = []
        high_risk: List[Dict[str, Any]] = []
        summary_metrics: Dict[str, Any] = {
            'total_rigs': len(rigs),
            'high_risk_count': 0,
            'average_efficiency': 0.0,
        }

        if include_rig_details:
            rig_snapshots = self._build_rig_snapshots(rigs, energy_efficiency)
            high_risk = self._get_high_risk_rigs(rig_snapshots)
            summary_metrics = self._calculate_metrics(rig_snapshots, high_risk)

        kpi_summary = self._compose_kpis(
            summary_metrics,
            thermal_report,
            algorithm_status,
            electricity_overview,
            electricity_snapshot,
        )
        recommendations = self._collect_recommendations(rig_snapshots, electricity_snapshot)

        summary: Dict[str, Any] = {
            'summary_generated': timestamp,
            'maintenance': maintenance,
            'thermal_status': thermal_status,
            'thermal_efficiency': thermal_report,
            'energy_efficiency': self._summarize_energy(energy_efficiency),
            'algorithm_status': algorithm_status,
            'electricity_snapshot': electricity_snapshot,
            'electricity_overview': electricity_overview,
            'kpi_summary': kpi_summary,
            'recommendations': recommendations,
        }

        if include_rig_details:
            summary.update(
                {
                    'rig_snapshots': rig_snapshots,
                    'high_risk_rigs': high_risk,
                    'summary_metrics': summary_metrics,
                }
            )

        log_event('OPTIMIZATION_SUMMARY_COLLECTED', {
            'timestamp': timestamp,
            'rigs_tracked': len(rig_snapshots),
            'high_risk': len(high_risk),
            'fleet_health': kpi_summary.get('fleet_health'),
        })

        return summary

    def export_summary(self, summary: Dict[str, Any], filename: Optional[str] = None) -> Path:
        """Speichert die Zusammenfassung als JSON-Datei."""
        filename = filename or f"optimization_summary_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        destination = self.export_dir / filename
        with destination.open('w', encoding='utf-8') as fh:
            json.dump(summary, fh, indent=2, ensure_ascii=False)
        return destination

    def render_dashboard(self, summary: Dict[str, Any]) -> str:
        """Erstellt eine kompakte Dashboard-Darstellung für die Konsole oder UI."""
        lines: List[str] = []
        lines.append('=== Optimization Summary ===')
        lines.append(f"Timestamp: {summary['summary_generated']}")
        lines.append(f"Monitoring Active: {summary['maintenance'].get('monitoring_active', False)}")
        lines.append(
            f"Temperature Optimization Active: {summary['thermal_status'].get('optimization_active', False)}"
        )

        kpis = summary.get('kpi_summary', {})
        lines.append(
            "Fleet Health: {fleet} | Thermal Eff.: {thermal:.1f}% | Profit Margin: {profit:.1f}%".format(
                fleet=kpis.get('fleet_health', 'n/a'),
                thermal=kpis.get('avg_thermal_efficiency', 0.0),
                profit=kpis.get('profit_margin_percent', 0.0),
            )
        )
        lines.append(
            "Algorithms: {current} (best {best}) | Cost CHF/kWh: {cost:.3f}".format(
                current=kpis.get('algorithm_current', 'n/a'),
                best=kpis.get('algorithm_best', 'n/a'),
                cost=kpis.get('electricity_cost_chf_kwh', 0.0),
            )
        )

        metrics = summary.get('summary_metrics', {})
        if metrics:
            lines.append(
                f"Rigs Monitored: {metrics.get('total_rigs', 0)} | High Risk: {metrics.get('high_risk_count', 0)}"
            )
            avg_eff = metrics.get('average_efficiency', 0)
            lines.append(
                f"Average Rig Efficiency: {avg_eff:.2f} MH/s/W" if avg_eff else "Average Rig Efficiency: n/a"
            )

        if summary.get('high_risk_rigs'):
            lines.append('Top Risky Rigs:')
            for rig in summary['high_risk_rigs'][:3]:
                lines.append(
                    f" - {rig['rig_id']} ({rig['risk_level'].upper()}): {rig['risk_notes']}"
                )
        else:
            lines.append('No rigs in high risk state')

        if summary.get('recommendations'):
            lines.append('-- Recommended Actions --')
            for recommendation in summary['recommendations'][:6]:
                lines.append(f" • {recommendation}")

        return '\n'.join(lines)

    def _summarize_energy(self, energy: Dict[str, Any]) -> Dict[str, Any]:
        """Bereitet die Energy Efficiency Daten für Export vor."""
        rig_count = len(energy)
        average_efficiency = 0.0
        if rig_count:
            scores = [vals.get('efficiency_mhs_per_watt', 0) for vals in energy.values()]
            valid_scores = [score for score in scores if score]
            average_efficiency = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0

        return {
            'rig_count': rig_count,
            'average_efficiency_mhs_per_watt': round(average_efficiency, 4),
            'per_rig': energy,
        }

    def _build_rig_snapshots(
        self,
        rigs: List[Dict[str, Any]],
        energy_efficiency: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        snapshots: List[Dict[str, Any]] = []

        for idx, rig in enumerate(rigs, start=1):
            rig_id = rig.get('id', f'rig_{idx}')
            risk = _predict_rig_failures(rig_id)
            health = _analyze_rig_health(rig)
            energy = energy_efficiency.get(rig_id, {})

            recommendations: List[str] = []
            for prediction in risk.get('predictions', []):
                recommendations.extend(prediction.get('recommendations', []))

            snapshot = {
                'rig_id': rig_id,
                'type': rig.get('type', 'unknown'),
                'algorithm': rig.get('algorithm'),
                'temperature': health.get('current_temperature', rig.get('temperature')),
                'hashrate': health.get('current_hashrate', rig.get('hash_rate')),
                'risk_level': risk.get('overall_risk_level', 'unknown'),
                'risk_notes': ', '.join(
                    {
                        p.get('component', '')
                        for p in risk.get('predictions', [])
                        if p.get('component')
                    }
                ),
                'health_recommendations': recommendations + health.get('recommendations', []),
                'energy_efficiency': energy,
                'status_flags': self._derive_status_flags(health, risk, energy),
                'health': health,
            }
            snapshots.append(snapshot)

        return snapshots

    def _get_high_risk_rigs(self, snapshots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        high_risk = [snap for snap in snapshots if RISK_LEVEL_ORDER.get(snap['risk_level'], 0) >= 3]
        return sorted(high_risk, key=lambda snap: RISK_LEVEL_ORDER.get(snap['risk_level'], 0), reverse=True)

    def _calculate_metrics(self, snapshots: List[Dict[str, Any]], high_risk: List[Dict[str, Any]]) -> Dict[str, Any]:
        efficiency_values = [snap['energy_efficiency'].get('efficiency_mhs_per_watt', 0) for snap in snapshots]
        valid = [value for value in efficiency_values if value]
        average_efficiency = sum(valid) / len(valid) if valid else 0.0

        return {
            'total_rigs': len(snapshots),
            'high_risk_count': len(high_risk),
            'average_efficiency': average_efficiency,
        }

    def _compose_kpis(
        self,
        summary_metrics: Dict[str, Any],
        thermal_report: Dict[str, Any],
        algorithm_status: Dict[str, Any],
        electricity_overview: Dict[str, Any],
        electricity_snapshot: Dict[str, Any],
    ) -> Dict[str, Any]:
        fleet_health = 'low'
        if summary_metrics.get('high_risk_count', 0):
            fleet_health = 'high'

        avg_thermal = thermal_report.get('average_thermal_efficiency', 0.0)
        overheating = thermal_report.get('overheating_rigs', 0)

        profit_margin = electricity_overview.get('daily_projection', {}).get('profit_margin_percent', 0.0)

        return {
            'fleet_health': fleet_health,
            'avg_thermal_efficiency': round(avg_thermal, 2),
            'overheating_rigs': overheating,
            'optimal_rigs': thermal_report.get('thermal_optimal_rigs', 0),
            'algorithm_current': algorithm_status.get('current_algorithm'),
            'algorithm_best': algorithm_status.get('best_algorithm'),
            'electricity_cost_chf_kwh': round(
                electricity_snapshot.get('current_cost_per_kwh', 0.0),
                3,
            ),
            'profit_margin_percent': round(profit_margin, 2),
            'alerts_active': bool(electricity_snapshot.get('alerts_active')),
        }

    def _collect_recommendations(
        self,
        rig_snapshots: List[Dict[str, Any]],
        electricity_snapshot: Dict[str, Any],
    ) -> List[str]:
        recommendations: List[str] = []

        for snapshot in rig_snapshots:
            for entry in snapshot.get('health_recommendations', []):
                if entry and entry not in recommendations:
                    recommendations.append(entry)

            temperature_actions = snapshot.get('health', {}).get('temperature_optimization', {})
            for action in temperature_actions.get('actions_taken', []):
                formatted = f"{snapshot['rig_id']}: {action}"
                if formatted not in recommendations:
                    recommendations.append(formatted)

        for entry in electricity_snapshot.get('recommendations', []) or []:
            if entry not in recommendations:
                recommendations.append(entry)

        return recommendations

    @staticmethod
    def _derive_status_flags(
        health: Dict[str, Any],
        prediction: Dict[str, Any],
        energy: Dict[str, Any],
    ) -> List[str]:
        flags: List[str] = []

        if health.get('temperature_status') == 'warning':
            flags.append('THERMAL_WARNING')
        if health.get('hashrate_status') in {'warning', 'critical'}:
            flags.append('HASHRATE_DROP')
        if energy.get('status') == 'throttle':
            flags.append('EFFICIENCY_ALERT')

        risk_level = prediction.get('overall_risk_level')
        if risk_level in {'critical', 'high'}:
            flags.append('MAINTENANCE_REQUIRED')

        return flags or ['OPTIMAL']

    @staticmethod
    def _safe_call(
        func: Callable[..., Any],
        *args: Any,
        default: Optional[Any] = None,
        **kwargs: Any,
    ) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as exc:  # pragma: no cover - Logging optional
            return default if default is not None else {'error': str(exc)}


if __name__ == '__main__':
    aggregator = OptimizationSummaryAggregator()
    summary = aggregator.collect_summary()
    print(aggregator.render_dashboard(summary))
    exported = aggregator.export_summary(summary)
    print(f"\n📦 Systemweite Zusammenfassung exportiert nach {exported}")
