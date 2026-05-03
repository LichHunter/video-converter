import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


DEFAULT_CONFIG_PATH = Path("config.yaml")
DEFAULT_LOG_LEVEL = "INFO"

LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


@dataclass
class WhisperConfig:
    model: str = "medium"
    device: str = "cpu"
    compute_type: str = "int8"
    beam_size: int = 5
    language: str | None = None


@dataclass
class DownloadConfig:
    output_dir: Path = field(default_factory=lambda: Path("video"))
    format: str = "mp3"
    quality: str = "192"


@dataclass
class TranscriptionConfig:
    output_dir: Path = field(default_factory=lambda: Path("transcription"))
    

@dataclass
class AppConfig:
    whisper: WhisperConfig = field(default_factory=WhisperConfig)
    download: DownloadConfig = field(default_factory=DownloadConfig)
    transcription: TranscriptionConfig = field(default_factory=TranscriptionConfig)
    log_level: str = DEFAULT_LOG_LEVEL


def load_config(config_path: Path | None = None) -> AppConfig:
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH
    
    if not config_path.exists():
        return AppConfig()
    
    with open(config_path) as f:
        data = yaml.safe_load(f) or {}
    
    return _parse_config(data)


def _parse_config(data: dict[str, Any]) -> AppConfig:
    whisper_data = data.get("whisper", {})
    download_data = data.get("download", {})
    transcription_data = data.get("transcription", {})
    
    whisper = WhisperConfig(
        model=whisper_data.get("model", WhisperConfig.model),
        device=whisper_data.get("device", WhisperConfig.device),
        compute_type=whisper_data.get("compute_type", WhisperConfig.compute_type),
        beam_size=whisper_data.get("beam_size", WhisperConfig.beam_size),
        language=whisper_data.get("language"),
    )
    
    download = DownloadConfig(
        output_dir=Path(download_data.get("output_dir", "video")),
        format=download_data.get("format", DownloadConfig.format),
        quality=download_data.get("quality", DownloadConfig.quality),
    )
    
    transcription = TranscriptionConfig(
        output_dir=Path(transcription_data.get("output_dir", "transcription")),
    )
    
    log_level = data.get("log_level", DEFAULT_LOG_LEVEL).upper()
    
    return AppConfig(
        whisper=whisper,
        download=download,
        transcription=transcription,
        log_level=log_level,
    )


def merge_with_cli(config: AppConfig, cli_args: dict[str, Any]) -> AppConfig:
    if cli_args.get("model"):
        config.whisper.model = cli_args["model"]
    
    if cli_args.get("output"):
        config.download.output_dir = cli_args["output"]
    
    if cli_args.get("transcription_dir"):
        config.transcription.output_dir = cli_args["transcription_dir"]
    
    return config


def setup_logging(level: str) -> None:
    level_value = LOG_LEVELS.get(level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=level_value,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
