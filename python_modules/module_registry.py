#!/usr/bin/env python3
"""
MODULE REGISTRY - Modul-Registrierung und -Verwaltung
"""

from typing import Dict, Any, Set
import logging

# Globale Modul-Registry
_module_registry: Set[str] = set()

def register_module(module_name: str, file_path: str = None):
    """Registriert ein Modul"""
    if module_name not in _module_registry:
        _module_registry.add(module_name)
        logging.info(f"Modul '{module_name}' registriert")

def get_registered_modules() -> Set[str]:
    """Gibt alle registrierten Module zurück"""
    return _module_registry.copy()

def is_module_registered(module_name: str) -> bool:
    """Prüft ob ein Modul registriert ist"""
    return module_name in _module_registry
