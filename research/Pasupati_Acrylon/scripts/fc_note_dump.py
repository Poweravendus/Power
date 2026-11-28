"""Final check helper: dump the note's paragraphs and tables with indices. Usage: fc_note_dump.py note.docx"""
import sys, docx
d = docx.Document(sys.argv[1])
body = d.element.body
pi = ti = 0
for el in body.iterchildren():
    tag = el.tag.split('}')[1]
    if tag == 'p':
        p = d.paragraphs[pi]; pi += 1
        if p.text.strip(): print(f'P{pi-1} [{p.style.name}] {p.text}')
    elif tag == 'tbl':
        t = d.tables[ti]; ti += 1
        print(f'--- T{ti-1} ({len(t.rows)}x{len(t.columns)})')
        for ri, r in enumerate(t.rows):
            print(f'  r{ri}: ' + ' | '.join(c.text.replace("\n", " / ") for c in r.cells))
for s in d.sections:
    for p in s.header.paragraphs + s.footer.paragraphs:
        if p.text.strip(): print('HDR/FTR:', p.text)
