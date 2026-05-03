from pathlib import Path

from config import WhisperConfig, TranscriptionConfig, get_logger

log = get_logger(__name__)


def transcribe_audio(
    audio_path: Path,
    whisper_config: WhisperConfig | None = None,
    transcription_config: TranscriptionConfig | None = None,
) -> Path | None:
    from faster_whisper import WhisperModel
    
    if whisper_config is None:
        whisper_config = WhisperConfig()
    
    if transcription_config is None:
        transcription_config = TranscriptionConfig()
    
    output_dir = Path(transcription_config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    log.debug(f"Whisper config: model={whisper_config.model}, device={whisper_config.device}")
    log.info(f"Loading Whisper model ({whisper_config.model})...")
    
    model = WhisperModel(
        whisper_config.model,
        device=whisper_config.device,
        compute_type=whisper_config.compute_type,
    )
    
    log.info(f"Transcribing: {audio_path.name}")
    
    transcribe_opts = {"beam_size": whisper_config.beam_size}
    if whisper_config.language:
        transcribe_opts["language"] = whisper_config.language
        log.debug(f"Forced language: {whisper_config.language}")
    
    segments, info = model.transcribe(str(audio_path), **transcribe_opts)
    
    log.debug("Processing segments...")
    segments_list = list(segments)
    
    log.info(f"Detected language: {info.language} (confidence: {info.language_probability:.0%})")
    log.debug(f"Total segments: {len(segments_list)}")
    
    text = "".join(segment.text for segment in segments_list)
    
    output_path = output_dir / f"{audio_path.stem}.txt"
    output_path.write_text(text.strip(), encoding="utf-8")
    
    log.info(f"Transcription saved: {output_path}")
    return output_path
