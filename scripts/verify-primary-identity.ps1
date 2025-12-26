[CmdletBinding(SupportsShouldProcess=$true, ConfirmImpact='Medium')]
param(
    [string]$RepoPath = (Get-Location).Path,

    [string]$PrimaryEmail = 'cashmoneycolors@gmail.com',
    [string]$PrimaryUserName = 'cashmoneycolors',
    [string]$PrimaryGitHubLogin = 'cashmoneycolors',

    [switch]$FixGit,
    [switch]$FixGh,

    [switch]$ListWindowsCredentials,
    [switch]$PurgeWindowsCredentials,
    [switch]$Force,

    [switch]$LaunchVsCode,
    [string]$VsCodeProfile = 'cashmoneycolors-primary',
    [string]$VsCodeUserDataDir = "$env:APPDATA\\Code-PrimaryOnly"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Ensure stable UTF-8 output (prevents garbled checkmarks on some Windows setups)
try {
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
} catch { }

function Write-Section([string]$Title) {
    Write-Host "" 
    Write-Host "==== $Title ===="
}

function Invoke-Checked([string]$Command) {
    Write-Host "> $Command"
    $output = & powershell -NoProfile -Command $Command 2>&1
    $exit = $LASTEXITCODE
    [pscustomobject]@{ Output = $output; ExitCode = $exit }
}

function Require-Command([string]$Name) {
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $cmd) {
        throw "Required command not found: $Name"
    }
}

Require-Command git

$repoFullPath = Resolve-Path -Path $RepoPath

Write-Section "Repo"
Write-Host "RepoPath: $repoFullPath"

Write-Section "Git identity (effective)"
$author = & git -C $repoFullPath var GIT_AUTHOR_IDENT
$committer = & git -C $repoFullPath var GIT_COMMITTER_IDENT
Write-Host "AUTHOR   : $author"
Write-Host "COMMITTER: $committer"

Write-Section "Git identity (origins)"
& git -C $repoFullPath config --show-origin --get-all user.email
& git -C $repoFullPath config --show-origin --get-all user.name

if ($FixGit) {
    Write-Section "Fix Git identity (global + remove local overrides)"

    if ($PSCmdlet.ShouldProcess("git config", "unset local user.email/user.name")) {
        & git -C $repoFullPath config --local --unset-all user.email 2>$null
        & git -C $repoFullPath config --local --unset-all user.name 2>$null
    }

    if ($PSCmdlet.ShouldProcess("git config", "set global user.email/user.name")) {
        & git config --global user.email $PrimaryEmail
        & git config --global user.name $PrimaryUserName
    }

    Write-Host "After fix:" 
    & git -C $repoFullPath var GIT_AUTHOR_IDENT
    & git -C $repoFullPath var GIT_COMMITTER_IDENT
}

Write-Section "Git remote + connectivity"
& git -C $repoFullPath remote -v
$refs = & git -C $repoFullPath ls-remote --heads origin
if (-not $refs) {
    Write-Host "WARN: ls-remote returned no refs (but may still be OK if repo empty)."
} else {
    Write-Host ($refs | Select-Object -First 10)
}

Require-Command gh
Write-Section "GitHub CLI (gh)"
$ghStatus = & gh auth status 2>&1
$ghStatus | ForEach-Object { $_ }

if ($FixGh) {
    Write-Section "Fix gh: ensure only primary account is present"
    $raw = (& gh auth status 2>&1) -join "`n"

    # Extract accounts from gh output lines like:
    # "✓ Logged in to github.com account <login> (keyring)"
    $accounts = @()
    foreach ($line in $raw -split "`n") {
        if ($line -match "Logged in to github\.com account\s+([^\s]+)\s+\(") {
            $accounts += $Matches[1]
        }
    }
    $accounts = $accounts | Select-Object -Unique

    foreach ($acct in $accounts) {
        if ($acct -ne $PrimaryGitHubLogin) {
            $msg = "gh auth logout -h github.com -u $acct"
            if ($Force -or $PSCmdlet.ShouldProcess("github.com", $msg)) {
                & gh auth logout -h github.com -u $acct
            }
        }
    }

    Write-Host "After fix:" 
    & gh auth status
}

function Get-WindowsCredentialTargets {
    $raw = (& cmdkey /list 2>&1) -join "`n"
    $targets = @()
    foreach ($line in $raw -split "`n") {
        $trim = $line.Trim()
        if ($trim -like 'Target:*') {
            $t = $trim.Substring('Target:'.Length).Trim()
            if ($t -match 'github|vscode\.github|git:https://github\.com' ) {
                $targets += $t
            }
        }
    }
    $targets | Select-Object -Unique
}

if ($ListWindowsCredentials -or $PurgeWindowsCredentials) {
    Write-Section "Windows Credential Manager (GitHub-related)"
    $targets = Get-WindowsCredentialTargets
    if (-not $targets -or $targets.Count -eq 0) {
        Write-Host "No GitHub-related Windows credentials found via cmdkey." 
    } else {
        $targets | ForEach-Object { Write-Host "- $_" }
    }

    if ($PurgeWindowsCredentials -and $targets -and $targets.Count -gt 0) {
        Write-Section "Purging Windows credentials"
        foreach ($t in $targets) {
            $action = "cmdkey /delete:$t"
            if ($Force -or $PSCmdlet.ShouldProcess("Windows Credential", $action)) {
                & cmdkey /delete:$t | Out-Null
                Write-Host "Deleted: $t"
            }
        }
    }
}

Write-Section "What remains (cannot be automated reliably)"
Write-Host "1) VS Code -> Accounts: ensure only GitHub '$PrimaryGitHubLogin' is signed in."
Write-Host "2) VS Code -> Command Palette: 'GitHub Copilot: Check Status' and confirm it shows Ready/Enabled."
Write-Host "If it says 'No subscription' or 'Blocked by organization', the fix is on GitHub/Org seat level."

if ($LaunchVsCode) {
    Write-Section "Launch VS Code (isolated Primary-only profile)"
    Require-Command code

    Write-Host "Profile       : $VsCodeProfile"
    Write-Host "User data dir  : $VsCodeUserDataDir"
    Write-Host "Repo           : $repoFullPath"
    Write-Host "" 
    Write-Host "This creates/uses a dedicated VS Code profile and user-data dir so secondary logins don't interfere." 
    Write-Host "After VS Code opens, run: GitHub Copilot: Check Status" 

    $args = @(
        '--reuse-window',
        '--profile', $VsCodeProfile,
        '--user-data-dir', $VsCodeUserDataDir,
        $repoFullPath
    )

    if ($Force -or $PSCmdlet.ShouldProcess('VS Code', ('code ' + ($args -join ' ')))) {
        & code @args | Out-Null
    }
}