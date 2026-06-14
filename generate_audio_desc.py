"""
Generate audio descriptions for a video clip using the Gemini API.
Descriptions are placed only in windows that avoid dialogue and sound effects.
Overlap with opera music or singing is allowed.

Output is a bilingual VTT file (Chinese + English per cue), matching the
format of feiyimeng-clip4-audiodesc.vtt.

Usage:
    python generate_audio_desc.py <video_file> <dialogue_vtt> <soundlabels_vtt> <output_vtt>

Example:
    python generate_audio_desc.py \
        assets/plays/guan-hanqing/feiyimeng-1964-opera-film/Feiyimeng_1964_OperaFilm_Clip_3_2x.mp4 \
        assets/subtitles/Feiyimeng_1964_OperaFilm_Clip_3_en.vtt \
        assets/subtitles/Feiyimeng_1964_OperaFilm_Clip_3_soundlabels.vtt \
        assets/subtitles/Feiyimeng_1964_OperaFilm_Clip_3_audiodesc.vtt

Requirements:
    pip install google-genai
    Set GEMINI_API_KEY environment variable before running.
"""

import sys
import os
import re
import json
import time
from google import genai
from google.genai import types

# Sound label keywords treated as hard blocks (must not overlap with descriptions)
HARD_SOUND_KEYWORDS = ["音效", "Sound effect"]


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


def is_hard_sound(cue):
    return any(kw in cue["text"] for kw in HARD_SOUND_KEYWORDS)


def find_windows(dialogue_cues, sound_cues, clip_end_ms, min_gap_ms=3000):
    """Find time windows free of dialogue and hard sound effects, minimum 3 seconds."""
    hard_blocks = []
    for c in dialogue_cues:
        hard_blocks.append((c["start_ms"], c["end_ms"]))
    for c in sound_cues:
        if is_hard_sound(c):
            hard_blocks.append((c["start_ms"], c["end_ms"]))

    # Merge overlapping hard blocks
    hard_blocks.sort()
    merged = []
    for s, e in hard_blocks:
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append([s, e])

    # Find gaps between hard blocks
    windows = []
    cursor = 0
    for s, e in merged:
        if s - cursor >= min_gap_ms:
            windows.append((cursor, s))
        cursor = max(cursor, e)
    if clip_end_ms - cursor >= min_gap_ms:
        windows.append((cursor, clip_end_ms))

    return [(ms_to_ts(s), ms_to_ts(e), e - s) for s, e in windows]


# TTS reading speed: ~2.2 English words per second, ~3 Chinese characters per second
def max_words(duration_ms):
    seconds = duration_ms / 1000
    return max(3, int(seconds * 2.2))


def build_prompt(windows):
    lines = []
    for s, e, dur_ms in windows:
        w = max_words(dur_ms)
        lines.append(f"- {s} to {e}  (max {w} English words)")
    window_list = "\n".join(lines)
    return f"""Watch this video clip carefully.

I will give you time windows where I need a brief visual description for audio playback.
These windows may overlap with background opera music, which is fine.

IMPORTANT: Each description will be read aloud by a TTS voice within the window duration.
You MUST stay within the word limit shown for each window — the audio must finish before the window ends.

For each window, write ONE phrase or short sentence describing what is visible:
costumes, physical movement, setting, facial expressions, or on-screen text.
Do NOT describe speech, dialogue, or music.

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


def generate_audio_desc(video_path, dialogue_vtt, soundlabels_vtt, output_path):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        sys.exit(1)

    dialogue_cues = parse_vtt_cues(dialogue_vtt)
    sound_cues = parse_vtt_cues(soundlabels_vtt)

    all_ends = [c["end_ms"] for c in dialogue_cues + sound_cues]
    clip_end_ms = max(all_ends) if all_ends else 120000

    windows = find_windows(dialogue_cues, sound_cues, clip_end_ms)
    if not windows:
        print("No suitable windows found.")
        sys.exit(0)
    print(f"Found {len(windows)} windows for audio descriptions:")
    for s, e, dur in windows:
        print(f"  {s} --> {e}  ({dur/1000:.1f}s, max {max_words(dur)} words)")

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

    prompt = build_prompt(windows)
    print("Generating audio descriptions...")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[types.Part.from_uri(file_uri=video_file.uri, mime_type="video/mp4"), prompt],
    )

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
    if len(sys.argv) != 5:
        print("Usage: python generate_audio_desc.py <video_file> <dialogue_vtt> <soundlabels_vtt> <output_vtt>")
        sys.exit(1)
    generate_audio_desc(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
