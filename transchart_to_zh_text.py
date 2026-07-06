"""
Extract the Chinese caption text for one clip from a CTC TransChart (.docx),
ready to paste into ArcTime Pro for timestamping (step 1 of the subtitle pipeline).

Outputs the whole Chinese Captions column verbatim, one row per line:
- speaker lines keep their label (e.g. "林肇德 [唱]:")
- stage / location-change directions (bracketed rows) are kept too
Only empty cells and the header row are dropped.

Usage:
    python transchart_to_zh_text.py <transchart_docx> --clip N [-o out.txt]

Example:
    python transchart_to_zh_text.py \\
        "CTC-source-materials-TEAMS/.../Feiyimeng_1964_OperaFilm_TransCharts.docx" \\
        --clip 2 -o Feiyimeng_1964_OperaFilm_Clip_2_zh.txt

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


def extract_zh_lines(table):
    """Left column (Chinese Captions) verbatim: speaker lines AND bracketed
    stage / location-change directions kept; only empty cells dropped."""
    lines = []
    for row in table.rows[1:]:  # skip header row
        cells = [c.text.replace("\xa0", " ").strip() for c in row.cells]
        if not cells:
            continue
        zh = cells[0]
        if not zh:
            continue
        lines.append(zh)
    return lines


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("docx", help="Path to the TransChart .docx")
    ap.add_argument("--clip", type=int, required=True, help="Clip number")
    ap.add_argument("-o", "--out", help="Output .txt path (default: clip<N>_zh.txt)")
    args = ap.parse_args()

    doc = Document(args.docx)
    table = find_clip_table(doc, args.clip)
    if table is None:
        sys.exit(f"No transchart table found for clip {args.clip}")

    lines = extract_zh_lines(table)
    if not lines:
        sys.exit(f"Clip {args.clip} table found but no Chinese caption lines extracted")

    out = args.out or f"clip{args.clip}_zh.txt"
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Wrote {len(lines)} caption line(s) to {out}\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
