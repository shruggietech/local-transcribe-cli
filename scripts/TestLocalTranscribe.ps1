<#
.SYNOPSIS
    Runs the test suite for local-transcribe-cli.

.DESCRIPTION
    This script executes the automated tests located in the 'tests' directory
    using the project's virtual environment. It wraps 'pytest' to provide
    a clean execution environment and user-friendly status reporting.

.PARAMETER Help
    Print the script help text to the terminal and exit.

.EXAMPLE
    # Run all tests:
    .\scripts\TestLocalTranscribe.ps1

.EXAMPLE
    # View help:
    .\scripts\TestLocalTranscribe.ps1 -Help
#>

param(
    [switch]$Help
)

$ErrorActionPreference = "Stop"

# Catch help text requests
if ($Help) {
    Get-Help $MyInvocation.MyCommand.Path -Detailed
    exit 0
}

# Resolve project root (repo root == parent of scripts/)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
Set-Location $projectRoot

$venvPath   = Join-Path $projectRoot ".venv"
$venvPython = Join-Path $venvPath "Scripts\python.exe"

Write-Host "[local-transcribe] Project root: $projectRoot"

# 1. Check for Virtual Environment
if (-not (Test-Path $venvPython)) {
    Write-Error "[local-transcribe] Virtual environment not found at $venvPath."
    Write-Host "Please run '.\scripts\InstallLocalTranscribe.ps1' first to set up the environment." -ForegroundColor Yellow
    exit 1
}

# 2. Check for pytest
Write-Host "[local-transcribe] Checking test dependencies..."
$pytestCheck = & $venvPython -c "import pytest; print('ok')" 2>$null
if ($pytestCheck -ne "ok") {
    Write-Error "[local-transcribe] 'pytest' is not installed in the virtual environment."
    Write-Host "Please run '.\scripts\InstallLocalTranscribe.ps1' to install development dependencies." -ForegroundColor Yellow
    exit 1
}

# 3. Run Tests
Write-Host "[local-transcribe] Starting test suite..." -ForegroundColor Cyan
Write-Host "[local-transcribe] Running pytest with short tracebacks..." -ForegroundColor Gray

# We use --tb=short to minimize stack trace noise ("nasty garbage")
# We use -v (verbose) to list test names so the user sees progress
$testCmd = @("-m", "pytest", "tests", "--tb=short", "-v")

try {
    & $venvPython $testCmd
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n[local-transcribe] SUCCESS: All tests passed!" -ForegroundColor Green
        exit 0
    } elseif ($LASTEXITCODE -eq 5) {
        # Exit code 5 means no tests were collected
        Write-Warning "[local-transcribe] No tests were found in the 'tests' directory."
        exit 0
    } else {
        # Any other non-zero exit code means failure
        throw "Test suite failed with exit code $LASTEXITCODE."
    }
}
catch {
    Write-Host "`n[local-transcribe] FAILURE: Some tests failed." -ForegroundColor Red
    Write-Host "Review the output above to identify the specific test cases that failed." -ForegroundColor Yellow
    Write-Host "Note: 'F' denotes a failure, '.' denotes a pass." -ForegroundColor Gray
    exit 1
}
