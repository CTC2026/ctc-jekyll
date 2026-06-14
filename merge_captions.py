"""
Merge dialogue VTT files with sound labels into two separate captions files —
one Chinese, one English — sorted by start time.

Usage:
    python merge_captions.py <zh_vtt> <en_vtt> <sound_labels_vtt> <output_zh> <output_en>

Example:
    python merge_captions.py \
        assets/subtitles/Feiyimeng_1964_OperaFilm_Clip_3_ch.vtt \
        assets/subtitles/Feiyimeng_1964_OperaFilm_Clip_3_en.vtt \
        assets/subtitles/Feiyimeng_1964_OperaFilm_Clip_3_soundlabels.vtt \
        assets/subtitles/Feiyimeng_1964_OperaFilm_Clip_3_ch.vtt \
        assets/subtitles/Feiyimeng_1964_OperaFilm_Clip_3_en.vtt
"""

import sys
import re


def parse_vtt(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()

    cues = []
    blocks = re.split(r"\n{2,}", text.strip())
    for block in blocks:
        lines = block.strip().splitlines()
        timestamp_line = None
        content_lines = []
        for line in lines:
            if "-->" in line:
                timestamp_line = line
            elif timestamp_line and not re.match(r"^\d+$", line.strip()):
                content_lines.append(line.strip())
        if timestamp_line and content_lines:
            m = re.match(r"(\S+)\s+-->\s+(\S+)", timestamp_line)
            if m:
                cues.append({
                    "start": m.group(1),
                    "end": m.group(2),
                    "lines": content_lines,
                })
    return cues


def timestamp_to_ms(ts):
    parts = ts.replace(",", ".").split(":")
    h, m, s = int(parts[0]), int(parts[1]), float(parts[2])
    return int((h * 3600 + m * 60 + s) * 1000)


def write_vtt(cues, output_path):
    output_lines = ["WEBVTT", ""]
    for i, cue in enumerate(cues, start=1):
        output_lines.append(str(i))
        output_lines.append(f"{cue['start']} --> {cue['end']}")
        output_lines.extend(cue["lines"])
        output_lines.append("")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    print(f"{len(cues)} cues written to {output_path}")


def merge(zh_path, en_path, sound_path, output_zh, output_en):
    zh_cues = parse_vtt(zh_path)
    en_cues = parse_vtt(en_path)
    sound_cues = parse_vtt(sound_path)

    # Build zh sound label cues (first line of each sound cue)
    zh_sound = [{"start": c["start"], "end": c["end"], "lines": [c["lines"][0]]} for c in sound_cues]
    # Build en sound label cues (second line of each sound cue)
    en_sound = [{"start": c["start"], "end": c["end"], "lines": [c["lines"][1] if len(c["lines"]) > 1 else c["lines"][0]]} for c in sound_cues]

    zh_all = sorted(zh_cues + zh_sound, key=lambda c: timestamp_to_ms(c["start"]))
    en_all = sorted(en_cues + en_sound, key=lambda c: timestamp_to_ms(c["start"]))

    write_vtt(zh_all, output_zh)
    write_vtt(en_all, output_en)


if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python merge_captions.py <zh_vtt> <en_vtt> <sound_labels_vtt> <output_zh> <output_en>")
        sys.exit(1)
    merge(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
