import argparse
import pathlib
import sys
from typing import Iterable

from faster_whisper import WhisperModel


DEFAULT_MODEL = "large-v3"
DEFAULT_PATTERN = "*.ogg"
DEFAULT_LANGUAGE = "en"


def iter_audio_files(root: pathlib.Path, pattern: str) -> Iterable[pathlib.Path]:
    # Simple non-recursive glob; switch to rglob if you want recursion later.
    return sorted(root.glob(pattern))


def transcribe_file(
    model: WhisperModel,
    audio_path: pathlib.Path,
    output_dir: pathlib.Path,
    language: str,
) -> pathlib.Path:
    print(f"[local-transcribe] Processing: {audio_path.name}")

    segments, info = model.transcribe(
        str(audio_path),
        language=language,
        beam_size=5,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / (audio_path.stem + ".txt")

    with out_path.open("w", encoding="utf-8") as f:
        for seg in segments:
            line = seg.text.strip()
            if line:
                f.write(line + "\n")

    print(
        f"[local-transcribe]   -> {out_path.name} "
        f"(duration={info.duration:.1f}s, language={info.language})"
    )
    return out_path


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="local-transcribe",
        description=(
            "Batch-transcribe audio files in a directory using faster-whisper "
            "(Whisper large-v3 by default)."
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
        default=DEFAULT_PATTERN,
        help=f"Filename glob pattern (default: {DEFAULT_PATTERN!r}).",
    )
    p.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default="transcripts",
        help="Directory to write transcript .txt files (default: transcripts).",
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

    files = list(iter_audio_files(input_dir, args.pattern))
    if not files:
        print(f"[local-transcribe] No files matching pattern {args.pattern!r} in {input_dir}")
        return 1

    model = create_model(args.model, args.device, args.compute_type)

    for path in files:
        try:
            transcribe_file(model, path, output_dir, args.language)
        except Exception as exc:  # pragma: no cover (basic safety)
            print(f"[local-transcribe] ERROR processing {path.name}: {exc}", file=sys.stderr)

    print("[local-transcribe] Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
