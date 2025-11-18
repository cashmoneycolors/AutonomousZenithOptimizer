#!/usr/bin/env python3
"""
MODULE UTILS - Dienstprogramme für Module
"""

import os
import logging

def check_env_vars(required_vars: list = None) -> list:
    """Prüft erforderliche Umgebungsvariablen"""
    if required_vars is None:
        required_vars = ['OPENAI_API_KEY', 'STRIPE_SECRET_KEY']

    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)

    return missing

def warn_if_demo_mode():
    """Warnt bei Demo-Modus"""
    if os.getenv('DEMO_MODE') == 'true':
        logging.warning("⚠️ SYSTEM LÄUFT IM DEMO-MODUS")

def get_env_config():
    """Holt Umgebungskonfiguration"""
    return {
        'demo_mode': os.getenv('DEMO_MODE', 'false') == 'true',
        'log_level': os.getenv('LOG_LEVEL', 'INFO'),
        'api_prefix': os.getenv('API_PREFIX', '/api')
    }
