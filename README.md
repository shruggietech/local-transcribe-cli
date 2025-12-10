# local-transcribe-cli

A Windows-focused tool for batch-transcribing audio and video files using [faster-whisper](https://github.com/SYSTRAN/faster-whisper). This tool prioritizes local execution with GPU support via [CTranslate2](https://github.com/OpenNMT/CTranslate2).

## Features

- **Batch Processing**: Transcribe all audio/video files in a directory at once.
- **Multi-Format Output**: Generate `txt` (plain text), `json` (structured data), and `srt` (subtitles).
- **Media Support**: Automatically targets common audio (`.mp3`, `.wav`, etc.) and video (`.mp4`, `.mkv`, etc.) extensions.
- **High Accuracy**: Uses Whisper `large-v3` model by default.
- **Live Progress**: Shows a progress bar with time estimation for each file.
- **GPU Acceleration**: Automatically installs and uses NVIDIA CUDA libraries if a compatible GPU is found.
- **Self-Healing**: Installation scripts automatically fix missing dependencies or virtual environments.

## Prerequisites

- **OS**: Windows 10 or 11.
- **Shell**: PowerShell 5.1 or 7+ (pwsh).
- **Python**: Python 3.9 or newer installed and on your PATH.
- **Git**: Required for downloading and updating the tool.
- **(Optional) GPU**: An NVIDIA GPU is highly recommended for speed. The tool will attempt to install the necessary CUDA 12 libraries automatically.

## Installation & Updates

We provide a single PowerShell script to handle initial installation, environment setup, and updates.

1.  **Clone the repository**:
    ```powershell
    git clone https://github.com/shruggietech/local-transcribe-cli.git
    cd local-transcribe-cli
    ```

2.  **Run the Installer**:
    This script will create a virtual environment (`.venv`), install all dependencies, and pull the latest code from GitHub.
    ```powershell
    .\scripts\InstallLocalTranscribe.ps1
    ```

    > **Tip**: Run this script again at any time to update the tool to the latest version.

## Usage

The primary way to use this tool is via the `LocalTranscribe.ps1` wrapper script.

### Basic Audio Transcription
Transcribe all audio files in a specific folder to text and JSON (default):

```powershell
.\scripts\LocalTranscribe.ps1 -AudioDir "C:\Users\You\Documents\VoiceNotes"
```

### Video to Subtitles
Generate `.srt` subtitle files for a folder of videos:

```powershell
.\scripts\LocalTranscribe.ps1 `
    -AudioDir "C:\Videos\Recordings" `
    -MediaType "video" `
    -OutputFormats "srt"
```

### Transcribe Everything
Process both audio and video files, generating all output formats:

```powershell
.\scripts\LocalTranscribe.ps1 `
    -AudioDir "C:\Media\Mixed" `
    -MediaType "all" `
    -OutputFormats "txt", "json", "srt"
```

### PowerShell Parameters

| Parameter | Description | Default |
| :--- | :--- | :--- |
| `-AudioDir` | Directory containing input files. | `.` (Current Dir) |
| `-OutDir` | Directory to write transcripts to. | `.\transcripts` |
| `-MediaType` | Files to target: `audio`, `video`, or `all`. | `audio` |
| `-OutputFormats` | Formats to generate: `txt`, `json`, `srt`. | `txt`, `json` |
| `-Model` | Whisper model size (e.g., `medium`, `large-v3`). | `large-v3` |
| `-Device` | Compute device: `auto`, `cuda`, or `cpu`. | `auto` |
| `-Language` | Spoken language code (e.g., `en`, `fr`). | `en` |
| `-Pattern` | Custom glob pattern (e.g., `*.m4a`). Additive to MediaType. | `$null` |

## Testing

To ensure the tool is working correctly on your system, you can run the included test suite. This will verify dependency installation and run a small integration test.

```powershell
.\scripts\TestLocalTranscribe.ps1
```

## Advanced Usage (Python CLI)

Power users can interact directly with the Python package inside the virtual environment.

**Activate the environment:**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Run via Module:**
```powershell
python -m local_transcribe_cli.cli --help
```

**Run via Console Script:**
```powershell
local-transcribe --input-dir "C:\Audio" --model medium
```

### Python Arguments
- `--input-dir`, `-i`: Input directory.
- `--output-dir`, `-o`: Output directory.
- `--media-type`: `audio`, `video`, or `all`.
- `--output-formats`: Space-separated list (e.g., `txt srt`).
- `--model`, `-m`: Whisper model name.
- `--device`: `cuda` or `cpu`.
- `--compute-type`: Quantization type (e.g., `int8`, `float16`).

## Troubleshooting

**"Script is not digitally signed" error:**
You may need to change your PowerShell execution policy to allow local scripts:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**"ModuleNotFoundError" or Import Errors:**
Run the install script again to repair the environment:
```powershell
.\scripts\InstallLocalTranscribe.ps1
```

**Slow Performance:**
Ensure you are running on a machine with a GPU and that `-Device` is set to `auto` or `cuda`. If you lack a GPU, try using a smaller model (`-Model medium` or `-Model small`) and `int8` quantization (`-ComputeType int8`).

## For contributors

The project-level interpreter pin for [pyshim](https://github.com/shruggietech/pyshim) lives in `.python-version`:

```text
py:3.12
```

Dependencies are listed in `requirements.txt`, and the main entry point is `src/local_transcribe_cli/cli.py`.
