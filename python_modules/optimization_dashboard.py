#!/usr/bin/env python3
"""
CASH MONEY COLORS ORIGINAL (R) - OPTIMIZATION DASHBOARD
Zentrale Aggregation aller System-Optimierungen mit Export-Funktionen
"""
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

try:
    from python_modules.predictive_maintenance import (
        get_maintenance_status,
        predict_rig_failures,
        analyze_rig_health
    )
    from python_modules.energy_efficiency import (
        get_global_efficiency_report,
        get_cost_analysis
    )
    from python_modules.temperature_optimizer import get_thermal_efficiency_report
    from python_modules.algorithm_switcher import get_algorithm_performance_report
    from python_modules.quantum_optimizer import (
        run_quantum_optimization,
        get_quantum_status
    )
    from python_modules.config_manager import get_config, get_rigs_config
    from python_modules.enhanced_logging import log_event
    from python_modules.alert_system import send_custom_alert
except ModuleNotFoundError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from predictive_maintenance import (
        get_maintenance_status,
        predict_rig_failures,
        analyze_rig_health
    )
    from energy_efficiency import (
        get_global_efficiency_report,
        get_cost_analysis
    )
    from temperature_optimizer import get_thermal_efficiency_report
    from algorithm_switcher import get_algorithm_performance_report
    from quantum_optimizer import (
        run_quantum_optimization,
        get_quantum_status
    )
    from config_manager import get_config, get_rigs_config
    from enhanced_logging import log_event
    from alert_system import send_custom_alert


