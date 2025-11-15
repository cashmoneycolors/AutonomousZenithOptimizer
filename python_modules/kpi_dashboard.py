#!/usr/bin/env python3
"""
QUANTUM KPI DASHBOARD - Performance Monitoring & Visualisierung
Enterprise Dashboard für KPIs und System-Metriken
"""
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import os

class QuantumKpiDashboard:
    """QUANTUM KPI Dashboard für Performance-Visualisierung"""

    def __init__(self, dashboard_name: str = "QUANTUM_KPI_DASHBOARD"):
        self.dashboard_name = dashboard_name
        self.kpis = {}
        self.historical_data = []
        self.performance_metrics = {}
        self.alert_thresholds = {}
        self.dashboard_config = self._initialize_dashboard()

        # Initialize Core KPIs
        self._initialize_core_kpis()

        print("[QUANTUM KPI DASHBOARD] Quantum KPI Dashboard initialized")
        print("[QUANTUM KPI DASHBOARD] Dashboard Name: {}".format(self.dashboard_name))
        print("[QUANTUM KPI DASHBOARD] Active KPIs: {}".format(len(self.kpis)))

    def _initialize_dashboard(self) -> Dict[str, Any]:
        """Initialize das KPI Dashboard"""
        return {
            'theme': 'dark_quantum',  # Dark theme for quantum systems
            'refresh_interval': 30,   # 30 seconds auto-refresh
            'max_historical_points': 1000,
            'alerts_enabled': True,
            'visualization_engine': 'quantum_charts_3d'
        }

    def _initialize_core_kpis(self):
        """Initialize zentrale KPIs"""
        core_kpis = {
            'system_performance': {
                'value': 0.0,
                'target': 99.9,
                'unit': '%',
                'trend': 'stable',
                'alert_threshold': 97.0
            },
            'profit_generation': {
                'value': 0.0,
                'target': 250.0,  # CHF/Day
                'unit': 'CHF/DAY',
                'trend': 'increasing',
                'alert_threshold': 100.0
            },
            'quantum_accuracy': {
                'value': 0.0,
                'target': 99.85,
                'unit': '%',
                'trend': 'stable',
                'alert_threshold': 98.0
            },
            'system_uptime': {
                'value': 99.99,
                'target': 99.99,
                'unit': '%',
                'trend': 'stable',
                'alert_threshold': 99.95
            },
            'risk_exposure': {
                'value': 0.0,
                'target': 5.0,   # Maximum 5% risk
                'unit': '%',
                'trend': 'stable',
                'alert_threshold': 8.0
            },
            'efficiency_score': {
                'value': 0.0,
                'target': 95.0,
                'unit': '%',
                'trend': 'improving',
                'alert_threshold': 85.0
            }
        }

        for kpi_name, kpi_data in core_kpis.items():
            self.kpis[kpi_name] = kpi_data
            self.alert_thresholds[kpi_name] = kpi_data['alert_threshold']

    def update_kpi_value(self, kpi_name: str, new_value: float, metadata: Optional[Dict[str, Any]] = None):
        """Update KPI Wert mit Metadaten"""
        if kpi_name in self.kpis:
            old_value = self.kpis[kpi_name]['value']
            self.kpis[kpi_name]['value'] = new_value

            # Trend berechnen
            trend = self._calculate_trend(kpi_name, old_value, new_value)
            self.kpis[kpi_name]['trend'] = trend

            # Historical Data aufzeichnen
            historical_point = {
                'timestamp': datetime.now().isoformat(),
                'kpi_name': kpi_name,
                'old_value': old_value,
                'new_value': new_value,
                'trend': trend,
                'metadata': metadata or {}
            }

            self.historical_data.append(historical_point)

            # Limite historische Daten
            if len(self.historical_data) > self.dashboard_config['max_historical_points']:
                self.historical_data = self.historical_data[-self.dashboard_config['max_historical_points']:]

            # Alarme prüfen
            self._check_alerts(kpi_name, new_value)

    def _calculate_trend(self, kpi_name: str, old_value: float, new_value: float) -> str:
        """Berechne KPI Trend"""
        if abs(new_value - old_value) < 0.01:  # Very small change
            return 'stable'
        elif new_value > old_value * 1.05:  # >5% increase
            return 'increasing'
        elif new_value < old_value * 0.95:  # >5% decrease
            return 'decreasing'
        elif new_value > old_value:
            return 'increasing_slightly'
        else:
            return 'decreasing_slightly'

    def _check_alerts(self, kpi_name: str, current_value: float):
        """Prüfe KPI alerts"""
        if not self.dashboard_config['alerts_enabled']:
            return

        if kpi_name in self.alert_thresholds:
            threshold = self.alert_thresholds[kpi_name]
            target = self.kpis[kpi_name]['target']

            # Alert Logik
            if kpi_name == 'profit_generation':
                if current_value < threshold:
                    self._trigger_alert(kpi_name, 'LOW_PROFIT_WARNING', current_value, threshold)
                elif current_value > target * 1.2:
                    self._trigger_alert(kpi_name, 'HIGH_PROFIT_ACHIEVEMENT', current_value, target)
            elif kpi_name == 'system_performance':
                if current_value < threshold:
                    self._trigger_alert(kpi_name, 'PERFORMANCE_DEGRADATION', current_value, threshold)
            elif kpi_name == 'risk_exposure':
                if current_value > threshold:
                    self._trigger_alert(kpi_name, 'HIGH_RISK_EXPOSURE', current_value, threshold)
            elif kpi_name == 'quantum_accuracy':
                if current_value < threshold:
                    self._trigger_alert(kpi_name, 'ACCURACY_DEGRADATION', current_value, threshold)

    def _trigger_alert(self, kpi_name: str, alert_type: str, current_value: float, threshold: float):
        """Trigger KPI Alert"""
        alert_data = {
            'timestamp': datetime.now().isoformat(),
            'kpi_name': kpi_name,
            'alert_type': alert_type,
            'current_value': current_value,
            'threshold': threshold,
            'severity': self._calculate_severity(kpi_name, current_value, threshold)
        }

        print("[QUANTUM KPI DASHBOARD] 🚨 ALERT: {} - {} (Current: {}, Threshold: {})".format(
            kpi_name.upper(), alert_type, current_value, threshold
        ))

    def _calculate_severity(self, kpi_name: str, current_value: float, threshold: float) -> str:
        """Berechne Alert Severity"""
        deviation = abs(current_value - threshold) / threshold

        if deviation > 0.5:
            return 'CRITICAL'
        elif deviation > 0.25:
            return 'HIGH'
        elif deviation > 0.1:
            return 'MEDIUM'
        else:
            return 'LOW'

    def get_dashboard_snapshot(self) -> Dict[str, Any]:
        """Hole komplette Dashboard Snapshot"""
        kpi_summary = {}
        for kpi_name, kpi_data in self.kpis.items():
            kpi_summary[kpi_name] = {
                'current_value': kpi_data['value'],
                'target': kpi_data['target'],
                'unit': kpi_data['unit'],
                'trend': kpi_data['trend'],
                'achievement_percent': min(100.0, (kpi_data['value'] / kpi_data['target']) * 100 if kpi_data['target'] != 0 else 0)
            }

        # Performance Score berechnen
        total_achievement = sum(kpi['achievement_percent'] for kpi in kpi_summary.values())
        overall_score = total_achievement / len(kpi_summary)

        return {
            'dashboard_name': self.dashboard_name,
            'timestamp': datetime.now().isoformat(),
            'kpis': kpi_summary,
            'overall_score': overall_score,
            'alerts_active': len([k for k in self.alert_thresholds.keys()]),
            'dashboard_config': self.dashboard_config,
            'historical_points': len(self.historical_data),
            'system_status': 'EXCELLENT' if overall_score > 95 else 'GOOD' if overall_score > 85 else 'NEEDS_ATTENTION'
        }

    def get_kpi_chart_data(self, kpi_name: str, hours: int = 24) -> Dict[str, Any]:
        """Hole KPI Chart-Daten für Visualisierung"""
        if kpi_name not in self.kpis:
            return {'error': 'KPI not found'}

        # Filter historical data for this KPI and time range
        cutoff_time = datetime.now() - timedelta(hours=hours)
        kpi_data = [
            point for point in self.historical_data
            if point['kpi_name'] == kpi_name and datetime.fromisoformat(point['timestamp']) > cutoff_time
        ]

        # Prepare chart data
        chart_data = {
            'kpi_name': kpi_name,
            'time_range_hours': hours,
            'data_points': [
                {
                    'timestamp': point['timestamp'],
                    'value': point['new_value'],
                    'trend': point['trend']
                }
                for point in kpi_data
            ],
            'current_value': self.kpis[kpi_name]['value'],
            'target': self.kpis[kpi_name]['target'],
            'unit': self.kpis[kpi_name]['unit']
        }

        return chart_data

    def generate_dashboard_report(self, include_charts: bool = False) -> Dict[str, Any]:
        """Generiere komplette Dashboard Report"""
        snapshot = self.get_dashboard_snapshot()

        report = {
            'report_generated': datetime.now().isoformat(),
            'dashboard_snapshot': snapshot,
            'performance_analysis': self._analyze_performance(snapshot),
            'recommendations': self._generate_recommendations(snapshot),
            'system_health': self._assess_system_health(snapshot)
        }

        if include_charts:
            charts_data = {}
            for kpi_name in self.kpis.keys():
                charts_data[kpi_name] = self.get_kpi_chart_data(kpi_name, 7)  # 7 day chart
            report['charts_data'] = charts_data

        return report

    def _analyze_performance(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Analyziere Performance"""
        kpis = snapshot['kpis']

        # Trend analysis
        improving_kpis = [k for k, v in kpis.items() if v['trend'] in ['increasing', 'increasing_slightly']]
        stable_kpis = [k for k, v in kpis.items() if v['trend'] == 'stable']
        declining_kpis = [k for k, v in kpis.items() if v['trend'] in ['decreasing', 'decreasing_slightly']]

        return {
            'improving_kpis_count': len(improving_kpis),
            'stable_kpis_count': len(stable_kpis),
            'declining_kpis_count': len(declining_kpis),
            'overall_trend': 'POSITIVE' if len(improving_kpis) > len(declining_kpis) * 2 else 'STABLE' if len(stable_kpis) > len(declining_kpis) else 'NEEDS_ATTENTION',
            'performance_score': snapshot['overall_score']
        }

    def _generate_recommendations(self, snapshot: Dict[str, Any]) -> List[str]:
        """Generiere Empfehlungen"""
        recommendations = []
        kpis = snapshot['kpis']

        for kpi_name, kpi_data in kpis.items():
            achievement = kpi_data['achievement_percent']

            if achievement < 80:
                recommendations.append(f"Improve {kpi_name.replace('_', ' ').title()}: Currently at {achievement:.1f}% of target")
            elif achievement > 120 and kpi_name == 'profit_generation':
                recommendations.append(f"Consider scaling up operations - {kpi_name.replace('_', ' ').title()} exceeded target by {achievement-100:.1f}%")

        if not recommendations:
            recommendations.append("All KPIs performing well - maintain current operations")

        return recommendations

    def _assess_system_health(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Bewerte System Health"""
        score = snapshot['overall_score']
        status = snapshot['system_status']

        health_indicators = {
            'cpu_usage': 45.2,  # Mock data
            'memory_usage': 62.8,
            'disk_io': 23.4,
            'network_latency': 12.5
        }

        health_score = score / 100 * 90 + 10  # Convert to 10-100 scale

        return {
            'overall_health_score': health_score,
            'system_status': status,
            'health_indicators': health_indicators,
            'last_assessment': datetime.now().isoformat()
        }

# Global Dashboard Instance
quantum_kpi_dashboard = QuantumKpiDashboard()

def update_kpi(kpi_name: str, value: float, metadata=None):
    """Update KPI Wert"""
    quantum_kpi_dashboard.update_kpi_value(kpi_name, value, metadata)

def get_dashboard_snapshot():
    """Hole Dashboard Snapshot"""
    return quantum_kpi_dashboard.get_dashboard_snapshot()

def generate_dashboard_report(include_charts=False):
    """Generiere Dashboard Report"""
    return quantum_kpi_dashboard.generate_dashboard_report(include_charts)

if __name__ == "__main__":
    print("QUANTUM KPI DASHBOARD - Performance Monitoring & Visualisierung")
    print("=" * 75)

    print("[QUANTUM KPI DASHBOARD] Testing Quantum KPI Dashboard...")

    # Test KPI Updates
    update_kpi('system_performance', 99.7)
    update_kpi('profit_generation', 285.50)
    update_kpi('quantum_accuracy', 99.82)
    update_kpi('risk_exposure', 3.2)

    # Get Dashboard Snapshot
    snapshot = get_dashboard_snapshot()
    print("[QUANTUM KPI DASHBOARD] KPIs Monitored: {}".format(len(snapshot['kpis'])))
    print("[QUANTUM KPI DASHBOARD] Overall Score: {:.2f}%".format(snapshot['overall_score']))
    print("[QUANTUM KPI DASHBOARD] System Status: {}".format(snapshot['system_status']))

    # Generate Report
    report = generate_dashboard_report()
    print("[QUANTUM KPI DASHBOARD] Report Generated with {} Recommendations".format(
        len(report['recommendations'])
    ))

    print("\n[QUANTUM KPI DASHBOARD] QUANTUM KPI MONITORING OPERATIONAL!")
    print("Enterprise Performance Visualization - Real-time Monitoring Active")
