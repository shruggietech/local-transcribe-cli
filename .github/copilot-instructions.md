# Copilot Instructions for local-transcribe-cli

## Project Overview
`local-transcribe-cli` is a Windows-focused Python tool for batch-transcribing audio files (specifically Telegram voice notes) using `faster-whisper`. It prioritizes local execution with GPU support via CTranslate2.

## Architecture & Data Flow
- **Core Logic**: `src/local_transcribe_cli/cli.py` contains the entry point, argument parsing, and transcription loop.
- **Wrapper**: `scripts/LocalTranscribe.ps1` is the primary user interface. It handles:
  - Virtual environment creation (`.venv`).
  - Dependency installation (`requirements.txt`).
  - Invoking the Python module with passed arguments.
- **Data Flow**: Input Directory -> Glob Pattern (default `*.ogg`) -> Whisper Model -> Text Output (one `.txt` per input file).

## Development Workflows
- **Bootstrapping**: Always use `scripts/LocalTranscribe.ps1` to initialize the environment.
  ```powershell
  .\scripts\LocalTranscribe.ps1 -AudioDir 'path/to/audio'
  ```
- **Direct Execution**:
  ```powershell
  # Activate venv first
  .\.venv\Scripts\Activate.ps1
  python -m local_transcribe_cli.cli --help
  ```
- **Dependencies**: Managed in `pyproject.toml` and `requirements.txt`. Keep them in sync.

## Code Conventions
- **Path Handling**: Use `pathlib.Path` exclusively over `os.path`.
- **Type Hinting**: Fully type-hint all functions (e.g., `def func(x: int) -> str:`).
- **Imports**: Group imports: standard library, third-party, local.
- **Output**: Print user-friendly status messages prefixed with `[local-transcribe]`.

## Key Files
- `src/local_transcribe_cli/cli.py`: Main application logic.
- `scripts/LocalTranscribe.ps1`: PowerShell wrapper for easy usage.
- `pyproject.toml`: Project metadata and entry point definition.
