#!/usr/bin/env python3
"""
CASH MONEY COLORS ORIGINAL (R) - PERFORMANCE DASHBOARD API SERVER
Flask-basierte API für das Performance Monitoring & Analytics System
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Importiere das Performance Monitoring System
try:
    from python_modules.performance_monitoring import (
        performance_monitor,
        get_dashboard_data,
        generate_performance_report,
        export_dashboard
    )
except ImportError:
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from python_modules.performance_monitoring import (
        performance_monitor,
        get_dashboard_data,
        generate_performance_report,
        export_dashboard
    )

app = Flask(__name__)
CORS(app)  # Aktiviere CORS für Mobile-Apps

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Endpoints

@app.route('/')
def index():
    """Liefert das Dashboard HTML"""
    return send_from_directory('.', 'index.html')

@app.route('/api/dashboard')
def api_dashboard():
    """Echtzeit-Dashboard-Daten"""
    try:
        data = get_dashboard_data()
        return jsonify({
            'success': True,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Dashboard API Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/metrics')
def api_metrics():
    """Echtzeit-Metriken für Mobile-Apps"""
    try:
        dashboard_data = get_dashboard_data()
        current_metrics = dashboard_data.get('current_metrics', {})
        
        metrics = {
            'hashrate': {
                'value': current_metrics.get('avg_hashrate', 0),
                'unit': 'MH/s',
                'trend': 'stable'  # Könnte aus Historie berechnet werden
            },
            'power': {
                'value': current_metrics.get('avg_power', 0),
                'unit': 'W',
                'trend': 'stable'
            },
            'temperature': {
                'value': current_metrics.get('avg_temperature', 0),
                'unit': '°C',
                'trend': 'stable'
            },
            'efficiency': {
                'value': current_metrics.get('avg_efficiency', 0) * 100,
                'unit': '%',
                'trend': 'stable'
            },
            'quantum_level': {
                'value': 75,  # Beispielwert
                'unit': 'Level',
                'trend': 'up'
            }
        }
        
        return jsonify({
            'success': True,
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Metrics API Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/alerts')
def api_alerts():
    """Aktive Alerts"""
    try:
        dashboard_data = get_dashboard_data()
        alerts = dashboard_data.get('alerts', [])
        
        # Filtere nur aktive Alerts
        active_alerts = [alert for alert in alerts if not alert.get('resolved', False)]
        
        return jsonify({
            'success': True,
            'alerts': active_alerts,
            'count': len(active_alerts),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Alerts API Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/kpis')
def api_kpis():
    """Key Performance Indicators"""
    try:
        dashboard_data = get_dashboard_data()
        kpis = dashboard_data.get('kpis', {})
        
        kpi_list = []
        for kpi_name, kpi_data in kpis.items():
            kpi_list.append({
                'name': kpi_name.replace('_', ' ').title(),
                'value': kpi_data.get('value', 0),
                'unit': kpi_data.get('unit', ''),
                'status': 'good' if kpi_data.get('value', 0) > 0.8 else 'warning'
            })
        
        return jsonify({
            'success': True,
            'kpis': kpi_list,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"KPIs API Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/report')
def api_report():
    """Performance-Report"""
    try:
        hours = request.args.get('hours', 24, type=int)
        report = generate_performance_report(hours)
        
        return jsonify({
            'success': True,
            'report': report,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Report API Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/export/<format>')
def api_export(format):
    """Daten-Export"""
    try:
        if format.lower() not in ['json', 'html', 'csv']:
            return jsonify({
                'success': False,
                'error': 'Invalid format. Supported: json, html, csv',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        data = export_dashboard(format)
        
        return jsonify({
            'success': True,
            'format': format,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Export API Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/system/status')
def api_system_status():
    """System-Status"""
    try:
        # Simulierte System-Status-Daten
        status = {
            'monitoring_active': performance_monitor.monitoring_active,
            'database_status': 'connected',
            'last_update': datetime.now().isoformat(),
            'version': '1.0.0',
            'uptime': '24h 15m',
            'rigs_count': 10,
            'active_rigs': 9
        }
        
        return jsonify({
            'success': True,
            'status': status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"System Status API Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/charts/data')
def api_chart_data():
    """Chart-Daten für Visualisierungen"""
    try:
        # Simulierte Chart-Daten (in der echten Anwendung aus DB laden)
        import random
        from datetime import datetime, timedelta
        
        labels = []
        hashrate_data = []
        efficiency_data = []
        temp_data = []
        
        # Generiere simulierte Zeitreihe
        for i in range(24):
            time_point = datetime.now() - timedelta(hours=23-i)
            labels.append(time_point.strftime('%H:%M'))
            
            hashrate_data.append(120 + random.uniform(-10, 10))
            efficiency_data.append(0.35 + random.uniform(-0.05, 0.05))
            temp_data.append(65 + random.uniform(-5, 5))
        
        chart_data = {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Hashrate (MH/s)',
                    'data': hashrate_data,
                    'borderColor': '#667eea',
                    'backgroundColor': 'rgba(102, 126, 234, 0.1)',
                    'tension': 0.4,
                    'fill': True
                },
                {
                    'label': 'Effizienz (%)',
                    'data': [eff * 100 for eff in efficiency_data],
                    'borderColor': '#28a745',
                    'backgroundColor': 'rgba(40, 167, 69, 0.1)',
                    'tension': 0.4,
                    'fill': True
                },
                {
                    'label': 'Temperatur (°C)',
                    'data': temp_data,
                    'borderColor': '#ffc107',
                    'backgroundColor': 'rgba(255, 193, 7, 0.1)',
                    'tension': 0.4,
                    'fill': True
                }
            ]
        }
        
        return jsonify({
            'success': True,
            'chart_data': chart_data,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Chart Data API Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/mobile/summary')
def api_mobile_summary():
    """Mobile-optimierte Zusammenfassung"""
    try:
        dashboard_data = get_dashboard_data()
        current_metrics = dashboard_data.get('current_metrics', {})
        
        summary = {
            'main_metric': {
                'label': 'Durchschnittliche Hashrate',
                'value': f"{current_metrics.get('avg_hashrate', 0):.1f}",
                'unit': 'MH/s',
                'icon': '⛏️'
            },
            'secondary_metrics': [
                {
                    'label': 'Stromverbrauch',
                    'value': f"{current_metrics.get('avg_power', 0):.0f}",
                    'unit': 'W',
                    'icon': '⚡'
                },
                {
                    'label': 'Temperatur',
                    'value': f"{current_metrics.get('avg_temperature', 0):.1f}",
                    'unit': '°C',
                    'icon': '🌡️'
                },
                {
                    'label': 'Effizienz',
                    'value': f"{current_metrics.get('avg_efficiency', 0) * 100:.1f}",
                    'unit': '%',
                    'icon': '📊'
                }
            ],
            'status': 'online' if current_metrics.get('avg_hashrate', 0) > 0 else 'offline',
            'alerts_count': len(dashboard_data.get('alerts', [])),
            'last_update': current_metrics.get('last_update', datetime.now().isoformat())
        }
        
        return jsonify({
            'success': True,
            'summary': summary,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Mobile Summary API Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/recommendations')
def api_recommendations():
    """Optimierungs-Empfehlungen"""
    try:
        report = generate_performance_report(24)
        recommendations = report.get('recommendations', [])
        
        # Strukturiere Empfehlungen für bessere Darstellung
        structured_recs = []
        for rec in recommendations:
            structured_recs.append({
                'text': rec,
                'priority': 'high' if '⚠️' in rec else 'medium' if '⚡' in rec else 'low',
                'category': 'performance' if 'Effizienz' in rec else 'maintenance' if 'Wartung' in rec else 'optimization'
            })
        
        return jsonify({
            'success': True,
            'recommendations': structured_recs,
            'count': len(structured_recs),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Recommendations API Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/predictions')
def api_predictions():
    """Vorhersagen und Trends"""
    try:
        # Simulierte Vorhersagedaten
        predictions = {
            'hashrate_trend': {
                'direction': 'up',
                'confidence': 0.85,
                'next_24h': 'Erwartete Steigerung um 5-8%'
            },
            'efficiency_trend': {
                'direction': 'stable',
                'confidence': 0.75,
                'next_24h': 'Stabile Effizienz erwartet'
            },
            'temperature_trend': {
                'direction': 'up',
                'confidence': 0.65,
                'next_24h': 'Leichte Temperaturerhöhung möglich'
            },
            'maintenance_needed': {
                'rigs': ['Rig #3', 'Rig #7'],
                'priority': 'medium',
                'description': 'Filterreinigung empfohlen'
            }
        }
        
        return jsonify({
            'success': True,
            'predictions': predictions,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Predictions API Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Error Handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'timestamp': datetime.now().isoformat()
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'timestamp': datetime.now().isoformat()
    }), 500

# Start-Funktion
def start_dashboard_server(host='0.0.0.0', port=5000, debug=False):
    """Startet den Dashboard-Server"""
    logger.info(f"Starting Performance Dashboard API Server on {host}:{port}")
    
    # Starte das Performance Monitoring
    if not performance_monitor.monitoring_active:
        performance_monitor.start_monitoring()
        logger.info("Performance Monitoring started")
    
    app.run(host=host, port=port, debug=debug, threaded=True)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Performance Dashboard API Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    print("🚀 PERFORMANCE DASHBOARD API SERVER")
    print("=" * 50)
    print(f"   Host: {args.host}")
    print(f"   Port: {args.port}")
    print(f"   Debug: {args.debug}")
    print("=" * 50)
    
    start_dashboard_server(args.host, args.port, args.debug)