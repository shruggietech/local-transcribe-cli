<#
.SYNOPSIS
    Updates the local-transcribe-cli environment.

.DESCRIPTION
    This script updates an existing installation of local-transcribe-cli.
    It performs the following actions:
    1. Checks if the project is already installed (verifies .venv exists).
    2. Pulls the latest changes from the remote git repository.
    3. Updates Python dependencies from requirements.txt.

    If the project is not installed (no .venv found), the script will exit with an error.
    Use InstallLocalTranscribe.ps1 for fresh installations.

.PARAMETER Help
    Print the script help text to the terminal and exit.

.EXAMPLE
    # Standard update:
    .\scripts\UpdateLocalTranscribe.ps1

.EXAMPLE
    # View help documentation:
    .\scripts\UpdateLocalTranscribe.ps1 -Help
#>

param(
    [switch]$Help
)

$ErrorActionPreference = "Stop"

# Catch help text requests
if ($Help) {
    Get-Help $MyInvocation.MyCommand.Path -Detailed -ErrorAction SilentlyContinue
    exit 0
}

# Resolve project root (repo root == parent of scripts/)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
Set-Location $projectRoot

Write-Host "[local-transcribe] Project root: $projectRoot"

$venvPath   = Join-Path $projectRoot ".venv"
$venvPython = Join-Path $venvPath "Scripts\python.exe"
$reqFile    = Join-Path $projectRoot "requirements.txt"

# 1. Check for existing installation
if (-not (Test-Path $venvPython)) {
    Write-Error "[local-transcribe] Virtual environment not found at $venvPath."
    Write-Error "[local-transcribe] Please run '.\scripts\InstallLocalTranscribe.ps1' to perform a fresh install."
    exit 1
}

# 2. Update from Git
if (Test-Path ".git") {
    if (Get-Command git -ErrorAction SilentlyContinue) {
        Write-Host "[local-transcribe] Pulling latest changes from GitHub..."
        try {
            git pull
        }
        catch {
            Write-Warning "[local-transcribe] Git pull failed. Continuing with current files..."
            Write-Warning $_
        }
    } else {
        Write-Warning "[local-transcribe] Git not found. Skipping update."
    }
} else {
    Write-Host "[local-transcribe] Not a git repository. Skipping git pull."
}

# 3. Update Dependencies
Write-Host "[local-transcribe] Updating dependencies from requirements.txt..."
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r $reqFile
& $venvPython -m pip install -e .

Write-Host "[local-transcribe] Update complete."
