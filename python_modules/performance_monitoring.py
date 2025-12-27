#!/usr/bin/env python3
"""
CASH MONEY COLORS ORIGINAL (R) - PERFORMANCE MONITORING & ANALYTICS SYSTEM
Phase 3: Echtzeit-Performance Dashboard mit Visualisierungen, historischer Trend-Analyse,
Mustererkennung, KPIs, Predictive Analytics und automatischen Reports
"""

import json
import time
import threading
import sqlite3
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging
import numpy as np
from collections import deque, defaultdict

try:
    from python_modules.config_manager import get_config, get_rigs_config
    from python_modules.enhanced_logging import log_event
    from python_modules.alert_system import send_custom_alert
    from python_modules.quantum_optimizer import get_quantum_status
    from python_modules.energy_efficiency import get_global_efficiency_report
    from python_modules.temperature_optimizer import get_thermal_efficiency_report
    from python_modules.algorithm_switcher import get_algorithm_performance_report
    from python_modules.predictive_maintenance import get_maintenance_status, predict_rig_failures
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config_manager import get_config, get_rigs_config
    from enhanced_logging import log_event
    from alert_system import send_custom_alert
    from quantum_optimizer import get_quantum_status
    from energy_efficiency import get_global_efficiency_report
    from temperature_optimizer import get_thermal_efficiency_report
    from algorithm_switcher import get_algorithm_performance_report
    from predictive_maintenance import get_maintenance_status, predict_rig_failures


