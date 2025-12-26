param(
    [switch]$Build
)

$ErrorActionPreference = 'Stop'

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
$solution = Join-Path $repoRoot 'AutonomousZenithOptimizer.sln'
$project  = Join-Path $repoRoot 'ZenithCoreSystem.csproj'

if ($Build) {
    dotnet build $solution -c Release
}

$env:DOTNET_ENVIRONMENT = 'Development'
$env:AZO_LIVE_MODE = 'false'

dotnet run --project $project -c Release --no-build
