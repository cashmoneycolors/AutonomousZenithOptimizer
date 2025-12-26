#!/usr/bin/env python3
"""
CASH MONEY COLORS ORIGINAL (R) - ENHANCED LOGGING SYSTEM
Erweiterte Logging-Funktionalität für das Performance Monitoring System
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class EnhancedLogger:
    """Erweiterte Logging-Klasse"""
    
    def __init__(self):
        self.log_file = Path("performance_monitoring.log")
        self.setup_logging()
    
    def setup_logging(self):
        """Richtet das Logging ein"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('PerformanceMonitoring')
    
    def log_event(self, event_type: str, data: Dict[str, Any]):
        """Loggt ein Event mit strukturierten Daten"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'data': data
        }
        
        self.logger.info(f"EVENT: {json.dumps(log_entry)}")


# Globale Instanz
enhanced_logger = EnhancedLogger()


def log_event(event_type: str, data: Dict[str, Any]):
    """Loggt ein Event"""
    enhanced_logger.log_event(event_type, data)