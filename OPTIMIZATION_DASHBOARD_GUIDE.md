# Optimization Dashboard - Benutzerhandbuch

## Überblick

Das **Optimization Dashboard** ist das zentrale Aggregations- und Reporting-Modul für alle System-Optimierungen im Autonomous Zenith Optimizer. Es sammelt Metriken aus allen Optimierungsmodulen und generiert umfassende Berichte in mehreren Formaten.

## Features

### 🎯 Zentrale Aggregation
- **Predictive Maintenance**: Rig-Gesundheit, Ausfallvorhersagen, Wartungsempfehlungen
- **Energy Efficiency**: Stromverbrauch, Kosten, Einsparpotenziale
- **Temperature Optimization**: Übertaktungs-Aktionen, thermische Effizienz
- **Algorithm Switching**: Algorithmus-Wechsel, Profit-Verbesserungen

### 📊 Key Performance Indicators (KPIs)
- **Kosten-Metriken**: Tägliche/monatliche Betriebskosten, Einsparpotenziale
- **Effizienz-Metriken**: Durchschnittliche Effizienz, Stromverbrauch, Effizienzgewinne
- **Zuverlässigkeits-Metriken**: Überwachte Rigs, Datenpunkte, vorhergesagte Ausfälle
- **Optimierungs-Metriken**: Temperatur-Optimierungen, Algorithmus-Wechsel

### 📄 Export-Formate
1. **JSON**: Maschinenlesbar, ideal für weitere Verarbeitung
2. **HTML**: Visuell ansprechend mit modernem Design und Farbcodierung
3. **TXT**: Einfacher Text-Report für CLI/Terminal

### 🏥 System-Gesundheitsindex
Automatische Berechnung des Gesamt-System-Gesundheitsstatus:
- **Excellent** (90-100%): Alle Systeme optimal
- **Good** (75-89%): Geringfügige Optimierungen empfohlen
- **Fair** (50-74%): Mehrere Maßnahmen erforderlich
- **Poor** (<50%): Dringende Wartung notwendig

## Verwendung

### 1. Dashboard-Summary auf Konsole ausgeben
```python
from python_modules.optimization_dashboard import print_dashboard_summary

print_dashboard_summary()
```

**Output:**
```
================================================================================
📊 OPTIMIZATION DASHBOARD - LIVE SUMMARY
================================================================================

🏥 System-Gesundheit: GOOD

💰 Kosten:
   Täglich:  CHF 39.12
   Ersparnis (Potenzial): CHF 0.72/Tag

⚡ Effizienz:
   Durchschnitt: 67.4%
   Stromverbrauch: 8150 W

🔧 Predictive Maintenance:
   Überwacht: 6 Rigs
   Risiko: 0 | Kritisch: 0

💡 Empfehlungen: 2
   [MEDIUM] Energie-Effizienz-Optimierung durchführen...
   [LOW] Temperatur-basierte Übertaktung aktivieren...
```

### 2. Vollständigen Report generieren
```python
from python_modules.optimization_dashboard import generate_optimization_report

report = generate_optimization_report()

# Report enthält:
# - report_metadata: Metadaten (Zeitstempel, Version, Uptime)
# - summary: Zusammenfassung aller Module
# - key_performance_indicators: Detaillierte KPIs
# - module_metrics: Rohdaten aus allen Modulen
# - recommendations: Priorisierte Handlungsempfehlungen
# - alerts: Aktive kritische Warnungen
```

### 3. Report exportieren
```python
from python_modules.optimization_dashboard import export_optimization_report

# Alle konfigurierten Formate exportieren
exported_files = export_optimization_report()

# Oder spezifische Formate
exported_files = export_optimization_report(['json', 'html'])

# Ausgabe: Liste von Dateipfaden
# ['optimization_reports/optimization_report_20251116_072304.json',
#  'optimization_reports/optimization_report_20251116_072304.html']
```

### 4. Nur Metriken sammeln
```python
from python_modules.optimization_dashboard import get_all_metrics

metrics = get_all_metrics()

# Zugriff auf spezifische Module:
pm_metrics = metrics['modules']['predictive_maintenance']
ee_metrics = metrics['modules']['energy_efficiency']
to_metrics = metrics['modules']['temperature_optimization']
alg_metrics = metrics['modules']['algorithm_switching']
```

## Konfiguration

In `settings.json` unter `"OptimizationDashboard"`:

```json
{
  "OptimizationDashboard": {
    "ExportPath": "optimization_reports",
    "AutoExportEnabled": true,
    "ExportIntervalHours": 24,
    "IncludeCharts": true,
    "ReportFormats": ["json", "html", "txt"]
  }
}
```

### Parameter
- **ExportPath**: Verzeichnis für exportierte Reports (Standard: `optimization_reports`)
- **AutoExportEnabled**: Automatischer Export aktiviert (Standard: `true`)
- **ExportIntervalHours**: Intervall für Auto-Export in Stunden (Standard: 24)
- **IncludeCharts**: Charts in HTML-Reports (zukünftig, Standard: `true`)
- **ReportFormats**: Liste der Export-Formate (Standard: `["json", "html", "txt"]`)

## Report-Struktur

### JSON-Report
```json
{
  "report_metadata": {
    "generated_at": "2025-11-16T07:23:04.197275",
    "report_type": "comprehensive_optimization",
    "version": "1.0.0",
    "uptime_hours": 0.01
  },
  "summary": {
    "predictive_maintenance": {
      "rigs_at_risk": 0,
      "critical_rigs": 0,
      "total_monitored": 6
    },
    "energy_efficiency": {
      "potential_savings_daily": 0.72,
      "current_daily_cost": 39.12,
      "avg_efficiency": 0.148
    },
    "overall_system_health": "good"
  },
  "key_performance_indicators": { ... },
  "module_metrics": { ... },
  "recommendations": [ ... ],
  "alerts": [ ... ]
}
```

