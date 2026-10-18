"""Markdown -> Word for the research note: bordered tables, content-based column widths,
landscape sections for wide tables, repeated header rows, inline bold/italic/code."""
import re, sys
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

SRC, OUT = sys.argv[1], sys.argv[2]
NAVY = RGBColor(0x1F, 0x38, 0x64)
GREY = RGBColor(0x59, 0x59, 0x59)
PORTRAIT_W, LANDSCAPE_W = Cm(17.0), Cm(25.7)   # usable widths with 2cm margins on A4

doc = Document()
st = doc.styles['Normal']; st.font.name = 'Calibri'; st.font.size = Pt(10)
st.element.rPr.rFonts.set(qn('w:eastAsia'), 'Calibri')
for name, size in (('Heading 1', 15), ('Heading 2', 12.5), ('Heading 3', 11)):
    s = doc.styles[name]; s.font.name = 'Calibri'; s.font.size = Pt(size); s.font.bold = True; s.font.color.rgb = NAVY
    s.element.rPr.rFonts.set(qn('w:eastAsia'), 'Calibri')
doc.styles['Title'].font.size = Pt(20); doc.styles['Title'].font.color.rgb = NAVY

def set_section(sec, landscape):
    sec.page_width, sec.page_height = (Cm(29.7), Cm(21.0)) if landscape else (Cm(21.0), Cm(29.7))
    sec.orientation = WD_ORIENT.LANDSCAPE if landscape else WD_ORIENT.PORTRAIT
    sec.left_margin = sec.right_margin = Cm(2.0); sec.top_margin = sec.bottom_margin = Cm(1.8)

set_section(doc.sections[0], False)
# header / footer with page number
def add_page_field(par):
    r = par.add_run(); f1 = OxmlElement('w:fldChar'); f1.set(qn('w:fldCharType'), 'begin')
    it = OxmlElement('w:instrText'); it.set(qn('xml:space'), 'preserve'); it.text = 'PAGE'
    f2 = OxmlElement('w:fldChar'); f2.set(qn('w:fldCharType'), 'end')
    r._r.append(f1); r._r.append(it); r._r.append(f2); r.font.size = Pt(8); r.font.color.rgb = GREY
hp = doc.sections[0].header.paragraphs[0]; hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
hr = hp.add_run('Asian Energy Services (ASIANENE) | Stage 2 research note v1 | 18-Oct-2026'); hr.font.size = Pt(8); hr.font.color.rgb = GREY
fp = doc.sections[0].footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
fr = fp.add_run('Internal research working note. Not for distribution. Page '); fr.font.size = Pt(8); fr.font.color.rgb = GREY
add_page_field(fp)

INLINE = re.compile(r'(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)')
def add_inline(par, text, size=None, bold=False, color=None):
    for tok in INLINE.split(text):
        if not tok: continue
        if tok.startswith('**') and tok.endswith('**'): r = par.add_run(tok[2:-2]); r.bold = True
        elif tok.startswith('*') and tok.endswith('*') and len(tok) > 2: r = par.add_run(tok[1:-1]); r.italic = True
        elif tok.startswith('`') and tok.endswith('`'): r = par.add_run(tok[1:-1]); r.font.name = 'Consolas'
        else: r = par.add_run(tok)
        if size: r.font.size = Pt(size)
        if bold: r.bold = True
        if color: r.font.color.rgb = color

def shade(cell, hexfill):
    tcPr = cell._tc.get_or_add_tcPr(); shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), hexfill); tcPr.append(shd)

def cell_margins(table, top=40, bottom=40, left=70, right=70):
    tblPr = table._tbl.tblPr; mar = OxmlElement('w:tblCellMar')
    for side, v in (('top', top), ('left', left), ('bottom', bottom), ('right', right)):
        e = OxmlElement(f'w:{side}'); e.set(qn('w:w'), str(v)); e.set(qn('w:type'), 'dxa'); mar.append(e)
    tblPr.append(mar)

