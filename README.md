# local-transcribe-cli

Local, on-device transcription CLI built on [faster-whisper](https://github.com/SYSTRAN/faster-whisper).  
Designed for Telegram voice notes and other short recordings.

## Features

- Batch transcribe all audio files in a directory.
- Uses Whisper `large-v3` by default for high accuracy.
- GPU support via CTranslate2 (CUDA 12 + cuDNN 9 recommended). 
- Works fine with or without [pyshim](https://github.com/shruggietech/pyshim).

## Requirements

- Windows 11
- Python 3.9+ on PATH (if you use pyshim, just ensure `python` resolves correctly).
- Optional: NVIDIA GPU with CUDA 12 + cuDNN 9 for faster inference.

## Quick start

```powershell
git clone https://github.com/shruggietech/local-transcribe-cli.git
cd local-transcribe-cli
```

# Optional but recommended if you use pyshim:
Use-Python -Spec 'py:3.12'

# First run bootstraps .venv and installs dependencies:
.\scripts\Invoke-LocalTranscribe.ps1 `
    -AudioDir 'C:\Telegram\TylerVoice' `
    -OutDir '.\transcripts'

Transcripts will be written as `.txt` files into the `transcripts` folder.

## Python CLI usage

Once the virtual environment exists, you can also call the CLI directly:

```powershell
# Activate .venv manually if you prefer:
.\.venv\Scripts\Activate.ps1

# Use the console script (installed via pyproject.toml):
local-transcribe --input-dir C:\Telegram\VoiceMessages --output-dir transcripts

# Or via -m:
python -m local_transcribe_cli.cli --input-dir C:\Telegram\VoiceMessages
```

### Common Options

- `--pattern "*.ogg"` - change to `"*.wav"`, `"*.mp3"`, etc
- `--model large-v3` - swap for `medium`, `small`, etc. to use less VRAM
- `--device cuda` - force usage of the GPU; `cpu` to force CPU; `auto` to allow CTranslate2 decide
- `--compute-type int8` - run int8 quantized for faster CPU or lower VRAM useage

## For contributors

The project-level interpreter pin for [pyshim](https://github.com/shruggietech/pyshim) lives in `.python-version`:

```text
py:3.12
```

Dependencies are listed in `requirements.txt`, and the main entry point is `src/local_transcribe_cli/cli.py`.
