"""
Generate sound labels for a video clip using the Gemini API.
Outputs a VTT file with non-speech audio events in both Chinese and English,
ready to merge with existing dialogue subtitles.

Usage:
    python generate_sound_labels.py <video_file> <output_vtt>

Example:
    python generate_sound_labels.py \
        assets/plays/guan-hanqing/feiyimeng-1964-opera-film/Feiyimeng_1964_OperaFilm_Clip_3_2x.mp4 \
        assets/subtitles/Feiyimeng_1964_OperaFilm_Clip_3_soundlabels.vtt

Requirements:
    pip install google-genai
    Set GEMINI_API_KEY environment variable before running.
"""

import sys
import os
import json
import time
from google import genai
from google.genai import types

PROMPT = """
Watch this video clip carefully and listen to the audio track.

Your task is to identify non-speech sound events for use as subtitle captions.
Focus on BROAD, MEANINGFUL sections — not every individual instrument hit or string pluck.

Rules:
- Each event must be at least 2 seconds long. Do NOT label single instrument plucks,
  brief stings, or short percussive hits as separate events — merge them into the
  surrounding musical passage.
- Group continuous or closely spaced music of the same character into ONE event
  spanning the whole passage.
- Only use a separate event for a clearly distinct sound (e.g. a dramatic gasp,
  footsteps, dog barking) that stands apart from the background music.
- Do NOT include speech or dialogue — only non-speech audio.
- Do NOT overlap events with each other.

Label categories to use:
- [戲曲演奏] / [Opera orchestra plays] — for opera instrumental music passages
- [音效：驚呼] / [Sound effect: Gasp] — for gasps, shouts, non-verbal exclamations
- [音效：腳步聲] / [Sound effect: Footsteps] — for audible footsteps
- [音效：{描述}] / [Sound effect: {description}] — for other distinct, prominent sounds
- [環境音] / [Ambient sound] — for silence or low background noise

For each event provide:
- start: timestamp in HH:MM:SS.mmm format
- end: timestamp in HH:MM:SS.mmm format
- zh: a short Chinese label in square brackets
- en: a short English label in square brackets

Return only a JSON array, no other text:
[
  {"start": "00:00:00.000", "end": "00:00:08.000", "zh": "[戲曲演奏]", "en": "[Opera orchestra plays]"},
  {"start": "00:00:15.000", "end": "00:00:15.800", "zh": "[音效：驚呼]", "en": "[Sound effect: Gasp]"}
]
"""


def format_vtt_cue(index, start, end, zh, en):
    return f"{index}\n{start} --> {end}\n{zh}\n{en}\n"


def generate_sound_labels(video_path, output_path):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    print(f"Uploading {video_path} to Gemini...")
    with open(video_path, "rb") as f:
        video_file = client.files.upload(
            file=f,
            config=types.UploadFileConfig(mime_type="video/mp4")
        )
    print(f"Upload complete: {video_file.name}")

    # Wait for file to be ready
    while video_file.state.name == "PROCESSING":
        print("Waiting for file to be processed...")
        time.sleep(5)
        video_file = client.files.get(name=video_file.name)

    print("Analyzing audio for sound events...")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[types.Part.from_uri(file_uri=video_file.uri, mime_type="video/mp4"), PROMPT]
    )

    raw = response.text.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    events = json.loads(raw)
    print(f"Found {len(events)} sound events.")

    lines = ["WEBVTT", ""]
    for i, event in enumerate(events, start=1):
        lines.append(format_vtt_cue(i, event["start"], event["end"], event["zh"], event["en"]))

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Sound labels written to {output_path}")
    print("\nReview the output and edit timestamps or labels as needed.")
    print("Then merge with the dialogue VTT using merge_captions.py.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_sound_labels.py <video_file> <output_vtt>")
        sys.exit(1)
    generate_sound_labels(sys.argv[1], sys.argv[2])
