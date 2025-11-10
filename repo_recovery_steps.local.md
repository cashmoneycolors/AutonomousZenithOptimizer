# Repository Recovery Steps

- Execute `git status` to inspect pending changes.
- Run `git restore .` to revert files to the last committed state when a full reset is required.
- Clean build artefacts with `git clean -fd bin obj tests/ZenithCoreSystem.Tests/bin tests/ZenithCoreSystem.Tests/obj`.
- Build the solution using `dotnet build AutonomousZenithOptimizer.sln`.
- Run the test suite with `dotnet test AutonomousZenithOptimizer.sln`.

> Hinweis: Diese Datei dient ausschließlich der Dokumentation. Keine der genannten Aktionen darf ohne ausdrückliche Freigabe ausgeführt werden.
