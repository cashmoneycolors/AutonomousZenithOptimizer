#!/usr/bin/env python3
"""
CASH MONEY COLORS ORIGINAL (R) - RISK MANAGEMENT SYSTEM
Stop-Loss Mechanismen, Diversifikation und Backup-Strategien
"""
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import threading
from python_modules.config_manager import get_config, get_rigs_config
from python_modules.alert_system import send_system_alert, send_custom_alert
from python_modules.market_integration import get_crypto_prices
from python_modules.nicehash_integration import optimize_mining_strategy, calculate_profit_comparison

class RiskManager:
    """Umfassendes Risiko-Management für Mining-Operationen"""

    def __init__(self):
        self.stop_loss_config = get_config('RiskManagement', {})
        self.monitoring_active = False
        self.risk_metrics = {}
        self.emergency_stop = False
        self.backup_rigs_cache = []

        # Standard-Konfiguration wenn nicht gesetzt
        if not self.stop_loss_config:
            self.stop_loss_config = {
                'StopLossEnabled': True,
                'StopLossPercentage': 15.0,
                'DiversificationEnabled': True,
                'MaxSingleCoinAllocation': 60.0,
                'BackupRigsEnabled': True,
                'AutoRestartOnFailure': True,
                'MonitorIntervalSeconds': 60,
                'MaxConsecutiveFailures': 3
            }

        print("[SHIELD] RISK MANAGEMENT SYSTEM INITIALIZED")
        print("Stop-Loss Protection:", "ENABLED" if self.stop_loss_config.get('StopLossEnabled') else "DISABLED")

    def start_monitoring(self):
        """Startet kontinuierliches Risiko-Monitoring"""
        if self.monitoring_active:
            print("Risk monitoring bereits aktiv")
            return

        self.monitoring_active = True
        self.emergency_stop = False

        monitor_thread = threading.Thread(target=self._risk_monitor_loop, daemon=True)
        monitor_thread.start()

        print("🔍 Risk-Monitoring gestartet")

    def stop_monitoring(self):
        """Stoppt Risiko-Monitoring"""
        self.monitoring_active = False
        print("⏹️ Risk-Monitoring gestoppt")

    def check_stop_loss(self, current_portfolio: Dict[str, float], baseline_profit: float) -> Dict[str, Any]:
        """Prüft Stop-Loss Bedingungen"""
        if not self.stop_loss_config.get('StopLossEnabled', False):
            return {'triggered': False, 'message': 'Stop-Loss deaktiviert'}

        total_current_value = sum(current_portfolio.values())
        loss_percentage = ((total_current_value - baseline_profit) / baseline_profit) * 100

        stop_loss_threshold = self.stop_loss_config.get('StopLossPercentage', 15.0)

        if loss_percentage <= -stop_loss_threshold:
            self.emergency_stop = True
            message = f"🚨 STOP-LOSS TRIGGERED: {loss_percentage:.1f}% Verlust (Schwelle: {stop_loss_threshold}%)"
            send_system_alert("STOP_LOSS_TRIGGERED", message,
                            {'loss_percentage': loss_percentage, 'threshold': stop_loss_threshold})

            # Emergency shutdown initiieren
            self._emergency_shutdown(message)

            return {
                'triggered': True,
                'loss_percentage': loss_percentage,
                'message': message,
                'recommended_action': 'shutdown'
            }

        return {
            'triggered': False,
            'current_loss': loss_percentage,
            'threshold': stop_loss_threshold,
            'message': f'Loss: {loss_percentage:.1f}% (Safe unter {stop_loss_threshold}%)'
        }

    def analyze_diversification(self, rig_allocations: Dict[str, float]) -> Dict[str, Any]:
        """Analysiert Portfolio-Diversifikation"""
        if not self.stop_loss_config.get('DiversificationEnabled', False):
            return {'diversified': False, 'message': 'Diversifikation deaktiviert'}

        total_allocation = sum(rig_allocations.values())
        max_single = self.stop_loss_config.get('MaxSingleCoinAllocation', 60.0)

        over_allocated = {}
        total_risk_score = 0

        for coin, allocation in rig_allocations.items():
            percentage = (allocation / total_allocation) * 100

            if percentage > max_single:
                over_allocated[coin] = percentage
                total_risk_score += (percentage - max_single) / max_single * 100

        suggestions = []
        if over_allocated:
            suggestions.append(f"Zu hohe Allokation in {len(over_allocated)} Coins reduzieren")
            suggestions.append(f"Umverteilen auf unterallokierte Algorithmen/Coin")

        status = 'high_risk' if total_risk_score > 50 else 'medium_risk' if total_risk_score > 20 else 'low_risk'

        return {
            'diversified': len(over_allocated) == 0,
            'over_allocated_coins': over_allocated,
            'risk_score': total_risk_score,
            'status': status,
            'suggestions': suggestions,
            'max_single_allocation': max_single
        }

    def manage_rig_failures(self, failed_rigs: List[Dict[str, Any]],
                           available_backup_rigs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Verwaltet Rig-Ausfälle und Backup-Aktivierung"""
        if not self.stop_loss_config.get('BackupRigsEnabled', False):
            return {'activated_backups': 0, 'message': 'Backup-Rigs deaktiviert'}

        activated_backups = []
        max_consecutive_failures = self.stop_loss_config.get('MaxConsecutiveFailures', 3)

        for failed_rig in failed_rigs:
            # Prüfe ob Rig zu oft ausgefallen ist
            consecutive_failures = failed_rig.get('consecutive_failures', 0)

            if consecutive_failures >= max_consecutive_failures:
                send_system_alert("CRITICAL_RIG_FAILURE",
                                f"Rig {failed_rig['id']} zu oft ausgefallen ({consecutive_failures}x)",
                                {'rig_id': failed_rig['id'], 'failures': consecutive_failures})
                continue

            # Finde passenden Backup-Rig
            backup_rig = self._find_backup_rig(failed_rig, available_backup_rigs)
            if backup_rig:
                activated_backups.append({
                    'failed_rig': failed_rig['id'],
                    'backup_rig': backup_rig['id'],
                    'algorithm': failed_rig.get('algorithm', 'unknown')
                })

                # Backup aus verfügbaren entfernen
                available_backup_rigs.remove(backup_rig)

                send_system_alert("BACKUP_RIG_ACTIVATED",
                                f"Backup-Rig {backup_rig['id']} für {failed_rig['id']} aktiviert",
                                {'failed': failed_rig['id'], 'backup': backup_rig['id']})

        return {
            'activated_backups': len(activated_backups),
            'backup_details': activated_backups,
            'message': f"{len(activated_backups)} Backup-Rigs aktiviert"
        }

    def optimize_portfolio_diversification(self, current_allocations: Dict[str, float],
                                         market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimiert Portfolio-Diversifikation basierend auf Marktbedingungen"""
        if not self.stop_loss_config.get('DiversificationEnabled', False):
            return {'optimized': False, 'message': 'Diversifikation deaktiviert'}

        # Analysiere Risiko jeder Coin-Allokation
        coin_risks = {}
        total_allocation = sum(current_allocations.values())

        for coin, allocation in current_allocations.items():
            percentage = (allocation / total_allocation) * 100
            market_info = market_data.get(coin, {})
            volatility = market_info.get('change_24h', 0)

            # Risiko-Score basierend auf Volatilität und Allokation
            risk_score = abs(volatility) * (percentage / 100)
            coin_risks[coin] = {
                'allocation_percentage': percentage,
                'volatility': volatility,
                'risk_score': risk_score
            }

        # Finde überrisikoreiche Coins
        high_risk_coins = [coin for coin, data in coin_risks.items()
                          if data['allocation_percentage'] > 50 or data['risk_score'] > 15]

        recommendations = []
        if high_risk_coins:
            recommendations.append(f"Verringere Allokation in: {', '.join(high_risk_coins)}")

            # Vorschlage alternative Algorithmen/Coin von NiceHash
            nh_optimization = optimize_mining_strategy(get_rigs_config())

            if nh_optimization.get('recommended_switch_all'):
                recommendations.append("Erwäge Pool-Mining für bessere Diversifikation")

        return {
            'optimized': len(high_risk_coins) == 0,
            'high_risk_coins': high_risk_coins,
            'coin_risk_analysis': coin_risks,
            'recommendations': recommendations,
            'overall_risk_score': sum(data['risk_score'] for data in coin_risks.values())
        }

    def predict_risk_events(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Vorhersage potenzieller Risiko-Events basierend auf historischen Daten"""
        if not historical_data:
            return {'predictions': [], 'message': 'Keine historischen Daten verfügbar'}

        predictions = []
        recent_failures = sum(1 for event in historical_data[-24:]  # Letzte 24h
                            if event.get('type') == 'RIG_FAILURE')

        if recent_failures >= 3:
            predictions.append({
                'event': 'Hardware-Failure Cluster',
                'probability': 'high',
                'description': f'{recent_failures} Ausfälle in 24h - Hardware-Problem wahrscheinlich',
                'recommended_action': 'Vollständige Hardware-Inspektion'
            })

        # Marktvolatilität analysieren
        price_changes = [abs(d.get('price_change_24h', 0)) for d in historical_data[-7:]]  # Letzte Woche
        if price_changes:
            avg_volatility = sum(price_changes) / len(price_changes)
            if avg_volatility > 10:
                predictions.append({
                    'event': 'Hohe Marktvolatilität',
                    'probability': 'medium' if avg_volatility < 15 else 'high',
                    'description': f'Durchschnittliche Volatilität: {avg_volatility:.1f}%',
                    'recommended_action': 'Stop-Loss Schwelle anpassen'
                })

        return {
            'predictions': predictions,
            'risk_assessment': 'high' if len(predictions) >= 2 else 'medium' if len(predictions) == 1 else 'low'
        }

    def _risk_monitor_loop(self):
        """Hauptschleife für kontinuierliches Risiko-Monitoring"""
        monitor_interval = self.stop_loss_config.get('MonitorIntervalSeconds', 60)

        while self.monitoring_active:
            try:
                self._perform_risk_assessment()

                if self.emergency_stop:
                    print("🚨 Emergency Stop aktiv - Monitoring pausiert")
                    time.sleep(300)  # 5 Minuten warten
                    continue

                time.sleep(monitor_interval)

            except Exception as e:
                print(f"Risk Monitor Fehler: {e}")
                send_system_alert("RISK_MONITOR_ERROR", f"Risk-Monitoring Fehler: {e}")
                time.sleep(60)

    def _perform_risk_assessment(self):
        """Führt komplette Risiko-Bewertung durch"""
        # Markt-Daten laden
        market_data = get_crypto_prices()

        # Rig-Konfiguration laden
        rigs = get_rigs_config()

        # Portfolio-Analyse
        current_allocations = {}
        total_profit = 0

        for rig in rigs:
            if rig.get('status') == 'ACTIVE':
                coin = rig.get('coin', 'UNKNOWN')
                profit = rig.get('profit_per_day', 0)
                total_profit += profit

                if coin not in current_allocations:
                    current_allocations[coin] = 0
                current_allocations[coin] += profit

        # Stop-Loss prüfen
        baseline_profit = 1000.0  # Konfigurierbar machen
        stop_loss_result = self.check_stop_loss(current_allocations, baseline_profit)

        # Diversifikation analysieren
        diversification_analysis = self.analyze_diversification(current_allocations)

        # Portfolio-Optimierung
        portfolio_optimization = self.optimize_portfolio_diversification(current_allocations, market_data)

        # Risiko-Metriken aktualisieren
        self.risk_metrics = {
            'timestamp': datetime.now().isoformat(),
            'stop_loss_status': stop_loss_result,
            'diversification_status': diversification_analysis,
            'portfolio_optimization': portfolio_optimization,
            'total_active_profit': total_profit,
            'emergency_stop': self.emergency_stop
        }

        # Alerts bei hohen Risiken
        if diversification_analysis.get('status') == 'high_risk':
            send_custom_alert("Portfolio Risk Alert",
                            f"Hohes Risiko durch Überallokation in {len(diversification_analysis['over_allocated_coins'])} Coins",
                            "[WARN]")

        if portfolio_optimization.get('overall_risk_score', 0) > 30:
            send_custom_alert("Market Risk Alert",
                            f"Hochvolatiles Markt-Environment - Risiko-Score: {portfolio_optimization['overall_risk_score']:.1f}",
                            "[STATS]")

    def _find_backup_rig(self, failed_rig: Dict[str, Any],
                        available_backups: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Findet passenden Backup-Rig für ausgefallenen Rig"""
        failed_algorithm = failed_rig.get('algorithm', '')
        failed_coin = failed_rig.get('coin', '')

        # Präferenz: Gleicher Algorithmus/Coin
        for backup in available_backups:
            if (backup.get('algorithm') == failed_algorithm and
                backup.get('coin') == failed_coin and
                backup.get('status') == 'STANDBY'):
                return backup

        # Fallback: Gleicher Algorithmus
        for backup in available_backups:
            if (backup.get('algorithm') == failed_algorithm and
                backup.get('status') == 'STANDBY'):
                return backup

        # Letzter Fallback: Erster verfügbarer
        for backup in available_backups:
            if backup.get('status') == 'STANDBY':
                return backup

        return None

    def _emergency_shutdown(self, reason: str):
        """Führt Emergency-Shutdown durch"""
        print(f"🚨 EMERGENCY SHUTDOWN: {reason}")

        # Alle aktiven Komponenten stoppen
        try:
            from python_modules.mining_system_integration import stop_mining_system
            stop_mining_system()
        except:
            pass

        try:
            from python_modules.auto_backup import stop_auto_backup
            stop_auto_backup()
        except:
            pass

        send_system_alert("EMERGENCY_SHUTDOWN",
                        f"System wurde wegen {reason} notausgeschaltet",
                        {'shutdown_time': datetime.now().isoformat()})

    def get_risk_status(self) -> Dict[str, Any]:
        """Gibt aktuellen Risiko-Status zurück"""
        return {
            'monitoring_active': self.monitoring_active,
            'emergency_stop': self.emergency_stop,
            'last_assessment': self.risk_metrics,
            'configuration': self.stop_loss_config
        }

# Globale Risiko-Management Instanz
risk_manager = RiskManager()

# Convenience-Funktionen
def start_risk_monitoring():
    """Startet Risiko-Monitoring"""
    risk_manager.start_monitoring()

def stop_risk_monitoring():
    """Stoppt Risiko-Monitoring"""
    risk_manager.stop_monitoring()

def check_stop_loss(portfolio, baseline):
    """Prüft Stop-Loss"""
    return risk_manager.check_stop_loss(portfolio, baseline)

def analyze_diversification(allocations):
    """Analysiert Diversifikation"""
    return risk_manager.analyze_diversification(allocations)

def manage_rig_failures(failed_rigs, backups):
    """Verwaltet Rig-Ausfälle"""
    return risk_manager.manage_rig_failures(failed_rigs, backups)

def optimize_portfolio_diversification(allocations, market_data):
    """Optimiert Portfolio"""
    return risk_manager.optimize_portfolio_diversification(allocations, market_data)

def get_risk_status():
    """Gibt Risiko-Status"""
    return risk_manager.get_risk_status()

if __name__ == "__main__":
    print("CASH MONEY COLORS ORIGINAL (R) - RISK MANAGEMENT SYSTEM")
    print("=" * 65)

    print("🧪 Teste Risk Management System...")

    # Test-Stop-Loss
    test_portfolio = {'BTC': 500, 'ETH': 300, 'RVN': 200}
    baseline = 1200

    stop_loss = check_stop_loss(test_portfolio, baseline)
    print(f"Stop-Loss Test: Triggered={stop_loss['triggered']}")

    # Test-Diversifikation
    test_allocations = {'BTC': 600, 'ETH': 300, 'RVN': 100}
    diversification = analyze_diversification(test_allocations)
    print(f"Diversifikations-Analyse: {'Diversifiziert' if diversification['diversified'] else 'Nicht diversifiziert'}")

    # Test-Portfolio-Optimierung
    test_market = {'BTC': {'change_24h': -12.5}, 'ETH': {'change_24h': 8.3}}
    portfolio_opt = optimize_portfolio_diversification(test_allocations, test_market)
    print(f"Portfolio-Optimierung: Risk Score={portfolio_opt.get('overall_risk_score', 0):.1f}")

    print("\n[OK] RISK MANAGEMENT SYSTEM BEREIT!")
    print("Verwende start_risk_monitoring(), check_stop_loss(), analyze_diversification(), etc.")
    print("Konfiguriere Risiko-Schwelle in settings.json unter 'RiskManagement'")
