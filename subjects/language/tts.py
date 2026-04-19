import asyncio
import hashlib
import logging
from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import FileResponse
from gtts import gTTS
from nicegui import app


log = logging.getLogger(__name__)

AUDIO_CACHE_DIR = Path(__file__).parent / "audio_cache"

SUPPORTED_TTS_LANGS = {"de", "fr", "en", "es", "it", "pt", "nl", "ar"}


def _normalize_text(text: str) -> str:
    """Clean text for TTS: normalize apostrophes and special characters."""
    text = text.replace("\u2019", "'")   # '  right single quotation mark
    text = text.replace("\u2018", "'")   # '  left single quotation mark
    text = text.replace("\u02BC", "'")   # ʼ  modifier letter apostrophe
    return text.strip()


def _generate_audio(text: str, lang: str, dest: Path) -> None:
    """Blocking helper — runs gTTS and writes the MP3 file."""
    text = _normalize_text(text)
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save(str(dest))


def init() -> None:
    """Register the /api/tts route. Call once at startup."""
    AUDIO_CACHE_DIR.mkdir(exist_ok=True)

    @app.get("/api/tts")
    async def tts_endpoint(text: str = "", lang: str = "de"):
        """Generate (or serve cached) MP3 pronunciation for *text* in *lang*."""
        text = text.strip()
        if not text:
            raise HTTPException(status_code=400, detail="Missing 'text' parameter")
        if lang not in SUPPORTED_TTS_LANGS:
            lang = "en"

        key = hashlib.md5(f"{lang}:{text}".encode()).hexdigest()
        mp3_path = AUDIO_CACHE_DIR / f"{key}.mp3"

        if not mp3_path.exists():
            log.info("TTS generating: lang=%s text=%r", lang, text)
            await asyncio.to_thread(_generate_audio, text, lang, mp3_path)

        return FileResponse(str(mp3_path), media_type="audio/mpeg")

