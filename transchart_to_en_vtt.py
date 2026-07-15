"""
Create an English VTT from a Chinese Arctime VTT and a CTC TransChart (.docx).

Finds the table for the specified clip number in the transchart, then matches
each VTT cue's Chinese text against the transchart rows to find the English
translation. Works even when one transchart row covers multiple VTT cues
(e.g., multi-line singing verses).

Speaker labels from the transchart's English column (e.g. "Lin Zhaode
(singing):") are kept and re-attached to the output, but only when the speaker
changes — so the caption identifies who is speaking (MDAS 1.2.2) without needing
a manual pass. Location cues (bracketed scene changes) still need to be added by
hand, since condensing them to a short tag takes judgment.

Usage:
    python transchart_to_en_vtt.py <zh_vtt> <transchart_docx> <output_en_vtt> --clip N

Example:
    python transchart_to_en_vtt.py \\
        assets/subtitles/Feiyimeng_1964_OperaFilm_Clip_3_ch.vtt \\
        "/Users/sophiali/Downloads/ctc-source-materials/Modules, Guan Hanqing/Modules, Feiyimeng Materials/Feiyimeng_1964_OperaFilm Materials/Feiyimeng_1964_OperaFilm_TransCharts.docx" \\
        assets/subtitles/Feiyimeng_1964_OperaFilm_Clip_3_en.vtt \\
        --clip 3

Requirements:
    pip install python-docx
"""

import sys
import re
import argparse
from docx import Document
from docx.table import Table
from docx.oxml.ns import qn


def find_clip_table(doc, clip_number):
    """Find the table that follows 'Translation notes for clip N' in the docx."""
    body = list(doc.element.body)
    for i, child in enumerate(body):
        if child.tag.endswith("}p"):
            text = "".join(r.text or "" for r in child.iter(qn("w:t")))
            if f"clip {clip_number}" in text.lower():
                for j in range(i + 1, len(body)):
                    if body[j].tag.endswith("}tbl"):
                        return Table(body[j], doc)
    return None


def is_stage_direction(zh, en):
    zh, en = zh.strip(), en.strip()
    return zh.startswith("[") and en.startswith("[")


def strip_speaker_label(text):
    """Remove 'Speaker [action]:' prefix from Chinese or English text."""
    # Matches patterns like: 女鬼 [唱]: or Zhang Peizan (singing): or 女鬼:
    text = re.sub(r"^[^\:：]{1,40}[\:：]\s*", "", text.replace("\xa0", " ")).strip()
    return text


def split_speaker(text):
    """Split 'Speaker (action): body' into (speaker, body).

    The speaker keeps its own parenthetical (e.g. 'Lin Zhaode (singing)'), which
    the caption track needs. Returns (None, text) when there is no speaker prefix.
    """
    text = text.replace("\xa0", " ").strip()
    m = re.match(r"^([^\:：]{1,40})[\:：]\s*(.*)$", text, re.S)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return None, text


def strip_stage_notes(en_text):
    """Remove inline stage direction parentheticals from English text."""
    return re.sub(r"\([^)]+\)\s*", "", en_text).strip()


def normalize_zh(text):
    """Strip spaces and punctuation for fuzzy matching."""
    return re.sub(r"[\s，。？！、：；""''「」【】…\.\,\?\!\:\;]", "", text)


def parse_clip_table(table):
    """Return list of (zh_clean, zh_norm, en_body, en_speaker) for dialogue rows.

    en_body is the translation with its speaker prefix split off (so matching and
    verse-splitting work on the words alone) and inline action notes removed; the
    speaker is kept separately and re-attached at output time, only when it changes.
    """
    entries = []
    for row in table.rows[1:]:  # skip header
        cells = [c.text.replace("\xa0", " ").strip() for c in row.cells]
        if len(cells) < 2:
            continue
        zh_raw, en_raw = cells[0], cells[1]
        if not zh_raw or not en_raw:
            continue
        if is_stage_direction(zh_raw, en_raw):
            continue
        zh_clean = strip_speaker_label(zh_raw)
        en_speaker, en_body = split_speaker(en_raw)
        en_body = strip_stage_notes(en_body)
        zh_norm = normalize_zh(zh_clean)
        entries.append((zh_clean, zh_norm, en_body, en_speaker))
    return entries


