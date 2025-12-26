
# Autonomous Zenith Optimizer (AZO)

## Run

Recommended (avoids Debug EXE locks): build once, then run the already-built Release output.

```powershell
dotnet build .\AutonomousZenithOptimizer.sln -c Release
dotnet run --project .\ZenithCoreSystem.csproj -c Release --no-build
```

### Environment-specific configuration

The application uses default configuration plus environment overlays loaded by .NET (`appsettings.json` + `appsettings.{Environment}.json`). Tuned profiles:

- Development: `appsettings.Development.json` (aggressive loop, demo enabled)
- Production: `appsettings.Production.json` (safe guardrails, live-ready)

Select the environment via `DOTNET_ENVIRONMENT`:

```powershell
$env:DOTNET_ENVIRONMENT = "Development"
dotnet run --project .\ZenithCoreSystem.csproj -c Release --no-build

# Production (requires real providers and QML endpoint)
$env:DOTNET_ENVIRONMENT = "Production"
dotnet run --project .\ZenithCoreSystem.csproj -c Release --no-build
```

Key Optimizer knobs per environment:

- Development: `CycleDelaySeconds=15`, `EnableDemoScenarios=true`, `SimulateQmlFailure=true`
- Production: `CycleDelaySeconds=20`, `EnableDemoScenarios=false`, `SimulateQmlFailure=false`

Note: In PowerShell, keep commands on separate lines (or use `;`). Do not append env assignments directly after `dotnet run`, otherwise paths like `ZenithCoreSystem.csprojDevelopment` will be parsed.

Live mode: set `AZO_LIVE_MODE=true` and ensure `Optimizer:QmlEndpoint` (or `AZO_QML_ENDPOINT`) is configured. Adapters throw in LiveMode when stubs are active.

## Local config (Python modules)

Some Python tools read `settings.json` via `python_modules/config_manager.py`. This repo does **not** commit `settings.json` (it is ignored).

```powershell
Copy-Item .\settings.example.json .\settings.json
Copy-Item .\.env.example .\.env
# then fill in real values in .env / settings.json locally
```