def add_table(rows, landscape):
    ncol = len(rows[0]); body = rows[1:]
    usable = LANDSCAPE_W if landscape else PORTRAIT_W
    # column weight = sqrt of average content length, floor so short columns stay readable
    import math
    weights = []
    for j in range(ncol):
        lens = [len(r[j]) for r in rows if j < len(r)]
        weights.append(max(2.0, (sum(lens) / max(1, len(lens))) ** 0.72))
    tot = sum(weights); widths = [max(Cm(1.25), usable * w / tot) for w in weights]
    over = sum(widths) - usable
    if over > 0:
        big = [k for k in range(ncol) if widths[k] > Cm(1.25)]; s = sum(widths[k] for k in big)
        widths = [w - over * (w / s) if k in big else w for k, w in enumerate(widths)]
    fsize = 8 if ncol <= 5 else (7.5 if ncol <= 8 else 7)
    table = doc.add_table(rows=len(rows), cols=ncol); table.style = 'Table Grid'; table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    tblPr = table._tbl.tblPr; lay = OxmlElement('w:tblLayout'); lay.set(qn('w:type'), 'fixed'); tblPr.append(lay)
    cell_margins(table)
    widths = [int(w) for w in widths]
    for j in range(ncol): table.columns[j].width = widths[j]
    for i, row in enumerate(rows):
        tr = table.rows[i]
        if i == 0:
            trPr = tr._tr.get_or_add_trPr(); h = OxmlElement('w:tblHeader'); h.set(qn('w:val'), 'true'); trPr.append(h)
        for j in range(ncol):
            cell = tr.cells[j]; cell.width = widths[j]
            txt = row[j] if j < len(row) else ''
            par = cell.paragraphs[0]; par.paragraph_format.space_after = Pt(0); par.paragraph_format.space_before = Pt(0)
            # right-align numeric cells
            if i > 0 and re.fullmatch(r'[\s\d.,%()x+\-–−/]*\d[\s\d.,%()x+\-–−/]*', txt or ''): par.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            add_inline(par, txt, size=fsize, bold=(i == 0))
            if i == 0: shade(cell, 'DCE6F1')
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

def flush_table(buf):
    rows = []
    for l in buf:
        cells = [c.strip() for c in l.strip().strip('|').split('|')]
        if all(re.fullmatch(r':?-{2,}:?', c) for c in cells if c): continue   # separator row
        rows.append(cells)
    if not rows: return
    ncol = max(len(r) for r in rows); rows = [r + [''] * (ncol - len(r)) for r in rows]
    landscape = ncol >= 6
    if landscape:
        set_section(doc.add_section(WD_SECTION.NEW_PAGE), True)
        add_table(rows, True)
        set_section(doc.add_section(WD_SECTION.NEW_PAGE), False)
    else:
        add_table(rows, False)

lines = open(SRC, encoding='utf-8').read().split('\n')
tbuf = []
for raw in lines:
    l = raw.rstrip()
    if l.startswith('|'):
        tbuf.append(l); continue
    if tbuf: flush_table(tbuf); tbuf = []
    if not l.strip(): continue
    if l.startswith('# '):
        doc.add_paragraph(l[2:], style='Title')
    elif l.startswith('## '):
        p = doc.add_paragraph(style='Heading 1'); p.add_run(l[3:])
    elif l.startswith('### '):
        p = doc.add_paragraph(style='Heading 2'); p.add_run(l[4:])
    elif l.startswith('#### '):
        p = doc.add_paragraph(style='Heading 3'); p.add_run(l[5:])
    elif l.strip() == '---':
        p = doc.add_paragraph(); pPr = p._p.get_or_add_pPr(); bdr = OxmlElement('w:pBdr'); b = OxmlElement('w:bottom')
        b.set(qn('w:val'), 'single'); b.set(qn('w:sz'), '6'); b.set(qn('w:space'), '1'); b.set(qn('w:color'), '999999'); bdr.append(b); pPr.append(bdr)
    elif re.match(r'^\s*[-*] ', l):
        indent = (len(l) - len(l.lstrip())) // 2
        p = doc.add_paragraph(style='List Bullet'); p.paragraph_format.left_indent = Cm(0.6 + 0.6 * indent); p.paragraph_format.space_after = Pt(2)
        add_inline(p, re.sub(r'^\s*[-*] ', '', l))
    elif re.match(r'^\s*\d+\. ', l):
        m = re.match(r'^(\s*)(\d+)\. (.*)$', l); indent = len(m.group(1)) // 2
        p = doc.add_paragraph(); p.paragraph_format.left_indent = Cm(0.9 + 0.6 * indent); p.paragraph_format.first_line_indent = Cm(-0.6); p.paragraph_format.space_after = Pt(2)
        add_inline(p, f'{m.group(2)}.\t{m.group(3)}')
    else:
        p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(5)
        add_inline(p, l.strip())
if tbuf: flush_table(tbuf)
doc.save(OUT); print('saved', OUT)
