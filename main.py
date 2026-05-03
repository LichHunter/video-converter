#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path

from config import load_config, AppConfig, setup_logging, get_logger
from download import download_as_mp3
from transcribe import transcribe_audio

log = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download YouTube videos and convert to MP3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py https://youtu.be/dQw4w9WgXcQ
  python main.py https://youtu.be/dQw4w9WgXcQ -t
  python main.py https://youtu.be/dQw4w9WgXcQ -t --model small
  python main.py URL1 URL2 URL3 -o ./downloads
  python main.py -f audio.mp3 --config my_config.yaml
        """,
    )
    
    parser.add_argument(
        "urls",
        nargs="*",
        help="YouTube video URL(s) to download",
    )
    
    parser.add_argument(
        "-f", "--file",
        type=Path,
        action="append",
        dest="files",
        help="Transcribe existing audio file(s)",
    )
    
    parser.add_argument(
        "-c", "--config",
        type=Path,
        help="Path to config file (default: config.yaml)",
    )
    
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output directory for MP3 files",
    )
    
    parser.add_argument(
        "-t", "--transcribe",
        action="store_true",
        help="Transcribe audio to text (auto-detects language)",
    )
    
    parser.add_argument(
        "--model",
        choices=["tiny", "base", "small", "medium", "large-v3", "turbo"],
        help="Whisper model size",
    )
    
    parser.add_argument(
        "--device",
        choices=["cpu", "cuda"],
        help="Device for Whisper inference",
    )
    
    parser.add_argument(
        "--language",
        help="Force language (skip auto-detection)",
    )
    
    parser.add_argument(
        "--transcription-dir",
        type=Path,
        help="Output directory for transcriptions",
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )
    
    return parser.parse_args()


def apply_cli_overrides(config: AppConfig, args: argparse.Namespace) -> AppConfig:
    if args.model:
        config.whisper.model = args.model
    if args.device:
        config.whisper.device = args.device
    if args.language:
        config.whisper.language = args.language
    if args.output:
        config.download.output_dir = args.output
    if args.transcription_dir:
        config.transcription.output_dir = args.transcription_dir
    if args.log_level:
        config.log_level = args.log_level
    return config


def main():
    args = parse_args()
    
    config = load_config(args.config)
    config = apply_cli_overrides(config, args)
    
    setup_logging(config.log_level)
    
    log.debug(f"Config loaded: {config}")
    
    if not args.urls and not args.files:
        log.error("Provide either YouTube URLs or --file paths")
        sys.exit(1)
    
    success_count = 0
    total = 0
    
    if args.files:
        for audio_file in args.files:
            total += 1
            if not audio_file.exists():
                log.error(f"File not found: {audio_file}")
                continue
            if transcribe_audio(audio_file, config.whisper, config.transcription):
                success_count += 1
        log.info(f"Transcribed {success_count}/{total} files")
    else:
        for url in args.urls:
            total += 1
            result = download_as_mp3(url, config.download.output_dir)
            if result:
                success_count += 1
                if args.transcribe:
                    transcribe_audio(result, config.whisper, config.transcription)
        
        log.info(f"Downloaded {success_count}/{total} videos successfully")
        if args.transcribe:
            log.info(f"Transcribed {success_count}/{total} audio files")
    
    sys.exit(0 if success_count == total else 1)


if __name__ == "__main__":
    main()
