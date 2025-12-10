import argparse
import json
import os
import pathlib
import sys
from typing import Iterable

if sys.platform == "win32":
    try:
        import nvidia.cublas
        import nvidia.cudnn

        def _add_nvidia_path(module):
            path = getattr(module, "__file__", None)
            if path:
                path = os.path.dirname(path)
            else:
                paths = getattr(module, "__path__", None)
                if paths and len(paths) > 0:
                    path = paths[0]
            
            if path:
                bin_path = os.path.join(path, "bin")
                if os.path.isdir(bin_path):
                    os.add_dll_directory(bin_path)
                    os.environ["PATH"] = bin_path + os.pathsep + os.environ["PATH"]

        _add_nvidia_path(nvidia.cublas)
        _add_nvidia_path(nvidia.cudnn)
    except (ImportError, AttributeError, OSError, TypeError):
        pass

from faster_whisper import WhisperModel
from tqdm import tqdm


DEFAULT_MODEL = "large-v3"
DEFAULT_LANGUAGE = "en"
DEFAULT_OUTPUT_FORMATS = ["txt", "json"]

AUDIO_EXTENSIONS = {
    ".wav", ".mp3", ".ogg", ".flac", ".m4a", ".aac", ".wma", ".ac3",
    ".aiff", ".amr", ".opus", ".alac", ".mid", ".midi", ".ra", ".ram",
    ".rm", ".rpm", ".snd", ".au"
}

VIDEO_EXTENSIONS = {
    ".mp4", ".mkv", ".mov", ".avi", ".wmv", ".flv", ".webm", ".m4v",
    ".mpg", ".mpeg", ".3gp", ".3g2", ".mts", ".m2ts", ".vob", ".ogv"
}


def iter_audio_files(root: pathlib.Path, patterns: list[str]) -> Iterable[pathlib.Path]:
    # Collect unique paths matching any of the patterns
    found_paths = set()
    for pat in patterns:
        found_paths.update(root.glob(pat))
    return sorted(found_paths)


def format_timestamp(seconds: float) -> str:
    """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)."""
    total_milliseconds = int(round(seconds * 1000))
    
    hours = total_milliseconds // 3600000
    total_milliseconds %= 3600000
    
    minutes = total_milliseconds // 60000
    total_milliseconds %= 60000
    
    secs = total_milliseconds // 1000
    milliseconds = total_milliseconds % 1000
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"


def write_txt(segments: list, out_path: pathlib.Path) -> None:
    with out_path.open("w", encoding="utf-8") as f:
        for seg in segments:
            line = seg.text.strip()
            if line:
                f.write(line + "\n")


