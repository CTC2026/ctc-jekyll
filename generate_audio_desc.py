"""
Generate audio descriptions for a video clip using the Gemini API.
Descriptions are placed in gaps between dialogue lines — music and sound
effects are allowed to overlap with descriptions.

Output is a bilingual VTT file (Chinese + English per cue).

Usage:
    python generate_audio_desc.py <video_file> <dialogue_vtt> <soundlabels_vtt> <output_vtt> \\
        [--transchart DOCX --clip N]

Example:
    python generate_audio_desc.py \\
        assets/plays/guan-hanqing/feiyimeng-1964-opera-film/Feiyimeng_1964_OperaFilm_Clip_4_2x.mp4 \\
        assets/subtitles/guan-hanqing/feiyimeng-1964-opera-film/clip_4/Feiyimeng_1964_OperaFilm_Clip_4_en.vtt \\
        assets/subtitles/guan-hanqing/feiyimeng-1964-opera-film/clip_4/Feiyimeng_1964_OperaFilm_Clip_4_soundlabels.vtt \\
        assets/subtitles/guan-hanqing/feiyimeng-1964-opera-film/clip_4/Feiyimeng_1964_OperaFilm_Clip_4_audiodesc.vtt \\
        --transchart "/path/to/Feiyimeng_1964_OperaFilm_TransCharts.docx" --clip 4

Requirements:
    pip install google-genai python-docx
    Set GEMINI_API_KEY environment variable before running.
"""

import sys
import os
import re
import json
import time
import argparse
from google import genai
from google.genai import types

MIN_GAP_MS = 2000       # minimum window to bother describing (2 seconds)
MAX_CHUNK_MS = 6000     # subdivide windows longer than this into ~6s chunks


# ---------------------------------------------------------------------------
# VTT parsing
# ---------------------------------------------------------------------------

def to_ms(ts):
    ts = ts.replace(",", ".")
    h, m, s = ts.split(":")
    return int((int(h) * 3600 + int(m) * 60 + float(s)) * 1000)


def ms_to_ts(ms):
    h = ms // 3600000
    m = (ms % 3600000) // 60000
    s = (ms % 60000) / 1000
    return f"{h:02d}:{m:02d}:{s:06.3f}"


