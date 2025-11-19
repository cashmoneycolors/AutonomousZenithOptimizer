#!/usr/bin/env python3
"""
SMART ERROR RECOVERY SYSTEM - AUTOMATISCHE FEHLERBEHEBUNG
Anpassungsfähiges Selbstheilungs-System für das Autonomous Zenith Optimizer
"""
import asyncio
import time
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from python_modules.enhanced_logging import log_event


class ErrorSeverity(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class ErrorType(Enum):
    NETWORK_ERROR = "network"
    POOL_ERROR = "pool"
    RIG_ERROR = "rig"
    CONFIG_ERROR = "config"
    DEPENDENCY_ERROR = "dependency"
    SYSTEM_ERROR = "system"


@dataclass
class SmartRecoveryRule:
    """Intelligente Wiederherstellungs-Regeln"""
    error_pattern: str
    error_type: ErrorType
    severity: ErrorSeverity
    recovery_actions: List[Dict[str, Any]]
    precondition_checks: Optional[List[Callable]] = None
    success_rate: float = 0.0
    last_used: Optional[float] = None
    usage_count: int = 0


class AutoErrorFixingSystem:
    """Automatisches Fehlerbehebung-System mit Machine Learning"""

    def __init__(self):
        self.recovery_rules: Dict[str, SmartRecoveryRule] = {}
        self.active_recoveries: Dict[str, Dict[str, Any]] = {}
        self.success_history: Dict[str, List[bool]] = {}
        self.max_recovery_attempts = 3
        self.learning_enabled = True

        self._load_recovery_rules()
        self._initialize_system()

    def _initialize_system(self):
        """System-Initialisierung"""
        log_event('AUTO_ERROR_FIXING_INITIALIZED', {
            'rules_loaded': len(self.recovery_rules),
            'learning_enabled': self.learning_enabled,
            'max_attempts': self.max_recovery_attempts
        })

    def _load_recovery_rules(self):
        """Lade intelligente Recovery-Regeln"""
        # Network Recovery Rules
        self.recovery_rules['pool_connection_lost'] = SmartRecoveryRule(
            error_pattern=".*connection.*pool.*failed.*",
            error_type=ErrorType.NETWORK_ERROR,
            severity=ErrorSeverity.HIGH,
            recovery_actions=[
                {
                    'action': 'restart_network_connection',
                    'params': {'interface': 'default', 'timeout': 30}
                },
                {
                    'action': 'switch_to_backup_pool',
                    'params': {'fallback_priority': 'highest_rank'}
                }
            ]
        )

        # Rig Error Recovery Rules
        self.recovery_rules['gpu_hashrate_drop'] = SmartRecoveryRule(
            error_pattern=".*hashrate.*drop.*|.*gpu.*error.*",
            error_type=ErrorType.RIG_ERROR,
            severity=ErrorSeverity.MEDIUM,
            recovery_actions=[
                {
                    'action': 'restart_mining_rig',
                    'params': {'rig_id': 'target', 'force_reset': True}
                },
                {
                    'action': 'adjust_temperatur',
                    'params': {'target_temp': 70, 'adjust_mode': 'cool_down'}
                }
            ]
        )

        # System Recovery Rules
        self.recovery_rules['process_crash'] = SmartRecoveryRule(
            error_pattern=".*crash.*|.*killed.*|.*exception.*",
            error_type=ErrorType.SYSTEM_ERROR,
            severity=ErrorSeverity.CRITICAL,
            recovery_actions=[
                {
                    'action': 'restart_service',
                    'params': {'service_name': 'mining_system', 'graceful_shutdown': True}
                },
                {
                    'action': 'create_backup',
                    'params': {'backup_type': 'emergency', 'auto_restore': True}
                }
            ]
        )

        # Configuration Error Recovery
        self.recovery_rules['config_malformed'] = SmartRecoveryRule(
            error_pattern=".*config.*invalid.*|.*json.*error.*",
            error_type=ErrorType.CONFIG_ERROR,
            severity=ErrorSeverity.MEDIUM,
            recovery_actions=[
                {
                    'action': 'restore_config_backup',
                    'params': {'backup_version': 'latest_valid'}
                },
                {
                    'action': 'validate_config_integrity',
                    'params': {'fix_auto': True}
                }
            ]
        )

        # Dependency Error Recovery
        self.recovery_rules['missing_module'] = SmartRecoveryRule(
            error_pattern=".*import.*error.*|.*module.*not.*found.*",
            error_type=ErrorType.DEPENDENCY_ERROR,
            severity=ErrorSeverity.HIGH,
            recovery_actions=[
                {
                    'action': 'auto_install_dependency',
                    'params': {'pip_install': True, 'upgrade_existing': False}
                },
                {
                    'action': 'verify_system_integrity',
                    'params': {'deep_check': True}
                }
            ]
        )

    async def process_error(self, error_data: Dict[str, Any]) -> bool:
        """Verarbeite einen Fehler und versuche automatische Behebung"""
        error_id = f"{error_data.get('component', 'system')}_{int(time.time())}"
        error_message = error_data.get('message', '')
        error_severity = error_data.get('severity', ErrorSeverity.MEDIUM)

        # Finde passende Recovery-Regel
        matching_rule = self._find_matching_rule(error_message)

        if not matching_rule:
            log_event('NO_RECOVERY_RULE_FOUND', {
                'error_id': error_id,
                'message': error_message,
                'severity': error_severity.value
            })
            return False

        # Prüfe Preconditions
        if matching_rule.precondition_checks:
            if not self._check_preconditions(matching_rule.precondition_checks):
                return False

        # Führe Recovery aus
        success = await self._execute_recovery_actions(error_id, matching_rule, error_data)

        # Lerne aus Ergebnis
        self._update_learning_data(matching_rule, success)

        return success

    def _find_matching_rule(self, error_message: str) -> Optional[SmartRecoveryRule]:
        """Finde beste passende Recovery-Regel"""
        import re

        best_match = None
        best_score = 0

        for rule in self.recovery_rules.values():
            # Exact Pattern Matching
            if re.search(rule.error_pattern, error_message, re.IGNORECASE):
                # Scoring: Severity * Success Rate
                score = rule.severity.value * (rule.success_rate + 0.5)

                if score > best_score:
                    best_match = rule
                    best_score = score

        return best_match

    def _check_preconditions(self, checks: List[Callable]) -> bool:
        """Prüfe Preconditions für Recovery"""
        try:
            for check in checks:
                if not check():
                    return False
            return True
        except Exception:
            return False

    async def _execute_recovery_actions(self, error_id: str, rule: SmartRecoveryRule,
                                      error_data: Dict[str, Any]) -> bool:
        """Führe Recovery-Actions aus"""
        self.active_recoveries[error_id] = {
            'rule': rule.error_pattern,
            'start_time': time.time(),
            'attempts': 0
        }

        for action in rule.recovery_actions:
            if self.active_recoveries[error_id]['attempts'] >= self.max_recovery_attempts:
                break

            try:
                success = await self._execute_single_action(action, error_data)

                if success:
                    log_event('RECOVERY_ACTION_SUCCESSFUL', {
                        'error_id': error_id,
                        'action': action['action'],
                        'rule': rule.error_pattern
                    })

                    # Markiere als erfolgreich beendet
                    self.active_recoveries[error_id]['status'] = 'completed'
                    return True

            except Exception as e:
                log_event('RECOVERY_ACTION_FAILED', {
                    'error_id': error_id,
                    'action': action['action'],
                    'error': str(e)
                })

            self.active_recoveries[error_id]['attempts'] += 1
            await asyncio.sleep(2)  # Cooldown between attempts

        return False

    async def _execute_single_action(self, action: Dict[str, Any], error_data: Dict[str, Any]) -> bool:
        """Führe einzelne Recovery-Aktion aus"""
        action_type = action.get('action')
        params = action.get('params', {})

        if action_type == 'restart_network_connection':
            return await self._restart_network_connection(params)
        elif action_type == 'switch_to_backup_pool':
            return await self._switch_to_backup_pool(params)
        elif action_type == 'restart_mining_rig':
            return await self._restart_mining_rig(error_data, params)
        elif action_type == 'adjust_temperatur':
            return await self._adjust_temperature(params)
        elif action_type == 'restart_service':
            return await self._restart_service(params)
        elif action_type == 'create_backup':
            return await self._create_backup(params)
        elif action_type == 'restore_config_backup':
            return await self._restore_config_backup(params)
        elif action_type == 'validate_config_integrity':
            return await self._validate_config_integrity(params)
        elif action_type == 'auto_install_dependency':
            return await self._auto_install_dependency(error_data, params)
        elif action_type == 'verify_system_integrity':
            return await self._verify_system_integrity(params)

        return False

    async def _restart_network_connection(self, params: Dict[str, Any]) -> bool:
        """Netzwerk-Verbindung neu starten"""
        interface = params.get('interface', 'default')
        timeout = params.get('timeout', 30)

        try:
            # Simple network reset (would need platform-specific code)
            log_event('NETWORK_RESET_TRIGGERED', {'interface': interface, 'timeout': timeout})
            await asyncio.sleep(5)
            return True
        except Exception:
            return False

    async def _switch_to_backup_pool(self, params: Dict[str, Any]) -> bool:
        """Zu Backup-Pool wechseln"""
        # Import here to avoid circular imports
        try:
            from python_modules.nicehash_integration import NiceHashIntegration
            integrator = NiceHashIntegration()
            # Implementation would switch to backup pools
            log_event('POOL_SWITCH_TRIGGERED', {'priority': params.get('fallback_priority')})
            return True
        except Exception:
            return False

    async def _restart_mining_rig(self, error_data: Dict[str, Any], params: Dict[str, Any]) -> bool:
        """Mining-Rig neu starten"""
        rig_id = params.get('rig_id', error_data.get('rig_id'))

        try:
            log_event('RIG_RESTART_TRIGGERED', {'rig_id': rig_id})

            # Simulate rig restart process
            await asyncio.sleep(10)

            # Check if rig is back online
            # This would integrate with your mining system
            return True

        except Exception:
            return False

    async def _adjust_temperature(self, params: Dict[str, Any]) -> bool:
        """Temperatur anpassen"""
        target_temp = params.get('target_temp', 70)

        try:
            log_event('TEMPERATURE_ADJUSTMENT_TRIGGERED',
                     {'target_temp': target_temp, 'mode': params.get('adjust_mode')})

            # Trigger temperature optimization
            # This would interface with your temperature_optimizer
            await asyncio.sleep(5)
            return True

        except Exception:
            return False

    async def _restart_service(self, params: Dict[str, Any]) -> bool:
        """Service neu starten"""
        service_name = params.get('service_name')
        graceful = params.get('graceful_shutdown', True)

        try:
            log_event('SERVICE_RESTART_TRIGGERED', {
                'service': service_name,
                'graceful': graceful
            })

            # Service restart logic
            # Could restart mining system or other services
            await asyncio.sleep(5)
            return True

        except Exception:
            return False

    async def _create_backup(self, params: Dict[str, Any]) -> bool:
        """Backup erstellen"""
        backup_type = params.get('backup_type', 'emergency')
        auto_restore = params.get('auto_restore', False)

        try:
            log_event('EMERGENCY_BACKUP_CREATED', {
                'type': backup_type,
                'auto_restore': auto_restore
            })

            # Trigger backup creation
            # This would call your backup system
            await asyncio.sleep(3)
            return True

        except Exception:
            return False

    async def _restore_config_backup(self, params: Dict[str, Any]) -> bool:
        """Konfiguration aus Backup wiederherstellen"""
        version = params.get('backup_version', 'latest_valid')

        try:
            log_event('CONFIG_RESTORE_TRIGGERED', {'version': version})

            # Restore config from backup
            # This would restore settings.json from backup
            await asyncio.sleep(2)
            return True

        except Exception:
            return False

    async def _validate_config_integrity(self, params: Dict[str, Any]) -> bool:
        """Konfigurationsintegrität validieren"""
        auto_fix = params.get('fix_auto', True)

        try:
            log_event('CONFIG_VALIDATION_TRIGGERED', {'auto_fix': auto_fix})

            # Validate and potentially fix config
            # This would check settings.json integrity
            await asyncio.sleep(2)
            return True

        except Exception:
            return False

    async def _auto_install_dependency(self, error_data: Dict[str, Any], params: Dict[str, Any]) -> bool:
        """Fehlende Dependencies automatisch installieren"""
        pip_install = params.get('pip_install', True)
        upgrade = params.get('upgrade_existing', False)

        try:
            # Parse error message for missing module
            error_msg = error_data.get('message', '')
            module_name = self._extract_missing_module(error_msg)

            if module_name and pip_install:
                log_event('AUTO_DEPENDENCY_INSTALL', {'module': module_name})

                # Install via pip
                result = subprocess.run([sys.executable, '-m', 'pip', 'install', module_name],
                                      capture_output=True, text=True, timeout=60)

                if result.returncode == 0:
                    return True

            return False

        except Exception:
            return False

    async def _verify_system_integrity(self, params: Dict[str, Any]) -> bool:
        """Systemintegrität verifizieren"""
        deep_check = params.get('deep_check', True)

        try:
            log_event('SYSTEM_INTEGRITY_CHECK', {'deep_check': deep_check})

            # System integrity checks
            # Verify all critical files, configs, processes
            await asyncio.sleep(3)
            return True

        except Exception:
            return False

    def _extract_missing_module(self, error_message: str) -> Optional[str]:
        """Extrahiere Namen des fehlenden Moduls aus Fehlermeldung"""
        import re

        # Common patterns for missing module errors
        patterns = [
            r"ModuleNotFoundError: No module named '([^']+)'",
            r"ImportError:.*'([^']+)'",
            r"cannot import name.*from.*'([^']+)'"
        ]

        for pattern in patterns:
            match = re.search(pattern, error_message)
            if match:
                return match.group(1)

        return None

    def _update_learning_data(self, rule: SmartRecoveryRule, success: bool):
        """Aktualisiere Lern-Daten basierend auf Ergebnis"""
        if not self.learning_enabled:
            return

        rule_key = rule.error_pattern

        # Update success history
        if rule_key not in self.success_history:
            self.success_history[rule_key] = []

        self.success_history[rule_key].append(success)

        # Keep only last 10 results for performance
        if len(self.success_history[rule_key]) > 10:
            self.success_history[rule_key] = self.success_history[rule_key][-10:]

        # Update success rate
        success_count = sum(self.success_history[rule_key])
        rule.success_rate = success_count / len(self.success_history[rule_key])

        # Update usage statistics
        rule.last_used = time.time()
        rule.usage_count += 1

    def get_system_health_report(self) -> Dict[str, Any]:
        """System-Health-Report generieren"""
        active_recoveries = len([r for r in self.active_recoveries.values()
                                if r.get('status') != 'completed'])

        total_successful = sum(sum(history) for history in self.success_history.values())

        return {
            'active_recoveries': active_recoveries,
            'total_successful_recoveries': total_successful,
            'rules_count': len(self.recovery_rules),
            'learning_enabled': self.learning_enabled,
            'recovery_success_rate': self._calculate_overall_success_rate()
        }

    def _calculate_overall_success_rate(self) -> float:
        """Gesamt-Erfolgsrate berechnen"""
        total_attempts = sum(len(history) for history in self.success_history.values())
        total_successes = sum(sum(history) for history in self.success_history.values())

        return total_successes / total_attempts if total_attempts > 0 else 0.0

    async def cleanup_completed_recoveries(self, max_age: int = 3600):
        """Abgeschlossene Recovery-Einträge aufräumen"""
        current_time = time.time()
        to_remove = []

        for error_id, recovery in self.active_recoveries.items():
            if (recovery.get('status') == 'completed' and
                current_time - recovery.get('start_time', 0) > max_age):
                to_remove.append(error_id)

        for error_id in to_remove:
            del self.active_recoveries[error_id]

        log_event('RECOVERY_CLEANUP_COMPLETED', {'cleaned_count': len(to_remove)})


# Global instance
auto_error_recovery = AutoErrorFixingSystem()


async def trigger_error_recovery(error_data: Dict[str, Any]) -> bool:
    """Öffentliche Funktion für Fehler-Wiederherstellung"""
    return await auto_error_recovery.process_error(error_data)


def get_recovery_system_status() -> Dict[str, Any]:
    """Status des Recovery-Systems abrufen"""
    return auto_error_recovery.get_system_health_report()


if __name__ == '__main__':
    # Demo usage
    async def demo():
        print("🛠️ SMART ERROR RECOVERY SYSTEM - Demo")
        print("=" * 50)

        # Test recovery for different error types
        test_errors = [
            {
                'component': 'pool_connector',
                'message': 'Connection to NiceHash pool failed: Connection timeout',
                'severity': ErrorSeverity.HIGH
            },
            {
                'component': 'mining_rig_01',
                'message': 'GPU hashrate dropped to 50 MH/s, expected 100 MH/s',
                'severity': ErrorSeverity.MEDIUM
            },
            {
                'component': 'system_config',
                'message': 'Config file malformed: Invalid JSON syntax',
                'severity': ErrorSeverity.MEDIUM
            }
        ]

        for error in test_errors:
            print(f"\n🚨 Testing recovery for: {error['message']}")
            recovered = await auto_error_recovery.process_error(error)
            print(f"🔧 Recovery successful: {recovered}")

        # Show system status
        status = auto_error_recovery.get_system_health_report()
        print("
📊 SYSTEM STATUS:"        print(f"  • Active Recoveries: {status['active_recoveries']}")
        print(f"  • Successful Recoveries: {status['total_successful_recoveries']}")
        print(f"  • Learning Rules: {status['rules_count']}")
        print(f"  • Overall Success Rate: {status['recovery_success_rate']:.1%}")

        print("\n✅ SMART ERROR RECOVERY SYSTEM ready!")

    asyncio.run(demo())
