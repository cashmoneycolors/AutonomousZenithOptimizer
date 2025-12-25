Copilot Instructions for Kontrollzentrum Modules
Architektur im Überblick
Das Kontrollzentrum besteht aus unabhängigen Python-Modulen im Wurzelverzeichnis (*_modul.py). Jedes Modul implementiert run() und kann eigenständig ausgeführt werden.
module_registry.py verwaltet alle Module. Neue Module müssen sich hier über register_module() eintragen, damit das Dashboard sie findet.
dashboard_modul.py (Streamlit) lädt eine feste Modulliste und führt run() aus; Fehler werden per Streamlit-Error ausgegeben.
module_dashboard.py liefert ergänzend einen FastAPI-Endpunkt modules als systemweite Registry-Ansicht.
Plugins liegen unter plugins und werden dynamisch via plugin_system.py geladen – identische Schnittstelle (run()), keine Registrierungsdatei notwendig.
Spezialbereiche (z.B. KI-Autonomie ki_core.py, Mining mining_system_max_profit_optimizer.py, Business-Flows business_execution_system.py) greifen auf dieselben Utilities und Registrierungsmechanismus zurück.
Entwickler-Workflows
Umgebung vorbereiten:
python -m venv .venv → activate → pip install -r requirements.txt
Anwendung starten:
streamlit run dashboard_modul.py für das zentrale UI,
uvicorn module_dashboard:app --port 8002 für den Module-FastAPI-Service.
Einzelmodule testen: python <modulname>.py (setzt meist .env und optionale Packages voraus).
Demo-Modus aktivieren sich automatisch, wenn Abhängigkeiten fehlen.
Volltests: python -m pytest bzw. gezielt python test_all_modules.py für Modul-spezifische Checks.
Build & CI: python build_pipeline.py erzeugt das Demo-Build; GitHub Actions liegen in ci.yml.
Projektkonventionen
Umgebungsvariablen zwingend über .env (siehe .env.example); Validierung erfolgt durch check_env_vars() und warn_if_demo_mode() in module_utils.py.
Optionale Bibliotheken immer mit check_optional_package() prüfen, bevor Funktionen aufgerufen werden.
Keine harten Secrets: Zugriff auf API-Keys erfolgt über apikey_manager.py / apikey_manager_new.py und apikeys.enc.json.
Logging & Statusmeldungen bevorzugt über Streamlit-Komponenten (st.info, st.warning, st.error) im UI-Kontext.
AI-/Automation-Module nutzen häufig Hilfsfunktionen aus ki_core.py, autonomous_execution_system.py oder cloud_platform.py. Bestehende Pattern wiederverwenden, statt neue Frameworks einzuführen.
Integration & Services
Lokale LLMs laufen über OllamaProxyServer (siehe README dort). Module greifen per HTTP-Proxy auf Modelle wie deepseek-coder zu.
Cloud-Deployments werden über dedizierte Skripte wie deploy_aws.sh, deploy_digitalocean.sh oder cloud_platform.py orchestriert; Konfigurationen sollten in JSON-Dateien (backup_schedule.json, business_analytics.json) gepflegt bleiben.
KI-Autonomie-Stacks (ki_max_autonom_modul.py, mega_ultra_roboter_ki.py) koordinieren sich mit cash_money_dashboard.py und Alerting (alerting.py) für Monitoring.
Qualitätssicherung & Wartung
Vor neuen Features auto_register_modules.py und check_registry.py ausführen, um Registry-Konsistenz sicherzustellen.
Backups laufen über backup_system.py und create_final_backup.py; neue Datenquellen dort hinterlegen.
Sicherheitsrichtlinien in SECURITY_FIX_README.md befolgen, insbesondere bei Integration externer APIs.
Für C#-/PowerShell-Anteile: fix_csharp_projects.py und FIX_CSHARP_PROJECTS.ps1 verwenden, danach dotnet restore && dotnet build ausführen.
Dokumentation aktuell halten (README.md, Modul-Docstrings), damit Dashboards und AI-Agents konsistente Metadaten liefern.
Offene Fragen?
Gibt es Stellen, die noch unklar sind oder weitere Details benötigen? Sag mir gern Bescheid, dann ergänze ich die Anleitung entsprechend!