def parse_vtt_cues(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    cues = []
    blocks = re.split(r"\n{2,}", text.strip())
    for block in blocks:
        lines = block.strip().splitlines()
        ts_line = next((l for l in lines if "-->" in l), None)
        if not ts_line:
            continue
        m = re.match(r"(\S+)\s+-->\s+(\S+)", ts_line)
        if not m:
            continue
        content = [l for l in lines if "-->" not in l and not re.match(r"^\d+$", l.strip())]
        cues.append({
            "start_ms": to_ms(m.group(1)),
            "end_ms": to_ms(m.group(2)),
            "start_ts": m.group(1).replace(",", "."),
            "end_ts": m.group(2).replace(",", "."),
            "text": " ".join(content),
        })
    return cues


# ---------------------------------------------------------------------------
# TransChart stage context extraction
# ---------------------------------------------------------------------------

def _find_clip_table(doc, clip_number):
    from docx.table import Table
    from docx.oxml.ns import qn
    body = list(doc.element.body)
    for i, child in enumerate(body):
        if child.tag.endswith("}p"):
            text = "".join(r.text or "" for r in child.iter(qn("w:t")))
            if f"clip {clip_number}" in text.lower():
                for j in range(i + 1, len(body)):
                    if body[j].tag.endswith("}tbl"):
                        return Table(body[j], doc)
    return None


def extract_stage_context(transchart_docx, clip_number):
    """
    Return a plain-text scene summary from the TransChart for use as Gemini
    prompt context. Includes standalone stage directions (in [brackets]) and
    inline parenthetical stage notes extracted from dialogue EN text.
    """
    try:
        from docx import Document
    except ImportError:
        print("Warning: python-docx not installed; skipping TransChart context.")
        return ""

    doc = Document(transchart_docx)
    table = _find_clip_table(doc, clip_number)
    if table is None:
        print(f"Warning: clip {clip_number} table not found in transchart; skipping context.")
        return ""

    lines = [f"Scene context from script (Clip {clip_number}):"]
    for row in table.rows[1:]:
        cells = [c.text.replace("\xa0", " ").strip() for c in row.cells]
        if len(cells) < 2:
            continue
        zh, en = cells[0], cells[1]
        if not zh and not en:
            continue

        # Standalone stage direction row
        if zh.startswith("[") and en.startswith("["):
            lines.append(f"  [SCENE] {en.strip('[]')}")
            continue

        # Dialogue row — extract inline parenthetical stage notes from EN
        inline = re.findall(r'\(([^)]{10,})\)', en)  # only notes ≥ 10 chars
        for note in inline:
            lines.append(f"  [ACTION] {note}")

    if len(lines) == 1:
        return ""  # nothing useful found
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Window calculation
# ---------------------------------------------------------------------------

def find_dialogue_windows(dialogue_cues, clip_end_ms):
    """Find gaps between dialogue cues — only dialogue is hard-blocked."""
    blocks = sorted((c["start_ms"], c["end_ms"]) for c in dialogue_cues)
    merged = []
    for s, e in blocks:
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append([s, e])

    windows = []
    cursor = 0
    for s, e in merged:
        if s - cursor >= MIN_GAP_MS:
            windows.append((cursor, s))
        cursor = max(cursor, e)
    if clip_end_ms - cursor >= MIN_GAP_MS:
        windows.append((cursor, clip_end_ms))
    return windows


def subdivide_window(start_ms, end_ms):
    """Split a long window into chunks of at most MAX_CHUNK_MS."""
    duration = end_ms - start_ms
    if duration <= MAX_CHUNK_MS:
        return [(start_ms, end_ms)]
    n_chunks = -(-duration // MAX_CHUNK_MS)  # ceiling division
    chunk_ms = duration // n_chunks
    chunks = []
    cur = start_ms
    for i in range(n_chunks):
        chunk_end = cur + chunk_ms if i < n_chunks - 1 else end_ms
        chunks.append((cur, chunk_end))
        cur = chunk_end
    return chunks


def max_words(duration_ms):
    return max(3, int(duration_ms / 1000 * 2.2))


# ---------------------------------------------------------------------------
# Prompt building
# ---------------------------------------------------------------------------

def build_prompt(chunks, stage_context=""):
    lines = []
    for s, e, dur_ms in chunks:
        w = max_words(dur_ms)
        lines.append(f"- {s} to {e}  (max {w} English words)")
    window_list = "\n".join(lines)

    context_block = ""
    if stage_context:
        context_block = f"""
IMPORTANT: The following stage directions from the script describe the visual action in this clip.
You MUST base every description on these stage directions. For each time window, identify which
action or scene transition is happening according to the script, and describe that.
Use the exact character names and props mentioned in the stage directions.

{stage_context}

"""

    return f"""Watch this video clip carefully.
{context_block}
I will give you time windows where I need a brief visual description for audio playback.
These windows fall between spoken dialogue. They may overlap with background opera music
or instrumental sound effects — that is fine.

IMPORTANT: Each description will be read aloud by a TTS voice within the window duration.
You MUST stay within the word limit shown for each window.

For each window, write ONE phrase or short sentence describing what is visible:
costumes, physical movement, setting, facial expressions, or on-screen text.
{"Always reference the stage directions above — use character names and scripted actions." if stage_context else "Do NOT describe speech, dialogue, or music."}

Write each description in both Chinese (Simplified) and English.
Keep the Chinese description proportionally brief to match the English word limit.

Return a JSON array only, no other text:
[
  {{
    "start": "HH:MM:SS.mmm",
    "end": "HH:MM:SS.mmm",
    "zh": "中文描述。",
    "en": "English description."
  }}
]

Time windows:
{window_list}
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def generate_audio_desc(video_path, dialogue_vtt, soundlabels_vtt, output_path,
                        transchart_docx=None, clip_number=None):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        sys.exit(1)

    dialogue_cues = parse_vtt_cues(dialogue_vtt)
    sound_cues = parse_vtt_cues(soundlabels_vtt) if soundlabels_vtt else []

    all_ends = [c["end_ms"] for c in dialogue_cues + sound_cues]
    clip_end_ms = max(all_ends) if all_ends else 120000

    raw_windows = find_dialogue_windows(dialogue_cues, clip_end_ms)
    chunks = []
    for s, e in raw_windows:
        chunks.extend(subdivide_window(s, e))
    chunks_with_dur = [(ms_to_ts(s), ms_to_ts(e), e - s) for s, e in chunks]

    print(f"Found {len(raw_windows)} dialogue gaps → {len(chunks_with_dur)} description slots:")
    for s, e, dur in chunks_with_dur:
        print(f"  {s} --> {e}  ({dur/1000:.1f}s, max {max_words(dur)} words)")

    stage_context = ""
    if transchart_docx and clip_number:
        stage_context = extract_stage_context(transchart_docx, clip_number)
        if stage_context:
            print(f"\nTransChart context loaded ({len(stage_context.splitlines())} lines)")

    client = genai.Client(api_key=api_key)

    print(f"\nUploading {video_path} to Gemini...")
    with open(video_path, "rb") as f:
        video_file = client.files.upload(
            file=f,
            config=types.UploadFileConfig(mime_type="video/mp4")
        )
    print(f"Upload complete: {video_file.name}")

    while video_file.state.name == "PROCESSING":
        print("Waiting for file to be processed...")
        time.sleep(5)
        video_file = client.files.get(name=video_file.name)

    prompt = build_prompt(chunks_with_dur, stage_context)
    print(f"Generating {len(chunks_with_dur)} audio descriptions...")
    response = None
    for model in ["gemini-2.5-flash", "models/gemini-3-flash-preview", "models/gemini-2.5-flash-lite"]:
        try:
            response = client.models.generate_content(
                model=model,
                contents=[types.Part.from_uri(file_uri=video_file.uri, mime_type="video/mp4"), prompt],
            )
            print(f"Used model: {model}")
            break
        except Exception as e:
            print(f"{model} failed: {e}, trying next...")
    if response is None:
        print("All models failed.")
        sys.exit(1)

    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    events = json.loads(raw)
    print(f"Generated {len(events)} descriptions.")

    lines = ["WEBVTT", ""]
    for i, event in enumerate(events, start=1):
        lines.append(str(i))
        lines.append(f"{event['start']} --> {event['end']}")
        lines.append(event["zh"])
        lines.append(event["en"])
        lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\nAudio descriptions written to {output_path}")
    print("Review timestamps and descriptions before publishing.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("video_file")
    parser.add_argument("dialogue_vtt")
    parser.add_argument("soundlabels_vtt")
    parser.add_argument("output_vtt")
    parser.add_argument("--transchart", default=None, help="Path to TransChart .docx")
    parser.add_argument("--clip", type=int, default=None, help="Clip number in the TransChart")
    args = parser.parse_args()

    generate_audio_desc(
        args.video_file, args.dialogue_vtt, args.soundlabels_vtt, args.output_vtt,
        transchart_docx=args.transchart, clip_number=args.clip,
    )