def write_json(segments: list, out_path: pathlib.Path) -> None:
    data = []
    for seg in segments:
        data.append({
            "start": seg.start,
            "end": seg.end,
            "text": seg.text.strip()
        })
    
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def write_srt(segments: list, out_path: pathlib.Path) -> None:
    with out_path.open("w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            start_ts = format_timestamp(seg.start)
            end_ts = format_timestamp(seg.end)
            text = seg.text.strip()
            
            f.write(f"{i}\n")
            f.write(f"{start_ts} --> {end_ts}\n")
            f.write(f"{text}\n\n")


def transcribe_file(
    model: WhisperModel,
    audio_path: pathlib.Path,
    output_dir: pathlib.Path,
    language: str,
    output_formats: list[str],
) -> None:
    # Run transcription
    segments_gen, info = model.transcribe(
        str(audio_path),
        language=language,
        beam_size=5,
    )

    print(
        f"[local-transcribe] Processing: {audio_path.name} "
        f"(Duration: {info.duration:.1f}s, Language: {info.language})"
    )
    
    # Materialize segments so we can write multiple formats
    segments = []
    with tqdm(total=round(info.duration, 2), unit="s", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}s") as pbar:
        for segment in segments_gen:
            segments.append(segment)
            pbar.update(segment.end - pbar.n)
        
        if pbar.n < pbar.total:
            pbar.update(pbar.total - pbar.n)

    output_dir.mkdir(parents=True, exist_ok=True)
    
    base_name = audio_path.stem
    
    if "txt" in output_formats:
        out_path = output_dir / (base_name + ".txt")
        write_txt(segments, out_path)
        print(f"[local-transcribe]   -> {out_path.name}")

    if "json" in output_formats:
        out_path = output_dir / (base_name + ".json")
        write_json(segments, out_path)
        print(f"[local-transcribe]   -> {out_path.name}")

    if "srt" in output_formats:
        out_path = output_dir / (base_name + ".srt")
        write_srt(segments, out_path)
        print(f"[local-transcribe]   -> {out_path.name}")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="local-transcribe",
        description=(
            "Batch-transcribe audio/video files in a directory using faster-whisper "
            "(Whisper large-v3 by default). Supports TXT, JSON, and SRT outputs."
        ),
    )

    p.add_argument(
        "--input-dir",
        "-i",
        type=str,
        default=".",
        help="Directory containing audio files (default: current directory).",
    )
    p.add_argument(
        "--pattern",
        "-p",
        type=str,
        default=None,
        help="Filename glob pattern (optional, additive to media-type defaults).",
    )
    p.add_argument(
        "--media-type",
        type=str,
        choices=["audio", "video", "all"],
        default="audio",
        help="Media type to target (default: audio).",
    )
    p.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default="transcripts",
        help="Directory to write transcript files (default: transcripts).",
    )
    p.add_argument(
        "--output-formats",
        nargs="+",
        choices=["txt", "json", "srt"],
        default=DEFAULT_OUTPUT_FORMATS,
        help=f"Output formats to generate (default: {' '.join(DEFAULT_OUTPUT_FORMATS)}).",
    )
    p.add_argument(
        "--model",
        "-m",
        type=str,
        default=DEFAULT_MODEL,
        help=f"Whisper model name to use (default: {DEFAULT_MODEL}).",
    )
    p.add_argument(
        "--language",
        "-l",
        type=str,
        default=DEFAULT_LANGUAGE,
        help=f"Language code hint (default: {DEFAULT_LANGUAGE}).",
    )
    p.add_argument(
        "--device",
        type=str,
        choices=["auto", "cpu", "cuda"],
        default="auto",
        help="Device to run on: auto / cpu / cuda (default: auto).",
    )
    p.add_argument(
        "--compute-type",
        type=str,
        default="auto",
        help=(
            "CTranslate2 compute type (e.g. auto, int8, float16, float32). "
            "See CTranslate2 docs for details."
        ),
    )

    return p


def create_model(model_name: str, device: str, compute_type: str) -> WhisperModel:
    # CTranslate2 supports device=cpu|cuda|auto and many compute types. 
    print(
        f"[local-transcribe] Loading model '{model_name}' "
        f"on device={device}, compute_type={compute_type}..."
    )
    return WhisperModel(
        model_name,
        device=device,
        compute_type=compute_type,
    )


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    input_dir = pathlib.Path(args.input_dir).expanduser().resolve()
    output_dir = pathlib.Path(args.output_dir).expanduser().resolve()

    if not input_dir.exists() or not input_dir.is_dir():
        parser.error(f"Input directory does not exist or is not a directory: {input_dir}")

    # Determine patterns based on media type
    patterns = []
    if args.media_type in ("audio", "all"):
        patterns.extend(f"*{ext}" for ext in AUDIO_EXTENSIONS)
    if args.media_type in ("video", "all"):
        patterns.extend(f"*{ext}" for ext in VIDEO_EXTENSIONS)
    
    # Add user-specified pattern if provided
    if args.pattern:
        patterns.append(args.pattern)

    files = list(iter_audio_files(input_dir, patterns))
    if not files:
        print(f"[local-transcribe] No files matching patterns in {input_dir}")
        return 1

    model = create_model(args.model, args.device, args.compute_type)

    for path in files:
        try:
            transcribe_file(model, path, output_dir, args.language, args.output_formats)
        except Exception as exc:  # pragma: no cover (basic safety)
            print(f"[local-transcribe] ERROR processing {path.name}: {exc}", file=sys.stderr)

    print("[local-transcribe] Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
