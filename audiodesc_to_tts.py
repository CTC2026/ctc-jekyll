"""
Convert audio description VTT to spoken audio files using OpenAI TTS.
Generates one MP3 per cue for both Chinese and English.

Usage:
    python audiodesc_to_tts.py <audiodesc_vtt> <output_folder>

Example:
    python audiodesc_to_tts.py \
        assets/subtitles/Feiyimeng_1964_OperaFilm_Clip_3_audiodesc.vtt \
        assets/subtitles/Feiyimeng_1964_OperaFilm_Clip_3_audiodesc_audio

Output structure:
    output_folder/
        en/cue_01.mp3, cue_02.mp3, ...
        zh/cue_01.mp3, cue_02.mp3, ...

Requirements:
    pip install openai
    Set OPENAI_API_KEY environment variable before running.
"""

import sys
import os
import re
from pathlib import Path
from openai import OpenAI

EN_VOICE = "nova"
MODEL = "tts-1"


def parse_audiodesc_vtt(path):
    """Parse bilingual audiodesc VTT — each cue has zh on line 1, en on line 2."""
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
        if not content:
            continue
        cues.append({
            "start": m.group(1).replace(",", "."),
            "end": m.group(2).replace(",", "."),
            "en": content[0].strip(),
        })
    return cues


def generate_tts(client, text, voice, output_path):
    response = client.audio.speech.create(
        model=MODEL,
        voice=voice,
        input=text,
        response_format="mp3",
    )
    response.stream_to_file(output_path)


def main(vtt_path, output_folder):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        sys.exit(1)

    cues = parse_audiodesc_vtt(vtt_path)
    if not cues:
        print("No cues found in VTT file.")
        sys.exit(1)
    print(f"Found {len(cues)} cues.")

    out_dir = Path(output_folder)
    out_dir.mkdir(parents=True, exist_ok=True)

    client = OpenAI(api_key=api_key)

    for i, cue in enumerate(cues, start=1):
        label = f"cue_{i:02d}"
        print(f"\n[{label}] {cue['start']} --> {cue['end']}")
        en_path = out_dir / f"{label}.mp3"
        print(f"  {cue['en']}")
        generate_tts(client, cue["en"], EN_VOICE, str(en_path))
        print(f"  → {en_path}")

    print(f"\nDone. {len(cues)} audio files written to {output_folder}/")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python audiodesc_to_tts.py <audiodesc_vtt> <output_folder>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
