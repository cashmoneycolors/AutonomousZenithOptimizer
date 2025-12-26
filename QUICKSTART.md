# 📖 Schnelleinstieg — AutonomousZenithOptimizer

Für detaillierte Instruktionen, siehe [.github/copilot-instructions.md](.github/copilot-instructions.md).

## Big Picture (30 Sekunden)

- **Einstiegspunkt**: [Program.cs](Program.cs) (DI, Config, Endlosschleife)
- **Orchestrator**: [Core/ZenithController.cs](Core/ZenithController.cs) (DRL-State → QML → Side-Effects)
- **Verträge**: [Core/Interfaces.cs](Core/Interfaces.cs)
- **Externe Services**: [Adapters](Adapters) (Trade, Text, Orders)
- **State/Cache**: [Modules](Modules) (HoloCache, Infrastructure, etc.)

## Kritische Invarianten

- QML-Retry muss exakt `MAINTAIN_LEVEL:1.0` liefern (Exponential-Backoff bis max 30s)
- Compliance-Gate: Text-Gen nur wenn Score > Threshold
- LiveMode blockiert Stubs und erzwingt reale QML-Endpoint

## Dev-Workflow (Schnell)

```powershell
# Format checken
dotnet format AutonomousZenithOptimizer.sln --verify-no-changes

# Build + Test
dotnet restore AutonomousZenithOptimizer.sln
dotnet build AutonomousZenithOptimizer.sln -c Release --no-restore
dotnet test AutonomousZenithOptimizer.sln -c Release --no-build --collect:"XPlat Code Coverage" --results-directory ./test-results

# Run
dotnet run --project ZenithCoreSystem.csproj
```

## Lokale Config (Python)

Für die Python-Module wird `settings.json` lokal genutzt (und nicht committed). Nutze die Templates:

```powershell
Copy-Item .\settings.example.json .\settings.json
Copy-Item .\.env.example .\.env
```

## Env-Gates (Produktiv)

```powershell
# Development (Standard)
$env:DOTNET_ENVIRONMENT = "Development"
dotnet run --project ZenithCoreSystem.csproj

# Production (mit QML-Service)
$env:DOTNET_ENVIRONMENT = "Production"
$env:AZO_LIVE_MODE = "true"
$env:AZO_QML_ENDPOINT = "https://<your-qml-service>"
dotnet run --project ZenithCoreSystem.csproj
```

## Remote Hub & Mobile (optional)

- Node UI + Flask Stats: [remote_hub/start_hub.ps1](remote_hub/start_hub.ps1)
- Android Client: [ZenithMobileApp](ZenithMobileApp)

---

Mehr Details → [.github/copilot-instructions.md](.github/copilot-instructions.md)
