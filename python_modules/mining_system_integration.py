#!/usr/bin/env python3
"""Autonomes Integrationsmodul für ein simuliertes Mining-Ökosystem.

Dieses Modul verknüpft vereinfachte Komponenten (Datenkollektoren, Analysen
und Optimierungsentscheidungen) zu einem konsistenten Kontrollsystem. Die
Funktionalität ist auf Unit-Tests ausgelegt und bildet typische Abläufe eines
Mining-Orchestrators nach."""

import json
import logging
import os
import random
import signal
import sys
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

logger = logging.getLogger("integrated_mining_system")


def _configure_logging() -> None:
    level_name = os.getenv("MINING_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            "[%(asctime)s] %(levelname)s [%(threadName)s] %(name)s: %(message)s"
        ))
        handler.setLevel(level)
        logger.addHandler(handler)
    else:
        for handler in logger.handlers:
            handler.setLevel(level)

    logger.setLevel(level)
    logger.propagate = False


_configure_logging()


@dataclass
class SystemConfig:
    """Konfiguration für das Mining-System."""
    
    monitoring_interval: float = 1.0
    collection_interval: float = 5.0
    analysis_interval: float = 7.0
    shutdown_timeout: float = 5.0
    enable_auto_optimization: bool = True
    log_performance_metrics: bool = True
    config_file: Optional[str] = None
    
    @classmethod
    def from_file(cls, filepath: str) -> "SystemConfig":
        """Lädt Konfiguration aus JSON-Datei."""
        path = Path(filepath)
        if not path.exists():
            logger.warning("Konfigurationsdatei %s nicht gefunden, nutze Defaults", filepath)
            return cls()
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info("Konfiguration aus %s geladen", filepath)
            return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})
        except Exception as exc:
            logger.error("Fehler beim Laden der Konfiguration: %s", exc)
            return cls()
    
    @classmethod
    def from_env(cls) -> "SystemConfig":
        """Lädt Konfiguration aus Umgebungsvariablen."""
        return cls(
            monitoring_interval=float(os.getenv("MINING_MONITOR_INTERVAL", "1.0")),
            collection_interval=float(os.getenv("MINING_COLLECTION_INTERVAL", "5.0")),
            analysis_interval=float(os.getenv("MINING_ANALYSIS_INTERVAL", "7.0")),
            shutdown_timeout=float(os.getenv("MINING_SHUTDOWN_TIMEOUT", "5.0")),
            enable_auto_optimization=os.getenv("MINING_AUTO_OPTIMIZE", "true").lower() == "true",
            log_performance_metrics=os.getenv("MINING_LOG_METRICS", "true").lower() == "true",
        )
    
    def save_to_file(self, filepath: str) -> None:
        """Speichert Konfiguration in JSON-Datei."""
        path = Path(filepath)
        data = {
            "monitoring_interval": self.monitoring_interval,
            "collection_interval": self.collection_interval,
            "analysis_interval": self.analysis_interval,
            "shutdown_timeout": self.shutdown_timeout,
            "enable_auto_optimization": self.enable_auto_optimization,
            "log_performance_metrics": self.log_performance_metrics,
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            logger.info("Konfiguration nach %s gespeichert", filepath)
        except Exception as exc:
            logger.error("Fehler beim Speichern der Konfiguration: %s", exc)


@dataclass(frozen=True)
class OptimizationAction:
    """Beschreibt eine konkrete Optimierungsmaßnahme für Mining-Rigs."""

    action: str
    rigs: Sequence[str] = field(default_factory=tuple)
    description: str = ""
    factor: Optional[float] = None
    delta_temperature: Optional[float] = None


@dataclass(frozen=True)
class RiskAssessment:
    """Repräsentiert eine Risikoeinschätzung des Gesamtsystems."""

    level: str
    score: float
    recommendation: str
    issues: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level,
            "score": round(self.score, 2),
            "recommendation": self.recommendation,
            "issues": list(self.issues),
        }

