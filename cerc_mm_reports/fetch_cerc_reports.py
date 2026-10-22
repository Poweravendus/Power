#!/usr/bin/env python3
"""Download CERC Market Monitoring (short-term market) monthly reports.

Source index: https://cercind.gov.in/report_MM.html
Each year page (report_MM-<year>.html) lists one PDF per month. Files are saved
next to this script as YYYY-MM.pdf (and YYYY-MM_comparison.pdf for the
"Comparison of Key Statistics" extras), and manifest.csv maps each saved file
back to its source URL and original filename.

Usage: python3 fetch_cerc_reports.py [first_year] [last_year]
"""
import csv, os, re, subprocess, sys, time, urllib.parse

BASE = "https://cercind.gov.in/"
MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
OUT = os.path.dirname(os.path.abspath(__file__))


def curl(url, dest=None):
    cmd = ["curl", "-sS", "-L", "--max-time", "300", "-w", "%{http_code} %{content_type}", url]
    cmd += ["-o", dest] if dest else []
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.stdout, r.stderr


def pdf_links(year):
    html_path = os.path.join(OUT, f".index-{year}.html")
    status, err = curl(f"{BASE}report_MM-{year}.html", html_path)
    if not status.startswith("200"):
        print(f"{year}: index fetch failed ({status.strip()}) {err.strip()}")
        return []
    html = open(html_path, encoding="utf-8", errors="replace").read()
    os.remove(html_path)
    links = re.findall(r'href="([^"]*\.pdf)"', html, flags=re.I)
    return [l for l in links if "market_monitoring" in l.lower()]


def normalized_name(rel, year):
    base = os.path.basename(rel)
    low = base.lower().replace("februrary", "february").replace("market", "").replace("mmc", "")
    kind = "comparison" if "comparison" in low else "report"
    m = next((i for i, k in enumerate(MONTHS, 1) if k in low), None)
    yr = re.search(r"(20\d\d)", low)
    yr = yr.group(1) if yr else str(year)
    if low.startswith("april22"):  # one-off oddly named file on the site
        yr, m = "2022", 4
    if m is None:
        raise ValueError(f"cannot infer month from {base!r}")
    return f"{yr}-{m:02d}.pdf" if kind == "report" else f"{yr}-{m:02d}_comparison.pdf"


def main():
    first = int(sys.argv[1]) if len(sys.argv) > 1 else 2020
    last = int(sys.argv[2]) if len(sys.argv) > 2 else time.gmtime().tm_year
    rows, fails = [], []
    for year in range(first, last + 1):
        for rel in pdf_links(year):
            name = normalized_name(rel, year)
            url = BASE + urllib.parse.quote(rel)
            rows.append((name, url, os.path.basename(rel)))
    assert len({r[0] for r in rows}) == len(rows), "duplicate normalized names"
    with open(os.path.join(OUT, "manifest.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["file", "url", "original_name"])
        w.writerows(rows)
    for name, url, _ in rows:
        dest = os.path.join(OUT, name)
        if os.path.exists(dest) and os.path.getsize(dest) > 10_000:
            continue
        ok = False
        for attempt in range(4):
            status, err = curl(url, dest)
            ok = status.startswith("200") and "pdf" in status
            if ok:
                break
            time.sleep(2 ** (attempt + 1))
        print(name, status.strip(), "OK" if ok else f"FAIL {err.strip()}")
        if not ok:
            fails.append(name)
    print(f"{len(rows)} files listed, {len(fails)} failed: {fails}")


if __name__ == "__main__":
    main()
