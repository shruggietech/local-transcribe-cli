import pathlib
import pytest
from local_transcribe_cli.cli import format_timestamp, iter_audio_files

def test_format_timestamp():
    # 0 seconds
    assert format_timestamp(0) == "00:00:00,000"
    # 1.5 seconds
    assert format_timestamp(1.5) == "00:00:01,500"
    # 1 minute 1.001 seconds
    assert format_timestamp(61.001) == "00:01:01,001"
    # 1 hour
    assert format_timestamp(3600) == "01:00:00,000"
    # Complex
    assert format_timestamp(3661.555) == "01:01:01,555"

def test_iter_audio_files(tmp_path):
    # Create dummy files
    (tmp_path / "test.wav").touch()
    (tmp_path / "test.mp3").touch()
    (tmp_path / "ignore.txt").touch()
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / "nested.flac").touch()

    # Test finding audio files
    patterns = ["*.wav", "*.mp3", "*.flac"]
    # Note: glob in iter_audio_files is not recursive unless pattern is recursive
    # The current implementation uses root.glob(pat). 
    # If we want recursive, we need "**/*.wav" etc.
    # Let's check the implementation of iter_audio_files in cli.py
    # It takes a list of patterns and does root.glob(pat).
    
    files = iter_audio_files(tmp_path, patterns)
    filenames = {f.name for f in files}
    assert "test.wav" in filenames
    assert "test.mp3" in filenames
    assert "ignore.txt" not in filenames
    # nested.flac won't be found unless we pass recursive pattern or the function handles it.
    # The current CLI implementation is non-recursive by default unless pattern has **.
    assert "nested.flac" not in filenames

def test_iter_audio_files_recursive(tmp_path):
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / "nested.wav").touch()
    
    patterns = ["**/*.wav"]
    files = iter_audio_files(tmp_path, patterns)
    filenames = {f.name for f in files}
    assert "nested.wav" in filenames