class OptimizationDashboard:
    """Zentrale Konsole für alle System-Optimierungen"""

    def __init__(self):
        self.dashboard_config = get_config('OptimizationDashboard', {
            'ExportPath': 'optimization_reports',
            'AutoExportEnabled': True,
            'ExportIntervalHours': 24,
            'IncludeCharts': True,
            'ReportFormats': ['json', 'html', 'txt']
        })

        self.export_path = Path(self.dashboard_config.get('ExportPath', 'optimization_reports'))
        self.export_path.mkdir(exist_ok=True)

        self.session_start = datetime.now()
        self.reports_generated = 0

        print("📊 OPTIMIZATION DASHBOARD INITIALIZED")
        print(f"   Export Path: {self.export_path.absolute()}")
        print(f"   Auto-Export: {self.dashboard_config.get('AutoExportEnabled', True)}")

    def gather_all_metrics(self) -> Dict[str, Any]:
        """Sammelt alle Metriken aus sämtlichen Optimierungsmodulen"""
        print("📈 Sammle System-Metriken...")

        all_metrics = {
            'timestamp': datetime.now().isoformat(),
            'session_start': self.session_start.isoformat(),
            'uptime_hours': (datetime.now() - self.session_start).total_seconds() / 3600,
            'modules': {}
        }

        # 1. Predictive Maintenance
        try:
            maintenance_status = get_maintenance_status()
            all_metrics['modules']['predictive_maintenance'] = {
                'status': 'active' if maintenance_status.get('monitoring_active') else 'inactive',
                'rigs_monitored': maintenance_status.get('rigs_monitored', 0),
                'total_data_points': maintenance_status.get('total_data_points', 0),
                'last_check': maintenance_status.get('last_monitoring_cycle')
            }

            # Rig-spezifische Vorhersagen
            rigs = get_rigs_config()
            rig_predictions = []
            for rig in rigs:
                rig_id = rig.get('id', 'unknown')
                try:
                    prediction = predict_rig_failures(rig_id)
                    health = analyze_rig_health(rig)
                    rig_predictions.append({
                        'rig_id': rig_id,
                        'risk_level': prediction.get('overall_risk_level', 'unknown'),
                        'immediate_action_required': prediction.get('immediate_actions_required', False),
                        'predictions_count': len(prediction.get('predictions', [])),
                        'temperature_status': health.get('temperature_status', 'unknown'),
                        'hashrate_status': health.get('hashrate_status', 'unknown'),
                        'efficiency': health.get('efficiency', 0)
                    })
                except Exception as e:
                    print(f"⚠️ Fehler bei Rig {rig_id} Predictive Maintenance: {e}")

            all_metrics['modules']['predictive_maintenance']['rig_predictions'] = rig_predictions

        except Exception as e:
            print(f"⚠️ Predictive Maintenance nicht verfügbar: {e}")
            all_metrics['modules']['predictive_maintenance'] = {'status': 'error', 'message': str(e)}

        # 2. Energy Efficiency
        try:
            efficiency_report = get_global_efficiency_report()
            cost_analysis = get_cost_analysis()

            all_metrics['modules']['energy_efficiency'] = {
                'total_rigs_analyzed': efficiency_report.get('total_rigs_analyzed', 0),
                'avg_efficiency_score': efficiency_report.get('avg_efficiency_score', 0),
                'power_savings_potential_watt': efficiency_report.get('power_savings_potential_watt', 0),
                'cost_savings_potential_hourly': efficiency_report.get('cost_savings_potential_hourly', 0),
                'total_power_consumption_watt': cost_analysis.get('total_power_consumption_watt', 0),
                'total_hourly_cost': cost_analysis.get('total_hourly_cost', 0),
                'total_daily_cost': cost_analysis.get('total_daily_cost', 0)
            }
        except Exception as e:
            print(f"⚠️ Energy Efficiency nicht verfügbar: {e}")
            all_metrics['modules']['energy_efficiency'] = {'status': 'error', 'message': str(e)}

        # 3. Temperature Optimization
        try:
            thermal_report = get_thermal_efficiency_report()

            all_metrics['modules']['temperature_optimization'] = {
                'total_optimizations': thermal_report.get('total_optimizations', 0),
                'total_efficiency_gains': thermal_report.get('total_efficiency_gains', 0),
                'avg_efficiency_gain': thermal_report.get('avg_efficiency_gain', 0),
                'optimizations_by_action': thermal_report.get('optimizations_by_action', {})
            }
        except Exception as e:
            print(f"⚠️ Temperature Optimization nicht verfügbar: {e}")
            all_metrics['modules']['temperature_optimization'] = {'status': 'error', 'message': str(e)}

        # 4. Algorithm Switching
        try:
            algo_report = get_algorithm_performance_report()

            all_metrics['modules']['algorithm_switching'] = {
                'total_switches': algo_report.get('total_switches', 0),
                'current_best_algorithm': algo_report.get('current_best_algorithm', 'unknown'),
                'avg_profit_improvement': algo_report.get('avg_profit_improvement', 0),
                'switch_history': algo_report.get('switch_history', [])[-10:]  # Letzte 10
            }
        except Exception as e:
            print(f"⚠️ Algorithm Switching nicht verfügbar: {e}")
            all_metrics['modules']['algorithm_switching'] = {'status': 'error', 'message': str(e)}

        # 5. Quantum Optimization
        try:
            quantum_status = get_quantum_status()

            all_metrics['modules']['quantum_optimization'] = {
                'total_optimizations': quantum_status.get('total_optimizations', 0),
                'recent_optimizations': quantum_status.get('recent_optimizations', 0),
                'avg_efficiency_gain': quantum_status.get('avg_efficiency_gain', 0),
                'avg_stability_score': quantum_status.get('avg_stability_score', 0),
                'avg_quantum_level': quantum_status.get('avg_quantum_level', 0),
                'max_quantum_level_achieved': quantum_status.get('max_quantum_level_achieved', 0),
                'last_optimization': quantum_status.get('last_optimization', 'never'),
                'quantum_states_count': quantum_status.get('quantum_states_count', 0)
            }
        except Exception as e:
            print(f"⚠️ Quantum Optimization nicht verfügbar: {e}")
            all_metrics['modules']['quantum_optimization'] = {'status': 'error', 'message': str(e)}

        print("✅ Metriken erfolgreich gesammelt")
        return all_metrics

    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generiert vollständigen Optimierungs-Report"""
        print("📝 Generiere Comprehensive Report...")

        metrics = self.gather_all_metrics()

        # Zusammenfassung berechnen
        summary = self._calculate_summary(metrics)

        # Empfehlungen generieren
        recommendations = self._generate_recommendations(metrics)

        # KPIs berechnen
        kpis = self._calculate_kpis(metrics)

        report = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'report_type': 'comprehensive_optimization',
                'version': '1.0.0',
                'uptime_hours': metrics.get('uptime_hours', 0)
            },
            'summary': summary,
            'key_performance_indicators': kpis,
            'module_metrics': metrics.get('modules', {}),
            'recommendations': recommendations,
            'alerts': self._get_active_alerts(metrics)
        }

        self.reports_generated += 1
        log_event('OPTIMIZATION_REPORT_GENERATED', {
            'report_number': self.reports_generated,
            'timestamp': report['report_metadata']['generated_at']
        })

        print("✅ Report erfolgreich generiert")
        return report

    def _calculate_summary(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Berechnet Zusammenfassung aller Optimierungen"""
        modules = metrics.get('modules', {})

        # Predictive Maintenance Summary
        pm = modules.get('predictive_maintenance', {})
        pm_summary = {
            'rigs_at_risk': 0,
            'critical_rigs': 0,
            'total_monitored': pm.get('rigs_monitored', 0)
        }

        if 'rig_predictions' in pm:
            for pred in pm['rig_predictions']:
                if pred.get('risk_level') in ['high', 'critical']:
                    pm_summary['rigs_at_risk'] += 1
                if pred.get('risk_level') == 'critical':
                    pm_summary['critical_rigs'] += 1

        # Energy Efficiency Summary
        ee = modules.get('energy_efficiency', {})
        ee_summary = {
            'potential_savings_daily': ee.get('cost_savings_potential_hourly', 0) * 24,
            'current_daily_cost': ee.get('total_daily_cost', 0),
            'avg_efficiency': ee.get('avg_efficiency_score', 0)
        }

        # Temperature Optimization Summary
        to = modules.get('temperature_optimization', {})
        to_summary = {
            'total_optimizations': to.get('total_optimizations', 0),
            'total_efficiency_gains': to.get('total_efficiency_gains', 0)
        }

        # Algorithm Switching Summary
        alg = modules.get('algorithm_switching', {})
        alg_summary = {
            'total_switches': alg.get('total_switches', 0),
            'current_algorithm': alg.get('current_best_algorithm', 'unknown')
        }

        # Quantum Optimization Summary
        qo = modules.get('quantum_optimization', {})
        qo_summary = {
            'total_optimizations': qo.get('total_optimizations', 0),
            'avg_efficiency_gain': qo.get('avg_efficiency_gain', 0),
            'avg_quantum_level': qo.get('avg_quantum_level', 0),
            'max_quantum_level': qo.get('max_quantum_level_achieved', 0)
        }

        return {
            'predictive_maintenance': pm_summary,
            'energy_efficiency': ee_summary,
            'temperature_optimization': to_summary,
            'algorithm_switching': alg_summary,
            'quantum_optimization': qo_summary,
            'overall_system_health': self._calculate_overall_health(pm_summary, ee_summary)
        }

    def _calculate_overall_health(self, pm_summary: Dict, ee_summary: Dict) -> str:
        """Berechnet Gesamt-System-Gesundheit"""
        health_score = 100

        # Abzüge für Risiken
        health_score -= pm_summary['critical_rigs'] * 20
        health_score -= pm_summary['rigs_at_risk'] * 10

        # Abzüge für ineffiziente Energie
        if ee_summary['avg_efficiency'] < 0.7:
            health_score -= 15
        elif ee_summary['avg_efficiency'] < 0.85:
            health_score -= 5

        if health_score >= 90:
            return 'excellent'
        elif health_score >= 75:
            return 'good'
        elif health_score >= 50:
            return 'fair'
        else:
            return 'poor'

    def _calculate_kpis(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Berechnet Key Performance Indicators"""
        modules = metrics.get('modules', {})

        ee = modules.get('energy_efficiency', {})
        pm = modules.get('predictive_maintenance', {})
        to = modules.get('temperature_optimization', {})

        kpis = {
            'cost_metrics': {
                'daily_operating_cost': ee.get('total_daily_cost', 0),
                'potential_daily_savings': ee.get('cost_savings_potential_hourly', 0) * 24,
                'monthly_savings_estimate': ee.get('cost_savings_potential_hourly', 0) * 24 * 30
            },
            'efficiency_metrics': {
                'avg_power_efficiency': ee.get('avg_efficiency_score', 0),
                'power_consumption_watt': ee.get('total_power_consumption_watt', 0),
                'efficiency_gain_from_temp_optimization': to.get('total_efficiency_gains', 0)
            },
            'reliability_metrics': {
                'rigs_monitored': pm.get('rigs_monitored', 0),
                'data_points_collected': pm.get('total_data_points', 0),
                'predicted_failure_count': len([
                    p for p in pm.get('rig_predictions', [])
                    if p.get('immediate_action_required', False)
                ])
            },
            'optimization_metrics': {
                'total_temperature_optimizations': to.get('total_optimizations', 0),
                'total_algorithm_switches': modules.get('algorithm_switching', {}).get('total_switches', 0)
            },
            'quantum_metrics': {
                'total_quantum_optimizations': modules.get('quantum_optimization', {}).get('total_optimizations', 0),
                'avg_quantum_efficiency_gain': modules.get('quantum_optimization', {}).get('avg_efficiency_gain', 0),
                'avg_quantum_stability': modules.get('quantum_optimization', {}).get('avg_stability_score', 0),
                'max_quantum_level_achieved': modules.get('quantum_optimization', {}).get('max_quantum_level_achieved', 0)
            }
        }

        return kpis

    def _generate_recommendations(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generiert Handlungsempfehlungen basierend auf Metriken"""
        recommendations = []
        modules = metrics.get('modules', {})

        # Predictive Maintenance Empfehlungen
        pm = modules.get('predictive_maintenance', {})
        if 'rig_predictions' in pm:
            for pred in pm['rig_predictions']:
                if pred.get('risk_level') == 'critical':
                    recommendations.append({
                        'priority': 'CRITICAL',
                        'category': 'Predictive Maintenance',
                        'rig_id': pred.get('rig_id'),
                        'action': f"Sofortige Wartung für Rig {pred.get('rig_id')} erforderlich",
                        'impact': 'high',
                        'estimated_downtime_hours': 4
                    })
                elif pred.get('risk_level') == 'high':
                    recommendations.append({
                        'priority': 'HIGH',
                        'category': 'Predictive Maintenance',
                        'rig_id': pred.get('rig_id'),
                        'action': f"Wartung für Rig {pred.get('rig_id')} innerhalb 7 Tagen einplanen",
                        'impact': 'medium',
                        'estimated_downtime_hours': 2
                    })

        # Energy Efficiency Empfehlungen
        ee = modules.get('energy_efficiency', {})
        if ee.get('avg_efficiency_score', 1.0) < 0.8:
            savings = ee.get('cost_savings_potential_hourly', 0) * 24 * 30
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Energy Efficiency',
                'action': 'Energie-Effizienz-Optimierung durchführen',
                'impact': 'medium',
                'estimated_monthly_savings': savings
            })

        # Temperature Optimization Empfehlungen
        to = modules.get('temperature_optimization', {})
        if to.get('total_optimizations', 0) == 0:
            recommendations.append({
                'priority': 'LOW',
                'category': 'Temperature Optimization',
                'action': 'Temperatur-basierte Übertaktung aktivieren',
                'impact': 'low-medium',
                'potential_hashrate_gain': '5-10%'
            })

        return recommendations

    def _get_active_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sammelt aktive Alerts aus allen Modulen"""
        alerts = []
        modules = metrics.get('modules', {})

        pm = modules.get('predictive_maintenance', {})
        if 'rig_predictions' in pm:
            for pred in pm['rig_predictions']:
                if pred.get('immediate_action_required', False):
                    alerts.append({
                        'type': 'CRITICAL',
                        'module': 'Predictive Maintenance',
                        'message': f"Rig {pred.get('rig_id')} benötigt sofortige Wartung",
                        'timestamp': datetime.now().isoformat()
                    })

        return alerts

    def export_report(self, report: Dict[str, Any], formats: Optional[List[str]] = None) -> List[Path]:
        """Exportiert Report in verschiedene Formate"""
        if formats is None:
            formats = self.dashboard_config.get('ReportFormats', ['json'])

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        exported_files = []

        for fmt in formats:
            if fmt == 'json':
                filepath = self.export_path / f'optimization_report_{timestamp}.json'
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                exported_files.append(filepath)
                print(f"✅ JSON-Report exportiert: {filepath}")

            elif fmt == 'html':
                filepath = self.export_path / f'optimization_report_{timestamp}.html'
                html_content = self._generate_html_report(report)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                exported_files.append(filepath)
                print(f"✅ HTML-Report exportiert: {filepath}")

            elif fmt == 'txt':
                filepath = self.export_path / f'optimization_report_{timestamp}.txt'
                txt_content = self._generate_text_report(report)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(txt_content)
                exported_files.append(filepath)
                print(f"✅ Text-Report exportiert: {filepath}")

        log_event('REPORTS_EXPORTED', {
            'formats': formats,
            'files': [str(f) for f in exported_files]
        })

        return exported_files

    def _generate_html_report(self, report: Dict[str, Any]) -> str:
        """Generiert HTML-Report"""
        metadata = report.get('report_metadata', {})
        summary = report.get('summary', {})
        kpis = report.get('key_performance_indicators', {})
        recommendations = report.get('recommendations', [])

        html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Optimization Dashboard Report - {metadata.get('generated_at', 'N/A')}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        h1 {{
            color: #667eea;
            text-align: center;
            margin-bottom: 10px;
        }}
        .subtitle {{
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }}
        .section {{
            margin: 20px 0;
            padding: 20px;
            background: #f9f9f9;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .kpi-card {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .kpi-title {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }}
        .kpi-value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #667eea;
        }}
        .recommendation {{
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid #ffa500;
        }}
        .recommendation.CRITICAL {{
            background: #ffe6e6;
            border-left-color: #ff0000;
        }}
        .recommendation.HIGH {{
            background: #fff4e6;
            border-left-color: #ff6600;
        }}
        .recommendation.MEDIUM {{
            background: #fffce6;
            border-left-color: #ffa500;
        }}
        .health-badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            color: white;
        }}
        .health-excellent {{ background: #28a745; }}
        .health-good {{ background: #17a2b8; }}
        .health-fair {{ background: #ffc107; color: #333; }}
        .health-poor {{ background: #dc3545; }}
        .timestamp {{
            text-align: right;
            color: #999;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 OPTIMIZATION DASHBOARD</h1>
        <div class="subtitle">Comprehensive System Report</div>
        <div class="timestamp">Generiert: {metadata.get('generated_at', 'N/A')}</div>

        <div class="section">
            <h2>📊 System-Übersicht</h2>
            <p><strong>Uptime:</strong> {metadata.get('uptime_hours', 0):.2f} Stunden</p>
            <p><strong>Gesamt-Gesundheit:</strong> 
                <span class="health-badge health-{summary.get('overall_system_health', 'unknown')}">
                    {summary.get('overall_system_health', 'unknown').upper()}
                </span>
            </p>
        </div>

        <div class="section">
            <h2>💰 Key Performance Indicators</h2>
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-title">Tägliche Betriebskosten</div>
                    <div class="kpi-value">CHF {kpis.get('cost_metrics', {}).get('daily_operating_cost', 0):.2f}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Potenzielle tägliche Ersparnis</div>
                    <div class="kpi-value">CHF {kpis.get('cost_metrics', {}).get('potential_daily_savings', 0):.2f}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Monatliche Ersparnis (geschätzt)</div>
                    <div class="kpi-value">CHF {kpis.get('cost_metrics', {}).get('monthly_savings_estimate', 0):.2f}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Durchschnittliche Effizienz</div>
                    <div class="kpi-value">{kpis.get('efficiency_metrics', {}).get('avg_power_efficiency', 0):.1%}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Stromverbrauch</div>
                    <div class="kpi-value">{kpis.get('efficiency_metrics', {}).get('power_consumption_watt', 0):.0f} W</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Überwachte Rigs</div>
                    <div class="kpi-value">{kpis.get('reliability_metrics', {}).get('rigs_monitored', 0)}</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>🔧 Modul-Status</h2>
            <h3>Predictive Maintenance</h3>
            <p><strong>Rigs überwacht:</strong> {summary.get('predictive_maintenance', {}).get('total_monitored', 0)}</p>
            <p><strong>Rigs mit Risiko:</strong> {summary.get('predictive_maintenance', {}).get('rigs_at_risk', 0)}</p>
            <p><strong>Kritische Rigs:</strong> {summary.get('predictive_maintenance', {}).get('critical_rigs', 0)}</p>

            <h3>Energy Efficiency</h3>
            <p><strong>Ø Effizienz-Score:</strong> {summary.get('energy_efficiency', {}).get('avg_efficiency', 0):.1%}</p>
            <p><strong>Tägliche Kosten:</strong> CHF {summary.get('energy_efficiency', {}).get('current_daily_cost', 0):.2f}</p>

            <h3>Temperature Optimization</h3>
            <p><strong>Durchgeführte Optimierungen:</strong> {summary.get('temperature_optimization', {}).get('total_optimizations', 0)}</p>
            <p><strong>Gesamt-Effizienzgewinn:</strong> {summary.get('temperature_optimization', {}).get('total_efficiency_gains', 0):.2f}%</p>

            <h3>Algorithm Switching</h3>
            <p><strong>Algorithmus-Wechsel:</strong> {summary.get('algorithm_switching', {}).get('total_switches', 0)}</p>
            <p><strong>Aktuell bester Algorithmus:</strong> {summary.get('algorithm_switching', {}).get('current_algorithm', 'N/A')}</p>
        </div>

        <div class="section">
            <h2>💡 Empfehlungen</h2>
"""

        if recommendations:
            for rec in recommendations:
                priority = rec.get('priority', 'LOW')
                html += f"""
            <div class="recommendation {priority}">
                <strong>[{priority}] {rec.get('category', 'N/A')}</strong><br>
                {rec.get('action', 'N/A')}<br>
                <em>Impact: {rec.get('impact', 'N/A')}</em>
            </div>
"""
        else:
            html += "<p>Keine Handlungsempfehlungen - System läuft optimal!</p>"

        html += """
        </div>

        <div class="timestamp">
            <small>CASH MONEY COLORS ORIGINAL (R) - Optimization Dashboard v1.0.0</small>
        </div>
    </div>
</body>
</html>
"""
        return html

    def _generate_text_report(self, report: Dict[str, Any]) -> str:
        """Generiert Text-Report"""
        metadata = report.get('report_metadata', {})
        summary = report.get('summary', {})
        kpis = report.get('key_performance_indicators', {})
        recommendations = report.get('recommendations', [])

        text = f"""
{'='*80}
CASH MONEY COLORS ORIGINAL (R) - OPTIMIZATION DASHBOARD
Comprehensive System Report
{'='*80}

Generiert: {metadata.get('generated_at', 'N/A')}
Uptime: {metadata.get('uptime_hours', 0):.2f} Stunden
System-Gesundheit: {summary.get('overall_system_health', 'unknown').upper()}

{'='*80}
KEY PERFORMANCE INDICATORS
{'='*80}

Kosten-Metriken:
  Tägliche Betriebskosten:        CHF {kpis.get('cost_metrics', {}).get('daily_operating_cost', 0):.2f}
  Potenzielle tägliche Ersparnis: CHF {kpis.get('cost_metrics', {}).get('potential_daily_savings', 0):.2f}
  Monatliche Ersparnis (geschätzt): CHF {kpis.get('cost_metrics', {}).get('monthly_savings_estimate', 0):.2f}

Effizienz-Metriken:
  Durchschnittliche Effizienz:    {kpis.get('efficiency_metrics', {}).get('avg_power_efficiency', 0):.1%}
  Stromverbrauch:                 {kpis.get('efficiency_metrics', {}).get('power_consumption_watt', 0):.0f} W
  Effizienzgewinn (Temp-Opt):     {kpis.get('efficiency_metrics', {}).get('efficiency_gain_from_temp_optimization', 0):.2f}%

Zuverlässigkeits-Metriken:
  Überwachte Rigs:                {kpis.get('reliability_metrics', {}).get('rigs_monitored', 0)}
  Gesammelte Datenpunkte:         {kpis.get('reliability_metrics', {}).get('data_points_collected', 0)}
  Vorhergesagte Ausfälle:         {kpis.get('reliability_metrics', {}).get('predicted_failure_count', 0)}

Optimierungs-Metriken:
  Temperatur-Optimierungen:       {kpis.get('optimization_metrics', {}).get('total_temperature_optimizations', 0)}
  Algorithmus-Wechsel:            {kpis.get('optimization_metrics', {}).get('total_algorithm_switches', 0)}

{'='*80}
MODUL-STATUS
{'='*80}

Predictive Maintenance:
  Überwachte Rigs:                {summary.get('predictive_maintenance', {}).get('total_monitored', 0)}
  Rigs mit Risiko:                {summary.get('predictive_maintenance', {}).get('rigs_at_risk', 0)}
  Kritische Rigs:                 {summary.get('predictive_maintenance', {}).get('critical_rigs', 0)}

Energy Efficiency:
  Ø Effizienz-Score:              {summary.get('energy_efficiency', {}).get('avg_efficiency', 0):.1%}
  Tägliche Kosten:                CHF {summary.get('energy_efficiency', {}).get('current_daily_cost', 0):.2f}
  Tägliche Ersparnis (Potenzial): CHF {summary.get('energy_efficiency', {}).get('potential_savings_daily', 0):.2f}

Temperature Optimization:
  Durchgeführte Optimierungen:    {summary.get('temperature_optimization', {}).get('total_optimizations', 0)}
  Gesamt-Effizienzgewinn:         {summary.get('temperature_optimization', {}).get('total_efficiency_gains', 0):.2f}%

Algorithm Switching:
  Algorithmus-Wechsel:            {summary.get('algorithm_switching', {}).get('total_switches', 0)}
  Aktuell bester Algorithmus:     {summary.get('algorithm_switching', {}).get('current_algorithm', 'N/A')}

{'='*80}
EMPFEHLUNGEN
{'='*80}

"""

        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                text += f"""
[{rec.get('priority', 'N/A')}] {rec.get('category', 'N/A')}
  → {rec.get('action', 'N/A')}
  Impact: {rec.get('impact', 'N/A')}
"""
                if 'estimated_monthly_savings' in rec:
                    text += f"  Ersparnis (geschätzt): CHF {rec.get('estimated_monthly_savings', 0):.2f}/Monat\n"
        else:
            text += "\nKeine Handlungsempfehlungen - System läuft optimal!\n"

        text += f"""
{'='*80}
CASH MONEY COLORS ORIGINAL (R) - Optimization Dashboard v1.0.0
{'='*80}
"""

        return text

    def print_dashboard_summary(self):
        """Gibt Dashboard-Zusammenfassung auf Konsole aus"""
        report = self.generate_comprehensive_report()
        summary = report.get('summary', {})
        kpis = report.get('key_performance_indicators', {})

        print("\n" + "="*80)
        print("📊 OPTIMIZATION DASHBOARD - LIVE SUMMARY")
        print("="*80)

        print(f"\n🏥 System-Gesundheit: {summary.get('overall_system_health', 'unknown').upper()}")

        print("\n💰 Kosten:")
        print(f"   Täglich:  CHF {kpis.get('cost_metrics', {}).get('daily_operating_cost', 0):.2f}")
        print(f"   Ersparnis (Potenzial): CHF {kpis.get('cost_metrics', {}).get('potential_daily_savings', 0):.2f}/Tag")

        print("\n⚡ Effizienz:")
        print(f"   Durchschnitt: {kpis.get('efficiency_metrics', {}).get('avg_power_efficiency', 0):.1%}")
        print(f"   Stromverbrauch: {kpis.get('efficiency_metrics', {}).get('power_consumption_watt', 0):.0f} W")

        print("\n🔧 Predictive Maintenance:")
        pm = summary.get('predictive_maintenance', {})
        print(f"   Überwacht: {pm.get('total_monitored', 0)} Rigs")
        print(f"   Risiko: {pm.get('rigs_at_risk', 0)} | Kritisch: {pm.get('critical_rigs', 0)}")

        recommendations = report.get('recommendations', [])
        if recommendations:
            print(f"\n💡 Empfehlungen: {len(recommendations)}")
            for rec in recommendations[:3]:  # Nur Top 3
                print(f"   [{rec.get('priority')}] {rec.get('action')[:60]}...")

        print("\n" + "="*80)


