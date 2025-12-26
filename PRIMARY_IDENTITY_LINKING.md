# Primär-Identität erzwingen (<cashmoneycolors@gmail.com>)

Ziel: Alles (Git, GitHub CLI, VS Code/Copilot) soll konsistent über das Primär‑Konto laufen.

## 1) Wichtige Wahrheit (damit es wirklich stabil ist)

- GitHub-**Accounts** kann man nicht „zusammenführen“.
- Was geht:
  - Mehrere **E‑Mail-Adressen** an EIN GitHub-Account binden (Secondary Emails) → alte Commits werden dem Primär‑Account zugeordnet.
  - Repos aus Zweit‑Accounts per **Transfer** auf `cashmoneycolors` verschieben (oder Collaborator-Rechte vergeben).
- Was nicht geht:
  - Zwei GitHub-Logins „verbinden“, so dass es nur noch einen Token/Konto-Kontext gibt.

## 2) Git (Commits) – nur Primär

Sollwerte:

- `user.email = cashmoneycolors@gmail.com`
- `user.name = cashmoneycolors`

Empfehlung:

- Nur global setzen und repo-lokale Overrides vermeiden.

## 3) GitHub CLI (gh) – nur Primär

- `gh auth status` muss genau ein aktives Konto zeigen: `cashmoneycolors`
- Andere Logins entfernen:
  - `gh auth logout -h github.com -u <andererLogin>`

## 4) GitHub Web – alle E‑Mails an den Primär‑Account binden

Damit Commits unter anderen Adressen (z. B. `mehmetigazmendmehmeti@gmail.com`, `amriswil1984@gmail.com`, `amriswil40@gmail.com`, `cashmonenycolors@outlook.com`) auch beim Primär‑Account erscheinen:

1. In GitHub als `cashmoneycolors` anmelden.
2. Settings → Emails
3. Jede zusätzliche Adresse als **Secondary Email** hinzufügen
4. Bestätigungs-Mail öffnen und **verifizieren**
5. Primary bleibt: `cashmoneycolors@gmail.com`

Hinweis: Wenn deine E‑Mail im Profil/über API nicht sichtbar sein soll, kann GitHub sie als „privat“ behandeln; das ist ok.

## 5) Zweit‑GitHub‑Accounts „zusammenziehen“ (Repos umziehen)

Wenn du Repos unter `Gazi8580` oder `amriswil40-dotcom` hast und alles unter `cashmoneycolors` willst:

Option A (empfohlen): Repo Ownership Transfer

1. In den Zweit‑Account einloggen.
2. Repo → Settings → Danger Zone → **Transfer ownership**
3. Ziel: `cashmoneycolors`
4. Transfer bestätigen.

Option B: Collaborator (wenn Transfer nicht möglich)

- `cashmoneycolors` als Collaborator mit Admin-Rechten hinzufügen.

## 6) VS Code / Visual Studio – nur Primär

Das kann nicht per Script sicher automatisiert werden, weil es UI/OAuth ist. Stabiler Ablauf:

1. Browser: komplett aus GitHub ausloggen, dann im Incognito/InPrivate nur `cashmoneycolors@gmail.com` anmelden.
2. VS Code:
   - Command Palette: `GitHub: Sign Out`
   - Command Palette: `GitHub Copilot: Sign Out`
   - Unten links „Accounts“: alles Nicht‑Primär abmelden/entfernen
3. Visual Studio:
   - Account‑Icon → Account Settings → Nicht‑Primär entfernen
4. Windows Anmeldeinformationsverwaltung:
   - Alle Einträge löschen, die `github`, `vscode.github`, `git:https://github.com` enthalten.
5. VS Code neu starten → nur `cashmoneycolors@gmail.com` anmelden.
6. Copilot prüfen:
   - Command Palette: `GitHub Copilot: Check Status`

## 7) Repo-Tooling im Workspace

- Das Script `clone-all-repos.sh` nutzt standardmäßig nur Primär‑Repos.
- Secondary-Repos sind optional: `INCLUDE_SECONDARY_REPOS=true ./clone-all-repos.sh`
