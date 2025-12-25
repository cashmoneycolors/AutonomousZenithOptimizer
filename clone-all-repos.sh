#!/usr/bin/env bash
set -euo pipefail

# Clone-All-Repos
# Ziel: Desktop-App (Desktop) + Android-App (Mobile) + Backend/Optimizer (\"Kern\") als getrennte Repos,
# aber als EIN Workspace zusammen öffnen.

ORG_DEFAULT="cashmoneycolors"
# Wichtig: Der Workspace-Ordner darf NICHT genauso heißen wie ein Repo.
# Du hast ein Repo namens "-MEGA-ULTRA-ROBOTER-KI" – deshalb ist der Default hier absichtlich anders.
WORKSPACE_DIR_NAME_DEFAULT="cashmoneycolors-workspace"
WORKSPACE_FILE_NAME_DEFAULT="mega-ultra-roboter-ki.code-workspace"

ORG="${ORG:-$ORG_DEFAULT}"
WORKSPACE_DIR_NAME="${WORKSPACE_DIR_NAME:-$WORKSPACE_DIR_NAME_DEFAULT}"
WORKSPACE_FILE_NAME="${WORKSPACE_FILE_NAME:-$WORKSPACE_FILE_NAME_DEFAULT}"

# Parent directory: default = current directory
PARENT_DIR="${PARENT_DIR:-$(pwd)}"

# Repos (als Geschwister-Verzeichnisse neben dem Workspace-Ordner)
# Quelle: deine Links im Chat.
# Unterstützte Formate pro Eintrag:
# - owner/repo
# - owner/repo@ref            (Branch/Tag/Commit-SHA)
# - owner/repo#pr:<nr>        (PR Checkout, eigener Ordner)
# - https://github.com/owner/repo
# - https://github.com/owner/repo/pull/<nr>
# - https://github.com/owner/repo/commit/<sha>
REPOS=(
  "cashmoneycolors/mega_app_launcher.py"
  "cashmoneycolors/gdp-dashboard"
  "cashmoneycolors/blueprints"
  "cashmoneycolors/Documents"
  "cashmoneycolors/gk-cli"
  "Gazi8580/quantum-avatar"
  "cashmoneycolors/AutonomousZenithOptimizer"
  "Gazi8580/GOOGLEAI-KEY-MEGA-ULTRA-ROBOTER-KI"
  "Gazi8580/quantum-avatar-cleaned"
  "Gazi8580/desktop-backup"
  "Gazi8580/quantum-avatar-v5"
  "cashmoneycolors/-MEGA-ULTRA-ROBOTER-KI"
  "https://github.com/cashmoneycolors/QuantumAvatar/pull/1"
)

WORKSPACE_PATH="$PARENT_DIR/$WORKSPACE_DIR_NAME"

mkdir -p "$WORKSPACE_PATH"

