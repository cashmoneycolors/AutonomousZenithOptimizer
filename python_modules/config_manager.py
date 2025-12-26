#!/usr/bin/env python3
"""
CASH MONEY COLORS ORIGINAL (R) - CONFIGURATION MANAGER
Konfigurationsverwaltung für das Performance Monitoring System
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """Konfigurationsmanager für das System"""
    
    def __init__(self):
        self.configs = {}
        self.config_file = Path("performance_config.json")
        self.load_configs()
    
    def load_configs(self):
        """Lädt Konfigurationen aus Datei"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.configs = json.load(f)
            except Exception as e:
                print(f"Fehler beim Laden der Konfiguration: {e}")
                self.configs = {}
    
    def save_configs(self):
        """Speichert Konfigurationen in Datei"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.configs, f, indent=2)
        except Exception as e:
            print(f"Fehler beim Speichern der Konfiguration: {e}")
    
    def get_config(self, section: str, default: Any = None) -> Any:
        """Holt Konfiguration für einen Abschnitt"""
        return self.configs.get(section, default)
    
    def set_config(self, section: str, config: Any):
        """Setzt Konfiguration für einen Abschnitt"""
        self.configs[section] = config
        self.save_configs()


# Globale Instanz
config_manager = ConfigManager()


def get_config(section: str, default: Any = None) -> Any:
    """Holt Konfiguration für einen Abschnitt"""
    return config_manager.get_config(section, default)


def get_rigs_config() -> list:
    """Holt Rig-Konfigurationen"""
    default_rigs = [
        {
            'id': 'rig_001',
            'name': 'Primary Mining Rig',
            'gpu_count': 8,
            'algorithm': 'ethash',
            'power_limit': 300
        },
        {
            'id': 'rig_002', 
            'name': 'Secondary Mining Rig',
            'gpu_count': 6,
            'algorithm': 'ethash',
            'power_limit': 250
        }
    ]
    
    rigs = get_config('MiningRigs', default_rigs)
    return rigs if rigs else default_rigs