class DeepSeekMiningBrain:
    """Fallback-Implementation der QML-Brain-Integration."""

    def __init__(self) -> None:
        logger.debug("DeepSeekMiningBrain (Fallback) initialisiert")

    def start_brain_operations(self) -> None:
        logger.debug("DeepSeek Mining Brain gestartet")

    def stop_brain_operations(self) -> None:
        logger.debug("DeepSeek Mining Brain gestoppt")

    def identify_optimization_opportunities(self, context: Dict[str, Any]) -> List[OptimizationAction]:
        assessment = context.get("last_risk_assessment") or {}
        rigs = context.get("rigs") or []
        overheating_ids = [
            rig.get("id")
            for rig in rigs
            if rig.get("temperature", 0.0) >= 86.0
            or str(rig.get("status", "")).upper() == "OVERHEATING"
        ]

        actions: List[OptimizationAction] = []
        if assessment.get("level") == "high" or overheating_ids:
            actions.append(
                OptimizationAction(
                    action="adjust_hashrate",
                    rigs=tuple(overheating_ids),
                    description="Hashrate drosseln für kritische Rigs",
                    factor=0.8,
                    delta_temperature=-6.0,
                )
            )
            actions.append(
                OptimizationAction(
                    action="increase_cooling",
                    rigs=tuple(overheating_ids),
                    description="Kühlleistung erhöhen",
                    delta_temperature=-8.0,
                )
            )
        elif assessment.get("level") == "medium":
            actions.append(
                OptimizationAction(
                    action="optimize_costs",
                    description="Kostenoptimierung durchführen und Parameter feinjustieren",
                )
            )
        else:
            actions.append(
                OptimizationAction(
                    action="maintain",
                    description="System beibehalten – Kennzahlen stabil",
                )
            )

        return actions


class SimpleDataCollector:
    """Sammelkomponente mit deterministischer Telemetrie für Tests."""

    def __init__(self, system: "IntegratedMiningSystem") -> None:
        self._system = system

    def collect_mining_data(self) -> Dict[str, Dict[str, float]]:
        snapshot: Dict[str, Dict[str, float]] = {}
        for rig in self._system.mining_rigs:
            snapshot[rig["id"]] = {
                "temperature": rig["temperature"] + random.uniform(-0.8, 0.8),
                "hash_rate": rig["hash_rate"] * random.uniform(0.98, 1.02),
                "power_consumption": rig["power_consumption"],
            }
        return snapshot