def parse_vtt(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    cues = []
    for block in re.split(r"\n{2,}", text.strip()):
        lines = block.strip().splitlines()
        ts_line = next((l for l in lines if "-->" in l), None)
        if not ts_line:
            continue
        m = re.match(r"(\S+)\s+-->\s+(\S+)", ts_line)
        if not m:
            continue
        content = [l.strip() for l in lines if "-->" not in l and not re.match(r"^\d+$", l.strip()) and l.strip()]
        if content:
            cues.append({"start": m.group(1), "end": m.group(2), "text": " ".join(content)})
    return cues


def split_en_sentences(en_text):
    """Split English text into sentences at strong punctuation boundaries."""
    sents = [s.strip() for s in re.split(r'(?<=[.?!])\s+', en_text.strip()) if s.strip()]
    return sents if len(sents) > 1 else [en_text.strip()]


def assign_sentences_to_positions(en_sents, n):
    """
    Assign m English sentences to n cue positions (n >= m).

    When n > m, the translator combined some Chinese lines into one English
    sentence. The longest English sentence(s) most likely cover multiple Chinese
    lines, so we expand the (n - m) longest sentences to fill 2 positions each.
    This gives content-correct alignment without requiring an external API.

    Returns a list of (sentence_idx, occurrence, total_occurrences) per position.
    """
    m = len(en_sents)
    if n <= m:
        return [(min(k * m // n, m - 1), 0, 1) for k in range(n)]
    # n > m: some sentences must be split across multiple cue positions.
    # Distribute the n positions across the m sentences as evenly as possible;
    # the longest sentences absorb the extra splits. Handles n > 2*m too (a
    # single sentence split into 3+ parts), which the old doubling-only logic
    # could not, and which crashed with an IndexError.
    base, rem = divmod(n, m)
    longest_first = sorted(range(m), key=lambda idx: len(en_sents[idx].split()), reverse=True)
    parts = {idx: base for idx in range(m)}
    for idx in longest_first[:rem]:
        parts[idx] += 1
    result = []
    for s_idx in range(m):
        total = parts[s_idx]
        for occ in range(total):
            result.append((s_idx, occ, total))
    return result  # length == sum(parts) == n


def match_all(cues, entries):
    """
    Match VTT cues to transchart entries in order.
    Uses a forward pointer so earlier entries are not reused once the sequence
    has moved past them, preventing short strings from matching the wrong row.
    Returns a list of (en_text, row_index) tuples, one per cue (None if unmatched).
    """
    results = [None] * len(cues)
    pointer = 0  # current position in entries

    for i, cue in enumerate(cues):
        # Strip the speaker label from the cue too: the Chinese VTT now carries
        # labels (e.g. "林肇德 [唱]:"), and leaving them in would keep the first
        # line of a verse from matching its transchart row.
        cue_norm = normalize_zh(strip_speaker_label(cue["text"]))
        matched = False
        # Search forward from pointer
        for j in range(pointer, len(entries)):
            zh_norm = entries[j][1]
            if cue_norm and cue_norm in zh_norm:
                results[i] = (entries[j][2], j)
                # Advance past this row if the cue covers it fully (exact match),
                # so subsequent cues don't re-match an exhausted row
                if cue_norm == zh_norm:
                    pointer = j + 1
                else:
                    pointer = j
                matched = True
                break
        if not matched:
            # Fallback: try reverse substring
            for j in range(pointer, len(entries)):
                zh_norm = entries[j][1]
                if zh_norm and zh_norm in cue_norm:
                    results[i] = (entries[j][2], j)
                    pointer = j
                    matched = True
                    break
    return results


def resolve_groups(translations, cues, entries):
    """
    Post-process match_all results: for groups of consecutive cues that matched
    the same transchart row (e.g. individual lines of a singing verse), assign
    each cue its own portion of the English translation.

    Uses assign_sentences_to_positions, which identifies which English sentence
    absorbed multiple Chinese lines by finding the longest sentence(s) and
    expanding them to cover the extra cue positions.
    """
    result = list(translations)
    i = 0
    while i < len(result):
        if result[i] is None:
            i += 1
            continue
        en_text, row_idx = result[i]
        j = i + 1
        while j < len(result) and result[j] is not None and result[j][1] == row_idx:
            j += 1
        group_size = j - i
        if group_size == 1:
            i = j
            continue

        en_sents = split_en_sentences(en_text)
        positions = assign_sentences_to_positions(en_sents, group_size)

        for k, cue_idx in enumerate(range(i, j)):
            s_idx, occ, total = positions[k]
            sentence = en_sents[s_idx]
            if total == 1:
                result[cue_idx] = (sentence, row_idx)
            else:
                words = sentence.split()
                start = len(words) * occ // total
                end = len(words) * (occ + 1) // total
                result[cue_idx] = (' '.join(words[start:end]), row_idx)

        i = j
    return result


def write_vtt(cues, path):
    lines = ["WEBVTT", ""]
    for i, cue in enumerate(cues, start=1):
        lines.append(str(i))
        lines.append(f"{cue['start']} --> {cue['end']}")
        lines.append(cue["en"])
        lines.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"{len(cues)} cues written to {path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("zh_vtt")
    parser.add_argument("transchart_docx")
    parser.add_argument("output_en_vtt")
    parser.add_argument("--clip", type=int, required=True,
                        help="Clip number to look up in the transchart (e.g. 3)")
    args = parser.parse_args()

    doc = Document(args.transchart_docx)
    table = find_clip_table(doc, args.clip)
    if table is None:
        print(f"ERROR: Could not find table for clip {args.clip} in {args.transchart_docx}")
        sys.exit(1)

    entries = parse_clip_table(table)
    print(f"Transchart dialogue rows for clip {args.clip}: {len(entries)}")

    cues = parse_vtt(args.zh_vtt)
    print(f"VTT cues: {len(cues)}")

    translations = match_all(cues, entries)
    translations = resolve_groups(translations, cues, entries)

    output_cues = []
    unmatched = []
    prev_speaker = None
    for cue, match in zip(cues, translations):
        if match is None:
            unmatched.append(cue["text"])
            en = f"[UNMATCHED: {cue['text']}]"
        else:
            en = match[0]
            speaker = entries[match[1]][3]
            # Prefix the speaker only when it changes (MDAS 1.2.2), matching the
            # caption convention of not repeating the label on continuation lines.
            if speaker and speaker != prev_speaker:
                en = f"{speaker}: {en}"
            if speaker:
                prev_speaker = speaker
        output_cues.append({**cue, "en": en})

    write_vtt(output_cues, args.output_en_vtt)

    if unmatched:
        print(f"\nWARNING: {len(unmatched)} cues could not be matched:")
        for t in unmatched:
            print(f"  {t}")
    else:
        print("\nAll cues matched successfully.")

    print("\nFirst 5 cues for review:")
    for c in output_cues[:5]:
        print(f"  [{c['start']}] {c['text']}")
        print(f"           → {c['en']}")


if __name__ == "__main__":
    main()
