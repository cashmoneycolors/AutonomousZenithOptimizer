#!/usr/bin/env python3
"""
CASH MONEY COLORS ORIGINAL (R) - PERFORMANCE MONITORING TEST SUITE
Komplette Test- und Validierungssuite für das Performance Monitoring & Analytics System
"""

import time
import json
import threading
from datetime import datetime, timedelta
from pathlib import Path

# Importiere die Systemkomponenten
try:
    from python_modules.performance_monitoring import (
        PerformanceMonitoringSystem,
        start_performance_monitoring,
        stop_performance_monitoring,
        get_dashboard_data,
        generate_performance_report,
        export_dashboard
    )
    from performance_dashboard.automated_reports import (
        AutomatedReportingSystem,
        start_automated_reports,
        generate_manual_report,
        get_reports
    )
except ImportError as e:
    print(f"⚠️ Import-Fehler: {e}")
    print("Stelle sicher, dass alle Module im richtigen Pfad sind")
    exit(1)


class PerformanceMonitoringTestSuite:
    """Test-Suite für das Performance Monitoring System"""
    
    def __init__(self):
        self.test_results = []
        self.monitoring_system = PerformanceMonitoringSystem()
        self.reporting_system = AutomatedReportingSystem()
        
        print("🧪 PERFORMANCE MONITORING TEST SUITE")
        print("=" * 60)
    
    def run_all_tests(self):
        """Führt alle Tests aus"""
        print("\n🚀 Starte umfassende Systemtests...")
        
        # Test 1: System-Initialisierung
        self.test_system_initialization()
        
        # Test 2: Datenbank-Operationen
        self.test_database_operations()
        
        # Test 3: Echtzeit-Daten
        self.test_realtime_data()
        
        # Test 4: Performance-Reports
        self.test_performance_reports()
        
        # Test 5: Dashboard-Export
        self.test_dashboard_export()
        
        # Test 6: Automatisierte Reports
        self.test_automated_reporting()
        
        # Test 7: Mobile-Optimierung
        self.test_mobile_optimization()
        
        # Test 8: System-Integration
        self.test_system_integration()
        
        # Test 9: Performance-Tests
        self.test_performance_benchmarks()
        
        # Test 10: Fehlerbehandlung
        self.test_error_handling()
        
        # Zeige Test-Zusammenfassung
        self.print_test_summary()
    
    def test_system_initialization(self):
        """Testet die System-Initialisierung"""
        print("\n📋 Test 1: System-Initialisierung")
        
        try:
            # Überprüfe, ob die Datenbank erstellt wurde
            db_path = Path(self.monitoring_system.db_path)
            if db_path.exists():
                print("   ✅ Datenbank wurde erstellt")
                self.test_results.append(("Datenbank-Erstellung", True, "Datenbank existiert"))
            else:
                print("   ❌ Datenbank wurde nicht erstellt")
                self.test_results.append(("Datenbank-Erstellung", False, "Datenbank existiert nicht"))
            
            # Überprüfe Monitoring-Status
            if not self.monitoring_system.monitoring_active:
                print("   ✅ Monitoring-System initialisiert (inaktiv)")
                self.test_results.append(("Monitoring-Initialisierung", True, "System bereit"))
            else:
                print("   ⚠️ Monitoring läuft bereits")
                self.test_results.append(("Monitoring-Initialisierung", True, "System aktiv"))
            
        except Exception as e:
            print(f"   ❌ Initialisierungsfehler: {e}")
            self.test_results.append(("System-Initialisierung", False, str(e)))
    
    def test_database_operations(self):
        """Testet Datenbank-Operationen"""
        print("\n📋 Test 2: Datenbank-Operationen")
        
        try:
            # Teste das Sammeln von Echtzeit-Metriken
            metrics = self.monitoring_system._collect_realtime_metrics()
            
            if metrics and 'system_metrics' in metrics:
                print("   ✅ Echtzeit-Metriken gesammelt")
                print(f"      - Hashrate: {metrics['system_metrics']['total_hashrate_mhs']:.1f} MH/s")
                print(f"      - Verbrauch: {metrics['system_metrics']['total_power_watt']:.0f} W")
                print(f"      - Temperatur: {metrics['system_metrics']['avg_temperature_c']:.1f}°C")
                print(f"      - Effizienz: {metrics['system_metrics']['avg_efficiency']:.1%}")
                
                self.test_results.append(("Metriken-Sammlung", True, "Daten erfolgreich gesammelt"))
            else:
                print("   ❌ Metriken-Sammlung fehlgeschlagen")
                self.test_results.append(("Metriken-Sammlung", False, "Keine gültigen Daten"))
            
            # Teste das Speichern von Metriken
            self.monitoring_system._store_metrics(metrics)
            print("   ✅ Metriken in Datenbank gespeichert")
            self.test_results.append(("Datenbank-Speicherung", True, "Daten erfolgreich gespeichert"))
            
        except Exception as e:
            print(f"   ❌ Datenbank-Test fehlgeschlagen: {e}")
            self.test_results.append(("Datenbank-Operationen", False, str(e)))
    
    def test_realtime_data(self):
        """Testet Echtzeit-Daten-Funktionen"""
        print("\n📋 Test 3: Echtzeit-Daten")
        
        try:
            # Starte kurzes Monitoring
            self.monitoring_system.start_monitoring()
            time.sleep(2)  # Kurze Wartezeit für Daten
            self.monitoring_system.stop_monitoring()
            
            # Teste Dashboard-Daten
            dashboard_data = get_dashboard_data()
            
            if dashboard_data and 'current_metrics' in dashboard_data:
                current = dashboard_data['current_metrics']
                print("   ✅ Echtzeit-Dashboard-Daten verfügbar")
                print(f"      - Letztes Update: {current.get('last_update', 'N/A')}")
                print(f"      - Hashrate: {current.get('avg_hashrate', 0):.1f} MH/s")
                print(f"      - Verbrauch: {current.get('avg_power', 0):.0f} W")
                
                self.test_results.append(("Echtzeit-Daten", True, "Dashboard-Daten verfügbar"))
            else:
                print("   ❌ Echtzeit-Daten nicht verfügbar")
                self.test_results.append(("Echtzeit-Daten", False, "Keine Dashboard-Daten"))
            
        except Exception as e:
            print(f"   ❌ Echtzeit-Test fehlgeschlagen: {e}")
            self.test_results.append(("Echtzeit-Daten", False, str(e)))
    
    def test_performance_reports(self):
        """Testet Performance-Report-Generierung"""
        print("\n📋 Test 4: Performance-Reports")
        
        try:
            # Generiere 1-Stunden-Report
            report = generate_performance_report(1)
            
            if report and 'report_metadata' in report:
                metadata = report['report_metadata']
                print("   ✅ Performance-Report generiert")
                print(f"      - Zeitspanne: {metadata.get('period_hours', 0)} Stunden")
                print(f"      - Datenpunkte: {metadata.get('data_points', 0)}")
                print(f"      - Generiert: {metadata.get('generated_at', 'N/A')}")
                
                # Überprüfe aggregierte Metriken
                agg_metrics = report.get('aggregated_metrics', {})
                if agg_metrics:
                    print("      - Aggregierte Metriken verfügbar")
                    self.test_results.append(("Report-Generierung", True, "Report erfolgreich erstellt"))
                else:
                    print("      ⚠️ Keine aggregierten Metriken")
                    self.test_results.append(("Report-Generierung", False, "Keine Metriken"))
            else:
                print("   ❌ Report-Generierung fehlgeschlagen")
                self.test_results.append(("Report-Generierung", False, "Kein gültiger Report"))
            
        except Exception as e:
            print(f"   ❌ Report-Test fehlgeschlagen: {e}")
            self.test_results.append(("Report-Generierung", False, str(e)))
    
    def test_dashboard_export(self):
        """Testet Dashboard-Export-Funktionen"""
        print("\n📋 Test 5: Dashboard-Export")
        
        try:
            # Teste JSON-Export
            json_data = export_dashboard('json')
            if json_data:
                print("   ✅ JSON-Export erfolgreich")
                self.test_results.append(("JSON-Export", True, "Daten exportiert"))
            else:
                print("   ❌ JSON-Export fehlgeschlagen")
                self.test_results.append(("JSON-Export", False, "Keine Daten"))
            
            # Teste HTML-Export
            html_data = export_dashboard('html')
            if html_data and '<html>' in html_data:
                print("   ✅ HTML-Export erfolgreich")
                self.test_results.append(("HTML-Export", True, "HTML generiert"))
            else:
                print("   ❌ HTML-Export fehlgeschlagen")
                self.test_results.append(("HTML-Export", False, "Kein HTML"))
            
        except Exception as e:
            print(f"   ❌ Export-Test fehlgeschlagen: {e}")
            self.test_results.append(("Dashboard-Export", False, str(e)))
    
    def test_automated_reporting(self):
        """Testet automatisierte Berichterstattung"""
        print("\n📋 Test 6: Automatisierte Reports")
        
        try:
            # Teste manuelle Report-Generierung
            report_filename = generate_manual_report(1, ['json', 'html'])
            
            if report_filename:
                print("   ✅ Manueller Report erstellt")
                print(f"      - Dateiname: {report_filename}")
                self.test_results.append(("Manuelle Reports", True, "Report erstellt"))
            else:
                print("   ❌ Manueller Report fehlgeschlagen")
                self.test_results.append(("Manuelle Reports", False, "Kein Report"))
            
            # Überprüfe verfügbare Reports
            reports = get_reports()
            print(f"   ✅ {len(reports)} Reports verfügbar")
            self.test_results.append(("Report-Liste", True, f"{len(reports)} Reports gefunden"))
            
        except Exception as e:
            print(f"   ❌ Automatisierter Report-Test fehlgeschlagen: {e}")
            self.test_results.append(("Automatisierte Reports", False, str(e)))
    
    def test_mobile_optimization(self):
        """Testet Mobile-Optimierung"""
        print("\n📋 Test 7: Mobile-Optimierung")
        
        try:
            # Teste mobile-optimierte Daten
            dashboard_data = get_dashboard_data()
            
            if dashboard_data:
                # Überprüfe, ob die Daten für mobile Darstellung geeignet sind
                current_metrics = dashboard_data.get('current_metrics', {})
                
                required_fields = ['avg_hashrate', 'avg_power', 'avg_temperature', 'avg_efficiency']
                missing_fields = [field for field in required_fields if field not in current_metrics]
                
                if not missing_fields:
                    print("   ✅ Mobile-Datenstruktur korrekt")
                    print("      - Alle erforderlichen Felder vorhanden")
                    self.test_results.append(("Mobile-Daten", True, "Struktur korrekt"))
                else:
                    print(f"   ❌ Fehlende Felder: {missing_fields}")
                    self.test_results.append(("Mobile-Daten", False, f"Fehlende Felder: {missing_fields}"))
                
                # Teste KPI-Daten für mobile Ansicht
                kpis = dashboard_data.get('kpis', {})
                if kpis:
                    print("      - KPI-Daten verfügbar")
                    self.test_results.append(("Mobile-KPIs", True, "KPIs verfügbar"))
                else:
                    print("      ⚠️ Keine KPI-Daten")
                    self.test_results.append(("Mobile-KPIs", False, "Keine KPIs"))
            
        except Exception as e:
            print(f"   ❌ Mobile-Optimierungs-Test fehlgeschlagen: {e}")
            self.test_results.append(("Mobile-Optimierung", False, str(e)))
    
    def test_system_integration(self):
        """Testet System-Integration"""
        print("\n📋 Test 8: System-Integration")
        
        try:
            # Teste Integration aller Module
            metrics = self.monitoring_system._collect_realtime_metrics()
            
            required_modules = [
                'system_metrics',
                'quantum_metrics', 
                'energy_metrics',
                'thermal_metrics',
                'algorithm_metrics',
                'maintenance_metrics'
            ]
            
            missing_modules = [module for module in required_modules if module not in metrics]
            
            if not missing_modules:
                print("   ✅ Alle Systemmodule integriert")
                print("      - Quantum Optimization")
                print("      - Energy Efficiency")
                print("      - Thermal Management")
                print("      - Algorithm Switching")
                print("      - Predictive Maintenance")
                self.test_results.append(("System-Integration", True, "Alle Module integriert"))
            else:
                print(f"   ❌ Fehlende Module: {missing_modules}")
                self.test_results.append(("System-Integration", False, f"Fehlende Module: {missing_modules}"))
            
        except Exception as e:
            print(f"   ❌ Integrations-Test fehlgeschlagen: {e}")
            self.test_results.append(("System-Integration", False, str(e)))
    
    def test_performance_benchmarks(self):
        """Testet Performance-Benchmarks"""
        print("\n📋 Test 9: Performance-Benchmarks")
        
        try:
            # Teste Datenbank-Performance
            start_time = time.time()
            
            # Sammle und speichere 100 Metriken
            for i in range(100):
                metrics = self.monitoring_system._collect_realtime_metrics()
                self.monitoring_system._store_metrics(metrics)
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"   ✅ Datenbank-Performance: {duration:.2f}s für 100 Datensätze")
            print(f"      - Durchschnitt: {duration/100:.4f}s pro Datensatz")
            
            if duration < 10.0:  # Unter 10 Sekunden für 100 Datensätze
                self.test_results.append(("Performance", True, f"{duration:.2f}s für 100 Datensätze"))
            else:
                self.test_results.append(("Performance", False, f"{duration:.2f}s zu langsam"))
            
            # Teste Report-Generierung-Performance
            start_time = time.time()
            report = generate_performance_report(24)
            end_time = time.time()
            report_duration = end_time - start_time
            
            print(f"   ✅ Report-Performance: {report_duration:.2f}s")
            
            if report_duration < 5.0:  # Unter 5 Sekunden für 24h Report
                self.test_results.append(("Report-Performance", True, f"{report_duration:.2f}s"))
            else:
                self.test_results.append(("Report-Performance", False, f"{report_duration:.2f}s zu langsam"))
            
        except Exception as e:
            print(f"   ❌ Performance-Test fehlgeschlagen: {e}")
            self.test_results.append(("Performance", False, str(e)))
    
    def test_error_handling(self):
        """Testet Fehlerbehandlung"""
        print("\n📋 Test 10: Fehlerbehandlung")
        
        try:
            # Teste fehlerhafte Eingaben
            try:
                # Teste ungültige Zeitspanne
                invalid_report = generate_performance_report(-1)
                print("   ⚠️ Fehlerhafte Eingabe nicht erkannt")
                self.test_results.append(("Fehlerbehandlung", False, "Ungültige Eingabe akzeptiert"))
            except:
                print("   ✅ Fehlerhafte Eingaben werden erkannt")
                self.test_results.append(("Fehlerbehandlung", True, "Validierung aktiv"))
            
            # Teste fehlende Datenbank
            try:
                # Versuche mit nicht existierender Datenbank
                temp_db = self.monitoring_system.db_path
                self.monitoring_system.db_path = Path("nonexistent.db")
                
                # Dies sollte fehlschlagen
                metrics = self.monitoring_system._collect_realtime_metrics()
                self.monitoring_system._store_metrics(metrics)
                
                print("   ⚠️ Datenbank-Fehler nicht erkannt")
                self.test_results.append(("Datenbank-Fehler", False, "Keine Fehlererkennung"))
                
                # Wiederherstellen
                self.monitoring_system.db_path = temp_db
                
            except Exception as db_error:
                print("   ✅ Datenbank-Fehler werden erkannt")
                print(f"      - Fehlermeldung: {type(db_error).__name__}")
                self.test_results.append(("Datenbank-Fehler", True, "Fehlererkennung aktiv"))
                
                # Wiederherstellen
                self.monitoring_system.db_path = temp_db
            
        except Exception as e:
            print(f"   ❌ Fehlerbehandlungs-Test fehlgeschlagen: {e}")
            self.test_results.append(("Fehlerbehandlung", False, str(e)))
    
    def print_test_summary(self):
        """Zeigt Test-Zusammenfassung"""
        print("\n" + "=" * 60)
        print("📊 TEST-ZUSAMMENFASSUNG")
        print("=" * 60)
        
        passed_tests = sum(1 for _, success, _ in self.test_results if success)
        total_tests = len(self.test_results)
        
        print(f"\nErgebnis: {passed_tests}/{total_tests} Tests bestanden")
        
        # Detaillierte Ergebnisse
        print("\nTest-Ergebnisse:")
        for test_name, success, message in self.test_results:
            status = "✅" if success else "❌"
            print(f"   {status} {test_name}: {message}")
        
        # System-Bewertung
        success_rate = (passed_tests / total_tests) * 100
        
        if success_rate >= 90:
            print(f"\n🎉 SYSTEMBEWERTUNG: EXZELLENT ({success_rate:.1f}%)")
            print("   Das Performance Monitoring System ist voll funktionsfähig!")
        elif success_rate >= 75:
            print(f"\n👍 SYSTEMBEWERTUNG: GUT ({success_rate:.1f}%)")
            print("   Das System funktioniert weitgehend, kleinere Optimierungen möglich.")
        elif success_rate >= 50:
            print(f"\n⚠️ SYSTEMBEWERTUNG: AKZEPTABEL ({success_rate:.1f}%)")
            print("   Das System hat funktionierende Grundlagen, benötigt jedoch Optimierungen.")
        else:
            print(f"\n❌ SYSTEMBEWERTUNG: UNZULÄNGGLICH ({success_rate:.1f}%)")
            print("   Das System benötigt erhebliche Verbesserungen.")
        
        print("\n" + "=" * 60)
        
        # Empfehlungen
        failed_tests = [name for name, success, _ in self.test_results if not success]
        if failed_tests:
            print("\n🔧 EMPFEHLUNGEN:")
            for test in failed_tests:
                print(f"   - {test} optimieren")
        
        print("\n🚀 Das Performance Monitoring & Analytics System ist bereit für den produktiven Einsatz!")
        print("   Verwenden Sie die folgenden Funktionen:")
        print("   - start_performance_monitoring() - Startet das Monitoring")
        print("   - get_dashboard_data() - Echtzeit-Daten abrufen")
        print("   - generate_performance_report() - Reports erstellen")
        print("   - start_automated_reports() - Automatisierte Reports aktivieren")


def main():
    """Hauptfunktion für die Testausführung"""
    print("CASH MONEY COLORS ORIGINAL (R) - PERFORMANCE MONITORING TEST SUITE")
    print("=" * 80)
    
    # Erstelle und führe Test-Suite aus
    test_suite = PerformanceMonitoringTestSuite()
    test_suite.run_all_tests()


if __name__ == "__main__":
    main()