class PerformanceMonitoringSystem:
    """Hauptklasse für das Performance Monitoring & Analytics System"""
    
    def __init__(self):
        self.monitoring_config = get_config('PerformanceMonitoring', {
            'DatabasePath': 'performance_data.db',
            'RealTimeUpdateInterval': 5,  # Sekunden
            'HistoricalDataRetentionDays': 30,
            'AlertThresholds': {
                'efficiency_drop': 0.15,  # 15% Effizienzverlust
                'temperature_critical': 75.0,
                'power_consumption_spike': 0.20,  # 20% Leistungsanstieg
                'hashrate_drop': 0.25  # 25% Hashrate-Verlust
            },
            'KPIs': [
                'hashrate_efficiency',
                'power_efficiency',
                'thermal_efficiency',
                'quantum_optimization_level',
                'system_reliability'
            ]
        })
        
        self.db_path = Path(self.monitoring_config.get('DatabasePath', 'performance_data.db'))
        self.init_database()
        
        # Daten-Puffer für Echtzeit-Analyse
        self.realtime_buffer = deque(maxlen=1000)  # Letzte 1000 Messungen
        self.kpi_history = defaultdict(list)
        
        # Monitoring-Threads
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Analyse-Threads
        self.analysis_thread = None
        self.prediction_thread = None
        
        print("🚀 PERFORMANCE MONITORING & ANALYTICS SYSTEM INITIALISIERT")
        print(f"   Datenbank: {self.db_path.absolute()}")
        print(f"   Update-Intervall: {self.monitoring_config.get('RealTimeUpdateInterval', 5)}s")
        
    def init_database(self):
        """Initialisiert die SQLite-Datenbank für Performance-Daten"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Haupttabelle für Echtzeit-Daten
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    rig_id TEXT,
                    hashrate_mhs REAL,
                    power_watt REAL,
                    temperature_c REAL,
                    efficiency REAL,
                    quantum_level INTEGER,
                    algorithm TEXT,
                    uptime_hours REAL,
                    energy_cost_per_hour REAL
                )
            ''')
            
            # Tabelle für KPIs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS kpis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    kpi_name TEXT,
                    kpi_value REAL,
                    kpi_unit TEXT,
                    target_value REAL
                )
            ''')
            
            # Tabelle für Vorhersagen
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    prediction_type TEXT,
                    predicted_value REAL,
                    confidence REAL,
                    time_horizon_hours INTEGER
                )
            ''')
            
            # Tabelle für Alerts
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    alert_type TEXT,
                    severity TEXT,
                    message TEXT,
                    resolved BOOLEAN DEFAULT FALSE
                )
            ''')
            
            conn.commit()
    
    def start_monitoring(self):
        """Startet das Echtzeit-Monitoring"""
        if self.monitoring_active:
            print("⚠️ Monitoring läuft bereits")
            return
            
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        # Starte Analyse-Threads
        self.analysis_thread = threading.Thread(target=self._analysis_loop, daemon=True)
        self.analysis_thread.start()
        
        self.prediction_thread = threading.Thread(target=self._prediction_loop, daemon=True)
        self.prediction_thread.start()
        
        print("✅ Echtzeit-Monitoring gestartet")
        
    def stop_monitoring(self):
        """Stoppt das Monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        print("🛑 Monitoring gestoppt")
    
    def _monitoring_loop(self):
        """Haupt-Monitoring-Schleife"""
        while self.monitoring_active:
            try:
                # Sammle aktuelle Metriken
                metrics = self._collect_realtime_metrics()
                
                # Speichere in Datenbank
                self._store_metrics(metrics)
                
                # Aktualisiere Echtzeit-Puffer
                self.realtime_buffer.append(metrics)
                
                # Überprüfe Alerts
                self._check_alerts(metrics)
                
                # Aktualisiere KPIs
                self._update_kpis(metrics)
                
                # Warte auf nächsten Update-Zyklus
                time.sleep(self.monitoring_config.get('RealTimeUpdateInterval', 5))
                
            except Exception as e:
                log_event('MONITORING_ERROR', {'error': str(e)})
                time.sleep(5)  # Warte vor Wiederholung
    
    def _collect_realtime_metrics(self) -> Dict[str, Any]:
        """Sammelt Echtzeit-Metriken von allen Systemen"""
        timestamp = datetime.now()
        
        # Basis-Metriken vom Quantum Optimizer
        quantum_status = get_quantum_status()
        
        # Energie-Effizienz-Metriken
        efficiency_report = get_global_efficiency_report()
        
        # Temperatur-Metriken
        thermal_report = get_thermal_efficiency_report()
        
        # Algorithmus-Metriken
        algo_report = get_algorithm_performance_report()
        
        # Predictive Maintenance Metriken
        maintenance_status = get_maintenance_status()
        
        # Rig-spezifische Daten sammeln
        rigs_data = []
        rigs = get_rigs_config()
        for rig in rigs:
            rig_id = rig.get('id', 'unknown')
            try:
                # Simulierte Rig-Daten (könnte durch echte API ersetzt werden)
                rig_data = {
                    'rig_id': rig_id,
                    'hashrate_mhs': 120.0 + np.random.normal(0, 5),  # Simulierte Werte
                    'power_watt': 320.0 + np.random.normal(0, 10),
                    'temperature_c': 68.0 + np.random.normal(0, 3),
                    'efficiency': 0.375 + np.random.normal(0, 0.02),
                    'quantum_level': quantum_status.get('avg_quantum_level', 50),
                    'algorithm': algo_report.get('current_best_algorithm', 'unknown'),
                    'uptime_hours': (timestamp - datetime.now().replace(hour=0, minute=0, second=0)).total_seconds() / 3600
                }
                rigs_data.append(rig_data)
            except Exception as e:
                log_event('RIG_METRICS_ERROR', {'rig_id': rig_id, 'error': str(e)})
        
        # Aggregierte System-Metriken
        total_hashrate = sum(r['hashrate_mhs'] for r in rigs_data)
        total_power = sum(r['power_watt'] for r in rigs_data)
        avg_temp = statistics.mean(r['temperature_c'] for r in rigs_data)
        avg_efficiency = statistics.mean(r['efficiency'] for r in rigs_data)
        
        return {
            'timestamp': timestamp,
            'system_metrics': {
                'total_hashrate_mhs': total_hashrate,
                'total_power_watt': total_power,
                'avg_temperature_c': avg_temp,
                'avg_efficiency': avg_efficiency,
                'rigs_count': len(rigs_data),
                'active_rigs': len([r for r in rigs_data if r['hashrate_mhs'] > 0])
            },
            'quantum_metrics': {
                'quantum_level': quantum_status.get('avg_quantum_level', 50),
                'optimization_count': quantum_status.get('total_optimizations', 0),
                'efficiency_gain': quantum_status.get('avg_efficiency_gain', 0)
            },
            'energy_metrics': {
                'efficiency_score': efficiency_report.get('avg_efficiency_score', 0.8),
                'power_savings_potential': efficiency_report.get('power_savings_potential_watt', 0),
                'cost_savings_potential': efficiency_report.get('cost_savings_potential_hourly', 0)
            },
            'thermal_metrics': {
                'optimizations_count': thermal_report.get('total_optimizations', 0),
                'efficiency_gains': thermal_report.get('total_efficiency_gains', 0)
            },
            'algorithm_metrics': {
                'current_algorithm': algo_report.get('current_best_algorithm', 'unknown'),
                'switch_count': algo_report.get('total_switches', 0),
                'profit_improvement': algo_report.get('avg_profit_improvement', 0)
            },
            'maintenance_metrics': {
                'rigs_monitored': maintenance_status.get('rigs_monitored', 0),
                'data_points': maintenance_status.get('total_data_points', 0),
                'risk_rigs': maintenance_status.get('rigs_at_risk', 0) if 'rigs_at_risk' in maintenance_status else 0
            },
            'rigs_data': rigs_data
        }
    
    def _store_metrics(self, metrics: Dict[str, Any]):
        """Speichert Metriken in der Datenbank"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Speichere Rig-Daten
            for rig_data in metrics['rigs_data']:
                cursor.execute('''
                    INSERT INTO performance_metrics (
                        timestamp, rig_id, hashrate_mhs, power_watt, 
                        temperature_c, efficiency, quantum_level, algorithm,
                        uptime_hours, energy_cost_per_hour
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    metrics['timestamp'],
                    rig_data['rig_id'],
                    rig_data['hashrate_mhs'],
                    rig_data['power_watt'],
                    rig_data['temperature_c'],
                    rig_data['efficiency'],
                    rig_data['quantum_level'],
                    rig_data['algorithm'],
                    rig_data['uptime_hours'],
                    rig_data['power_watt'] * 0.20 / 1000  # Simulierte Energiekosten
                ))
            
            conn.commit()
    
    def _check_alerts(self, metrics: Dict[str, Any]):
        """Überprüft auf kritische Bedingungen und sendet Alerts"""
        alerts = []
        
        # Effizienz-Alerts
        avg_efficiency = metrics['system_metrics']['avg_efficiency']
        if avg_efficiency < 0.30:  # Unter 30% Effizienz
            alerts.append({
                'type': 'LOW_EFFICIENCY',
                'severity': 'HIGH',
                'message': f'System-Effizienz unterkritisch: {avg_efficiency:.1%}'
            })
        
        # Temperatur-Alerts
        avg_temp = metrics['system_metrics']['avg_temperature_c']
        if avg_temp > 75.0:
            alerts.append({
                'type': 'HIGH_TEMPERATURE',
                'severity': 'CRITICAL',
                'message': f'Kritische Temperatur erreicht: {avg_temp:.1f}°C'
            })
        
        # Power-Alerts
        total_power = metrics['system_metrics']['total_power_watt']
        if total_power > 4000:  # Über 4kW Gesamtverbrauch
            alerts.append({
                'type': 'HIGH_POWER_CONSUMPTION',
                'severity': 'MEDIUM',
                'message': f'Hoher Stromverbrauch: {total_power:.0f}W'
            })
        
        # Quantum-Level Alerts
        quantum_level = metrics['quantum_metrics']['quantum_level']
        if quantum_level < 30:
            alerts.append({
                'type': 'LOW_QUANTUM_LEVEL',
                'severity': 'MEDIUM',
                'message': f'Niedriger Quantum-Level: {quantum_level}'
            })
        
        # Speichere und sende Alerts
        for alert in alerts:
            self._store_alert(alert)
            send_custom_alert(
                alert_type=alert['type'],
                severity=alert['severity'],
                message=alert['message'],
                source='PerformanceMonitoring'
            )
    
    def _store_alert(self, alert: Dict[str, Any]):
        """Speichert Alert in der Datenbank"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO alerts (alert_type, severity, message)
                VALUES (?, ?, ?)
            ''', (alert['type'], alert['severity'], alert['message']))
            conn.commit()
    
    def _update_kpis(self, metrics: Dict[str, Any]):
        """Aktualisiert Key Performance Indicators"""
        timestamp = metrics['timestamp']
        
        # Hashrate-Effizienz KPI
        hashrate_eff = metrics['system_metrics']['total_hashrate_mhs'] / max(metrics['system_metrics']['total_power_watt'], 1)
        self._store_kpi('hashrate_efficiency', hashrate_eff, 'MH/s per Watt', 0.4)
        
        # Power-Effizienz KPI
        power_eff = metrics['energy_metrics']['efficiency_score']
        self._store_kpi('power_efficiency', power_eff, 'Score', 0.85)
        
        # Thermal-Effizienz KPI
        thermal_eff = 1.0 - (metrics['system_metrics']['avg_temperature_c'] / 80.0)
        self._store_kpi('thermal_efficiency', thermal_eff, 'Score', 0.8)
        
        # Quantum-Optimization KPI
        quantum_kpi = metrics['quantum_metrics']['quantum_level'] / 100.0
        self._store_kpi('quantum_optimization_level', quantum_kpi, 'Level', 0.8)
        
        # System-Reliability KPI
        reliability = metrics['system_metrics']['active_rigs'] / max(metrics['system_metrics']['rigs_count'], 1)
        self._store_kpi('system_reliability', reliability, 'Score', 0.95)
    
    def _store_kpi(self, kpi_name: str, kpi_value: float, unit: str, target: float):
        """Speichert KPI in der Datenbank"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO kpis (kpi_name, kpi_value, kpi_unit, target_value)
                VALUES (?, ?, ?, ?)
            ''', (kpi_name, kpi_value, unit, target))
            conn.commit()
    
    def _analysis_loop(self):
        """Hintergrund-Analyse-Schleife für historische Daten"""
        while self.monitoring_active:
            try:
                # Historische Trend-Analyse
                self._analyze_trends()
                
                # Mustererkennung
                self._detect_patterns()
                
                time.sleep(60)  # Alle 60 Sekunden
                
            except Exception as e:
                log_event('ANALYSIS_ERROR', {'error': str(e)})
                time.sleep(30)
    
    def _analyze_trends(self):
        """Analysiert historische Trends"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Trend der letzten 24 Stunden
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            cursor.execute('''
                SELECT 
                    datetime(timestamp) as time_bucket,
                    AVG(hashrate_mhs) as avg_hashrate,
                    AVG(power_watt) as avg_power,
                    AVG(temperature_c) as avg_temp,
                    AVG(efficiency) as avg_efficiency
                FROM performance_metrics 
                WHERE timestamp > ?
                GROUP BY strftime('%H', timestamp)
                ORDER BY time_bucket
            ''', (cutoff_time,))
            
            trend_data = cursor.fetchall()
            
            if trend_data:
                # Berechne Trend-Richtungen
                hashrate_trend = self._calculate_trend([row[1] for row in trend_data])
                power_trend = self._calculate_trend([row[2] for row in trend_data])
                temp_trend = self._calculate_trend([row[3] for row in trend_data])
                
                # Speichere Trend-Analyse
                self._store_prediction('hashrate_trend', hashrate_trend, 0.8, 24)
                self._store_prediction('power_trend', power_trend, 0.8, 24)
                self._store_prediction('temperature_trend', temp_trend, 0.8, 24)
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Berechnet Trend-Richtung (steigend = positiv, fallend = negativ)"""
        if len(values) < 2:
            return 0.0
        
        # Lineare Regression für Trend-Berechnung
        x = np.arange(len(values))
        y = np.array(values)
        
        # Berechne Steigung
        slope = np.polyfit(x, y, 1)[0]
        
        # Normalisiere auf -1 bis 1
        normalized_slope = np.tanh(slope / 100)  # Annahme: typische Werte im Bereich 100
        
        return float(normalized_slope)
    
    def _detect_patterns(self):
        """Erkennt Muster in den Performance-Daten"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Letzte 1000 Messungen für Musteranalyse
            cursor.execute('''
                SELECT hashrate_mhs, power_watt, temperature_c, efficiency
                FROM performance_metrics 
                ORDER BY timestamp DESC 
                LIMIT 1000
            ''')
            
            data = cursor.fetchall()
            
            if len(data) >= 100:
                # Berechne Korrelationen
                hashrate_vals = [row[0] for row in data]
                power_vals = [row[1] for row in data]
                temp_vals = [row[2] for row in data]
                eff_vals = [row[3] for row in data]
                
                # Korrelationsanalysen
                hr_power_corr = np.corrcoef(hashrate_vals, power_vals)[0, 1]
                hr_temp_corr = np.corrcoef(hashrate_vals, temp_vals)[0, 1]
                eff_temp_corr = np.corrcoef(eff_vals, temp_vals)[0, 1]
                
                # Speichere Muster-Erkennung
                self._store_prediction('hashrate_power_correlation', hr_power_corr, 0.9, 1)
                self._store_prediction('hashrate_temperature_correlation', hr_temp_corr, 0.9, 1)
                self._store_prediction('efficiency_temperature_correlation', eff_temp_corr, 0.9, 1)
    
    def _prediction_loop(self):
        """Hintergrund-Vorhersage-Schleife"""
        while self.monitoring_active:
            try:
                # Predictive Analytics für zukünftige Performance
                self._generate_predictions()
                
                time.sleep(300)  # Alle 5 Minuten
                
            except Exception as e:
                log_event('PREDICTION_ERROR', {'error': str(e)})
                time.sleep(60)
    
    def _generate_predictions(self):
        """Generiert Vorhersagen für zukünftige Performance"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Letzte 24 Stunden Daten für Vorhersage
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            cursor.execute('''
                SELECT hashrate_mhs, power_watt, temperature_c, efficiency
                FROM performance_metrics 
                WHERE timestamp > ?
                ORDER BY timestamp
            ''', (cutoff_time,))
            
            historical_data = cursor.fetchall()
            
            if len(historical_data) >= 100:
                # Extrahiere Zeitreihen
                hashrate_series = [row[0] for row in historical_data]
                power_series = [row[1] for row in historical_data]
                temp_series = [row[2] for row in historical_data]
                eff_series = [row[3] for row in historical_data]
                
                # Einfache Zeitreihen-Vorhersage (könnte durch ML-Modelle ersetzt werden)
                hr_prediction = self._simple_time_series_prediction(hashrate_series, 24)  # 24 Stunden Vorhersage
                power_prediction = self._simple_time_series_prediction(power_series, 24)
                temp_prediction = self._simple_time_series_prediction(temp_series, 24)
                eff_prediction = self._simple_time_series_prediction(eff_series, 24)
                
                # Speichere Vorhersagen
                self._store_prediction('hashrate_prediction_24h', hr_prediction, 0.7, 24)
                self._store_prediction('power_prediction_24h', power_prediction, 0.7, 24)
                self._store_prediction('temperature_prediction_24h', temp_prediction, 0.7, 24)
                self._store_prediction('efficiency_prediction_24h', eff_prediction, 0.7, 24)
    
    def _simple_time_series_prediction(self, series: List[float], horizon_hours: int) -> float:
        """Einfache Zeitreihen-Vorhersage basierend auf Durchschnitt und Trend"""
        if len(series) < 10:
            return series[-1] if series else 0.0
        
        # Letzte Werte
        recent_values = series[-10:]
        
        # Durchschnitt der letzten Werte
        avg_recent = statistics.mean(recent_values)
        
        # Trend berechnen
        trend = self._calculate_trend(recent_values)
        
        # Vorhersage: aktueller Wert + Trend * Horizont
        prediction = avg_recent + (trend * horizon_hours * 10)  # Skalierungsfaktor
        
        return prediction
    
    def _store_prediction(self, prediction_type: str, predicted_value: float, confidence: float, horizon: int):
        """Speichert Vorhersage in der Datenbank"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO predictions (prediction_type, predicted_value, confidence, time_horizon_hours)
                VALUES (?, ?, ?, ?)
            ''', (prediction_type, predicted_value, confidence, horizon))
            conn.commit()
    
    def get_realtime_dashboard_data(self) -> Dict[str, Any]:
        """Gibt Echtzeit-Daten für das Dashboard zurück"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Aktuelle System-Metriken
            cursor.execute('''
                SELECT 
                    AVG(hashrate_mhs) as avg_hashrate,
                    AVG(power_watt) as avg_power,
                    AVG(temperature_c) as avg_temp,
                    AVG(efficiency) as avg_efficiency,
                    MAX(timestamp) as last_update
                FROM performance_metrics 
                WHERE timestamp > datetime('now', '-1 hour')
            ''')
            
            current_metrics = cursor.fetchone()
            
            # KPIs der letzten Stunde
            cursor.execute('''
                SELECT kpi_name, AVG(kpi_value) as avg_value, kpi_unit
                FROM kpis 
                WHERE timestamp > datetime('now', '-1 hour')
                GROUP BY kpi_name
            ''')
            
            kpis = {row[0]: {'value': row[1], 'unit': row[2]} for row in cursor.fetchall()}
            
            # Aktive Alerts
            cursor.execute('''
                SELECT alert_type, severity, message, timestamp
                FROM alerts 
                WHERE resolved = FALSE
                ORDER BY timestamp DESC
                LIMIT 10
            ''')
            
            alerts = [{'type': row[0], 'severity': row[1], 'message': row[2], 'time': row[3]} 
                     for row in cursor.fetchall()]
            
            return {
                'current_metrics': {
                    'avg_hashrate': current_metrics[0] if current_metrics[0] else 0,
                    'avg_power': current_metrics[1] if current_metrics[1] else 0,
                    'avg_temperature': current_metrics[2] if current_metrics[2] else 0,
                    'avg_efficiency': current_metrics[3] if current_metrics[3] else 0,
                    'last_update': current_metrics[4]
                },
                'kpis': kpis,
                'alerts': alerts,
                'timestamp': datetime.now().isoformat()
            }
    
    def generate_performance_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generiert detaillierten Performance-Report"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # Aggregierte Metriken
            cursor.execute('''
                SELECT 
                    COUNT(*) as measurement_count,
                    AVG(hashrate_mhs) as avg_hashrate,
                    MIN(hashrate_mhs) as min_hashrate,
                    MAX(hashrate_mhs) as max_hashrate,
                    AVG(power_watt) as avg_power,
                    MIN(power_watt) as min_power,
                    MAX(power_watt) as max_power,
                    AVG(temperature_c) as avg_temp,
                    MAX(temperature_c) as max_temp,
                    AVG(efficiency) as avg_efficiency,
                    MIN(efficiency) as min_efficiency
                FROM performance_metrics 
                WHERE timestamp > ?
            ''', (cutoff_time,))
            
            agg_data = cursor.fetchone()
            
            # KPI-Trends
            cursor.execute('''
                SELECT kpi_name, AVG(kpi_value) as avg_value, MIN(kpi_value) as min_value, MAX(kpi_value) as max_value
                FROM kpis 
                WHERE timestamp > ?
                GROUP BY kpi_name
            ''', (cutoff_time,))
            
            kpi_trends = {row[0]: {
                'avg': row[1], 'min': row[2], 'max': row[3]
            } for row in cursor.fetchall()}
            
            # Vorhersagen
            cursor.execute('''
                SELECT prediction_type, predicted_value, confidence, time_horizon_hours
                FROM predictions 
                WHERE timestamp > ?
                ORDER BY timestamp DESC
            ''', (cutoff_time,))
            
            predictions = [{'type': row[0], 'value': row[1], 'confidence': row[2], 'horizon': row[3]} 
                          for row in cursor.fetchall()]
            
            # Alerts-Zusammenfassung
            cursor.execute('''
                SELECT alert_type, COUNT(*) as count, MAX(severity) as max_severity
                FROM alerts 
                WHERE timestamp > ?
                GROUP BY alert_type
            ''', (cutoff_time,))
            
            alert_summary = [{'type': row[0], 'count': row[1], 'max_severity': row[2]} 
                           for row in cursor.fetchall()]
            
            return {
                'report_metadata': {
                    'period_hours': hours,
                    'generated_at': datetime.now().isoformat(),
                    'data_points': agg_data[0] if agg_data[0] else 0
                },
                'aggregated_metrics': {
                    'hashrate': {
                        'avg': agg_data[1] if agg_data[1] else 0,
                        'min': agg_data[2] if agg_data[2] else 0,
                        'max': agg_data[3] if agg_data[3] else 0
                    },
                    'power': {
                        'avg': agg_data[4] if agg_data[4] else 0,
                        'min': agg_data[5] if agg_data[5] else 0,
                        'max': agg_data[6] if agg_data[6] else 0
                    },
                    'temperature': {
                        'avg': agg_data[7] if agg_data[7] else 0,
                        'max': agg_data[8] if agg_data[8] else 0
                    },
                    'efficiency': {
                        'avg': agg_data[9] if agg_data[9] else 0,
                        'min': agg_data[10] if agg_data[10] else 0
                    }
                },
                'kpi_trends': kpi_trends,
                'predictions': predictions,
                'alert_summary': alert_summary,
                'recommendations': self._generate_performance_recommendations(agg_data, kpi_trends)
            }
    
    def _generate_performance_recommendations(self, agg_data: tuple, kpi_trends: dict) -> List[str]:
        """Generiert Leistungs-Empfehlungen basierend auf den Daten"""
        recommendations = []
        
        # Effizienz-Empfehlungen
        avg_efficiency = agg_data[9] if agg_data[9] else 0
        if avg_efficiency < 0.35:
            recommendations.append("⚠️ System-Effizienz unter 35% - Überprüfen Sie Kühlung und Übertaktung")
        
        # Temperatur-Empfehlungen
        max_temp = agg_data[8] if agg_data[8] else 0
        if max_temp > 75:
            recommendations.append("🔥 Hohe Temperaturen detektiert - Erhöhen Sie die Lüfterdrehzahl oder verbessern Sie die Belüftung")
        
        # Power-Empfehlungen
        avg_power = agg_data[4] if agg_data[4] else 0
        if avg_power > 3500:
            recommendations.append("⚡ Hoher Stromverbrauch - Prüfen Sie auf unnötige Leistungsaufnahme")
        
        # Quantum-Level Empfehlungen
        if 'quantum_optimization_level' in kpi_trends:
            quantum_kpi = kpi_trends['quantum_optimization_level']['avg']
            if quantum_kpi < 0.6:
                recommendations.append("🔬 Niedriger Quantum-Level - Aktivieren Sie Quantum-Optimierungen")
        
        # Algorithmus-Empfehlungen
        if 'hashrate_efficiency' in kpi_trends:
            hr_eff_kpi = kpi_trends['hashrate_efficiency']['avg']
            if hr_eff_kpi < 0.3:
                recommendations.append("⚙️ Hashrate-Effizienz niedrig - Prüfen Sie Algorithmus-Auswahl und Rig-Konfiguration")
        
        if not recommendations:
            recommendations.append("✅ System läuft optimal - keine weiteren Maßnahmen erforderlich")
        
        return recommendations
    
    def export_dashboard_data(self, format: str = 'json') -> str:
        """Exportiert Dashboard-Daten in verschiedenen Formaten"""
        dashboard_data = self.get_realtime_dashboard_data()
        
        if format.lower() == 'json':
            return json.dumps(dashboard_data, indent=2, default=str)
        elif format.lower() == 'html':
            return self._generate_dashboard_html(dashboard_data)
        else:
            return str(dashboard_data)
    
    def _generate_dashboard_html(self, data: Dict[str, Any]) -> str:
        """Generiert HTML-Dashboard"""
        current = data['current_metrics']
        kpis = data['kpis']
        alerts = data['alerts']
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Performance Monitoring Dashboard</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .header {{ background: #667eea; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
                .card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .metric {{ font-size: 2em; font-weight: bold; color: #667eea; }}
                .label {{ color: #666; font-size: 0.9em; }}
                .alert {{ padding: 10px; margin: 5px 0; border-radius: 4px; }}
                .alert.CRITICAL {{ background: #ffe6e6; border-left: 4px solid #ff0000; }}
                .alert.HIGH {{ background: #fff4e6; border-left: 4px solid #ff6600; }}
                .alert.MEDIUM {{ background: #fffce6; border-left: 4px solid #ffa500; }}
                .kpi-value {{ font-size: 1.5em; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Performance Monitoring Dashboard</h1>
                    <p>Letztes Update: {current['last_update']}</p>
                </div>
                
                <div class="grid">
                    <div class="card">
                        <h3>📊 Aktuelle Metriken</h3>
                        <div class="metric">{current['avg_hashrate']:.1f} MH/s</div>
                        <div class="label">Durchschnittliche Hashrate</div>
                        <br>
                        <div class="metric">{current['avg_power']:.0f} W</div>
                        <div class="label">Stromverbrauch</div>
                        <br>
                        <div class="metric">{current['avg_temperature']:.1f}°C</div>
                        <div class="label">Durchschnittstemperatur</div>
                        <br>
                        <div class="metric">{current['avg_efficiency']:.1%}</div>
                        <div class="label">System-Effizienz</div>
                    </div>
                    
                    <div class="card">
                        <h3>📈 Key Performance Indicators</h3>
        """
        
        for kpi_name, kpi_data in kpis.items():
            html += f"""
                        <div style="margin-bottom: 15px;">
                            <div class="label">{kpi_name.replace('_', ' ').title()}</div>
                            <div class="kpi-value">{kpi_data['value']:.2f} {kpi_data['unit']}</div>
                        </div>
            """
        
        html += """
                    </div>
                    
                    <div class="card">
                        <h3>🚨 Aktive Alerts</h3>
        """
        
        if alerts:
            for alert in alerts:
                html += f"""
                        <div class="alert {alert['severity']}">
                            <strong>{alert['severity']}</strong>: {alert['message']}
                            <br><small>{alert['time']}</small>
                        </div>
                """
        else:
            html += "<p>Keine aktiven Alerts</p>"
        
        html += """
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html


# Globale Instanz
performance_monitor = PerformanceMonitoringSystem()


# Convenience-Funktionen
def start_performance_monitoring():
    """Startet das Performance Monitoring"""
    performance_monitor.start_monitoring()

def stop_performance_monitoring():
    """Stoppt das Performance Monitoring"""
    performance_monitor.stop_monitoring()

def get_dashboard_data():
    """Gibt Echtzeit-Dashboard-Daten zurück"""
    return performance_monitor.get_realtime_dashboard_data()

def generate_performance_report(hours: int = 24):
    """Generiert Performance-Report"""
    return performance_monitor.generate_performance_report(hours)

def export_dashboard(format: str = 'json'):
    """Exportiert Dashboard-Daten"""
    return performance_monitor.export_dashboard_data(format)


if __name__ == "__main__":
    print("CASH MONEY COLORS ORIGINAL (R) - PERFORMANCE MONITORING & ANALYTICS")
    print("=" * 70)
    
    # Starte Monitoring
    start_performance_monitoring()
    
    # Warte auf Daten
    print("⏳ Sammle Performance-Daten...")
    time.sleep(10)
    
    # Zeige Dashboard
    print("\n📊 Echtzeit-Dashboard:")
    dashboard_data = get_dashboard_data()
    print(f"   Aktuelle Hashrate: {dashboard_data['current_metrics']['avg_hashrate']:.1f} MH/s")
    print(f"   Aktueller Verbrauch: {dashboard_data['current_metrics']['avg_power']:.0f} W")
    print(f"   Durchschnittstemperatur: {dashboard_data['current_metrics']['avg_temperature']:.1f}°C")
    print(f"   System-Effizienz: {dashboard_data['current_metrics']['avg_efficiency']:.1%}")
    
    # Generiere Report
    print("\n📈 Generiere 24-Stunden-Report...")
    report = generate_performance_report(24)
    print(f"   Datenpunkte: {report['report_metadata']['data_points']}")
    print(f"   Durchschnittliche Hashrate: {report['aggregated_metrics']['hashrate']['avg']:.1f} MH/s")
    print(f"   Durchschnittlicher Verbrauch: {report['aggregated_metrics']['power']['avg']:.0f} W")
    
    # Zeige Empfehlungen
    print("\n💡 Empfehlungen:")
    for rec in report['recommendations']:
        print(f"   {rec}")
    
    print("\n✅ PERFORMANCE MONITORING SYSTEM VOLLENDEN")
    print("Verwende start_performance_monitoring() für kontinuierliches Monitoring")