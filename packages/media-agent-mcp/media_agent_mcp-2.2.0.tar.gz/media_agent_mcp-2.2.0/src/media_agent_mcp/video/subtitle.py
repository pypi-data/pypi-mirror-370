"""Subtitle rendering utilities using FFmpeg.

This module renders subtitles (plain text or SRT) onto a video using FFmpeg.  It handles:
1. Automatic line-wrapping for long text.
2. Custom font / colour via `.ttf` files placed in *video/fonts*.
3. On-demand download of five free Google Fonts.
"""
from __future__ import annotations

import logging
import os
import re
import subprocess
import tempfile
import textwrap
import time
import uuid
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from urllib.parse import urlparse

import requests

from media_agent_mcp.storage.tos_client import upload_to_tos
from media_agent_mcp.video.processor import download_video_from_url

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Font management
# ---------------------------------------------------------------------------
FONTS_DIR = Path(__file__).parent / "fonts"
FONTS_DIR.mkdir(parents=True, exist_ok=True)

# Font map: font display name -> (download_url_or_None, relative_file_name)
AVAILABLE_FONTS: Dict[str, Tuple[Optional[str], str]] = {
    # English fonts (local)
    "EduNSWACTCursive": (None, "en/EduNSWACTCursive-VariableFont_wght.ttf"),
    "MozillaText": (None, "en/MozillaText-VariableFont_wght.ttf"),
    "RobotoCondensed": (None, "en/Roboto_Condensed-Regular.ttf"),

    # Chinese fonts (local)
    "MaShanZheng": (None, "zh/MaShanZheng-Regular.ttf"),
    "NotoSerifSC": (None, "zh/NotoSerifSC-VariableFont_wght.ttf"),
    "ZCOOLXiaoWei": (None, "zh/ZCOOLXiaoWei-Regular.ttf"),
}

SRT_TIMING_RE = re.compile(r"\d{2}:\d{2}:\d{2},\d{3}\s+-->\s+\d{2}:\d{2}:\d{2},\d{3}")


def ensure_font(font_name: str) -> Path:
    """
    Return the local font path.

    Raises:
        ValueError: If the font name is not supported.
        FileNotFoundError: If the font file does not exist locally.
    """
    # Allow absolute or direct file path to be provided
    p = Path(font_name)
    if p.suffix.lower() in {".ttf", ".otf"} and p.exists():
        return p

    if font_name not in AVAILABLE_FONTS:
        raise ValueError(f"Unsupported font {font_name}. Choices: {list(AVAILABLE_FONTS)}")

    _, fname = AVAILABLE_FONTS[font_name]
    fpath = FONTS_DIR / fname
    if not fpath.exists():
        raise FileNotFoundError(
            f"Font file {fpath} not found. Please ensure the font is available in {FONTS_DIR}."
        )
    return fpath


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _hex_to_ass(colour: str) -> str:
    colour = colour.lstrip("#")
    if len(colour) != 6:
        raise ValueError("Colour must be 6-digit hex")
    r, g, b = colour[0:2], colour[2:4], colour[4:6]
    return f"&H00{b}{g}{r}&"


def _wrap_lines(txt: str, width: int = 40) -> List[str]:
    lines: List[str] = []
    for para in txt.split("\n"):
        lines.extend(textwrap.wrap(para, width=width) or [""])
    return lines


def _probe_duration(path: Path) -> float:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError("ffprobe failed")
    return float(res.stdout.strip())


def _seconds_to_timestamp(seconds: float) -> str:
    """Convert seconds to SRT timestamp (HH:MM:SS,mmm)."""
    hrs, rem = divmod(seconds, 3600)
    mins, secs = divmod(rem, 60)
    msec = int((secs % 1) * 1000)
    return f"{int(hrs):02d}:{int(mins):02d}:{int(secs):02d},{msec:03d}"


def _parse_time_token(tok: str) -> float:
    """Parse a time token which can be seconds or HH:MM:SS(.mmm)."""
    if ":" in tok:
        parts = tok.split(":")
        parts = [float(p) for p in parts]
        while len(parts) < 3:
            parts.insert(0, 0.0)  # pad to [hh, mm, ss]
        hrs, mins, secs = parts
        return hrs * 3600 + mins * 60 + secs
    return float(tok)


