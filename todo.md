# TODO: Bibliotheken erstellen und Docker-Fehler beheben

## Schritt 1: Virtuelle Umgebung einrichten
- Virtuelle Umgebung erstellen (.venv) - FEHLGESCHLAGEN wegen Python 3.14 Bug, aber Pakete installiert

## Schritt 2: Pakete installieren
- Installiere requests, numpy, qiskit, cirq - ERLEDIGT
- Erstelle/aktualisiere requirements.txt - ERLEDIGT

## Schritt 3: Datenbank einrichten (falls erforderlich)
- Überprüfe und richte Datenbanken ein (z.B. aus den Skripten)

## Schritt 4: Docker-Fehler beheben
- Überprüfe Docker-Status
- Starte Docker Desktop
- Baue Dev Container neu auf

## Schritt 5: Verifizierung
- Teste die Installationen
- Stelle sicher, dass alles funktioniert


## Schritt 6: Optimierungsreport-Sammlung
- Bestehende Reports unter optimization_reports/ einsammeln und vereinheitlichen
- Aggregationsskript/Notebook für Zusammenfassung (JSON->CSV/HTML)
- Artefakt-Ablage strukturieren (YYYYMMDD/HHMM)

## Schritt 7: Tests erweitern
- Zusätzliche Unit- und Integrationstests für Mining-/Optimizer-Module
- Smoke-Tests für Start/Stop-Flows und API-Keys (ohne Secrets zu leaken)

## Schritt 8: Validierungsläufe
- Lokale Dry-Runs mit Debug-Logging
- Vergleich aktueller Kennzahlen vs. letzter erfolgreicher Lauf
