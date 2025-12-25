
# Autonomous Zenith Optimizer (AZO)

## Run

To run the autonomous optimizer locally:

```powershell
dotnet run --project ZenithCoreSystem.csproj
```

### Environment-specific configuration

The application uses default configuration plus environment overlays loaded by .NET (`appsettings.json` + `appsettings.{Environment}.json`). Tuned profiles:

- Development: `appsettings.Development.json` (aggressive loop, demo enabled)
- Production: `appsettings.Production.json` (safe guardrails, live-ready)

Select the environment via `DOTNET_ENVIRONMENT`:

```powershell
$env:DOTNET_ENVIRONMENT = "Development"
dotnet run --project ZenithCoreSystem.csproj

# Production (requires real providers and QML endpoint)
$env:DOTNET_ENVIRONMENT = "Production"
dotnet run --project ZenithCoreSystem.csproj
```

Key Optimizer knobs per environment:

- Development: `CycleDelaySeconds=15`, `EnableDemoScenarios=true`, `SimulateQmlFailure=true`
- Production: `CycleDelaySeconds=20`, `EnableDemoScenarios=false`, `SimulateQmlFailure=false`

Note: For true live mode with external providers, set `AZO_LIVE_MODE=true` and ensure `Optimizer:QmlEndpoint` is configured. Adapters throw in LiveMode when stubs are active.

