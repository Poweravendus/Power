"""Helpers to edit the IndiGrid report in place while keeping its formatting."""
import copy
import docx
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

W = lambda t: qn('w:' + t)


def body_elements(doc):
    return list(doc.element.body.iterchildren())


def remove(el):
    el.getparent().remove(el)


def _template_rpr(p_el):
    r = p_el.find('.//' + W('r'))
    if r is not None and r.find(W('rPr')) is not None:
        return copy.deepcopy(r.find(W('rPr')))
    return None


def _make_run(text, rpr, bold=None, italic=None):
    r = OxmlElement('w:r')
    if rpr is not None:
        rp = copy.deepcopy(rpr)
        for tag, val in (('b', bold), ('bCs', bold), ('i', italic), ('iCs', italic)):
            if val is None:
                continue
            for old in rp.findall(W(tag)):
                rp.remove(old)
            if val:
                e = OxmlElement('w:' + tag)
                # keep schema order loosely: b/i near the start is accepted by Word
                rp.insert(0, e)
        # drop highlight / comment-related shading from template runs
        for old in rp.findall(W('highlight')):
            rp.remove(old)
        r.append(rp)
    elif bold or italic:
        rp = OxmlElement('w:rPr')
        if bold:
            rp.append(OxmlElement('w:b'))
        if italic:
            rp.append(OxmlElement('w:i'))
        r.append(rp)
    t = OxmlElement('w:t')
    t.set(qn('xml:space'), 'preserve')
    t.text = text
    r.append(t)
    return r


def set_par(p_el, segments, keep_drawing=False):
    """Replace the runs of paragraph element p_el with segments: str or [(text, bold), ...]."""
    if isinstance(segments, str):
        segments = [(segments, None)]
    rpr = _template_rpr(p_el)
    for child in list(p_el):
        if child.tag in (W('r'), W('hyperlink'), W('ins'), W('del'), W('commentRangeStart'), W('commentRangeEnd'),
                         W('proofErr'), W('bookmarkStart'), W('bookmarkEnd'), W('smartTag'), W('fldSimple')):
            if keep_drawing and child.find('.//' + W('drawing')) is not None:
                continue
            p_el.remove(child)
    for seg in segments:
        text, bold = (seg if isinstance(seg, tuple) else (seg, None))[:2]
        italic = seg[2] if isinstance(seg, tuple) and len(seg) > 2 else None
        p_el.append(_make_run(text, rpr, bold, italic))
    return p_el


def clone_par(p_el, after=None):
    new = copy.deepcopy(p_el)
    # strip section properties from clones
    ppr = new.find(W('pPr'))
    if ppr is not None and ppr.find(W('sectPr')) is not None:
        ppr.remove(ppr.find(W('sectPr')))
    (after if after is not None else p_el).addnext(new)
    return new


# ------------------------------------------------------------------ tables
def rows(tbl):
    return tbl.findall(W('tr'))


def cells(tr):
    return tr.findall(W('tc'))


def span(tc):
    tcpr = tc.find(W('tcPr'))
    if tcpr is not None and tcpr.find(W('gridSpan')) is not None:
        return int(tcpr.find(W('gridSpan')).get(W('val')))
    return 1


def set_cell(tc, text, bold=None, italic=None):
    """Set the text of a cell (str or list of lines / segment lists), keeping its formatting."""
    ps = tc.findall(W('p'))
    first = ps[0]
    for extra in ps[1:]:
        tc.remove(extra)
    lines = text if isinstance(text, list) else [text]
    prev = first
    for k, line in enumerate(lines):
        p = first if k == 0 else copy.deepcopy(first)
        if k:
            prev.addnext(p)
        segs = line if isinstance(line, list) else [(line if line is not None else '', bold, italic)]
        set_par(p, segs)
        prev = p


def cell_text(tc):
    return ''.join(t.text or '' for t in tc.iter(W('t')))


def clone_row(tbl, src_idx, after_idx=None):
    rs = rows(tbl)
    new = copy.deepcopy(rs[src_idx])
    rs[after_idx if after_idx is not None else src_idx].addnext(new)
    return new


def delete_rows(tbl, idxs):
    rs = rows(tbl)
    for i in sorted(set(idxs), reverse=True):
        tbl.remove(rs[i])


def keep_rows(tbl, idxs):
    n = len(rows(tbl))
    delete_rows(tbl, [i for i in range(n) if i not in set(idxs)])


def fill_row(tr, values, bold=None):
    """values: list aligned to the row's cells (None = leave as is)."""
    for tc, v in zip(cells(tr), values):
        if v is not None:
            set_cell(tc, v, bold=bold)


def delete_grid_cols(tbl, grid_idxs, keep_width=True):
    """Delete grid columns (0-based grid positions), handling gridSpan; redistribute widths."""
    grid = tbl.find(W('tblGrid'))
    gcols = grid.findall(W('gridCol'))
    widths = [int(g.get(W('w'))) for g in gcols]
    total = sum(widths)
    del_set = set(grid_idxs)
    for tr in rows(tbl):
        pos = 0
        for tc in list(cells(tr)):
            s = span(tc)
            covered = [p for p in range(pos, pos + s) if p in del_set]
            if covered:
                if len(covered) >= s:
                    tr.remove(tc)
                else:
                    tc.find(W('tcPr')).find(W('gridSpan')).set(W('val'), str(s - len(covered)))
            pos += s
    for i in sorted(del_set, reverse=True):
        grid.remove(gcols[i])
    remaining = [w for i, w in enumerate(widths) if i not in del_set]
    if keep_width and remaining:
        scale = total / sum(remaining)
        new_w = [int(w * scale) for w in remaining]
        for g, w in zip(grid.findall(W('gridCol')), new_w):
            g.set(W('w'), str(w))
        # update tcW of every cell
        for tr in rows(tbl):
            pos = 0
            for tc in cells(tr):
                s = span(tc)
                tcpr = tc.find(W('tcPr'))
                if tcpr is not None and tcpr.find(W('tcW')) is not None:
                    tcpr.find(W('tcW')).set(W('w'), str(sum(new_w[pos:pos + s])))
                    tcpr.find(W('tcW')).set(W('type'), 'dxa')
                pos += s


def grid_texts(tbl):
    out = []
    for tr in rows(tbl):
        out.append([cell_text(tc) for tc in cells(tr)])
    return out
