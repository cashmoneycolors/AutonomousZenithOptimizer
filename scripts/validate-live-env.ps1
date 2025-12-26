param(
    [string]$SettingsPath
)

$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot 'load-dotenv.ps1')

function Require-Env {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Reason
    )

    $val = (Get-Item -Path "Env:$Name" -ErrorAction SilentlyContinue).Value

    if ([string]::IsNullOrWhiteSpace($val)) {
        return @{ Name = $Name; Reason = $Reason }
    }

    $trim = $val.Trim()
    # Treat common template placeholders as missing
    if ($trim -match '^your_.+_here$') {
        return @{ Name = $Name; Reason = "$Reason (placeholder)" }
    }
    if ($trim -match '^https?://dein-') {
        return @{ Name = $Name; Reason = "$Reason (placeholder)" }
    }
    if ($trim -match '^https?://<.+>$') {
        return @{ Name = $Name; Reason = "$Reason (placeholder)" }
    }

    return $null
}

function Try-ReadJson {
    param([string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) { return $null }
    if (-not (Test-Path -LiteralPath $Path)) { return $null }

    try {
        return (Get-Content -LiteralPath $Path -Raw -ErrorAction Stop) | ConvertFrom-Json
    } catch {
        Write-Host "[WARN] settings.json ist nicht parsebar, skippe feature-genaue Checks." -ForegroundColor Yellow
        return $null
    }
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
if ([string]::IsNullOrWhiteSpace($SettingsPath)) {
    $SettingsPath = Join-Path $repoRoot 'settings.json'
}

$settings = Try-ReadJson -Path $SettingsPath

$missing = @()

# Minimal required for .NET LiveMode
$missing += Require-Env -Name 'AZO_QML_ENDPOINT' -Reason 'QML Endpoint (LiveMode)'

# Validate endpoint scheme quickly
if (-not [string]::IsNullOrWhiteSpace($env:AZO_QML_ENDPOINT)) {
    try {
        $uri = [Uri]$env:AZO_QML_ENDPOINT
        if ($uri.Scheme -ne 'http' -and $uri.Scheme -ne 'https') {
            throw "Ungültiges Scheme: $($uri.Scheme)"
        }
    } catch {
        throw "AZO_QML_ENDPOINT ist keine gültige http(s) URL: '$env:AZO_QML_ENDPOINT'"
    }
}

# Optional groups based on local settings.json (if present)
if ($null -ne $settings) {
    # LLM
    if ($settings.API.OpenRouter.Enabled -eq $true) {
        $missing += Require-Env -Name 'OPENROUTER_API_KEY' -Reason 'API.OpenRouter.Enabled=true'
    }
    if ($settings.API.Gemini.Enabled -eq $true) {
        $missing += Require-Env -Name 'GEMINI_API_KEY' -Reason 'API.Gemini.Enabled=true'
    }

    # Alerts
    if ($settings.Alerts.Telegram.Enabled -eq $true) {
        $missing += Require-Env -Name 'TELEGRAM_BOT_TOKEN' -Reason 'Alerts.Telegram.Enabled=true'
        $missing += Require-Env -Name 'TELEGRAM_CHAT_ID' -Reason 'Alerts.Telegram.Enabled=true'
    }
    if ($settings.Alerts.Discord.Enabled -eq $true) {
        $missing += Require-Env -Name 'DISCORD_WEBHOOK_URL' -Reason 'Alerts.Discord.Enabled=true'
    }

    # NiceHash: if any set via env or settings, require all three.
    $nhKey = $settings.Pools.NiceHash.ApiKey
    $nhSecret = $settings.Pools.NiceHash.ApiSecret
    $nhOrg = $settings.Pools.NiceHash.OrganizationId

    $hasAnyNiceHash = (
        -not [string]::IsNullOrWhiteSpace($env:POOLS_NICEHASH_API_KEY) -or
        -not [string]::IsNullOrWhiteSpace($env:POOLS_NICEHASH_API_SECRET) -or
        -not [string]::IsNullOrWhiteSpace($env:POOLS_NICEHASH_ORG_ID) -or
        -not [string]::IsNullOrWhiteSpace($nhKey) -or
        -not [string]::IsNullOrWhiteSpace($nhSecret) -or
        -not [string]::IsNullOrWhiteSpace($nhOrg)
    )

    if ($hasAnyNiceHash) {
        $missing += Require-Env -Name 'POOLS_NICEHASH_API_KEY' -Reason 'NiceHash (vollständig setzen)'
        $missing += Require-Env -Name 'POOLS_NICEHASH_API_SECRET' -Reason 'NiceHash (vollständig setzen)'
        $missing += Require-Env -Name 'POOLS_NICEHASH_ORG_ID' -Reason 'NiceHash (vollständig setzen)'
    }
} else {
    Write-Host "[INFO] settings.json nicht gefunden; prüfe nur AZO_QML_ENDPOINT." -ForegroundColor DarkGray
    Write-Host "       Für exakte Prüfungen (Telegram/Discord/LLM/NiceHash): settings.json lokal anlegen." -ForegroundColor DarkGray
}

$missing = $missing | Where-Object { $_ -ne $null }

if ($missing.Count -gt 0) {
    Write-Host "FEHLENDE ENV-VARIABLEN:" -ForegroundColor Red
    foreach ($m in $missing) {
        Write-Host "- $($m.Name)  (Grund: $($m.Reason))" -ForegroundColor Red
    }
    exit 1
}

Write-Host "OK: Live ENV vollständig (für die aktivierten Features)." -ForegroundColor Green
