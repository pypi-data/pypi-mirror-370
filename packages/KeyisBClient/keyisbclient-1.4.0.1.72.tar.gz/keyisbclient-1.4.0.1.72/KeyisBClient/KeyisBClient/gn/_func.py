
def guess_type(filename: str) -> str:
    """
    Возвращает актуальный MIME-тип по расширению файла.
    Только современные и часто используемые типы.
    """
    ext = filename.lower().rsplit('.', 1)[-1] if '.' in filename else ''

    mime_map = {
        # 🔹 Текст и данные
        "txt": "text/plain",
        "html": "text/html",
        "css": "text/css",
        "csv": "text/csv",
        "xml": "application/xml",
        "json": "application/json",
        "js": "application/javascript",

        # 🔹 Изображения (актуальные для веба)
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp",
        "svg": "image/svg+xml",
        "avif": "image/avif",

        # 🔹 Видео (современные форматы)
        "mp4": "video/mp4",
        "webm": "video/webm",

        # 🔹 Аудио (современные форматы)
        "mp3": "audio/mpeg",
        "ogg": "audio/ogg",
        "oga": "audio/ogg",
        "m4a": "audio/mp4",
        "flac": "audio/flac",

        # 🔹 Архивы
        "zip": "application/zip",
        "gz": "application/gzip",
        "tar": "application/x-tar",
        "7z": "application/x-7z-compressed",
        "rar": "application/vnd.rar",

        # 🔹 Документы (актуальные офисные)
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",

        # 🔹 Шрифты
        "woff": "font/woff",
        "woff2": "font/woff2",
        "ttf": "font/ttf",
        "otf": "font/otf",
    }

    return mime_map.get(ext, "application/octet-stream")


import re
from typing import List

# regex для !{var}, поддерживает вложенность через точку
TPL_VAR_RE = re.compile(r'(?<!\\)!\{([A-Za-z_][A-Za-z0-9_\.]*)\}')

# список mime, которые считаем текстовыми
TEXTUAL_MIME_PREFIXES = [
    "text/",                       # text/html, text/css, text/plain
]
TEXTUAL_MIME_EXACT = {
    "application/javascript",
    "application/json",
    "application/xml",
    "application/xhtml+xml"
}
TEXTUAL_MIME_SUFFIXES = (
    "+xml",  # например application/rss+xml
    "+json", # application/ld+json
)

def extract_template_vars(filedata: bytes, mime: str) -> List[str]:
    """
    Ищет все !{var} в тексте, если MIME относится к текстовым.
    """
    mime = (mime or "").lower().strip()

    # определяем, текстовый ли mime
    is_textual = (
        mime.startswith(tuple(TEXTUAL_MIME_PREFIXES))
        or mime in TEXTUAL_MIME_EXACT
        or mime.endswith(TEXTUAL_MIME_SUFFIXES)
        or "javascript" in mime
        or "json" in mime
        or "xml" in mime
    )

    if not is_textual:
        return []

    try:
        text = filedata.decode("utf-8", errors="ignore")
    except Exception:
        return []

    return list(set(m.group(1) for m in TPL_VAR_RE.finditer(text)))


import re
import asyncio
from functools import lru_cache
from typing import Dict, Any

_SIGILS = (b'%', b'!', b'&')
_PATTERNS: dict[bytes, re.Pattern[bytes]] = {
    s: re.compile(rb'(?<!\\)' + re.escape(s) + rb'\{([A-Za-z_][A-Za-z0-9_\.]*)\}')
    for s in _SIGILS
}

@lru_cache(maxsize=4096)
def _split_path(path: str) -> tuple[str, ...]:
    return tuple(path.split('.'))

def _resolve(path: str, ctx: Dict[str, Any]) -> Any:
    cur: Any = ctx
    for k in _split_path(path):
        if not isinstance(cur, dict) or k not in cur:
            raise KeyError(path)
        cur = cur[k]
    return cur

def make_renderer(sigil: bytes = b'%'):
    """
    Возвращает рендер для одного сигила. Работает с bytes.
    """
    if sigil not in _PATTERNS:
        raise ValueError(f"unsupported sigil: {sigil!r}")
    rx = _PATTERNS[sigil]
    esc_seq = b'\\' + sigil + b'{'
    unesc_seq = sigil + b'{'

    def render(data: bytes, ctx: Dict[str, Any], *, keep_unresolved: bool = False) -> bytes:
        parts: list[bytes] = []
        append = parts.append
        last = 0
        finditer = rx.finditer

        for m in finditer(data):
            start, end = m.span()
            append(data[last:start])

            key = m.group(1).decode('utf-8')
            try:
                val = _resolve(key, ctx)
                append(b"" if val is None else str(val).encode('utf-8'))
            except KeyError:
                if keep_unresolved:
                    append(data[start:end])
                else:
                    raise
            last = end

        if last < len(data):
            append(data[last:])

        out = b''.join(parts)
        if esc_seq in out:
            out = out.replace(esc_seq, unesc_seq)
        return out

    return render

# предсобранные
render_pct = make_renderer(b'%')
render_bang = make_renderer(b'!')
render_amp = make_renderer(b'&')

# асинхронные обёртки
_BIG = 256 * 1024

async def render_pct_async(data: bytes, ctx: Dict[str, Any], *, keep_unresolved: bool = False) -> bytes:
    return render_pct(data, ctx, keep_unresolved=keep_unresolved) if len(data) < _BIG \
        else await asyncio.to_thread(render_pct, data, ctx, keep_unresolved=keep_unresolved)

async def render_bang_async(data: bytes, ctx: Dict[str, Any], *, keep_unresolved: bool = False) -> bytes:
    return render_bang(data, ctx, keep_unresolved=keep_unresolved) if len(data) < _BIG \
        else await asyncio.to_thread(render_bang, data, ctx, keep_unresolved=keep_unresolved)

async def render_amp_async(data: bytes, ctx: Dict[str, Any], *, keep_unresolved: bool = False) -> bytes:
    return render_amp(data, ctx, keep_unresolved=keep_unresolved) if len(data) < _BIG \
        else await asyncio.to_thread(render_amp, data, ctx, keep_unresolved=keep_unresolved)
