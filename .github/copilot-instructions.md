# GitHub Copilot Instructions — AutonomousZenithOptimizer

## Big Picture
- Host setup in [Program.cs](Program.cs) wires DI, loads `Optimizer` config, enforces live guardrails, and runs the endless loop.
- Core orchestrator is [Core/ZenithController.cs](Core/ZenithController.cs) (`AutonomousZenithOptimizer`): builds DRL state → QML decision → trade + text-gen → feedback + compliance gates.
- Side effects live in [Adapters](Adapters) (HFT/CRM/Text) and [Modules](Modules) (QML bridge, Redis wrapper, logging, governance); core talks via interfaces only. Data records sit in [Core/DataModels.cs](Core/DataModels.cs).

## Critical Flows & Invariants
- QML retry in `ExecuteQMLWithRetry` uses exponential backoff (`QmlBaseDelayMilliseconds * 2^attempt`, cap 30s); terminal fallback must stay exactly `MAINTAIN_LEVEL:1.0`.
- Decision parsing in `NormalizeDecision` clamps `SCALE_UP:<factor>` to settings bounds (`ScaleUpMinFactor`..`ScaleUpMaxFactor`, max 100) and only then triggers `IHFT_AMAD_Adapter.ExecuteTrade`.
- Compliance: `RegulatoryHyperAdaptor.PerformLegalIntegrityCheck` blocks FR orders >10k; `GetComplianceScore` can be overridden by env and gates text generation via `ComplianceThreshold`.

## Configuration & Guardrails
- Live mode: `OptimizerSettings.LiveMode` or env `AZO_LIVE_MODE=true` (enforced in [Program.cs](Program.cs)) requires `EnableDemoScenarios=false`, `SimulateQmlFailure=false`, and a QML endpoint (`Optimizer:QmlEndpoint` or `AZO_QML_ENDPOINT`). Adapters throw in live mode until real providers exist.
- Config overlays: `appsettings.json` + environment (`DOTNET_ENVIRONMENT`). Dev profile enables demos and QML failure simulation; prod disables both.
- Console: UTF-8 attempt with ASCII fallback when output is redirected (use `-` and `PASS` instead of box drawing/✓).

## Caching & Memory
- Redis abstraction in [Modules/HoloCache.cs](Modules/HoloCache.cs) wraps StackExchange.Redis; without a connection string, `RedisMock` is used.
- Cache keys: `context:{query}` (5-minute TTL) and `context:probe:{id}` for latency probes; `ContextualMemoryHandler` calls `ProbeCacheLatencyMsAsync` each cycle and surfaces hits/misses/latency for console/telemetry output.
- Cache stats reset only on process restart (no auto-reset per cycle); both cache hits and misses re-set TTL to keep hot keys alive.

## Logging & Console Output
- Use `ZenithLogger.LogAutonomousCycle`/`LogCriticalError` for structured logs; cycle summary is printed directly to console with cache stats, spend, scaling factor, and correlation ID.
- Adapters color-log (e.g., green for HFT) except in live mode.

## Developer Workflow
- Common commands: `dotnet restore AutonomousZenithOptimizer.sln`, `dotnet build AutonomousZenithOptimizer.sln -c Release --no-restore`, `dotnet test AutonomousZenithOptimizer.sln -c Release --no-build --collect:"XPlat Code Coverage"`, `dotnet run --project ZenithCoreSystem.csproj`.
- Formatting gate: `dotnet format AutonomousZenithOptimizer.sln` (CI enforced).
- Iteration loop delay uses `CycleDelaySeconds`; exponential backoff shuts down after 5 consecutive failures.

## Tests & Fakes
- Tests live in [tests/ZenithCoreSystem.Tests/AutonomousZenithOptimizerTests.cs](tests/ZenithCoreSystem.Tests/AutonomousZenithOptimizerTests.cs); they use recording adapters (`RecordingHftAdapter`) and deterministic QML fakes (`AlwaysFailingQml`, `ScaleUpQml`).
- Changing [Core/Interfaces.cs](Core/Interfaces.cs) requires updating all adapter implementations and tests in the same change.

## Adapters & External Edges
- HFT_AMAD: `ExecuteTrade(symbol, amount, direction)` stub returns `amount * 1.0001m` plus console log.
- GEF_MSA: `GenerateText(prompt, styleGuide)` stub echoes prompt with ~100ms delay and governance status.
- ECA_AHA: `SubmitOrder(order, supplierId)` stub always true with ~50ms delay. All adapters throw `InvalidOperationException` in live mode.

## Python & Remote Hub
- `agent.py` and [python_modules](python_modules) (NiceHash, mining control, dashboards) run standalone; .NET host does not invoke them by default.
- Remote Hub in [remote_hub](remote_hub): Node UI on 3000 (`npm install && npm start`), Flask stats on 8503 (`python -m venv .venv && .venv/Scripts/pip install -r requirements.txt && .venv/Scripts/python webhook_server.py`), combined launcher `remote_hub/start_hub.ps1`.
- URLs: UI `http://localhost:3000/mobile`, stats `http://localhost:8503/stats`; binds to `0.0.0.0` by default, override with env `REMOTE_HUB_HOST`.

## Environment Variables
- `AZO_LIVE_MODE`, `AZO_QML_ENDPOINT`, `AZO_COMPLIANCE_SCORE`, `AZO_COMPLIANCE_APPROVED`, `REDIS_CONNECTION_STRING`, `REMOTE_HUB_HOST`, `REMOTE_HUB_PORT`, `REMOTE_HUB_API_PORT` (see profiles in `appsettings.*.json`).

## Mobile App (WebView)
- Android client in [ZenithMobileApp](ZenithMobileApp) loads the Remote Hub UI via WebView; default URL in `app/src/main/res/values/strings.xml`.
- Emulator URL: `http://10.0.2.2:3000/mobile?api=http://10.0.2.2:8503`; physical device: replace host with LAN IP (e.g., `http://192.168.178.20:3000/mobile?api=http://192.168.178.20:8503`).
- Build via Android Studio or `./gradlew :app:assembleDebug`; cleartext HTTP allowed for dev, switch to HTTPS for production.

