from pathlib import Path

import yt_dlp

from config import get_logger

log = get_logger(__name__)


def download_as_mp3(url: str, output_dir: Path | None = None) -> Path | None:
    if output_dir is None:
        output_dir = Path.cwd()
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    log.debug(f"Output directory: {output_dir}")
    
    output_template = str(output_dir / "%(title)s.%(ext)s")
    
    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "outtmpl": output_template,
        "quiet": True,
        "no_warnings": True,
    }
    
    downloaded_file = None
    
    def progress_hook(d):
        nonlocal downloaded_file
        if d["status"] == "finished":
            filepath = Path(d["filename"])
            downloaded_file = filepath.with_suffix(".mp3")
            log.info(f"Download complete: {filepath.name}")
            log.debug("Converting to MP3...")
    
    ydl_opts["progress_hooks"] = [progress_hook]
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            log.info(f"Downloading: {url}")
            ydl.download([url])
            
        if downloaded_file and downloaded_file.exists():
            log.info(f"Saved: {downloaded_file}")
            return downloaded_file
        else:
            log.error("Could not find converted file")
            return None
            
    except Exception as e:
        log.error(f"Download failed: {e}")
        return None