# Globale Instanz
dashboard = OptimizationDashboard()


# Convenience-Funktionen
def generate_optimization_report() -> Dict[str, Any]:
    """Generiert Optimierungs-Report"""
    return dashboard.generate_comprehensive_report()


def export_optimization_report(formats: Optional[List[str]] = None) -> List[Path]:
    """Exportiert Report in verschiedene Formate"""
    report = dashboard.generate_comprehensive_report()
    return dashboard.export_report(report, formats)


def print_dashboard_summary():
    """Gibt Dashboard-Zusammenfassung aus"""
    dashboard.print_dashboard_summary()


def get_all_metrics() -> Dict[str, Any]:
    """Sammelt alle Metriken"""
    return dashboard.gather_all_metrics()


if __name__ == "__main__":
    print("CASH MONEY COLORS ORIGINAL (R) - OPTIMIZATION DASHBOARD")
    print("=" * 65)

    print("\n🧪 Teste Dashboard-Funktionen...")

    # Metriken sammeln
    print("\n[1/3] Sammle Metriken...")
    metrics = get_all_metrics()
    print(f"✅ {len(metrics.get('modules', {}))} Module analysiert")

    # Report generieren
    print("\n[2/3] Generiere Report...")
    report = generate_optimization_report()
    print(f"✅ Report mit {len(report.get('recommendations', []))} Empfehlungen erstellt")

    # Report exportieren
    print("\n[3/3] Exportiere Report...")
    exported = export_optimization_report(['json', 'html', 'txt'])
    print(f"✅ {len(exported)} Dateien exportiert")

    # Dashboard-Summary anzeigen
    print("\n" + "="*65)
    print_dashboard_summary()

    print("\n[OK] OPTIMIZATION DASHBOARD BEREIT!")
    print("Verwende generate_optimization_report() für vollständige Berichte")
