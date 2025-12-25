# Mining Hardware Adapter - Dokumentation

## Übersicht

Der **Mining Hardware Adapter** ermöglicht echte Hardware-Steuerung für Mining-Rigs über NVIDIA GPUs. Dies ersetzt die bisherige Simulation durch tatsächliche Befehle an die Hardware.

## Komponenten

### 1. `mining_hardware_adapter.py`
Kern-Adapter für direkte GPU-Steuerung via nvidia-smi

**Hauptfunktionen:**
- `set_power_limit(gpu_index, power_watts)` - Setzt Power Limit
- `set_fan_speed(gpu_index, fan_percent)` - Steuert Lüftergeschwindigkeit
- `get_gpu_stats(gpu_index)` - Liest GPU-Statistiken
- `optimize_for_temperature(gpu_index, target_temp)` - Automatische Temperatur-Optimierung
- `apply_mining_profile(gpu_index, profile)` - Vordefinierte Profile (efficiency/balanced/performance)

### 2. `hardware_integration.py`
Integration-Layer zwischen Adapter und bestehendem System

**Hauptfunktionen:**
- `handle_mining_power_limit_event()` - Behandelt Power Limit Events
- `handle_fan_speed_event()` - Behandelt Lüfter Events
- `apply_profile_to_rig()` - Wendet Profile auf Rigs an

### 3. `rig_gpu_mapper.py` ⭐ NEU
Mapping-System für Rig-IDs zu GPU-Indizes

**Hauptfunktionen:**
- `get_gpu_index(rig_id)` - Ermittelt GPU-Index für Rig
- `add_mapping(rig_id, gpu_index)` - Fügt Mapping hinzu
- `list_mappings()` - Zeigt alle Mappings

**Konfiguration:**
```json
{
  "version": "1.0",
  "rig_to_gpu": {
    "RIG_001": 0,
    "RIG_002": 1,
    "RIG_003": 2
  }
}
```

## Voraussetzungen

### Software:
- **Python 3.14+** (erforderlich)
- NVIDIA GPU Treiber (für echte Hardware-Steuerung)

### NVIDIA GPUs (erforderlich für echte Steuerung):
```bash
# nvidia-smi muss verfügbar sein
nvidia-smi --version

# Für Fan Control (optional):
sudo apt-get install nvidia-settings
```

### Berechtigungen:
```bash
# nvidia-smi benötigt ggf. Root-Rechte für Power Limit:
sudo chmod +s /usr/bin/nvidia-smi

# Oder per sudoers (empfohlen):
# Füge hinzu: username ALL=(ALL) NOPASSWD: /usr/bin/nvidia-smi
```

## Verwendung

### Standalone-Test

```bash
# Test des Hardware-Adapters
cd python_modules
python3 mining_hardware_adapter.py

# Test der Integration
python3 hardware_integration.py
```

### Programmatische Verwendung

```python
from mining_hardware_adapter import get_hardware_adapter

# Adapter initialisieren
adapter = get_hardware_adapter()

# GPU 0: Power Limit auf 180W setzen
adapter.set_power_limit(0, 180)

# GPU 0: Lüfter auf 75% setzen
adapter.set_fan_speed(0, 75)

# Aktuelle Stats abrufen
stats = adapter.get_gpu_stats(0)
print(f"Temperatur: {stats['temperature']}°C")
print(f"Power Draw: {stats['power_draw']}W")

# Balanced-Profil anwenden
adapter.apply_mining_profile(0, "balanced")
```

### Integration mit Temperature Optimizer

```python
from hardware_integration import (
    handle_mining_power_limit_event,
    handle_fan_speed_event
)

# Event vom Temperature Optimizer verarbeiten
result = handle_mining_power_limit_event(
    rig_id="RIG_001",
    temperature=75.0,
    power_limit=180
)

if result['success']:
    print(f"Power Limit erfolgreich auf {result['power_limit']}W gesetzt")
```

## Mining-Profile

### Efficiency (Effizienz)
- Power Limit: 65% des Defaults
- Lüfter: 60%
- Ideal für: Niedriger Stromverbrauch, kühler Betrieb

### Balanced (Ausgewogen) - Default
- Power Limit: 80% des Defaults  
- Lüfter: 70%
- Ideal für: Bester Profit/Watt-Ratio

### Performance (Leistung)
- Power Limit: 95% des Defaults
- Lüfter: 85%
- Ideal für: Maximale Hashrate

## Beispiel-Szenarien

### Szenario 1: Automatische Temperatur-Regelung

```python
from mining_hardware_adapter import get_hardware_adapter

adapter = get_hardware_adapter()

# Optimiere alle GPUs für 70°C Zieltemperatur
for gpu in adapter.available_gpus:
    result = adapter.optimize_for_temperature(gpu['index'], target_temp=70)
    print(f"GPU {gpu['index']}: {result['actions']}")
```

### Szenario 2: Notfall-Abschaltung bei Überhitzung

