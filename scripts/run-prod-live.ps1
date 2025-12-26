param(
    [string]$QmlEndpoint,

    [switch]$Build
)

$ErrorActionPreference = 'Stop'

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
$solution = Join-Path $repoRoot 'AutonomousZenithOptimizer.sln'
$project  = Join-Path $repoRoot 'ZenithCoreSystem.csproj'

if ($Build) {
    dotnet build $solution -c Release
}

$env:DOTNET_ENVIRONMENT = 'Production'
$env:AZO_LIVE_MODE = 'true'

# Ensure local config files exist/are valid
& (Join-Path $PSScriptRoot 'init-local-config.ps1')

# Load local .env (never overrides already-set env vars)
. (Join-Path $PSScriptRoot 'load-dotenv.ps1')

if (-not [string]::IsNullOrWhiteSpace($QmlEndpoint)) {
    $env:AZO_QML_ENDPOINT = $QmlEndpoint
}

# Fail-fast before starting
& (Join-Path $PSScriptRoot 'validate-live-env.ps1')

dotnet run --project $project -c Release --no-build
