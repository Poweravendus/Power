#!/usr/bin/env python3
"""Extract the two Day Ahead Market (DAM) entity-volume tables from each CERC
Market Monitoring report in this directory:

  * Volume of Electricity SOLD in Day Ahead Market through Power Exchanges
  * Volume of Electricity PURCHASED in Day Ahead Market through Power Exchanges

Jan-May 2020 reports (before RTM launched) title these "... through Power
Exchanges" without the words "Day Ahead"; the printed total equals the
day-ahead collective volume quoted in the report text, so they are the same
tables and are included.

Output: dam_volumes.csv (long format) and dam_volumes.xlsx (long + pivots),
plus a validation summary on stdout.
"""
import csv, glob, os, re, subprocess, sys
import pdfplumber

HERE = os.path.dirname(os.path.abspath(__file__))
TITLE = re.compile(
    r"Table-\s*\d+\s*:\s*VOLUME OF ELECTRICITY\s+(SOLD|PURCHASED)\s+"
    r"(?:IN\s+DAY\s+AHEAD\s+MARKET\s+)?THROUGH\s+POWER", re.I)
EXCLUDE = re.compile(r"GREEN|HIGH PRICE|REAL TIME|TERM AHEAD|BILATERAL|RTM|G-DAM|HP-DAM", re.I)
NUM = re.compile(r"^-?[\d,]*\.?\d+$")
TOTAL = re.compile(r"^\s*TOTAL\s*$", re.I)


def to_num(s):
    s = (s or "").replace(",", "").strip()
    return float(s) if NUM.match(s) else None


def clean_cells(row):
    return [(c or "").replace("\n", " ").strip() for c in row]


def split_row(row):
    """Return (name, [numbers]) where either part may be empty."""
    cells = [c for c in clean_cells(row) if c]
    nums = [to_num(c) for c in cells]
    k = len(cells)
    while k > 0 and nums[k - 1] is not None:
        k -= 1
    return " ".join(cells[:k]).strip(), nums[k:]


HEADERISH = re.compile(r"^(Table-\s*\d+|POWER EXCHANGES,|EXCHANGES,\s*[A-Z]+\s*\d{4}|Name of the Entity|Volume of (Sale|Purchase)|\(MUs?\)$)", re.I)


def extract_table(pdf, start_page, kind, log):
    """Collect rows from start_page onward until a Total row is found.

    A wrapped entity name comes out of pdfplumber as separate rows: a name-only
    fragment before and/or after the row carrying the numbers (at a page break
    even the numbers sit in a row of their own). A name-only fragment is held
    until the next row shows whether it prefixes that row (numbers-only) or
    suffixes the previous one (anything else).
    """
    rows, pending = [], ""

    def flush_as_suffix():
        nonlocal pending
        if pending:
            if rows:
                rows[-1] = (rows[-1][0] + " " + pending,) + rows[-1][1:]
            else:
                log.append(f"orphan name fragment dropped: {pending!r}")
            pending = ""

    for pno in range(start_page, min(start_page + 8, len(pdf.pages))):
        for tbl in pdf.pages[pno].find_tables():
            for raw in tbl.extract():
                name, numeric = split_row(raw)
                if not name and not numeric:
                    continue
                if name and (TITLE.search(name) or HEADERISH.match(name)
                             or re.match(r"volume (sold|purchased) by top", name, re.I)):
                    continue
                if TOTAL.match(name):
                    flush_as_suffix()
                    return rows, numeric[0] if numeric else None
                if name and not numeric:
                    flush_as_suffix()
                    pending = name
                    continue
                if not name:                       # numbers only: pending is the prefix
                    if not pending:
                        log.append(f"numbers without a name dropped: {numeric}")
                        continue
                    name, pending = pending, ""
                else:
                    flush_as_suffix()
                rows.append((name, numeric[0], numeric[1] if len(numeric) > 1 else None))
    flush_as_suffix()
    return rows, None


def page_texts(path):
    """Per-page text via pdftotext (much faster than pdfplumber for a scan)."""
    out = subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True, text=True).stdout
    return out.split("\f")


def find_tables(path):
    """Map 'sold'/'purchased' -> page index of the actual table (skip TOC)."""
    found = {}
    for i, text in enumerate(page_texts(path)):
        if i < 6 and text.count("Table-") > 5:   # table-of-contents pages
            continue
        for m in TITLE.finditer(text):
            snippet = text[m.start(): m.start() + 120]
            if EXCLUDE.search(snippet):
                continue
            found.setdefault(m.group(1).lower(), i)
    return found


def main():
    out_rows, summary = [], []
    files = sorted(f for f in glob.glob(os.path.join(HERE, "20??-??.pdf")))
    for f in files:
        month = os.path.basename(f)[:7]
        with pdfplumber.open(f) as pdf:
            pages = find_tables(f)
            for kind in ("sold", "purchased"):
                if kind not in pages:
                    summary.append((month, kind, "TABLE NOT FOUND", 0, None, None, None))
                    continue
                log = []
                rows, total = extract_table(pdf, pages[kind], kind, log)
                for line in log:
                    print(f"  {month} {kind}: {line}")
                s = round(sum(r[1] for r in rows), 2)
                p = round(sum(r[2] for r in rows if r[2] is not None), 2)
                status = "ok"
                if total is None:
                    status = "NO TOTAL ROW"
                elif abs(s - total) > max(0.5, 0.001 * total):
                    status = f"SUM MISMATCH diff={s - total:.2f}"
                elif not rows or abs(p - 100) > 1.0:
                    status = f"PCT SUM {p}"
                summary.append((month, kind, status, len(rows), s, total, p))
                for name, vol, pct in rows:
                    out_rows.append((month, kind, name, vol, pct))

    with open(os.path.join(HERE, "dam_volumes.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["month", "table", "entity", "volume_mu", "pct_of_volume"])
        w.writerows(out_rows)
    with open(os.path.join(HERE, "dam_volumes_validation.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["month", "table", "status", "rows", "sum_volume", "printed_total", "sum_pct"])
        w.writerows(summary)

    bad = [s for s in summary if s[2] != "ok"]
    print(f"{len(files)} reports, {len(out_rows)} rows, {len(bad)} tables with issues")
    for s in bad:
        print("  ", s)


if __name__ == "__main__":
    main()