```python
from mining_hardware_adapter import get_hardware_adapter

adapter = get_hardware_adapter()

for gpu in adapter.available_gpus:
    stats = adapter.get_gpu_stats(gpu['index'])
    
    if stats['temperature'] > 85:
        # Kritisch! Reduziere Power drastisch
        adapter.set_power_limit(gpu['index'], 100)  # Minimum
        adapter.set_fan_speed(gpu['index'], 100)    # Maximum
        print(f"⚠️ GPU {gpu['index']} ÜBERHITZT - Notfall-Drosselung aktiv!")
```

### Szenario 3: Nacht-Modus (leise)

```python
from mining_hardware_adapter import get_hardware_adapter

adapter = get_hardware_adapter()

# Wende Efficiency-Profil für leisen Betrieb an
for gpu in adapter.available_gpus:
    adapter.apply_mining_profile(gpu['index'], "efficiency")
    print(f"GPU {gpu['index']}: Nacht-Modus aktiviert")
```

## Simulation vs. Hardware-Modus

Der Adapter erkennt automatisch, ob NVIDIA GPUs verfügbar sind:

- **Hardware-Modus**: nvidia-smi verfügbar und GPUs erkannt
  - Echte Befehle werden ausgeführt
  - `success=True` bei erfolgreicher Steuerung
  
- **Simulations-Modus**: Keine GPUs verfügbar
  - Befehle werden nur geloggt
  - `success=False`, `hardware_mode=False`
  - Ideal für Entwicklung ohne Mining-Hardware

## Logging

Alle Hardware-Aktionen werden geloggt in:
- **mining_hardware.log** - Hardware-Adapter Log
- Systemweites Logging über `logging` Modul

```python
# Log-Beispiele:
# INFO - GPU erkannt: NVIDIA GeForce RTX 3080 (Index 0)
# INFO - GPU 0: Power Limit auf 200W gesetzt
# INFO - GPU 0: Profil 'balanced' angewendet
# ERROR - GPU 0: Power Limit Fehler - Permission denied
```

## Fehlerbehebung

### "nvidia-smi nicht verfügbar"
```bash
# NVIDIA Driver installieren
sudo apt-get install nvidia-driver-525
sudo reboot

# Testen
nvidia-smi
```

### "Permission denied" bei Power Limit
```bash
# Temporär (benötigt sudo):
sudo python3 mining_hardware_adapter.py

# Permanent (empfohlen):
sudo visudo
# Füge hinzu: username ALL=(ALL) NOPASSWD: /usr/bin/nvidia-smi
```

### "nvidia-settings nicht verfügbar" bei Fan Control
```bash
# Installiere nvidia-settings
sudo apt-get install nvidia-settings

# Für Headless-Server (ohne X11):
# Fan Control funktioniert nur mit aktivem X Server
# Alternative: NVIDIA Management Library (NVML) via pynvml
```

## API-Referenz

### MiningHardwareAdapter

#### `__init__(log_file: str = "mining_hardware.log")`
Initialisiert den Adapter und erkennt GPUs.

#### `detect_gpus() -> List[Dict[str, Any]]`
Erkennt alle verfügbaren NVIDIA GPUs.

**Returns:**
```python
[
    {
        'index': 0,
        'name': 'NVIDIA GeForce RTX 3080',
        'memory_mb': 10240,
        'current_power_limit': 320,
        'default_power_limit': 320,
        'fan_speed': 70,
        'temperature': 65,
        'vendor': 'NVIDIA'
    }
]
```

#### `set_power_limit(gpu_index: int, power_watts: int) -> bool`
Setzt Power Limit für eine GPU.

**Args:**
- `gpu_index`: GPU Index (0, 1, 2, ...)
- `power_watts`: Power Limit in Watt

**Returns:** `True` bei Erfolg, `False` bei Fehler

**Beispiel:**
```python
adapter.set_power_limit(0, 200)  # GPU 0 auf 200W
```

#### `get_gpu_stats(gpu_index: int) -> Optional[Dict[str, Any]]`
Liest aktuelle GPU-Statistiken.

**Returns:**
```python
{
    'index': 0,
    'temperature': 67,
    'power_draw': 195.5,
    'fan_speed': 72,
    'utilization': 98,
    'memory_used_mb': 8192,
    'memory_total_mb': 10240,
    'timestamp': '2025-12-23T22:00:00'
}
```

## Sicherheitshinweise

1. **Überwachung**: Überwache immer die Temperaturen beim Ändern von Power Limits
2. **Schrittweise Änderungen**: Ändere Power Limits in kleinen Schritten (10-20W)
3. **Backup-Profile**: Speichere funktionierende Konfigurationen
4. **Grenzwerte**: Überschreite nie die vom Hersteller empfohlenen Werte
5. **Lüftersteuerung**: Automatischer Lüfter-Modus ist oft sicherer als manuell

## Support & Weiterentwicklung

Geplante Features:
- [ ] AMD GPU Support via ROCm
- [ ] Web-Dashboard für Remote-Steuerung
- [ ] Automatische Profil-Umschaltung basierend auf Strompreis
- [ ] Integration mit Mining-Pool APIs
- [ ] Machine Learning für optimale Settings

## Lizenz

CASH MONEY COLORS ORIGINAL (R) - Alle Rechte vorbehalten
