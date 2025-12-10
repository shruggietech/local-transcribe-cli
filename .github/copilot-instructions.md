# Copilot Instructions for local-transcribe-cli

## Project Overview
`local-transcribe-cli` is a Windows-focused Python tool for batch-transcribing audio and video files using `faster-whisper`. It prioritizes local execution with GPU support via CTranslate2.

## Architecture & Data Flow
- **Core Logic**: `src/local_transcribe_cli/cli.py` contains the entry point, argument parsing, and transcription loop. It supports live progress bars and automatic GPU library loading.
- **Scripts**:
  - `scripts/InstallLocalTranscribe.ps1`: Handles environment setup, dependency installation, and updates.
  - `scripts/LocalTranscribe.ps1`: Primary user interface. Wraps the Python CLI and ensures the environment is ready.
  - `scripts/TestLocalTranscribe.ps1`: Runs the test suite.
- **Data Flow**: Input Directory -> Media Type Filter (Audio/Video) -> Whisper Model -> Multi-format Output (`.txt`, `.json`, `.srt`).

## Development Workflows
- **Installation/Update**:
  ```powershell
  .\scripts\InstallLocalTranscribe.ps1
  ```
- **Running Tests**:
  ```powershell
  .\scripts\TestLocalTranscribe.ps1
  ```
- **Direct Execution**:
  ```powershell
  # Activate venv first
  .\.venv\Scripts\Activate.ps1
  python -m local_transcribe_cli.cli --help
  ```
- **Dependencies**: Managed in `requirements.txt`. `pyproject.toml` defines the package structure.

## Code Conventions
- **Path Handling**: Use `pathlib.Path` exclusively over `os.path` (except for `os.add_dll_directory` on Windows).
- **Type Hinting**: Fully type-hint all functions.
- **Imports**: Group imports: standard library, third-party, local.
- **Output**: Print user-friendly status messages prefixed with `[local-transcribe]`. Use `tqdm` for progress bars.

## Key Files
- `src/local_transcribe_cli/cli.py`: Main application logic.
- `scripts/LocalTranscribe.ps1`: Main execution wrapper.
- `scripts/InstallLocalTranscribe.ps1`: Installation and update logic.
- `tests/`: Pytest test suite.
