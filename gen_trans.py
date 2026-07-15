#!/usr/bin/env python3
import zipfile, re, html, sys
from xml.etree import ElementTree as ET
ns='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

def tables(docx):
    z=zipfile.ZipFile(docx); root=ET.fromstring(z.read('word/document.xml').decode())
    out=[]
    for tbl in root.find(ns+'body').iter(ns+'tbl'):
        rows=[]
        for tr in tbl.iter(ns+'tr'):
            cells=[]
            for tc in tr.findall(ns+'tc'):
                txt='\n'.join(''.join(t.text for t in p.iter(ns+'t') if t.text) for p in tc.iter(ns+'p'))
                cells.append(txt.strip())
            rows.append(cells)
        out.append(rows)
    return out

def block(rows, summary):
    body=[]
    body.append('<details class="translation">')
    body.append(f'<summary>{summary}</summary>')
    body.append('<table class="transcript">')
    # header row assumed first
    hdr=rows[0]
    body.append('<thead><tr>'+''.join(f'<th scope="col">{html.escape(c)}</th>' for c in hdr)+'</tr></thead>')
    body.append('<tbody>')
    for r in rows[1:]:
        cells=''.join(f'<td>{html.escape(c)}</td>' for c in r)
        body.append(f'<tr>{cells}</tr>')
    body.append('</tbody>')
    body.append('</table>')
    body.append('</details>')
    return '\n'.join(body)

if __name__=='__main__':
    docx=sys.argv[1]
    tbs=tables(docx)
    summaries=sys.argv[2:]
    for i,rows in enumerate(tbs):
        s=summaries[i] if i<len(summaries) else f'Translation notes for clip {i+1}'
        print(f'@@@CLIP{i+1}@@@')
        print(block(rows,s))