### HTML-Report
Moderner, responsiver HTML-Report mit:
- Gradient-Hintergrund (Lila/Violett-Theme)
- KPI-Grid mit Card-Design
- Farbcodierte Empfehlungen (Critical=Rot, High=Orange, Medium=Gelb)
- Gesundheits-Badges (Excellent=Grün, Good=Blau, Fair=Gelb, Poor=Rot)
- Übersichtliche Tabellen und Sektionen

### Text-Report
Strukturierter ASCII-Report für CLI:
```
================================================================================
CASH MONEY COLORS ORIGINAL (R) - OPTIMIZATION DASHBOARD
Comprehensive System Report
================================================================================

Generiert: 2025-11-16T07:23:04.197275
Uptime: 0.01 Stunden
System-Gesundheit: GOOD

================================================================================
KEY PERFORMANCE INDICATORS
================================================================================
...
```

## Empfehlungs-Priorisierung

Das Dashboard generiert automatisch priorisierte Handlungsempfehlungen:

### CRITICAL
- Rigs mit **kritischem Risiko-Level**
- Sofortige Maßnahmen erforderlich
- Geschätzte Ausfallzeit: 4 Stunden

### HIGH
- Rigs mit **hohem Risiko-Level**
- Wartung innerhalb 7 Tagen
- Geschätzte Ausfallzeit: 2 Stunden

### MEDIUM
- Energie-Effizienz unter 80%
- Monatliche Einsparpotenziale verfügbar

### LOW
- Präventive Maßnahmen
- Langfristige Optimierungen

## Integration in bestehende Workflows

### Täglicher Auto-Report
```python
import schedule
from python_modules.optimization_dashboard import export_optimization_report

def daily_report():
    export_optimization_report(['json', 'html', 'txt'])

# Jeden Tag um 06:00 Uhr
schedule.every().day.at("06:00").do(daily_report)
```

### Webhook-Integration
```python
import requests
from python_modules.optimization_dashboard import generate_optimization_report

report = generate_optimization_report()

# Sende an Monitoring-Service
requests.post('https://your-monitoring-service.com/webhook', json=report)
```

### Slack/Teams-Benachrichtigung
```python
from python_modules.optimization_dashboard import generate_optimization_report
from python_modules.alert_system import send_custom_alert

report = generate_optimization_report()
summary = report['summary']

# Kritische Alerts
if summary['predictive_maintenance']['critical_rigs'] > 0:
    send_custom_alert(
        "Kritische Wartung erforderlich",
        f"{summary['predictive_maintenance']['critical_rigs']} Rig(s) benötigen sofortige Wartung!",
        "[CRITICAL]"
    )
```

## Best Practices

### 1. Regelmäßige Berichte
Exportiere mindestens täglich Reports für historische Nachverfolgung.

### 2. Empfehlungen umsetzen
Priorisiere Empfehlungen nach Impact und Dringlichkeit:
- CRITICAL: Sofort
- HIGH: Innerhalb 1 Woche
- MEDIUM: Innerhalb 1 Monat
- LOW: Bei nächster geplanter Wartung

### 3. Trend-Analyse
Vergleiche tägliche Reports, um Trends zu erkennen:
- Steigende Betriebskosten
- Sinkende Effizienz
- Zunehmende Wartungsanforderungen

### 4. Backup
Sichere exportierte Reports regelmäßig:
```bash
# Windows
xcopy optimization_reports backups\reports /E /I /Y

# Linux/Mac
cp -r optimization_reports backups/reports/
```

## Troubleshooting

### "Modul nicht verfügbar"-Fehler
Falls ein Optimierungsmodul nicht verfügbar ist:
1. Überprüfe `settings.json` Konfiguration
2. Stelle sicher, dass alle Abhängigkeiten installiert sind
3. Prüfe Logs in `logs/` Verzeichnis

### Fehlende Daten
Wenn Metriken leer sind:
1. Rigs müssen mindestens 24h laufen für aussagekräftige Daten
2. Predictive Maintenance benötigt historische Daten
3. Starte Monitoring-Dienste: `start_predictive_monitoring()`, `start_algorithm_monitoring()`

### Export-Fehler
Bei Export-Fehlern:
1. Überprüfe Schreibrechte für `ExportPath`
2. Stelle sicher, dass Verzeichnis existiert (wird automatisch erstellt)
3. Prüfe Festplatten-Speicherplatz

## Changelog

### v1.0.0 (2025-11-16)
- Initial Release
- JSON/HTML/TXT Export
- 4 Optimierungs-Module integriert
- KPI-Berechnung
- Empfehlungs-Engine
- System-Gesundheitsindex

## Weitere Module (geplant)

Zukünftige Integrationen:
- **Real-time Market Feed**: Live-Preisdaten in Reports
- **Risk Management**: Diversifikations-Metriken
- **Mining Pool Analytics**: Pool-Performance-Vergleiche
- **Cloud Auto-Scaling**: Ressourcen-Optimierung
- **Charts & Grafiken**: Visualisierungen in HTML-Reports
- **PDF-Export**: Professionelle PDF-Reports
- **API-Endpunkt**: RESTful API für externe Tools

---

**CASH MONEY COLORS ORIGINAL (R)** - Optimization Dashboard v1.0.0
