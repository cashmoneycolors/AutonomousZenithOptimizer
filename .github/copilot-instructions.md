## Kurzüberblick

Dieses Repo enthält den "Autonomous Zenith Optimizer" (AZO) - eine modulare C# basierte Simulationsschicht (Ziel: .NET 8.0). Die Implementierung ist in mehrere Bereiche aufgeteilt:

- Core/: Geschäftslogik und Schnittstellen (z. B. `Core/ZenithController.cs`, `Core/Interfaces.cs`, `Core/DataModels.cs`).
- Modules/: Infrastruktur-, Cache- und ML-Bridge-Implementierungen (z. B. `Modules/HoloCache.cs`, `Modules/QMLBridge.cs`, `Modules/Infrastructure.cs`).
- Adapters/: externe API-Adapter (Finance/KI/eCommerce — `Adapters/*_Adapter.cs`).
- `Program.cs`: HostBuilder-Bootstrap, registriert alle Module/Adapter und triggert zwei Demo-Laeufe.

Lies zuerst `Program.cs` — dort siehst du die Startsequenz, welche die wichtigsten Integrationspunkte (QML-Bridge, HoloCache, Adapters) verbindet.

## Wichtige Konzepte & Datenflüsse (Kurz)

- DRL-StateVector: zentrale Datenstruktur für Entscheidungen (`Core/DataModels.cs`, Typ `DRL_StateVector`).
- SCSC (Self-Correcting System Core): Retry-/Fallback-Pattern rund um ML-Calls — siehe `AutonomousZenithOptimizer.ExecuteQMLWithRetry` in `Core/ZenithController.cs`.
- Aktionspfade in `RunAutonomousGrowthStrategy`: 1) Aggregation → 2) QML-Entscheidung → 3) HFT-Trade → 4) KI-Textproduktion → 5) Feedback-Reporting.
- Governance/Compliance: `RegulatoryHyperAdaptor` führt schnelle LIC-Checks durch; wenn fehlschlägt, wird die Transaktion geblockt (siehe `ProcessIncomingOrder`).

## Konkrete Regeln & Konventionen (nur dieses Projekt)

- Verwende `record` für Datenmodelle (Immutable-ish pattern) — `Core/DataModels.cs` ist die Referenz.
- Alle Typen verwenden namespace `ZenithCoreSystem` (oder `ZenithCoreSystem.Modules` / `.Adapters` / `.Core`) — ändere Namespaces konsistent.
- Cache-Key-Konvention: `context:{query}` (siehe `HoloKognitivesRepository.RetrieveHyperCognitiveContext`).
- SCSC-Test-Simulation wird über `QML_Python_Bridge(simulateFailure: true)` in `Program.cs` gesteuert — 2 erste Aufrufe werfen Timeout zur Simulation.
- Fehlerbehandlung für QML nutzt 3 Retries mit wachsendem Delay und einen stabilen Fallback `MAINTAIN_LEVEL:1.0`.
- HostBuilder-Registrierung: neue Dienste als Singleton in `Program.cs` registrieren; Konstruktoren setzen auf DI (keine manuellen `new`-Ketten).

## Developer Workflows (Build / Run / Debug)

- Ziel-Framework: .NET 8.0. Nutze das Solution-File `AutonomousZenithOptimizer.sln`:
  - Restore & Build: `dotnet build AutonomousZenithOptimizer.sln`
  - Demo starten: `dotnet run --project ZenithCoreSystem.csproj`
  - Tests ausführen: `dotnet test AutonomousZenithOptimizer.sln`
- `tests/ZenithCoreSystem.Tests/FallbackTests.cs` zeigt, wie Stubs genutzt werden, um den SCSC-Fallback ohne echten Trade zu prüfen.
- `Program.cs` enthält weiterhin zwei manuelle Demos (`RunAutonomousGrowthStrategy`, `ProcessIncomingOrder` Szenarien) – laufen automatisch beim Programmstart.
- CI: GitHub Actions Workflow `./.github/workflows/dotnet.yml` baut & testet auf windows-latest (dotnet 8.0.x).

## Integration Points / externe Abhängigkeiten

- HoloCache: aktuell als `RedisMock` und `HoloKognitivesRepository` implementiert (`Modules/HoloCache.cs`). Wenn du echten Redis anschließt, ersetze `RedisMock` durch `StackExchange.Redis` `IConnectionMultiplexer`.
- ML-Bridge: `QML_Python_Bridge` simuliert die DRL-API. Produktion: ersetze die Bridge durch echte RPC/HTTP-Client oder gRPC-Client, behalte Schnittstelle `IProfitGuarantor_QML` bei.
- Adapters: `IHFT_AMAD_Adapter`, `IGEF_MSA_Adapter`, `IECA_AHA_Adapter` sind die einzigen Stellen, die externe APIs ansprechen — implementiere echte Clients hinter diesen Interfaces.

## Hinweise für KI-Codieragenten (konkret und handlungsorientiert)

1. Ändere keine Signaturen der Interfaces in `Core/Interfaces.cs` ohne Rückwärts-Impact-Analyse — viele Komponenten sind darauf abgestimmt.
2. Wenn du Resilience oder Telemetry erweiterst, erweitere `ZenithLogger` in `Modules/Infrastructure.cs` (zentrale Logging-Schnittstelle für das Projekt).
3. Für Änderungen an der QML-Integration: nutze `ExecuteQMLWithRetry` als zentrale Stelle für Retry-/Fallback-Logik; neue Features sollten dort zentralisiert werden.
4. Tests/Demos: `Program.cs` enthält reproduzierbare Szenarien. Passe den HostBuilder-Eintrag (`QML_Python_Bridge(simulateFailure: true)`) oder nutze Stubs in Tests für SCSC-Simulationen.
5. Caching: benutze Key-Pattern `context:{query}` und kurze TTLs (aktuell 5 Minuten im Beispiel). Beim Wechsel zu echtem Redis, prüfe Serialisierung (string vs. JSON).

## Beispiele im Repo (Schnellzugriff)

- Entscheidung/Retry: `Core/ZenithController.cs` → `ExecuteQMLWithRetry`
- Cache-API & Key-Pattern: `Modules/HoloCache.cs` → `HoloKognitivesRepository.RetrieveHyperCognitiveContext`
- HostBuilder-Aufbau: `Program.cs` → Services via `Host.CreateApplicationBuilder`
- Simulationseinstellung: `Program.cs` → `new QML_Python_Bridge(simulateFailure: true)`
- Tests: `tests/ZenithCoreSystem.Tests/FallbackTests.cs`
- Logging & Governance: `Modules/Infrastructure.cs` (`ZenithLogger`, `RegulatoryHyperAdaptor`)

## Änderungsregeln für Agenten

- Wenn du Code änderst, liefere kleine, getestete Änderungen (eine Änderung = Commit). Führe `dotnet build` nach Änderungen durch. Stelle sicher, dass `Program.Main` mindestens die zwei Demo-Szenarien ohne Exceptions durchläuft.
- Dokumentiere jede API-Änderung in `Core/Interfaces.cs` im selben Commit.

---
Wenn etwas unklar ist oder du mehr Beispiele möchtest (z. B. konkretere Unit-Test-Scaffolds oder ein HostBuilder-basiertes Startup), sag kurz, welche Bereiche du priorisieren willst — ich iteriere die Datei dann zügig nach.