class SimpleDataAnalyzer:
    """Aggregiert Mining-Daten in einfache Kennzahlen."""

    def __init__(self, system: "IntegratedMiningSystem") -> None:
        self._system = system

    def analyze_mining_performance(self, rigs: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
        rigs_list = list(rigs)
        if not rigs_list:
            return {"message": "Keine Rigs aktiv"}
        avg_temp = sum(rig["temperature"] for rig in rigs_list) / len(rigs_list)
        avg_eff = sum(rig.get("efficiency", 0.0) for rig in rigs_list) / len(rigs_list)
        hottest = max(rigs_list, key=lambda rig: rig["temperature"])
        return {
            "average_temperature": round(avg_temp, 2),
            "average_efficiency": round(avg_eff, 3),
            "hottest_rig": hottest["id"],
        }


class SimpleControlPanel:
    """Stellt ein minimales Interface für Benachrichtigungen bereit."""

    def __init__(self) -> None:
        self.last_notification: Optional[str] = None

    def push_notification(self, message: str) -> None:
        self.last_notification = message
        logger.info("[CONTROL] %s", message)


class IntegratedMiningSystem:
    """Zentrale Steuerlogik für das Mining-Ökosystem."""

    DEFAULT_SYSTEM_NAME = "Integrated Mining System"
    DEFAULT_VERSION = "2024.1"

    def __init__(
        self,
        monitoring_interval: float = 1.0,
        collection_interval: float = 5.0,
        analysis_interval: float = 7.0,
        config: Optional[SystemConfig] = None,
    ) -> None:
        if config is not None:
            self.config = config
        else:
            self.config = SystemConfig(
                monitoring_interval=monitoring_interval,
                collection_interval=collection_interval,
                analysis_interval=analysis_interval,
            )
        
        self.monitoring_interval = max(0.05, float(self.config.monitoring_interval))
        self.collection_interval = max(0.1, float(self.config.collection_interval))
        self.analysis_interval = max(0.1, float(self.config.analysis_interval))
        self.system_name = self.DEFAULT_SYSTEM_NAME
        self.version = self.DEFAULT_VERSION

        self._lock = threading.RLock()
        self._shutdown_event = threading.Event()
        self.is_running = False
        self._monitoring_thread: Optional[threading.Thread] = None
        self._collection_thread: Optional[threading.Thread] = None
        self._analysis_thread: Optional[threading.Thread] = None

        self.mining_rigs: List[Dict[str, Any]] = self._create_default_rigs()
        self.system_status: Dict[str, Any] = self._create_initial_status()
        self.system_status["last_update"] = datetime.now(timezone.utc)

        self.deepseek_brain: Optional[DeepSeekMiningBrain] = None
        self.control_panel: Optional[SimpleControlPanel] = None
        self.data_collector: Optional[SimpleDataCollector] = None
        self.data_analyzer: Optional[SimpleDataAnalyzer] = None
        self.crypto_mining: Optional[Any] = None

        self._last_analysis: Dict[str, Any] = {}
        self._last_collected_data: Optional[Dict[str, Dict[str, float]]] = None
        self._performance_metrics: Dict[str, Any] = {
            "monitoring_cycles": 0,
            "collection_cycles": 0,
            "analysis_cycles": 0,
            "optimization_calls": 0,
            "errors": 0,
        }
        
        # Signal Handler für graceful shutdown
        self._original_sigint_handler = None
        self._original_sigterm_handler = None

    @staticmethod
    def _create_default_rigs() -> List[Dict[str, Any]]:
        rigs: List[Dict[str, Any]] = []
        template = [
            ("GPU_1", "RTX 4090", 120.0, 450.0, 16.5, 72.0),
            ("GPU_2", "RX 7900 XT", 98.0, 360.0, 12.4, 68.5),
            ("GPU_3", "ASIC S19", 95.0, 325.0, 11.3, 74.0),
        ]
        for identifier, rig_type, hashrate, power, profit, temperature in template:
            rigs.append(
                {
                    "id": identifier,
                    "type": rig_type,
                    "algorithm": "Ethash",
                    "coin": "ETH",
                    "hash_rate": hashrate,
                    "power_consumption": power,
                    "profit_per_day": profit,
                    "temperature": temperature,
                    "status": "ACTIVE",
                    "efficiency": round(hashrate / max(power, 1.0), 3),
                }
            )
        return rigs

    @staticmethod
    def _create_initial_status() -> Dict[str, Any]:
        return {
            "daily_profit": 0.0,
            "total_profit": 0.0,
            "active_rigs": 0,
            "last_update": datetime.now(timezone.utc),
            "advisories": [],
            "last_risk_assessment": RiskAssessment(
                level="unknown",
                score=0.0,
                recommendation="System initialisiert",
                issues=[],
            ).to_dict(),
        }

    def initialize_components(self) -> None:
        with self._lock:
            if self.deepseek_brain is None:
                self.deepseek_brain = DeepSeekMiningBrain()
            if self.control_panel is None:
                self.control_panel = SimpleControlPanel()
            if self.data_collector is None:
                self.data_collector = SimpleDataCollector(self)
            if self.data_analyzer is None:
                self.data_analyzer = SimpleDataAnalyzer(self)
            if self.crypto_mining is None:
                self.crypto_mining = object()

            self.system_status.setdefault("advisories", [])
            if "last_risk_assessment" not in self.system_status:
                self.system_status["last_risk_assessment"] = RiskAssessment(
                    level="unknown",
                    score=0.0,
                    recommendation="System initialisiert",
                    issues=[],
                ).to_dict()

            self._update_mining_status()
            self._perform_risk_assessment()

    def _start_thread(self, name: str, target) -> threading.Thread:
        thread = threading.Thread(
            target=target,
            name=f"mining_{name}_thread",
            daemon=True,
        )
        thread.start()
        return thread
    
    def _setup_signal_handlers(self) -> None:
        """Registriert Signal-Handler für graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info("Signal %s empfangen, fahre System herunter...", signum)
            self.stop_integrated_mining()
        
        if sys.platform != "win32":
            self._original_sigint_handler = signal.signal(signal.SIGINT, signal_handler)
            self._original_sigterm_handler = signal.signal(signal.SIGTERM, signal_handler)
    
    def _restore_signal_handlers(self) -> None:
        """Stellt ursprüngliche Signal-Handler wieder her."""
        if sys.platform != "win32":
            if self._original_sigint_handler:
                signal.signal(signal.SIGINT, self._original_sigint_handler)
            if self._original_sigterm_handler:
                signal.signal(signal.SIGTERM, self._original_sigterm_handler)

    def start_integrated_mining(self) -> None:
        with self._lock:
            if self.is_running:
                logger.warning("System läuft bereits")
                return
            self.initialize_components()
            self.is_running = True
            self._shutdown_event.clear()
            logger.info("Starte Mining-System...")

        self._setup_signal_handlers()
        self._monitoring_thread = self._start_thread("monitoring", self._monitoring_loop)
        self._collection_thread = self._start_thread("collection", self._data_collection_loop)
        self._analysis_thread = self._start_thread("analysis", self._analysis_loop)
        logger.info("Mining-System gestartet")

    def stop_integrated_mining(self) -> None:
        with self._lock:
            if not self.is_running:
                logger.debug("System ist bereits gestoppt")
                return
            logger.info("Stoppe Mining-System...")
            self.is_running = False
            self._shutdown_event.set()

        timeout = self.config.shutdown_timeout
        threads = [
            (self._monitoring_thread, "monitoring"),
            (self._collection_thread, "collection"),
            (self._analysis_thread, "analysis"),
        ]
        
        for thread, name in threads:
            if thread and thread.is_alive():
                logger.debug("Warte auf %s Thread...", name)
                thread.join(timeout=timeout)
                if thread.is_alive():
                    logger.warning("%s Thread konnte nicht sauber beendet werden", name)

        self._monitoring_thread = None
        self._collection_thread = None
        self._analysis_thread = None
        self._restore_signal_handlers()
        
        if self.config.log_performance_metrics:
            self._log_performance_metrics()
        
        logger.info("Mining-System gestoppt")

    def _monitoring_loop(self) -> None:
        logger.debug("Monitoring Loop gestartet")
        while self.is_running and not self._shutdown_event.is_set():
            start = time.monotonic()
            try:
                self.step_once(include_collection=False, include_analysis=False)
                with self._lock:
                    self._performance_metrics["monitoring_cycles"] += 1
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.exception("Fehler im Monitoring-Loop: %s", exc)
                with self._lock:
                    self._performance_metrics["errors"] += 1
            elapsed = time.monotonic() - start
            wait = max(0.0, self.monitoring_interval - elapsed)
            if wait and not self._shutdown_event.wait(timeout=min(wait, self.monitoring_interval)):
                continue
        logger.debug("Monitoring Loop beendet")

    def _data_collection_loop(self) -> None:
        logger.debug("Data Collection Loop gestartet")
        while self.is_running and not self._shutdown_event.is_set():
            try:
                if self.data_collector:
                    data = self.data_collector.collect_mining_data()
                    with self._lock:
                        self._process_mining_data(data)
                        self._performance_metrics["collection_cycles"] += 1
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.exception("Fehler im Data-Collector-Loop: %s", exc)
                with self._lock:
                    self._performance_metrics["errors"] += 1
            if self._shutdown_event.wait(timeout=self.collection_interval):
                break
        logger.debug("Data Collection Loop beendet")

    def _analysis_loop(self) -> None:
        logger.debug("Analysis Loop gestartet")
        while self.is_running and not self._shutdown_event.is_set():
            try:
                if self.data_analyzer:
                    analysis = self.data_analyzer.analyze_mining_performance(self.mining_rigs)
                    with self._lock:
                        self._apply_analysis_insights(analysis)
                        self._performance_metrics["analysis_cycles"] += 1
                        
                    if self.config.enable_auto_optimization:
                        self.optimize_mining_strategy()
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.exception("Fehler im Analyse-Loop: %s", exc)
                with self._lock:
                    self._performance_metrics["errors"] += 1
            if self._shutdown_event.wait(timeout=self.analysis_interval):
                break
        logger.debug("Analysis Loop beendet")
    
    def _log_performance_metrics(self) -> None:
        """Loggt Performance-Metriken beim Shutdown."""
        with self._lock:
            logger.info("=== Performance Metriken ===")
            logger.info("Monitoring Cycles: %d", self._performance_metrics["monitoring_cycles"])
            logger.info("Collection Cycles: %d", self._performance_metrics["collection_cycles"])
            logger.info("Analysis Cycles: %d", self._performance_metrics["analysis_cycles"])
            logger.info("Optimization Calls: %d", self._performance_metrics["optimization_calls"])
            logger.info("Errors: %d", self._performance_metrics["errors"])

    def _update_mining_status(self) -> None:
        active_rigs = sum(1 for rig in self.mining_rigs if rig.get("status") != "INACTIVE")
        self.system_status["active_rigs"] = active_rigs
        self.system_status["last_update"] = datetime.now(timezone.utc)

    def _check_rig_health(self) -> None:
        for rig in self.mining_rigs:
            temp = rig.get("temperature", 0.0)
            if temp >= 90.0:
                rig["status"] = "OVERHEATING"
            elif temp >= 85.0:
                rig["status"] = "HOT"
            elif temp <= 40.0:
                rig["status"] = "COOLING"
            else:
                rig["status"] = "ACTIVE"

    def _calculate_profit(self) -> None:
        daily_profit = sum(rig.get("profit_per_day", 0.0) for rig in self.mining_rigs)
        self.system_status["daily_profit"] = round(daily_profit, 2)
        accrued = daily_profit * (self.monitoring_interval / 86400.0)
        self.system_status["total_profit"] = round(
            self.system_status.get("total_profit", 0.0) + accrued,
            4,
        )

    def _process_mining_data(self, data: Dict[str, Dict[str, float]]) -> None:
        self._last_collected_data = data
        for rig in self.mining_rigs:
            metrics = data.get(rig["id"])
            if not metrics:
                continue
            rig["temperature"] = round(max(25.0, metrics.get("temperature", rig["temperature"])), 2)
            rig["hash_rate"] = round(max(0.0, metrics.get("hash_rate", rig["hash_rate"])), 2)
            rig["power_consumption"] = round(
                max(0.0, metrics.get("power_consumption", rig["power_consumption"])),
                2,
            )
            rig["efficiency"] = round(rig["hash_rate"] / max(rig["power_consumption"], 1.0), 3)

    def _apply_analysis_insights(self, insights: Dict[str, Any]) -> None:
        self._last_analysis = insights
        self.system_status["analysis_summary"] = insights
        message = insights.get("message")
        if message:
            self.system_status["advisories"].append(message)

    def _perform_risk_assessment(self) -> RiskAssessment:
        issues: List[str] = []
        score = 0.0
        overheating_ids: List[str] = []

        for rig in self.mining_rigs:
            temp = rig.get("temperature", 0.0)
            status = str(rig.get("status", "")).upper()
            if temp >= 90.0 or status == "OVERHEATING":
                issues.append(f"Rig {rig['id']} überhitzt bei {temp:.1f}°C")
                overheating_ids.append(rig["id"])
                score += 45.0
            elif temp >= 85.0:
                issues.append(f"Rig {rig['id']} zeigt hohe Temperatur ({temp:.1f}°C)")
                score += 25.0

            if rig.get("hash_rate", 0.0) <= 0.0:
                issues.append(f"Rig {rig['id']} liefert keine Hashrate")
                score += 20.0

        profit = self.system_status.get("daily_profit", 0.0)
        if profit < 5.0:
            issues.append("Tagesprofit unter 5 CHF – Profitabilität prüfen")
            score += 15.0

        if score >= 60.0:
            level = "high"
            recommendation = "Sofortige Drosselung und Kühlung erforderlich"
        elif score >= 30.0:
            level = "medium"
            recommendation = "Parameter optimieren und eng überwachen"
        else:
            level = "low"
            recommendation = "System stabil halten"

        assessment = RiskAssessment(
            level=level,
            score=score,
            recommendation=recommendation,
            issues=issues,
        )
        self.system_status["last_risk_assessment"] = assessment.to_dict()
        self.system_status["hot_rigs"] = overheating_ids
        return assessment

    def optimize_mining_strategy(self) -> None:
        with self._lock:
            if not self.deepseek_brain:
                logger.warning("Keine DeepSeek Brain Instanz verfügbar – Optimierung übersprungen")
                return
            context = dict(self.system_status)
            context["rigs"] = [rig.copy() for rig in self.mining_rigs]
            self._performance_metrics["optimization_calls"] += 1

        actions = self.deepseek_brain.identify_optimization_opportunities(context)
        if not actions:
            actions = [OptimizationAction(action="maintain", description="Keine Maßnahmen erforderlich")]

        for action in actions:
            self._apply_optimization_action(action)

        with self._lock:
            self.system_status["last_update"] = datetime.now(timezone.utc)
            self._perform_risk_assessment()

    def _find_rigs(self, rig_ids: Sequence[str]) -> List[Dict[str, Any]]:
        if not rig_ids:
            return list(self.mining_rigs)
        lookup = {rig["id"]: rig for rig in self.mining_rigs}
        return [lookup[rig_id] for rig_id in rig_ids if rig_id in lookup]

    def _apply_optimization_action(self, action: OptimizationAction) -> None:
        with self._lock:
            rigs = self._find_rigs(action.rigs)
            if action.rigs and not rigs:
                logger.warning("[OPTIMIZE] Keine passenden Rigs für Aktion '%s' gefunden", action.action)
                return

            logger.info("[OPTIMIZE] %s", action.description or action.action)

            if action.action == "adjust_hashrate":
                factor = action.factor or 1.0
                for rig in rigs:
                    rig["hash_rate"] = round(max(0.0, rig["hash_rate"] * factor), 2)
                    rig["profit_per_day"] = round(max(0.0, rig["profit_per_day"] * factor), 2)
                    if action.delta_temperature is not None:
                        rig["temperature"] = round(max(25.0, rig["temperature"] + action.delta_temperature), 2)
                    if factor < 1.0:
                        rig["status"] = "COOLING"
                self.system_status["advisories"].append(action.description or "Hashrate angepasst")

            elif action.action == "increase_cooling":
                delta = action.delta_temperature if action.delta_temperature is not None else -5.0
                for rig in rigs:
                    rig["temperature"] = round(max(20.0, rig["temperature"] + delta), 2)
                    rig["status"] = "COOLING"
                self.system_status["advisories"].append(action.description or "Kühlung erhöht")

            elif action.action == "optimize_costs":
                self.system_status["advisories"].append(action.description or "Kostenoptimierung starten")

            elif action.action == "maintain":
                self.system_status["advisories"].append(action.description or "Systemzustand halten")

            else:
                self.system_status["advisories"].append(f"Unbekannte Aktion '{action.action}' ignoriert")

    def evaluate_operational_health(self) -> Dict[str, Any]:
        with self._lock:
            last_assessment = self.system_status.get("last_risk_assessment", {})
            total_profit = sum(rig.get("profit_per_day", 0.0) for rig in self.mining_rigs)
            total_power = sum(rig.get("power_consumption", 0.0) for rig in self.mining_rigs)
            avg_efficiency = (
                sum(rig.get("efficiency", 0.0) for rig in self.mining_rigs) / len(self.mining_rigs)
            ) if self.mining_rigs else 0.0

            return {
                "risk_level": last_assessment.get("level", "unknown"),
                "risk_score": last_assessment.get("score"),
                "recommendation": last_assessment.get("recommendation"),
                "active_rigs": self.system_status.get("active_rigs", 0),
                "daily_profit": self.system_status.get("daily_profit", 0.0),
                "total_profit": round(self.system_status.get("total_profit", 0.0), 2),
                "total_power_consumption": round(total_power, 2),
                "average_efficiency": round(avg_efficiency, 3),
                "advisories": list(self.system_status.get("advisories", [])),
                "performance_metrics": dict(self._performance_metrics) if self.config.log_performance_metrics else {},
            }

    def step_once(self, include_collection: bool = False, include_analysis: bool = False) -> None:
        with self._lock:
            self._update_mining_status()
            self._check_rig_health()
            self._calculate_profit()
            self._perform_risk_assessment()
            self.system_status["last_update"] = datetime.now(timezone.utc)

        if include_collection and self.data_collector:
            data = self.data_collector.collect_mining_data()
            with self._lock:
                self._process_mining_data(data)

        if include_analysis and self.data_analyzer:
            analysis = self.data_analyzer.analyze_mining_performance(self.mining_rigs)
            with self._lock:
                self._apply_analysis_insights(analysis)

    def run_for(self, seconds: float) -> None:
        self.start_integrated_mining()
        try:
            end_time = time.monotonic() + max(0.0, seconds)
            while time.monotonic() < end_time and self.is_running:
                remaining = end_time - time.monotonic()
                time.sleep(min(0.5, max(0.05, remaining)))
        finally:
            self.stop_integrated_mining()

    def __enter__(self):
        self.start_integrated_mining()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_integrated_mining()

    def scale_mining_operation(self, target_rigs: int) -> None:
        with self._lock:
            current_rigs = len(self.mining_rigs)
            if target_rigs > current_rigs:
                for index in range(current_rigs + 1, target_rigs + 1):
                    new_rig = {
                        "id": f"GPU_{index}",
                        "type": "RTX 4090",
                        "algorithm": "Ethash",
                        "coin": "ETH",
                        "hash_rate": 118.0,
                        "power_consumption": 430.0,
                        "profit_per_day": 15.8,
                        "temperature": 71.0,
                        "status": "ACTIVE",
                        "efficiency": round(118.0 / 430.0, 3),
                    }
                    self.mining_rigs.append(new_rig)
                    logger.info("[ADD] Neuer Rig hinzugefügt: %s", new_rig["id"])
            elif target_rigs < current_rigs:
                removed = self.mining_rigs[target_rigs:]
                del self.mining_rigs[target_rigs:]
                if removed:
                    logger.info("[REMOVE] %d Rigs entfernt", len(removed))

            self._update_mining_status()

    def get_system_status(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "system_name": self.system_name,
                "version": self.version,
                "is_running": self.is_running,
                "system_status": dict(self.system_status),
                "mining_rigs": [rig.copy() for rig in self.mining_rigs],
                "active_components": {
                    "deepseek_brain": self.deepseek_brain is not None,
                    "control_panel": self.control_panel is not None,
                    "data_analyzer": self.data_analyzer is not None,
                    "data_collector": self.data_collector is not None,
                    "crypto_mining": self.crypto_mining is not None,
                },
            }

    def generate_system_report(self) -> str:
        status = self.get_system_status()
        assessment = status["system_status"].get("last_risk_assessment", {})
        report_lines = [
            "INTEGRATED MINING SYSTEM - STATUS REPORT",
            "=" * 47,
            "",
            f"System: {status['system_name']} v{status['version']}",
            f"Status: {'ACTIVE' if status['is_running'] else 'INACTIVE'}",
            f"Timestamp: {datetime.now(timezone.utc):%Y-%m-%d %H:%M:%S}",
            "",
            "MINING PERFORMANCE:",
            f"- Active Rigs: {status['system_status'].get('active_rigs', 0)}",
            f"- Daily Profit: CHF {status['system_status'].get('daily_profit', 0.0):.2f}",
            f"- Total Profit: CHF {status['system_status'].get('total_profit', 0.0):.2f}",
            "",
            "RISK ASSESSMENT:",
            f"- Level: {assessment.get('level', 'unknown')}",
            f"- Score: {assessment.get('score', 0.0)}",
            f"- Recommendation: {assessment.get('recommendation', 'n/a')}",
            "",
            "ADVISORIES:",
        ]
        advisories = status["system_status"].get("advisories", [])
        if advisories:
            report_lines.extend(f"- {item}" for item in advisories[-5:])
        else:
            report_lines.append("- Keine Hinweise")

        return "\n".join(report_lines)


integrated_mining_system = IntegratedMiningSystem()


def start_mining_system() -> None:
    integrated_mining_system.start_integrated_mining()


def stop_mining_system() -> None:
    integrated_mining_system.stop_integrated_mining()


def get_mining_status() -> Dict[str, Any]:
    return integrated_mining_system.get_system_status()


def generate_mining_report() -> str:
    return integrated_mining_system.generate_system_report()


def optimize_mining() -> None:
    integrated_mining_system.optimize_mining_strategy()


def scale_mining(rigs: int) -> None:
    integrated_mining_system.scale_mining_operation(rigs)


def run() -> None:
    logger.info("Modul %s wurde ausgeführt", __name__)


if __name__ == "__main__":
    run()
