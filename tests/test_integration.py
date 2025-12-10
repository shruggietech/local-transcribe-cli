import pathlib
import pytest
from local_transcribe_cli.cli import transcribe_file
from unittest.mock import MagicMock

# We only run this if the data file exists
DATA_DIR = pathlib.Path(__file__).parent / "data"
JFK_WAV = DATA_DIR / "jfk.wav"

@pytest.mark.skipif(not JFK_WAV.exists(), reason="jfk.wav not found")
def test_transcribe_jfk_real_model(tmp_path):
    """
    Integration test that actually loads a small model and transcribes a real file.
    This ensures the whole pipeline works.
    We use 'tiny' model to be fast.
    """
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        pytest.skip("faster-whisper not installed")

    # Use tiny model for speed in tests
    # device="cpu" to ensure it runs everywhere
    # compute_type="int8" for speed
    try:
        model = WhisperModel("tiny", device="cpu", compute_type="int8")
    except Exception as e:
        pytest.skip(f"Failed to load model: {e}")

    output_dir = tmp_path / "out"
    
    transcribe_file(
        model=model,
        audio_path=JFK_WAV,
        output_dir=output_dir,
        language="en",
        output_formats=["txt", "json", "srt"]
    )

    # Check outputs
    base = JFK_WAV.stem
    txt_path = output_dir / f"{base}.txt"
    json_path = output_dir / f"{base}.json"
    srt_path = output_dir / f"{base}.srt"

    assert txt_path.exists()
    assert json_path.exists()
    assert srt_path.exists()

    # Check content roughly
    txt_content = txt_path.read_text(encoding="utf-8").lower()
    # JFK quote: "And so, my fellow Americans: ask not what your country can do for you--ask what you can do for your country."
    assert "fellow americans" in txt_content
    assert "ask not" in txt_content
