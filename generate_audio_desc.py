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


def extract_stage_events(transchart_docx, clip_number, dialogue_cues):
    """
    Return a list of (start_ms, end_ms, description) tuples from the TransChart,
    with timestamps derived from the matched dialogue VTT cues.

    Each TransChart dialogue row is assigned the timestamp of the next unmatched
    VTT cue. Stage direction rows and inline parenthetical notes inherit the
    timestamp of the surrounding dialogue row.
    """
    try:
        from docx import Document
    except ImportError:
        return []

    doc = Document(transchart_docx)
    table = _find_clip_table(doc, clip_number)
    if table is None:
        return []

    events = []   # (start_ms, description)
    cue_idx = 0

    for row in table.rows[1:]:
        cells = [c.text.replace("\xa0", " ").strip() for c in row.cells]
        if len(cells) < 2:
            continue
        zh, en = cells[0], cells[1]
        if not zh and not en:
            continue

        if cue_idx < len(dialogue_cues):
            ts = dialogue_cues[cue_idx]["start_ms"]
        else:
            ts = dialogue_cues[-1]["end_ms"] if dialogue_cues else 0

        if zh.startswith("[") and en.startswith("["):
            # Standalone scene direction — attach to current timestamp
            events.append((ts, en.strip("[]")))
            continue

        # Dialogue row — extract inline parenthetical stage notes from EN
        inline = re.findall(r'\(([^)]{10,})\)', en)
        for note in inline:
            events.append((ts, note))
        cue_idx += 1

    return events


def stage_hint_for_window(stage_events, window_start_ms, window_end_ms):
    """
    Return the most relevant stage event description for a given window.
    Prefers events whose timestamp falls inside the window; falls back to
    the last event before the window starts.
    """
    inside = [desc for ts, desc in stage_events if window_start_ms <= ts < window_end_ms]
    if inside:
        return " / ".join(inside)
    before = [desc for ts, desc in stage_events if ts < window_start_ms]
    return before[-1] if before else ""


# ---------------------------------------------------------------------------
# Window calculation
# ---------------------------------------------------------------------------

def find_all_windows(dialogue_cues, clip_end_ms):
    """Return silence gaps between dialogue cues only.
    Each window also carries references to the preceding and following dialogue blocks."""
    blocks = sorted((c["start_ms"], c["end_ms"]) for c in dialogue_cues)
    merged = []
    for s, e in blocks:
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append([s, e])

    # windows: (gap_start, gap_end, prev_dialogue_end, next_dialogue_start)
    windows = []
    cursor = 0
    for i, (s, e) in enumerate(merged):
        if s - cursor >= MIN_GAP_MS:
            prev_end = cursor  # end of preceding dialogue block (0 if none)
            next_start = s     # start of following dialogue block
            windows.append((cursor, s, prev_end, next_start))
        cursor = max(cursor, e)
    if clip_end_ms - cursor >= MIN_GAP_MS:
        windows.append((cursor, clip_end_ms, cursor, clip_end_ms))
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

def build_prompt(chunks, stage_events=None):
    lines = []
    for i, (s, e, dur_ms, hint, prev_end, next_start) in enumerate(chunks):
        w = max_words(dur_ms)
        # For the first window: if the clip opened with dialogue before this gap,
        # prepend the very first stage event so Gemini knows to reference the opening.
        if i == 0 and stage_events and prev_end != "00:00:00.000":
            opening = stage_events[0][1]
            combined = f"OPENING CONTEXT: {opening} | {hint}" if hint else f"OPENING CONTEXT: {opening}"
            hint_str = f"  [Script: {combined}]"
        else:
            hint_str = f"  [Script: {hint}]" if hint else ""
        lines.append(f"- {s} to {e}  (max {w} English words){hint_str}")
    window_list = "\n".join(lines)

    timeline_block = ""
    if stage_events:
        timeline_lines = [f"  {ms_to_ts(ts)}: {desc}" for ts, desc in stage_events]
        timeline_block = "NARRATIVE TIMELINE (from stage directions):\n" + "\n".join(timeline_lines)

    context_block = ""
    if stage_events:
        context_block = f"""
{timeline_block}

Use the timeline above to understand what is happening at each moment in the clip.
Each description window below also carries a [Script: ...] note indicating the most
relevant stage action for that window — base your description on it.

"""

    return f"""Watch this video clip carefully.
{context_block}
I will give you silence windows (gaps between dialogue) where a brief visual description
will be read aloud by a TTS voice. Each description plays during the silence but should
describe the visual scene — including what is happening in the dialogue moments just
before and after the gap, since the visual action continues across both.

IMPORTANT: Each description will be read aloud within the window duration.
You MUST stay within the word limit shown for each window.

For each window, write ONE phrase or short sentence describing what is VISUALLY happening:
physical movement, setting, facial expressions, camera angle, or on-screen text.
Do NOT describe costumes or clothing unless they carry important narrative meaning.
Do NOT repeat or paraphrase what characters are saying — focus only on visuals.
{"Base each description firmly on the [Script: ...] note and the narrative timeline." if stage_events else ""}
Write in plain flowing sentences. Do NOT use parentheses.

IMPORTANT — avoid repetition: each description must highlight something NOTICEABLY
DIFFERENT from adjacent ones. Vary focus — zoom level, facial expression, gesture,
other characters, setting detail. Never use the same sentence structure twice in a row.

Write each description in English only.

Return a JSON array only, no other text:
[
  {{
    "start": "HH:MM:SS.mmm",
    "end": "HH:MM:SS.mmm",
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

    raw_windows = find_all_windows(dialogue_cues, clip_end_ms)
    chunks = []
    for s, e, prev_end, next_start in raw_windows:
        for cs, ce in subdivide_window(s, e):
            chunks.append((cs, ce, prev_end, next_start))

    # Load TransChart stage events and annotate each chunk with its hint
    stage_events = []
    if transchart_docx and clip_number:
        stage_events = extract_stage_events(transchart_docx, clip_number, dialogue_cues)
        print(f"TransChart stage events loaded: {len(stage_events)}")

    chunks_with_hints = [
        (ms_to_ts(s), ms_to_ts(e), e - s,
         stage_hint_for_window(stage_events, s, e),
         ms_to_ts(prev_end), ms_to_ts(next_start))
        for s, e, prev_end, next_start in chunks
    ]

    print(f"Found {len(raw_windows)} silence gaps → {len(chunks_with_hints)} description slots:")
    for s, e, dur, hint, prev_end, next_start in chunks_with_hints:
        print(f"  {s} --> {e}  ({dur/1000:.1f}s)  {('['+hint+']') if hint else ''}")

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

    prompt = build_prompt(chunks_with_hints, stage_events)
    print(f"Generating {len(chunks_with_hints)} audio descriptions...")
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