done
parse_repo_spec() {
  local spec="$1"

  # outputs (via echo): owner repo ref_type ref_value dir
  # ref_type: none|ref|pr|commit

  local owner=""
  local repo=""
  local ref_type="none"
  local ref_value=""
  local dir=""

  # URL forms
  if [[ "$spec" =~ ^https?://github\.com/([^/]+)/([^/]+)/pull/([0-9]+) ]]; then
    owner="${BASH_REMATCH[1]}"
    repo="${BASH_REMATCH[2]}"
    ref_type="pr"
    ref_value="${BASH_REMATCH[3]}"
    dir="${repo}-pr-${ref_value}"
    echo "$owner $repo $ref_type $ref_value $dir"
    return 0
  fi
  if [[ "$spec" =~ ^https?://github\.com/([^/]+)/([^/]+)/commit/([0-9a-fA-F]{7,40}) ]]; then
    owner="${BASH_REMATCH[1]}"
    repo="${BASH_REMATCH[2]}"
    ref_type="commit"
    ref_value="${BASH_REMATCH[3]}"
    dir="${repo}-commit-${ref_value:0:7}"
    echo "$owner $repo $ref_type $ref_value $dir"
    return 0
  fi
  if [[ "$spec" =~ ^https?://github\.com/([^/]+)/([^/]+)(/)?$ ]]; then
    owner="${BASH_REMATCH[1]}"
    repo="${BASH_REMATCH[2]}"
    dir="$repo"
    echo "$owner $repo $ref_type $ref_value $dir"
    return 0
  fi

  # owner/repo#pr:<nr>
  if [[ "$spec" =~ ^([^/]+)/([^#@]+)#pr:([0-9]+)$ ]]; then
    owner="${BASH_REMATCH[1]}"
    repo="${BASH_REMATCH[2]}"
    ref_type="pr"
    ref_value="${BASH_REMATCH[3]}"
    dir="${repo}-pr-${ref_value}"
    echo "$owner $repo $ref_type $ref_value $dir"
    return 0
  fi

  # owner/repo@ref
  if [[ "$spec" =~ ^([^/]+)/([^@#]+)@(.+)$ ]]; then
    owner="${BASH_REMATCH[1]}"
    repo="${BASH_REMATCH[2]}"
    ref_type="ref"
    ref_value="${BASH_REMATCH[3]}"
    # keep folder stable-ish; append short ref indicator
    local safe_ref
    safe_ref="${ref_value//\//-}"
    safe_ref="${safe_ref//[^A-Za-z0-9_.-]/-}"
    dir="${repo}-ref-${safe_ref}"
    echo "$owner $repo $ref_type $ref_value $dir"
    return 0
  fi

  # owner/repo
  if [[ "$spec" =~ ^([^/]+)/([^/]+)$ ]]; then
    owner="${BASH_REMATCH[1]}"
    repo="${BASH_REMATCH[2]}"
    dir="$repo"
    echo "$owner $repo $ref_type $ref_value $dir"
    return 0
  fi

  echo ""; return 1
}

declare -A _seen_dir
UNIQUE_SPECS=()
for spec in "${REPOS[@]}"; do
  parsed="$(parse_repo_spec "$spec" || true)"
  if [[ -z "$parsed" ]]; then
    echo "❌ Ungültiger Repo-Eintrag: $spec"
    exit 1
  fi
  read -r owner repo ref_type ref_value dir <<<"$parsed"
  # Dedupe nur nach Ziel-Ordner (damit gleiche Repo-Namen/PRs nicht kollidieren)
  if [[ -z "${_seen_dir[$dir]+x}" ]]; then
    _seen_dir[$dir]=1
    UNIQUE_SPECS+=("$spec")
  fi

clone_repo() {
  local spec="$1"
  local parsed
  parsed="$(parse_repo_spec "$spec")"
  read -r owner repo ref_type ref_value dir <<<"$parsed"
  local url="https://github.com/$owner/$repo.git"
  local target="$PARENT_DIR/$dir"

  if [[ -d "$target/.git" ]]; then
    echo "✅ Skip: $dir already cloned"
    return 0
  fi

  echo "⬇️  Cloning $url"
  git clone "$url" "$target"

  if [[ "$ref_type" == "ref" ]]; then
    echo "↪️  Checkout ref: $ref_value ($dir)"
    (cd "$target" && git checkout "$ref_value")
  elif [[ "$ref_type" == "commit" ]]; then
    echo "↪️  Checkout commit: $ref_value ($dir)"
    (cd "$target" && git checkout "$ref_value")
  elif [[ "$ref_type" == "pr" ]]; then
    echo "↪️  Fetch/Checkout PR #$ref_value ($dir)"
    (cd "$target" && git fetch origin "pull/$ref_value/head:pr-$ref_value" && git checkout "pr-$ref_value")
  fi
}

for spec in "${UNIQUE_SPECS[@]}"; do
  clone_repo "$spec" || {
    echo "⚠️  Konnte Repo nicht klonen: $spec"
    exit 1
  }
done

# Workspace-Datei erzeugen (oder überschreiben)
{
  echo '{'
  echo '  "folders": ['
  for i in "${!UNIQUE_SPECS[@]}"; do
    spec="${UNIQUE_SPECS[$i]}"
    parsed="$(parse_repo_spec "$spec")"
    read -r owner repo ref_type ref_value dir <<<"$parsed"
    comma=","
    if [[ $i -eq $((${#UNIQUE_SPECS[@]} - 1)) ]]; then comma=""; fi
    echo "    { \"path\": \"../$dir\" }$comma"
  done
  echo '  ],'
  echo '  "settings": {'
  echo '    "files.exclude": {'
  echo '      "**/bin": true,'
  echo '      "**/obj": true,'
  echo '      "**/node_modules": true'
  echo '    }'
  echo '  }'
  echo '}'
} > "$WORKSPACE_FILE_NAME"

echo ""
echo "🚀 Öffne VS Code Workspace:"
echo "   cd $PARENT_DIR/$WORKSPACE_DIR_NAME"
echo "   code $WORKSPACE_FILE_NAME"
echo "   code-insiders $WORKSPACE_FILE_NAME"
echo ""
echo "Hinweis: Die Workspace-Datei erwartet, dass alle Repos"
echo "als Geschwister-Verzeichnisse geclont wurden."
echo ""
