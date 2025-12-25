# Mining Optimization Integration für A.Z.O.

## Übersicht

Das Mining Optimization System ist jetzt vollständig in das A.Z.O. (Autonomous Zenith Optimizer) .NET System integriert.

## Architektur

### Komponenten

1. **MiningOptimizationHostedService.cs** (.NET Background Service)
   - Läuft als BackgroundService im Hintergrund
   - Führt periodisch Python-basierte Mining-Optimierungen aus
   - Cached die Ergebnisse in Redis/Mock-Cache

2. **mining_optimization_dashboard.py** (Python Optimization Script)
   - Analysiert Mining-Sessions
   - Generiert Optimization-Reports als JSON
   - Nutzt AlgorithmOptimizer und MarketIntegration

3. **OptimizerSettings** (Konfiguration)
   - `EnableMiningOptimization`: Service ein/aus (Standard: false)
   - `MiningOptimizationIntervalSeconds`: Intervall zwischen Optimierungen (Standard: 300s = 5 Min)
   - `PythonExecutablePath`: Pfad zum Python Executable (Standard: "python")

## Verwendung

### 1. Service aktivieren

In `appsettings.json`:

```json
{
  "Optimizer": {
    "EnableMiningOptimization": true,
    "MiningOptimizationIntervalSeconds": 300,
    "PythonExecutablePath": "python"
  }
}
```

### 2. Service starten

Der Service startet automatisch mit dem A.Z.O. Host:

```bash
dotnet run --project ZenithCoreSystem.csproj
```

### 3. Optimization-Daten abrufen

Die Optimization-Reports werden im Cache gespeichert:

```csharp
// Über HoloKognitivesRepository
var report = await cache.GetAsync("mining:optimization:report");
var timestamp = await cache.GetAsync("mining:optimization:timestamp");
var totalProfit = await cache.GetAsync("mining:optimization:total_profit");
var bestAlgorithm = await cache.GetAsync("mining:optimization:best_algorithm");
```

## Datenfluss

1. **MiningOptimizationHostedService** wacht auf nach Intervall
2. Service startet Python-Prozess: `python mining_optimization_dashboard.py`
3. Python-Script analysiert Mining-Sessions und erstellt `mining_optimization_report.json`
4. Service liest JSON-Report und cached die Daten in Redis
5. Andere A.Z.O. Komponenten können auf die Optimization-Daten zugreifen

## Cached Keys

- `mining:optimization:report` - Vollständiger JSON-Report
- `mining:optimization:timestamp` - Zeitstempel der letzten Optimierung
- `mining:optimization:total_profit` - Gesamtprofit
- `mining:optimization:best_algorithm` - Bester Mining-Algorithmus
- `mining:optimization:last_run` - Raw Python Output (Fallback)

## Monitoring

Der Service loggt alle Aktionen mit Microsoft.Extensions.Logging:

```
[07:10:57] Mining Optimization Service gestartet - Intervall: 300s
[07:10:57] Starte Mining Optimization Zyklus...
[07:10:57] Python Optimization erfolgreich abgeschlossen
[07:10:57] Optimization Report erfolgreich im Cache gespeichert
```

## Python Dependencies

Das Optimization-Script benötigt:
- `algorithm_optimizer.py`
- `market_integration.py`
- Optionale Mining-Session-Daten: `mining_session_1_export.json`

Falls Module fehlen, läuft das Script im "minimal mode" und gibt trotzdem einen gültigen Report zurück.

## Troubleshooting

### Service läuft nicht

Prüfe in der Console:
```
Mining Optimization Service ist deaktiviert (siehe appsettings.json)
```
→ Setze `EnableMiningOptimization: true` in appsettings.json

### Python-Script nicht gefunden

```
Python Optimization Script nicht gefunden: [Pfad]
```
→ Stelle sicher, dass `python_modules/mining_optimization_dashboard.py` existiert

### Python-Fehler

```
Python Optimization fehlgeschlagen (Exit Code: 1)
```
→ Prüfe Python-Installation und Dependencies
→ Teste manuell: `python python_modules/mining_optimization_dashboard.py`

## Erweiterung

Um eigene Metriken zu cachen, erweitere `CacheOptimizationResults()` in `MiningOptimizationHostedService.cs`:

```csharp
if (report.RootElement.TryGetProperty("my_metric", out var metric))
{
    await _db.StringSetAsync("mining:optimization:my_metric", 
        metric.ToString(), 
        TimeSpan.FromHours(1));
}
```

## Sicherheit

- Python-Prozess läuft mit denselben Rechten wie der A.Z.O. Host
- Keine Shell-Ausführung (`UseShellExecute = false`)
- Output-Redirects verhindern UI-Pop ups
- Timeouts über CancellationToken

## Performance

- Standard-Intervall: 5 Minuten (konfigurierbar)
- Python-Prozess läuft asynchron
- Keine Blockierung des Hauptsystems
- Cache-TTL: 1 Stunde
