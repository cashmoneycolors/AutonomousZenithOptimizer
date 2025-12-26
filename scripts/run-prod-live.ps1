param(
    [Parameter(Mandatory=$true)]
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
$env:AZO_QML_ENDPOINT = $QmlEndpoint

dotnet run --project $project -c Release --no-build
