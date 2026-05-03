# Video Converter

Download YouTube videos as MP3 and transcribe audio to text with automatic language detection.

## Features

- Download YouTube videos and convert to MP3
- Transcribe audio using Whisper (faster-whisper)
- Automatic language detection
- YAML configuration with CLI overrides
- Structured logging

## Requirements

- Nix (with flakes enabled) or manually install: Python 3.12+, ffmpeg, uv

## Setup

```bash
# Enter dev environment
direnv allow
# or
nix develop

# Install dependencies
uv sync
```

## Usage

### Download YouTube video as MP3

```bash
uv run python main.py https://youtu.be/VIDEO_ID
uv run python main.py https://youtu.be/VIDEO_ID -o ~/Music
```

### Download and transcribe

```bash
uv run python main.py https://youtu.be/VIDEO_ID -t
```

### Transcribe existing audio file

```bash
uv run python main.py -f audio.mp3
uv run python main.py -f audio1.mp3 -f audio2.mp3
```

### Options

| Flag | Description |
|------|-------------|
| `-t, --transcribe` | Transcribe audio after download |
| `-f, --file` | Transcribe existing audio file |
| `-o, --output` | Output directory for MP3 files |
| `--transcription-dir` | Output directory for transcriptions |
| `--model` | Whisper model: tiny, base, small, medium, large-v3, turbo |
| `--device` | Device: cpu, cuda |
| `--language` | Force language (skip auto-detection) |
| `--log-level` | Logging: DEBUG, INFO, WARNING, ERROR |
| `-c, --config` | Path to config file |

## Configuration

Copy `config.example.yaml` to `config.yaml`:

```yaml
log_level: INFO

whisper:
  model: medium
  device: cpu
  compute_type: int8
  beam_size: 5
  language: null

download:
  output_dir: video
  format: mp3
  quality: "192"

transcription:
  output_dir: transcription
```

CLI flags override config values.

## License

MIT