def _create_srt(text: str) -> Path:
    """Create an SRT file from plain text or simple time-range lines.

    Supported input formats:
    1. Plain text – single block lasting full video (END placeholder).
    2. Timed lines – each line starts with "start-end " where start/end can be seconds
       or HH:MM:SS(.mmm). Example::

           0-2 Hello world
           2-3 Another line
    """
    tmp = Path(tempfile.NamedTemporaryFile(suffix=".srt", delete=False).name)

    timed_lines: List[str] = []
    pattern = re.compile(r"^\s*([\d:.]+)\s*-\s*([\d:.]+)\s+(.*)$")
    for ln in text.split("\n"):
        if not ln.strip():
            continue  # skip empty lines
        m = pattern.match(ln)
        if m:
            start_s = _parse_time_token(m.group(1))
            end_s = _parse_time_token(m.group(2))
            caption = _wrap_lines(m.group(3))
            timed_lines.append((start_s, end_s, caption))  # type: ignore[arg-type]
        else:
            timed_lines = []  # invalidate timed mode and fall back
            break

    content: List[str] = []
    if timed_lines:
        for idx, (st, ed, cap_lines) in enumerate(timed_lines, 1):
            content.append(str(idx))
            content.append(f"{_seconds_to_timestamp(st)} --> {_seconds_to_timestamp(ed)}")
            content.extend(cap_lines)
            content.append("")
    else:
        # Fallback: plain text shown for entire video (replaced later)
        lines = _wrap_lines(text)
        content = [
            "1",
            "00:00:00,000 --> {END}",
            *lines,
            "",
        ]

    tmp.write_text("\n".join(content), encoding="utf-8")
    return tmp


# New helpers for drawtext flow ------------------------------------------------
Cue = Tuple[float, float, str]


def _parse_srt_content(text: str) -> List[Cue]:
    """
    Args:
        text: SRT formatted subtitle content

    Returns:
        result: List of cues as tuples (start_seconds, end_seconds, caption_text)
    """
    # Normalize line endings
    blocks = re.split(r"\r?\n\r?\n+", text.strip())
    cues: List[Cue] = []
    ts_re = re.compile(r"^(\d{2}:\d{2}:\d{2},\d{3})\s+-->\s+(\d{2}:\d{2}:\d{2},\d{3})$")
    for blk in blocks:
        lines = [ln for ln in blk.splitlines() if ln.strip() != ""]
        if not lines:
            continue
        # Optional index line at top
        if len(lines) >= 2 and ts_re.match(lines[1]):
            ts_line = lines[1]
            text_lines = lines[2:]
        elif ts_re.match(lines[0]):
            ts_line = lines[0]
            text_lines = lines[1:]
        else:
            continue
        m = ts_re.match(ts_line)
        if not m:
            continue
        # Convert SRT timestamps HH:MM:SS,mmm to HH:MM:SS.mmm then to seconds
        st = _parse_time_token(m.group(1).replace(",", "."))
        ed = _parse_time_token(m.group(2).replace(",", "."))
        # Keep original line breaks for SRT content
        caption = "\n".join(text_lines)
        cues.append((st, ed, caption))
    return cues


def _parse_simple_timed(text: str) -> List[Cue]:
    """
    Args:
        text: Lines like "start-end caption" with times in seconds or HH:MM:SS(.mmm)

    Returns:
        result: List of cues parsed from the simple timed format
    """
    pattern = re.compile(r"^\s*([\d:.]+)\s*-\s*([\d:.]+)\s+(.*)$")
    cues: List[Cue] = []
    for ln in text.splitlines():
        if not ln.strip():
            continue
        m = pattern.match(ln)
        if not m:
            return []
        st = _parse_time_token(m.group(1))
        ed = _parse_time_token(m.group(2))
        caption = "\n".join(_wrap_lines(m.group(3)))
        cues.append((st, ed, caption))
    return cues


# ---------------------------------------------------------------------------
# Main public function
# ---------------------------------------------------------------------------

DEFAULT_FONT_SIZE = 60  # Fixed size for subtitles
DEFAULT_ALIGNMENT = 2  # Bottom-center in ASS/SSA


