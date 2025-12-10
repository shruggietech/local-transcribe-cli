import argparse
import pytest
from unittest.mock import MagicMock, patch
from local_transcribe_cli.cli import build_arg_parser, main

def test_arg_parser_defaults():
    parser = build_arg_parser()
    args = parser.parse_args([])
    assert args.input_dir == "."
    assert args.output_dir == "transcripts"
    assert args.media_type == "audio"
    assert args.model == "large-v3"
    assert args.device == "auto"

def test_arg_parser_custom():
    parser = build_arg_parser()
    args = parser.parse_args([
        "--input-dir", "in",
        "--output-dir", "out",
        "--media-type", "video",
        "--model", "tiny",
        "--device", "cpu"
    ])
    assert args.input_dir == "in"
    assert args.output_dir == "out"
    assert args.media_type == "video"
    assert args.model == "tiny"
    assert args.device == "cpu"

@patch("local_transcribe_cli.cli.WhisperModel")
@patch("local_transcribe_cli.cli.iter_audio_files")
def test_main_no_files(mock_iter, mock_model, capsys):
    mock_iter.return_value = []
    
    # main() returns an int, it does not raise SystemExit (that happens in if __name__ == "__main__")
    ret = main([])
    assert ret == 1
    
    captured = capsys.readouterr()
    assert "No files matching patterns" in captured.out

@patch("local_transcribe_cli.cli.WhisperModel")
@patch("local_transcribe_cli.cli.iter_audio_files")
@patch("local_transcribe_cli.cli.transcribe_file")
def test_main_success(mock_transcribe, mock_iter, mock_model, tmp_path):
    # Mock finding one file
    f = tmp_path / "test.wav"
    f.touch()
    mock_iter.return_value = [f]
    
    # Mock model
    mock_model_instance = MagicMock()
    mock_model.return_value = mock_model_instance
    
    ret = main(["--input-dir", str(tmp_path)])
    assert ret == 0
    
    # Verify transcribe was called
    assert mock_transcribe.call_count == 1
    args, _ = mock_transcribe.call_args
    # args: (model, audio_path, output_dir, language, output_formats)
    assert args[1] == f
