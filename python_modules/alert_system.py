#!/usr/bin/env python3
"""
CASH MONEY COLORS ORIGINAL (R) - ALERT SYSTEM
Alert-System für das Performance Monitoring System
"""

from typing import Dict, Any


class AlertSystem:
    """Alert-System für kritische Ereignisse"""
    
    def __init__(self):
        self.alerts = []
    
    def send_custom_alert(self, alert_type: str, severity: str, message: str, source: str = "System"):
        """Sendet einen benutzerdefinierten Alert"""
        alert = {
            'type': alert_type,
            'severity': severity,
            'message': message,
            'source': source
        }
        self.alerts.append(alert)
        print(f"ALERT [{severity}]: {message} (Source: {source})")


# Globale Instanz
alert_system = AlertSystem()


def send_custom_alert(alert_type: str, severity: str, message: str, source: str = "System"):
    """Sendet einen benutzerdefinierten Alert"""
    alert_system.send_custom_alert(alert_type, severity, message, source)