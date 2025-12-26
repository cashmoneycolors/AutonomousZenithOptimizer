param(
    [string]$EnvPath
)

$ErrorActionPreference = 'Stop'

function Set-EnvIfMissing {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Value
    )

    if ([string]::IsNullOrWhiteSpace($Name)) { return }
    if ($env:$Name) { return }

    $env:$Name = $Value
}

if ([string]::IsNullOrWhiteSpace($EnvPath)) {
    # Default: repo root .env
    $repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
    $EnvPath = Join-Path $repoRoot '.env'
}

if (-not (Test-Path -LiteralPath $EnvPath)) {
    $repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
    $examplePath = Join-Path $repoRoot '.env.example'

    if (Test-Path -LiteralPath $examplePath) {
        Copy-Item -LiteralPath $examplePath -Destination $EnvPath -Force
        throw "Keine .env gefunden. Ich habe $EnvPath aus .env.example erzeugt. Bitte Keys lokal eintragen und erneut starten."
    }

    Write-Warning "Keine .env gefunden unter: $EnvPath"
    return
}

$loaded = 0
foreach ($rawLine in Get-Content -LiteralPath $EnvPath -ErrorAction Stop) {
    $line = $rawLine.Trim()

    if ([string]::IsNullOrWhiteSpace($line)) { continue }
    if ($line.StartsWith('#')) { continue }

    $idx = $line.IndexOf('=')
    if ($idx -lt 1) { continue }

    $name = $line.Substring(0, $idx).Trim()
    $value = $line.Substring($idx + 1).Trim()

    if ($value.StartsWith('"') -and $value.EndsWith('"')) {
        $value = $value.Substring(1, $value.Length - 2)
    } elseif ($value.StartsWith("'") -and $value.EndsWith("'")) {
        $value = $value.Substring(1, $value.Length - 2)
    }

    if ([string]::IsNullOrWhiteSpace($name)) { continue }

    # Niemals echte ENV überschreiben (damit CI/Secrets-Manager Vorrang hat)
    if ($env:$name) { continue }

    Set-EnvIfMissing -Name $name -Value $value
    $loaded++
}

if ($loaded -gt 0) {
    Write-Host "[ENV] Loaded $loaded values from $EnvPath" -ForegroundColor DarkGray
}
