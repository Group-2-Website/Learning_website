import asyncio
import hashlib
import logging
from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import FileResponse
from gtts import gTTS
from nicegui import app

log = logging.getLogger(__name__)

# project_root/audio_cache (passt zu deinem Workspace)
AUDIO_CACHE_DIR = Path(__file__).resolve().parents[2] / "audio_cache"
AUDIO_CACHE_DIR.mkdir(exist_ok=True)

SUPPORTED_TTS_LANGS = {"de", "fr", "en", "es", "it", "pt", "nl", "ar"}


def _normalize_text(text: str) -> str:
    """Clean text for TTS: normalize apostrophes and special characters."""
    # Replace typographic / curly apostrophes with ASCII apostrophe
    text = text.replace("\u2019", "'")
    text = text.replace("\u2018", "'")
    text = text.replace("\u02BC", "'")
    return text.strip()


def _generate_audio(text: str, lang: str, dest: Path) -> None:
    """Blocking helper — runs gTTS and writes the MP3 file."""
    text = _normalize_text(text)
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save(str(dest))


@app.get("/api/tts")
async def tts_endpoint(text: str = "", lang: str = "de"):
    """Generate (or serve cached) MP3 pronunciation for *text* in *lang*."""
    text = text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Missing 'text' parameter")
    if lang not in SUPPORTED_TTS_LANGS:
        lang = "en"

    # Deterministic filename based on text + lang
    key = hashlib.md5(f"{lang}:{text}".encode("utf-8")).hexdigest()
    mp3_path = AUDIO_CACHE_DIR / f"{key}.mp3"

    if not mp3_path.exists():
        log.info("TTS generating: lang=%s text=%r", lang, text)
        # Run blocking gTTS in a thread so we don't stall the event loop
        await asyncio.to_thread(_generate_audio, text, lang, mp3_path)

    return FileResponse(str(mp3_path), media_type="audio/mpeg")
