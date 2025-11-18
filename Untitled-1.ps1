tools/install-aishell.ps1# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

#Requires -Version 7.4.6
[CmdletBinding(DefaultParameterSetName = "Install")]
param(
    [Parameter(HelpMessage = "Specify the version to install, e.g. 'v1.0.0-preview.2'", ParameterSetName = "Install")]
    [ValidatePattern("^v\d+\.\d+\.\d+(-\w+\.\d{1,2})?$")]
    [string] $Version,

    [Parameter(HelpMessage = "Specify this parameter to uninstall AI Shell", ParameterSetName = "Uninstall")]
    [switch] $Uninstall
)

$Script:MacSymbolicLink = '/usr/local/bin/aish'
$Script:MacInstallationLocation = "/usr/local/AIShell"
$Script:WinInstallationLocation = "$env:LOCALAPPDATA\Programs\AIShell"
$Script:InstallLocation = $null
$Script:PackageURL = $null
$Script:ModuleVersion = $null
$Script:NewPSRLInstalled = $false
$Script:PSRLDependencyMap = @{
    '1.0.4-preview4' = '2.4.2-beta2'
    '1.0.6-preview6' = '2.4.3-beta3'
}

function Resolve-Environment {
    if ($PSVersionTable.PSVersion -lt [version]"7.4.6") {
        throw "PowerShell v7.4.6 or higher is required for using the AIShell module. You can download it at https://github.com/PowerShell/PowerShell/releases/tag/v7.4.6 "
    }
    if ($IsLinux) {
        throw "Sorry, this install script is only compatible with Windows and macOS. If you want to install on Linux, please download the package directly from the GitHub repo at aka.ms/AIShell-Repo."
    }

    ($platShortName, $platFullName, $pkgExt, $Script:InstallLocation) = if ($IsWindows) {
        'win', 'Windows', 'zip', $Script:WinInstallationLocation
    } else {
        'osx', 'macOS', 'tar.gz', $Script:MacInstallationLocation
    }

    if ($Uninstall) {
        return
    }

    $architecture = [System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture.ToString()
    if ($architecture -notin @('X86', 'X64', 'Arm64')) {
        throw "AI Shell doesn't support the $architecture architecture on $platFullName."
    }

    $tags = (Invoke-RestMethod -Uri "https://api.github.com/repos/PowerShell/AIShell/tags" -ErrorAction Stop).name
    if ($Version -and $Version -notin $tags) {
        throw "The specified version '$Version' doesn't exist. Available versions are: $($tags -join ', ')"
    }

    $tagToUse = [string]::IsNullOrEmpty($Version) ? $tags[0] : $Version
    $appVersion = $tagToUse.TrimStart('v')

    $Script:PackageURL = "https://github.com/PowerShell/AIShell/releases/download/${tagToUse}/AIShell-${appVersion}-${platShortName}-$($architecture.ToLower()).${pkgExt}"

    $dashIndex = $appVersion.IndexOf('-')
    $Script:ModuleVersion = if ($dashIndex -eq -1) {
        throw "Not implemented for stable releases."
    } else {
        $previewLabel = $appVersion.Substring($dashIndex + 1)
        $previewDigit = $previewLabel.Substring($previewLabel.LastIndexOf('.') + 1)
        $patchDotIndex = $appVersion.LastIndexOf('.', $dashIndex)
        $appVersion.Substring(0, $patchDotIndex) + ".$previewDigit-" + $previewLabel.Replace('.', '')
    }
}

function Install-AIShellApp { … }
# (lasse den restlichen Funktionsblock unverändert wie im gelieferten Skript)