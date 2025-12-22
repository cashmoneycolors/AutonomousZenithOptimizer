# GitHub Copilot Instructions — AutonomousZenithOptimizer

## Big Picture
- Entry/DI: `Program.cs` baut den .NET Generic Host, registriert DI, liest `appsettings.json` (`Optimizer`-Section) und führt den Endlos-Loop aus.
- Core-Orchestrator: `Core/ZenithController.cs` (`AutonomousZenithOptimizer`) koordiniert QML-Entscheidung → Trade → Text-Gen → Feedback + Compliance-Gates.
- “Außenkante”: Side-Effects gehören in `Adapters/` (HFT/CRM/Text) und `Modules/` (QML/Redis/Logging/Governance). Core spricht nur über Interfaces.

## Kritische Flows & Invarianten
- QML-Retry/Fallback ist zentral in `AutonomousZenithOptimizer.ExecuteQMLWithRetry(...)`:
  - Fallback-Decision muss exakt `MAINTAIN_LEVEL:1.0` bleiben (Tests erwarten das).
- Decision-Parsing/Clamp ist in `AutonomousZenithOptimizer.NormalizeDecision(...)`:
  - Nur `SCALE_UP:<factor>` führt zu `IHFT_AMAD_Adapter.ExecuteTrade(...)`.
  - Faktor wird aus Settings geclamped (`ScaleUpMinFactor/ScaleUpMaxFactor`).
- Compliance/Governance:
  - `RegulatoryHyperAdaptor.PerformLegalIntegrityCheck(...)` blockiert Orders (FR + > 10k) in `ProcessIncomingOrder(...)`.
  - `RegulatoryHyperAdaptor.GetComplianceScore()` nutzt ENV (`AZO_COMPLIANCE_SCORE`/`AZO_COMPLIANCE_APPROVED`) und steuert Text-Gen (Threshold in Settings).

## Konfiguration & Guardrails
- LiveMode: `OptimizerSettings.LiveMode` oder ENV `AZO_LIVE_MODE=true` aktiviert Guardrails in `Program.cs`:
  - `EnableDemoScenarios` und `SimulateQmlFailure` müssen dann `false` sein.
  - QML Endpoint muss gesetzt sein (`Optimizer:QmlEndpoint` oder ENV `AZO_QML_ENDPOINT`).
- Adapter sind Stubs und werfen in LiveMode absichtlich Exceptions: `Adapters/*_Adapter.cs`.

## Caching/Memory
- Redis-Abstraktion in `Modules/HoloCache.cs`:
  - Ohne ConnectionString wird `RedisMock` genutzt (In-Memory).
  - Cache-Key-Konvention: `context:{query}` (TTL 5 Minuten) in `HoloKognitivesRepository`.
  - `ContextualMemoryHandler` ruft `RetrieveHyperCognitiveContext(...)` für präventiven Kontext.

## Logging
- Nutze `ZenithLogger.LogAutonomousCycle(...)` und `ZenithLogger.LogCriticalError(...)` (Scopes mit Properties/Component).

## Dev Workflow (lokal & CI)
- CI ist Windows/.NET 8: `.github/workflows/dotnet.yml`.
- Standard-Kommandos:
  - `dotnet restore AutonomousZenithOptimizer.sln`
  - `dotnet build AutonomousZenithOptimizer.sln -c Release --no-restore`
  - `dotnet test AutonomousZenithOptimizer.sln -c Release --no-build --collect:"XPlat Code Coverage"`
  - `dotnet run --project ZenithCoreSystem.csproj`

## Tests (Repo-Pattern)
- Unit-Tests bleiben offline: `tests/ZenithCoreSystem.Tests/AutonomousZenithOptimizerTests.cs` nutzt In-Process-Fakes/Recording-Adapter.
- Wenn du `Core/Interfaces.cs` änderst: Implementierungen + Tests im gleichen PR nachziehen.

## Python-Agent (optional)
- `agent.py` ist ein eigenständiger RL/LLM-Experiment-Runner und wird vom .NET Host nicht automatisch ausgeführt.
- `.env` enthält nur Platzhalter-API-Keys; echte Secrets gehören in ENV/Secret Store (nicht committen).

