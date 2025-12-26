# Session-Übersicht (Repo-lokal)

Ziel: Kontext aus mehreren alten Sessions/Chats **im Repo** bündig halten, damit ein Neustart/Tab-Cleanup ohne Informationsverlust möglich ist.

## Aktueller Zustand

- Git Working Tree: **clean** (keine lokalen Änderungen)
- Relevante Kurz-Notiz: `todo.md`

## Gefundene Session-/Kontextdateien

- `conversation_summary.local.md` – ältere Zusammenfassung (Cleanup/CI/Reset-Kontext)
- `repo_recovery_steps.local.md` – Recovery-Checkliste (mit Hinweis: nur nach expliziter Freigabe ausführen)
- `INTEGRATION_PROGRESS.md` – Integrationsstatus/Phasenplan
- `saved/kilo_code_task_dec-24-2025_12-19-44-am.md` – langes Terminal-Log/Task-Notizen

## Wichtigste Beobachtungen aus `saved/kilo_code_task_dec-24-2025_12-19-44-am.md`

- Wiederkehrend: **QML Bridge Verbindungsfehler**
  - Meldung: Verbindung verweigert zu `localhost:8501` → „Fallback verwendet“
  - Interpretation: Der QML/Service-Endpunkt läuft lokal nicht (oder falscher Endpoint konfiguriert).
- Trotz Fallback wird im Log ein „Live-Trade“ ausgeführt.
  - Wenn das „Live“ wirklich ernst gemeint ist, sollte geklärt werden, ob bei QML-Fallback Trades blockiert werden müssen.

## Empfohlene nächste Schritte (nach Neustart)

1. Entscheiden, ob `localhost:8501` der richtige QML-Endpunkt ist.
2. Falls ja: Service starten und Health prüfen.
3. Falls nein: Endpoint über Settings/Env setzen (z. B. `AZO_QML_ENDPOINT`) und erneut laufen lassen.
4. Optional: Guardrail klären/anpassen (LiveMode + QML nicht erreichbar → keine Trades / nur MAINTAIN).
