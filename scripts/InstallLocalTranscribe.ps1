<#
.SYNOPSIS
    Installs or updates the local-transcribe-cli environment.

.DESCRIPTION
    This script automates the setup and update process for the local-transcribe-cli tool.
    It performs the following actions:
    1. Pulls the latest changes from the remote git repository (if the directory is a git repo).
    2. Checks for a valid Python installation.
    3. Creates or updates the Python virtual environment (.venv) in the project root.
    4. Installs or updates Python dependencies from requirements.txt.

.PARAMETER Help
    Print the script help text to the terminal and exit.

.EXAMPLE
    # Standard installation or update:
    .\scripts\InstallLocalTranscribe.ps1

.EXAMPLE
    # View help documentation:
    .\scripts\InstallLocalTranscribe.ps1 -Help
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

# 1. Update from Git
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

# 2. Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "No 'python' on PATH. Install Python 3.9+ or configure pyshim first."
}

$venvPath   = Join-Path $projectRoot ".venv"
$venvPython = Join-Path $venvPath "Scripts\python.exe"
$reqFile    = Join-Path $projectRoot "requirements.txt"

# 3. Create/Update Venv
if (-not (Test-Path $venvPython)) {
    Write-Host "[local-transcribe] Creating virtual environment at $venvPath..."
    python -m venv ".venv"
}

if (-not (Test-Path $venvPython)) {
    throw "Failed to create virtual environment; expected '$venvPython'."
}

# 4. Install Dependencies
Write-Host "[local-transcribe] Installing/Updating dependencies from requirements.txt..."
& $venvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "Pip upgrade failed." }

& $venvPython -m pip install -r $reqFile
if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed." }

& $venvPython -m pip install -e .
if ($LASTEXITCODE -ne 0) { throw "Package installation failed." }

Write-Host "[local-transcribe] Installation/Update complete."
Write-Host "[local-transcribe] You can now run: .\scripts\LocalTranscribe.ps1"