def add_subtitles_to_video(
    video_url: str,
    subtitles_input: str,
    font_name: str = "RobotoCondensed",
    font_color: str = "#FFFFFF",
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Add subtitles to video and upload result to TOS."""
    temp_files: List[Path] = []
    try:
        # video download/locate
        if video_url.startswith(("http://", "https://")):
            res = download_video_from_url(video_url)
            if res["status"] == "error":
                return res
            vpath = Path(res["data"]["file_path"])
            temp_files.append(vpath)
        else:
            vpath = Path(video_url)
            if not vpath.exists():
                return {"status": "error", "data": None, "message": f"Video {vpath} not found"}

        # Build cues from input (support SRT text, SRT file/URL, or simple timed lines)
        cues: List[Cue] = []
        content_text: Optional[str] = None

        # If input looks like inline SRT text
        if SRT_TIMING_RE.search(subtitles_input):
            content_text = subtitles_input
        # If input refers to a path or URL
        elif subtitles_input.lower().endswith(".srt") or os.path.exists(subtitles_input):
            if subtitles_input.startswith(("http://", "https://")):
                resp = requests.get(subtitles_input, timeout=120)
                resp.raise_for_status()
                content_text = resp.content.decode("utf-8", errors="replace")
            else:
                content_text = Path(subtitles_input).read_text(encoding="utf-8")
        else:
            # maybe simple timed text
            cues = _parse_simple_timed(subtitles_input)

        # If we have SRT content text, normalize {END} placeholder then parse
        if content_text is not None:
            if "{END}" in content_text:
                dur = _probe_duration(vpath)
                end_ts = time.strftime("%H:%M:%S", time.gmtime(dur)) + f",{int((dur % 1)*1000):03d}"
                content_text = content_text.replace("{END}", end_ts)
            cues = _parse_srt_content(content_text)

        # Fallback: plain text covering entire video
        if not cues:
            dur = _probe_duration(vpath)
            caption = "\n".join(_wrap_lines(subtitles_input))
            cues = [(0.0, dur, caption)]

        # font path (absolute)
        font_file = ensure_font(font_name).resolve()

        # Prepare drawtext filter for each cue using textfile to avoid escaping issues
        filter_parts: List[str] = []
        # Normalize color for ffmpeg drawtext (accept #RRGGBB or named)
        color_value = font_color if not font_color.startswith('#') else f"0x{font_color[1:]}"
        for st, ed, cap in cues:
            txt_path = Path(tempfile.NamedTemporaryFile(suffix=".txt", delete=False).name)
            txt_path.write_text(cap, encoding="utf-8")
            temp_files.append(txt_path)
            part = (
                "drawtext="
                f"fontfile='{font_file.as_posix()}':"
                f"textfile='{txt_path.as_posix()}':"
                f"fontcolor='{color_value}':"
                f"fontsize={DEFAULT_FONT_SIZE}:"
                "x=(w-text_w)/2:"
                "y=h-text_h-2*lh:"
                "line_spacing=6:"
                "bordercolor=black:borderw=2:"
                "shadowcolor=black:shadowx=1:shadowy=1:"
                f"enable='between(t,{st:.3f},{ed:.3f})'"
            )
            filter_parts.append(part)

        vf_str = ",".join(filter_parts)

        if output_path is None:
            output_path = f"video_sub_{uuid.uuid4().hex}.mp4"

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(vpath),
            "-vf",
            vf_str,
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "18",
            "-c:a",
            "copy",
            output_path,
        ]
        logger.debug("FFmpeg cmd: %s", " ".join(cmd))
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode != 0:
            logger.error("FFmpeg error: %s", proc.stderr[-500:])
            return {"status": "error", "data": None, "message": "FFmpeg failed"}

        url = upload_to_tos(output_path)
        try:
            os.unlink(output_path)
        except Exception:
            pass
        return {"status": "success", "data": {"tos_url": url}, "message": "Subtitles added"}
    except Exception as e:
        logger.exception("Subtitle error: %s", e)
        return {"status": "error", "data": None, "message": str(e)}
    finally:
        for f in temp_files:
            try:
                f.unlink(missing_ok=True)  # type: ignore[attr-defined]
            except Exception:
                pass

if __name__ == "__main__":
    input = """1
00:00:00,000 --> 00:00:01,000
你好，世界！

2
00:00:01,000 --> 00:00:02,000
这是第二行字幕。

3
00:00:02,000 --> 00:00:03,500
支持小数秒与多行换行
哈哈哈哈
像这样。"""

    result = add_subtitles_to_video(
            video_url='https://carey.tos-ap-southeast-1.bytepluses.com/demo/02175205870921200000000000000000000ffffc0a85094bda733.mp4',
            subtitles_input=input,
            font_name='EduNSWACTCursive',
            font_color='#FFFF00',
            output_path='./output_subtitled.mp4',
        )
    print(result)