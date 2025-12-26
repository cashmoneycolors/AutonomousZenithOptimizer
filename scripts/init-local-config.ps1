param(
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

function Is-PlaceholderValue {
    param([string]$Value)

    if ([string]::IsNullOrWhiteSpace($Value)) { return $true }

    $v = $Value.Trim()
    if ($v -match '^your_.+_here$') { return $true }
    if ($v -match '^https?://dein-') { return $true }
    if ($v -match '^https?://<.+>$') { return $true }

    return $false
}

function Read-EnvFile {
    param([string]$Path)

    $map = @{}
    if (-not (Test-Path -LiteralPath $Path)) { return $map }

    foreach ($rawLine in Get-Content -LiteralPath $Path -ErrorAction Stop) {
        $line = $rawLine.Trim()
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        if ($line.StartsWith('#')) { continue }

        $idx = $line.IndexOf('=')
        if ($idx -lt 1) { continue }

        $name = $line.Substring(0, $idx).Trim()
        $value = $line.Substring($idx + 1).Trim()
        if ([string]::IsNullOrWhiteSpace($name)) { continue }

        if ($value.StartsWith('"') -and $value.EndsWith('"')) {
            $value = $value.Substring(1, $value.Length - 2)
        } elseif ($value.StartsWith("'") -and $value.EndsWith("'")) {
            $value = $value.Substring(1, $value.Length - 2)
        }

        $map[$name] = $value
    }

    return $map
}

function Normalize-Env {
    param(
        [Parameter(Mandatory = $true)][string]$ExamplePath,
        [Parameter(Mandatory = $true)][string]$EnvPath
    )

    if (-not (Test-Path -LiteralPath $ExamplePath)) {
        throw "Fehlt: $ExamplePath"
    }

    $existing = Read-EnvFile -Path $EnvPath

    $outLines = New-Object System.Collections.Generic.List[string]
    foreach ($rawLine in Get-Content -LiteralPath $ExamplePath -ErrorAction Stop) {
        $line = $rawLine
        $trim = $line.Trim()

        if ($trim -match '^[A-Z0-9_]+\s*=') {
            $idx = $trim.IndexOf('=')
            $name = $trim.Substring(0, $idx).Trim()

            if ($existing.ContainsKey($name) -and -not (Is-PlaceholderValue -Value $existing[$name])) {
                $outLines.Add("$name=$($existing[$name])")
            } else {
                # Keep placeholder empty
                $outLines.Add("$name=")
            }
        } else {
            $outLines.Add($line)
        }
    }

    $outText = ($outLines -join "`n") + "`n"
    Set-Content -LiteralPath $EnvPath -Value $outText -Encoding utf8 -Force
}

function Ensure-ValidSettingsJson {
    param(
        [Parameter(Mandatory = $true)][string]$ExamplePath,
        [Parameter(Mandatory = $true)][string]$SettingsPath
    )

    if (-not (Test-Path -LiteralPath $ExamplePath)) {
        throw "Fehlt: $ExamplePath"
    }

    if (-not (Test-Path -LiteralPath $SettingsPath)) {
        Copy-Item -LiteralPath $ExamplePath -Destination $SettingsPath -Force
        return
    }

    try {
        Get-Content -LiteralPath $SettingsPath -Raw -ErrorAction Stop | ConvertFrom-Json | Out-Null
    } catch {
        $bak = "$SettingsPath.local.bak"
        Copy-Item -LiteralPath $SettingsPath -Destination $bak -Force
        Copy-Item -LiteralPath $ExamplePath -Destination $SettingsPath -Force
    }
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
$envExample = Join-Path $repoRoot '.env.example'
$envPath = Join-Path $repoRoot '.env'
$settingsExample = Join-Path $repoRoot 'settings.example.json'
$settingsPath = Join-Path $repoRoot 'settings.json'

# Ensure settings.json is present and parseable (used by validate-live-env.ps1)
Ensure-ValidSettingsJson -ExamplePath $settingsExample -SettingsPath $settingsPath

# Normalize .env to include all keys from .env.example, preserving existing non-placeholder values
Normalize-Env -ExamplePath $envExample -EnvPath $envPath

Write-Host "[INIT] Local config ready (.env + settings.json)." -ForegroundColor DarkGray
