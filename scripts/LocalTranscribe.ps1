<#
.SYNOPSIS
    Convenience wrapper for the local-transcribe CLI.

.DESCRIPTION
    Ensures a local virtual environment exists, installs dependencies
    from requirements.txt if needed, and then calls the Python entry
    point "local-transcribe" with the provided options.

.PARAMETER AudioDir
    Directory containing audio files to transcribe. Default: project root.

.PARAMETER OutDir
    Directory where transcript files will be written. Default: "transcripts" under project root.

.PARAMETER Pattern
    Filename glob pattern for input files. Optional.
    If provided, this is ADDITIVE to the default extensions for the selected MediaType.
    Example: "*.xyz"

.PARAMETER Model
    Whisper model name (e.g. "large-v3"). Default: "large-v3".

.PARAMETER Language
    Language hint (e.g. "en"). Default: "en".

.PARAMETER Device
    Compute device: "auto", "cpu", or "cuda". Default: "auto".

.PARAMETER ComputeType
    CTranslate2 compute type (e.g. "auto", "int8", "float16"). Default: "auto".

.PARAMETER OutputFormats
    List of output formats to generate. Options: "txt", "json", "srt".
    Default: "txt", "json".

.PARAMETER MediaType
    Type of media to process. Options: "audio", "video", "all".
    Default: "audio".
    - audio: targets common audio extensions (.mp3, .wav, .ogg, etc.)
    - video: targets common video extensions (.mp4, .mkv, .mov, etc.)
    - all: targets both audio and video extensions.

.PARAMETER Help
    Print the script help text to the terminal and exit.

.EXAMPLE
    # Basic usage with Telegram-exported voice messages (defaults to audio):
    .\scripts\LocalTranscribe.ps1 `
        -AudioDir 'C:\Telegram\TylerVoice' `
        -OutDir '.\transcripts'

.EXAMPLE
    # Transcribe video files to SRT subtitles:
    .\scripts\LocalTranscribe.ps1 `
        -AudioDir 'C:\Videos' `
        -MediaType 'video' `
        -OutputFormats 'srt'

.EXAMPLE
    # Force CPU with int8 quantization:
    .\scripts\LocalTranscribe.ps1 `
        -AudioDir 'C:\Telegram\TylerVoice' `
        -Device 'cpu' `
        -ComputeType 'int8'
#>

param(
    [string]$AudioDir    = ".",
    [string]$OutDir      = "transcripts",
    [string]$Pattern     = $null,
    [string]$Model       = "large-v3",
    [string]$Language    = "en",
    [ValidateSet("auto","cpu","cuda")]
    [string]$Device      = "auto",
    [string]$ComputeType = "auto",
    [string[]]$OutputFormats = @("txt", "json"),
    [ValidateSet("audio","video","all")]
    [string]$MediaType   = "audio",
    [switch]$Help
)

$ErrorActionPreference = "Stop"

# Catch help text requests
if ($Help) {
    Get-Help $MyInvocation.MyCommand.Path -Detailed
    exit
}

# Resolve project root (repo root == parent of scripts/)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
Set-Location $projectRoot

$venvPath   = Join-Path $projectRoot ".venv"
$venvPython = Join-Path $venvPath "Scripts\python.exe"
$reqFile    = Join-Path $projectRoot "requirements.txt"

Write-Host "[local-transcribe] Project root: $projectRoot"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "No 'python' on PATH. Install Python 3.9+ or configure pyshim first."
}

# Create venv if missing
if (-not (Test-Path $venvPython)) {
    Write-Host "[local-transcribe] Creating virtual environment at $venvPath..."
    python -m venv ".venv"

    if (-not (Test-Path $venvPython)) {
        throw "Failed to create virtual environment; expected '$venvPython'."
    }

    Write-Host "[local-transcribe] Installing dependencies from requirements.txt..."
    & $venvPython -m pip install --upgrade pip
    & $venvPython -m pip install -r $reqFile
}

# Build argument list for the Python CLI
$argv = @(
    "-m", "local_transcribe_cli.cli",
    "--input-dir", $AudioDir,
    "--output-dir", $OutDir,
    "--model", $Model,
    "--language", $Language,
    "--device", $Device,
    "--compute-type", $ComputeType,
    "--output-formats", $OutputFormats,
    "--media-type", $MediaType
)

if (-not [string]::IsNullOrWhiteSpace($Pattern)) {
    $argv += "--pattern"
    $argv += $Pattern
}

Write-Host "[local-transcribe] Using venv interpreter: $venvPython"
Write-Host "[local-transcribe] Invoking CLI..."
& $venvPython @argv
