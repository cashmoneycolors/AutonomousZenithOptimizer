#!/usr/bin/env python3
"""
CASH MONEY COLORS ORIGINAL (R) - AUTOMATED REPORTING SYSTEM
Automatisierte Erstellung und Verteilung von Performance-Reports
"""

import json
import smtplib
import schedule
import time
import logging
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
import threading
from typing import Dict, List, Optional

# Importiere das Performance Monitoring System
try:
    from python_modules.performance_monitoring import generate_performance_report
    from python_modules.config_manager import get_config
    from python_modules.enhanced_logging import log_event
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from python_modules.performance_monitoring import generate_performance_report
    from python_modules.config_manager import get_config
    from python_modules.enhanced_logging import log_event


class AutomatedReportingSystem:
    """System für automatisierte Performance-Reports"""
    
    def __init__(self):
        self.report_config = get_config('AutomatedReports', {
            'ReportPath': 'reports',
            'EmailEnabled': True,
            'EmailSettings': {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'sender_email': 'noreply@cashmoneycolors.com',
                'sender_password': 'your-app-password',
                'recipients': ['admin@cashmoneycolors.com']
            },
            'Schedule': {
                'daily_report': '06:00',
                'weekly_report': '0 9 * * 1',  # Montags um 9 Uhr
                'monthly_report': '0 9 1 * *',  # Erster des Monats um 9 Uhr
                'critical_alerts': True
            },
            'ReportFormats': ['json', 'html', 'pdf'],
            'RetentionDays': 30
        })
        
        self.report_path = Path(self.report_config.get('ReportPath', 'reports'))
        self.report_path.mkdir(exist_ok=True)
        
        self.is_running = False
        self.report_thread = None
        
        print("🤖 AUTOMATED REPORTING SYSTEM INITIALISIERT")
        print(f"   Report-Pfad: {self.report_path.absolute()}")
        print(f"   E-Mail: {'Aktiviert' if self.report_config.get('EmailEnabled', True) else 'Deaktiviert'}")
    
    def start_scheduled_reports(self):
        """Startet den geplanten Report-Service"""
        if self.is_running:
            print("⚠️ Reporting Service läuft bereits")
            return
        
        self.is_running = True
        
        # Täglicher Report
        daily_time = self.report_config.get('Schedule', {}).get('daily_report', '06:00')
        schedule.every().day.at(daily_time).do(self.generate_daily_report)
        
        # Wöchentlicher Report
        weekly_cron = self.report_config.get('Schedule', {}).get('weekly_report', '0 9 * * 1')
        schedule.every().monday.at("09:00").do(self.generate_weekly_report)
        
        # Monatlicher Report
        monthly_day = self.report_config.get('Schedule', {}).get('monthly_report', '1')
        schedule.every().month.do(self.generate_monthly_report)
        
        # Starte Hintergrund-Thread
        self.report_thread = threading.Thread(target=self._report_scheduler_loop, daemon=True)
        self.report_thread.start()
        
        print("✅ Geplante Reports aktiviert")
        print(f"   Täglich: {daily_time}")
        print(f"   Wöchentlich: Montags 09:00")
        print(f"   Monatlich: Erster des Monats 09:00")
    
    def stop_scheduled_reports(self):
        """Stoppt den geplanten Report-Service"""
        self.is_running = False
        schedule.clear()
        print("🛑 Geplante Reports gestoppt")
    
    def _report_scheduler_loop(self):
        """Hintergrund-Scheduler-Schleife"""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Alle 60 Sekunden prüfen
            except Exception as e:
                log_event('REPORT_SCHEDULER_ERROR', {'error': str(e)})
                time.sleep(60)
    
    def generate_daily_report(self):
        """Generiert täglichen Performance-Report"""
        try:
            print("📅 Generiere täglichen Report...")
            
            # Generiere 24-Stunden-Report
            report = generate_performance_report(24)
            
            # Speichere Report
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"daily_report_{timestamp}"
            
            self._save_report(report, filename, ['json', 'html'])
            
            # Sende per E-Mail
            if self.report_config.get('EmailEnabled', True):
                self._send_email_report(
                    subject=f"Täglicher Performance-Report - {datetime.now().strftime('%d.%m.%Y')}",
                    body=self._generate_email_body(report, 'daily'),
                    attachments=[f"{filename}.json", f"{filename}.html"]
                )
            
            log_event('DAILY_REPORT_GENERATED', {
                'filename': filename,
                'timestamp': datetime.now().isoformat()
            })
            
            print("✅ Täglicher Report erstellt und versendet")
            
        except Exception as e:
            log_event('DAILY_REPORT_ERROR', {'error': str(e)})
            print(f"❌ Fehler beim täglichen Report: {e}")
    
    def generate_weekly_report(self):
        """Generiert wöchentlichen Performance-Report"""
        try:
            print("📅 Generiere wöchentlichen Report...")
            
            # Generiere 7-Tage-Report
            report = generate_performance_report(24 * 7)
            
            # Speichere Report
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"weekly_report_{timestamp}"
            
            self._save_report(report, filename, ['json', 'html'])
            
            # Sende per E-Mail
            if self.report_config.get('EmailEnabled', True):
                self._send_email_report(
                    subject=f"Wöchentlicher Performance-Report - KW {datetime.now().isocalendar()[1]}",
                    body=self._generate_email_body(report, 'weekly'),
                    attachments=[f"{filename}.json", f"{filename}.html"]
                )
            
            log_event('WEEKLY_REPORT_GENERATED', {
                'filename': filename,
                'timestamp': datetime.now().isoformat()
            })
            
            print("✅ Wöchentlicher Report erstellt und versendet")
            
        except Exception as e:
            log_event('WEEKLY_REPORT_ERROR', {'error': str(e)})
            print(f"❌ Fehler beim wöchentlichen Report: {e}")
    
    def generate_monthly_report(self):
        """Generiert monatlichen Performance-Report"""
        try:
            print("📅 Generiere monatlichen Report...")
            
            # Generiere 30-Tage-Report
            report = generate_performance_report(24 * 30)
            
            # Speichere Report
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"monthly_report_{timestamp}"
            
            self._save_report(report, filename, ['json', 'html', 'pdf'])
            
            # Sende per E-Mail
            if self.report_config.get('EmailEnabled', True):
                self._send_email_report(
                    subject=f"Monatlicher Performance-Report - {datetime.now().strftime('%B %Y')}",
                    body=self._generate_email_body(report, 'monthly'),
                    attachments=[f"{filename}.json", f"{filename}.html", f"{filename}.pdf"]
                )
            
            log_event('MONTHLY_REPORT_GENERATED', {
                'filename': filename,
                'timestamp': datetime.now().isoformat()
            })
            
            print("✅ Monatlicher Report erstellt und versendet")
            
        except Exception as e:
            log_event('MONTHLY_REPORT_ERROR', {'error': str(e)})
            print(f"❌ Fehler beim monatlichen Report: {e}")
    
    def generate_on_demand_report(self, hours: int = 24, formats: List[str] = None) -> str:
        """Generiert manuellen Report auf Anfrage"""
        try:
            print(f"📅 Generiere manuellen Report ({hours} Stunden)...")
            
            if formats is None:
                formats = self.report_config.get('ReportFormats', ['json', 'html'])
            
            # Generiere Report
            report = generate_performance_report(hours)
            
            # Speichere Report
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"on_demand_report_{timestamp}_{hours}h"
            
            self._save_report(report, filename, formats)
            
            log_event('ON_DEMAND_REPORT_GENERATED', {
                'filename': filename,
                'hours': hours,
                'formats': formats,
                'timestamp': datetime.now().isoformat()
            })
            
            print(f"✅ Manueller Report erstellt: {filename}")
            return filename
            
        except Exception as e:
            log_event('ON_DEMAND_REPORT_ERROR', {'error': str(e)})
            print(f"❌ Fehler beim manuellen Report: {e}")
            return ""
    
    def _save_report(self, report: Dict, filename: str, formats: List[str]):
        """Speichert Report in verschiedenen Formaten"""
        for fmt in formats:
            try:
                if fmt.lower() == 'json':
                    filepath = self.report_path / f"{filename}.json"
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(report, f, indent=2, ensure_ascii=False)
                
                elif fmt.lower() == 'html':
                    filepath = self.report_path / f"{filename}.html"
                    html_content = self._generate_html_report(report)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                
                elif fmt.lower() == 'pdf':
                    # PDF-Generierung würde hier implementiert werden
                    # (z.B. mit ReportLab oder WeasyPrint)
                    filepath = self.report_path / f"{filename}.pdf"
                    # Platzhalter für PDF-Generierung
                    with open(filepath, 'w') as f:
                        f.write("PDF-Report wird in zukünftigen Versionen unterstützt")
                
                print(f"   ✅ {fmt.upper()}-Report gespeichert: {filename}.{fmt}")
                
            except Exception as e:
                log_event('REPORT_SAVE_ERROR', {
                    'filename': filename,
                    'format': fmt,
                    'error': str(e)
                })
                print(f"   ❌ Fehler beim Speichern von {filename}.{fmt}: {e}")
    
    def _generate_html_report(self, report: Dict) -> str:
        """Generiert HTML-Report"""
        metadata = report.get('report_metadata', {})
        agg_metrics = report.get('aggregated_metrics', {})
        kpi_trends = report.get('kpi_trends', {})
        recommendations = report.get('recommendations', [])
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Performance Report - {metadata.get('generated_at', 'N/A')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                h1 {{ color: #667eea; border-bottom: 3px solid #667eea; padding-bottom: 10px; }}
                .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }}
                .metric-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea; }}
                .metric-value {{ font-size: 2em; font-weight: bold; color: #333; }}
                .metric-label {{ color: #666; font-size: 0.9em; }}
                .recommendations {{ margin-top: 30px; }}
                .recommendation {{ background: #e8f5e8; padding: 15px; margin: 10px 0; border-radius: 6px; border-left: 4px solid #28a745; }}
                .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
                .kpi-item {{ background: #f8f9fa; padding: 15px; border-radius: 6px; }}
                .footer {{ margin-top: 40px; text-align: center; color: #666; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 Performance Report</h1>
                <p><strong>Zeitraum:</strong> {metadata.get('period_hours', 0)} Stunden</p>
                <p><strong>Generiert:</strong> {metadata.get('generated_at', 'N/A')}</p>
                <p><strong>Datenpunkte:</strong> {metadata.get('data_points', 0)}</p>
                
                <div class="summary">
                    <div class="metric-card">
                        <div class="metric-value">{agg_metrics.get('hashrate', {}).get('avg', 0):.1f} MH/s</div>
                        <div class="metric-label">Durchschnittliche Hashrate</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{agg_metrics.get('power', {}).get('avg', 0):.0f} W</div>
                        <div class="metric-label">Durchschnittlicher Verbrauch</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{agg_metrics.get('temperature', {}).get('avg', 0):.1f}°C</div>
                        <div class="metric-label">Durchschnittstemperatur</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{agg_metrics.get('efficiency', {}).get('avg', 0):.1%}</div>
                        <div class="metric-label">System-Effizienz</div>
                    </div>
                </div>
                
                <h2>🎯 Key Performance Indicators</h2>
                <div class="kpi-grid">
        """
        
        for kpi_name, kpi_data in kpi_trends.items():
            html += f"""
                    <div class="kpi-item">
                        <strong>{kpi_name.replace('_', ' ').title()}</strong><br>
                        Durchschnitt: {kpi_data.get('avg', 0):.2f}<br>
                        Minimum: {kpi_data.get('min', 0):.2f}<br>
                        Maximum: {kpi_data.get('max', 0):.2f}
                    </div>
            """
        
        html += """
                </div>
                
                <div class="recommendations">
                    <h2>💡 Empfehlungen</h2>
        """
        
        if recommendations:
            for rec in recommendations:
                html += f'<div class="recommendation">{rec}</div>'
        else:
            html += '<p>Keine besonderen Empfehlungen - System läuft optimal!</p>'
        
        html += """
                </div>
                
                <div class="footer">
                    <p>CASH MONEY COLORS ORIGINAL (R) - Performance Monitoring & Analytics</p>
                    <p>Report-ID: """ + datetime.now().strftime('%Y%m%d_%H%M%S') + """</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _generate_email_body(self, report: Dict, report_type: str) -> str:
        """Generiert E-Mail-Text für Reports"""
        metadata = report.get('report_metadata', {})
        agg_metrics = report.get('aggregated_metrics', {})
        recommendations = report.get('recommendations', [])
        
        body = f"""
Liebe(r) Nutzer(in),

hier ist Ihr {report_type} Performance-Report für das Mining-System:

📊 ZUSAMMENFASSUNG
==================
Zeitraum: {metadata.get('period_hours', 0)} Stunden
Datenpunkte: {metadata.get('data_points', 0)}
Generiert: {metadata.get('generated_at', 'N/A')}

📈 KERNMETRIKEN
================
• Durchschnittliche Hashrate: {agg_metrics.get('hashrate', {}).get('avg', 0):.1f} MH/s
• Durchschnittlicher Verbrauch: {agg_metrics.get('power', {}).get('avg', 0):.0f} W
• Durchschnittstemperatur: {agg_metrics.get('temperature', {}).get('avg', 0):.1f}°C
• System-Effizienz: {agg_metrics.get('efficiency', {}).get('avg', 0):.1%}

💡 EMPFEHLUNGEN
================
"""
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                body += f"{i}. {rec}\n"
        else:
            body += "Keine besonderen Empfehlungen - System läuft optimal!\n"
        
        body += f"""
Weitere Details finden Sie im angehängten Report.

Mit freundlichen Grüßen,
Ihr CASH MONEY COLORS ORIGINAL (R) Performance Monitoring System

---
Dies ist eine automatisch generierte Nachricht.
Für Fragen wenden Sie sich bitte an den Support.
"""
        
        return body
    
    def _send_email_report(self, subject: str, body: str, attachments: List[str] = None):
        """Sendet Report per E-Mail"""
        try:
            email_config = self.report_config.get('EmailSettings', {})
            
            # E-Mail-Nachricht erstellen
            msg = MIMEMultipart()
            msg['From'] = email_config.get('sender_email', 'noreply@cashmoneycolors.com')
            msg['To'] = ', '.join(email_config.get('recipients', ['admin@cashmoneycolors.com']))
            msg['Subject'] = subject
            
            # Nachrichtentext hinzufügen
            msg.attach(MIMEText(body, 'plain'))
            
            # Anhänge hinzufügen
            if attachments:
                for attachment in attachments:
                    filepath = self.report_path / attachment
                    if filepath.exists():
                        with open(filepath, 'rb') as attachment_file:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment_file.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {attachment}'
                            )
                            msg.attach(part)
            
            # E-Mail senden
            server = smtplib.SMTP(
                email_config.get('smtp_server', 'smtp.gmail.com'),
                email_config.get('smtp_port', 587)
            )
            server.starttls()
            server.login(
                email_config.get('sender_email'),
                email_config.get('sender_password')
            )
            
            text = msg.as_string()
            server.sendmail(
                email_config.get('sender_email'),
                email_config.get('recipients', ['admin@cashmoneycolors.com']),
                text
            )
            server.quit()
            
            print(f"   ✅ E-Mail versendet an {len(email_config.get('recipients', []))} Empfänger")
            
        except Exception as e:
            log_event('EMAIL_SEND_ERROR', {
                'subject': subject,
                'error': str(e)
            })
            print(f"   ❌ Fehler beim Senden der E-Mail: {e}")
    
    def cleanup_old_reports(self):
        """Löscht alte Report-Dateien"""
        try:
            retention_days = self.report_config.get('RetentionDays', 30)
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            deleted_count = 0
            for filepath in self.report_path.glob('*'):
                if filepath.is_file():
                    file_time = datetime.fromtimestamp(filepath.stat().st_mtime)
                    if file_time < cutoff_date:
                        filepath.unlink()
                        deleted_count += 1
            
            print(f"🧹 {deleted_count} alte Report-Dateien bereinigt")
            
        except Exception as e:
            log_event('REPORT_CLEANUP_ERROR', {'error': str(e)})
            print(f"❌ Fehler bei der Bereinigung: {e}")
    
    def get_report_list(self) -> List[Dict]:
        """Gibt Liste der gespeicherten Reports zurück"""
        reports = []
        
        for filepath in self.report_path.glob('*'):
            if filepath.is_file():
                stat = filepath.stat()
                reports.append({
                    'filename': filepath.name,
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'path': str(filepath)
                })
        
        # Sortiere nach Erstellungsdatum
        reports.sort(key=lambda x: x['created'], reverse=True)
        return reports


# Globale Instanz
reporting_system = AutomatedReportingSystem()


# Convenience-Funktionen
def start_automated_reports():
    """Startet den automatisierten Report-Service"""
    reporting_system.start_scheduled_reports()

def stop_automated_reports():
    """Stoppt den automatisierten Report-Service"""
    reporting_system.stop_scheduled_reports()

def generate_manual_report(hours: int = 24, formats: List[str] = None) -> str:
    """Generiert manuellen Report"""
    return reporting_system.generate_on_demand_report(hours, formats)

def cleanup_reports():
    """Bereinigt alte Report-Dateien"""
    reporting_system.cleanup_old_reports()

def get_reports():
    """Gibt Liste der gespeicherten Reports zurück"""
    return reporting_system.get_report_list()


if __name__ == "__main__":
    print("CASH MONEY COLORS ORIGINAL (R) - AUTOMATED REPORTING SYSTEM")
    print("=" * 70)
    
    # Starte automatisierte Reports
    start_automated_reports()
    
    # Generiere manuellen Test-Report
    print("\n🧪 Generiere Test-Report...")
    test_report = generate_manual_report(1, ['json', 'html'])
    
    # Zeige verfügbare Reports
    print("\n📁 Verfügbare Reports:")
    reports = get_reports()
    for report in reports[:5]:  # Zeige nur die letzten 5
        print(f"   {report['filename']} ({report['created']})")
    
    print("\n✅ AUTOMATED REPORTING SYSTEM BEREIT")
    print("Verwende start_automated_reports() für kontinuierliche Berichterstattung")
    
    # Warte auf Benutzereingabe zum Beenden
    try:
        input("\nDrücken Sie Enter zum Beenden...")
    except KeyboardInterrupt:
        pass
    finally:
        stop_automated_reports()