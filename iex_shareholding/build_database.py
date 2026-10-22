#!/usr/bin/env python3
"""
Build a full historical shareholding database for Indian Energy Exchange (NSE: IEX)
from the company's SEBI Regulation 31 shareholding-pattern filings (XBRL) hosted by NSE.

Buckets produced per filing:
    promoter, fii, dii, government, kmp, public, others   (shares, % of total, no. of holders)

Usage:
    python3 build_database.py              # build from cached files in data/
    python3 build_database.py --refresh    # also pull new filings / insider data from NSE first

Outputs go to output/ (CSV, SQLite, Excel).
"""
import argparse
import json
import re
import sqlite3
import sys
import time
from datetime import datetime, date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RAW = DATA / "raw_xbrl"
OUT = ROOT / "output"
MASTER_JSON = DATA / "nse_shareholding_master.json"
INSIDER_JSON = DATA / "nse_insider_disclosures.json"
SYMBOL = "IEX"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")

BUCKETS = ["promoter", "fii", "dii", "government", "kmp", "public", "others"]
BUCKET_LABELS = {
    "promoter": "Promoter & promoter group",
    "fii": "FII / FPI (foreign institutions)",
    "dii": "DII (domestic institutions)",
    "government": "Government",
    "kmp": "Key Managerial Personnel",
    "public": "Public (non-institutional, excl. KMP)",
    "others": "Others (non-promoter non-public: employee trusts, DR holders)",
}

# --------------------------------------------------------------------------- NSE download
def _nse_session():
    import requests
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept": "*/*", "Accept-Language": "en-US,en;q=0.9",
                      "Referer": "https://www.nseindia.com/"})
    try:
        s.get("https://www.nseindia.com/", timeout=30)   # sets cookies; a 403 body is fine
    except Exception as e:  # noqa
        print(f"  warning: NSE homepage request failed ({e}); continuing", file=sys.stderr)
    return s


def refresh_from_nse():
    s = _nse_session()
    print("Fetching shareholding master list from NSE ...")
    r = s.get("https://www.nseindia.com/api/corporate-share-holdings-master",
              params={"index": "equities", "symbol": SYMBOL}, timeout=60)
    r.raise_for_status()
    master = r.json()
    MASTER_JSON.write_text(json.dumps(master, indent=1))
    print(f"  {len(master)} filings listed")
    RAW.mkdir(parents=True, exist_ok=True)
    for rec in master:
        target = RAW / f"SHP_{rec['date']}.xml"
        if target.exists() and target.stat().st_size > 0:
            continue
        print(f"  downloading {rec['date']} ...")
        rr = s.get(rec["xbrl"], timeout=120)
        if rr.status_code != 200 or b"<xbrli:xbrl" not in rr.content[:2000]:
            print(f"  warning: could not fetch {rec['xbrl']} (HTTP {rr.status_code})", file=sys.stderr)
            continue
        target.write_bytes(rr.content)
        time.sleep(1)
    print("Fetching insider-trading (PIT Reg. 7) disclosures ...")
    r = s.get("https://www.nseindia.com/api/corporates-pit",
              params={"index": "equities", "symbol": SYMBOL}, timeout=60)
    if r.status_code == 200:
        INSIDER_JSON.write_text(json.dumps(r.json(), indent=1))
    else:
        print(f"  warning: insider API returned HTTP {r.status_code}", file=sys.stderr)


# --------------------------------------------------------------------------- XBRL parsing
FACT_RE = r'<in-bse-shp:(\w+) contextRef="{ctx}"[^>]*>([^<]*)<'


def _facts(xml, ctx):
    """All in-bse-shp facts for one contextRef -> {tag: value}."""
    return {m.group(1): m.group(2).strip()
            for m in re.finditer(FACT_RE.format(ctx=re.escape(ctx)), xml)}


def _num(v):
    if v in (None, "", "-"):
        return None
    try:
        return int(v)
    except ValueError:
        return float(v)


def _norm_member(name):
    n = name[:-6] if name.endswith("Member") else name
    n = n.lower()
    n = n.replace("goverments", "governments").replace("catergory", "category")
    return n


def parse_filing(path: Path):
    xml = path.read_text(encoding="utf-8", errors="ignore")
    d = datetime.strptime(path.stem[4:], "%d-%b-%Y").date()
    tax = re.search(r'xbrl/shp/([\d-]+)/in-bse-shp"', xml)
    taxonomy = tax.group(1) if tax else "unknown"

    contexts = re.findall(r'<xbrli:context id="([^"]+)">(.*?)</xbrli:context>', xml, re.S)

    # 1) category-of-shareholder rows (one explicit member on the category axis)
    members = {}
    for cid, body in contexts:
        if "typedMember" in body:
            continue
        mem = re.findall(r'<xbrldi:explicitMember dimension="([^"]+)">in-bse-shp:(\w+)</xbrldi:explicitMember>', body)
        if len(mem) != 1 or not mem[0][0].endswith("CategoryOfShareholdersAxis"):
            continue
        if "<xbrli:instant>" not in body:
            continue
        f = _facts(xml, cid)
        shares = _num(f.get("NumberOfShares")) if f.get("NumberOfShares") not in (None, "") else _num(f.get("NumberOfFullyPaidUpEquityShares"))
        if shares is None:
            continue
        key = _norm_member(mem[0][1])
        members[key] = {
            "member": mem[0][1],
            "context": cid,
            "holders": _num(f.get("NumberOfShareholders")),
            "shares": shares,
            "pct_reported": _num(f.get("ShareholdingAsAPercentageOfTotalNumberOfShares")),
            "demat_shares": _num(f.get("NumberOfEquitySharesHeldInDematerializedForm")),
        }

    # 2) named / detail rows (typed-member duration contexts with a NameOfTheShareholder fact)
    details = []
    for cid, body in contexts:
        if "typedMember" not in body:
            continue
        f = _facts(xml, cid)
        name = f.get("NameOfTheShareholder")
        if not name:
            continue
        axis = re.search(r'typedMember dimension="in-bse-shp:(\w+)Axis"', body)
        inst_ctx = cid[:-1] + "I" if cid.endswith("D") else cid[2:] if cid.startswith("D_") else None
        fi = _facts(xml, inst_ctx) if inst_ctx else {}
        shares = _num(fi.get("NumberOfShares")) if fi.get("NumberOfShares") else _num(fi.get("NumberOfFullyPaidUpEquityShares"))
        sub = f.get("CategoryOfOtherInstitutions") or f.get("CategoryOfOtherNonInstitutions") or ""
        details.append({
            "table": axis.group(1) if axis else cid,
            "name": name,
            "sub_category": sub,
            "pac_names": f.get("NameOfThePAC", ""),
            "pan_disclosed": "yes" if any(k.startswith("PermanentAccountNumber") for k in f) else "no",
            "holders": _num(fi.get("NumberOfShareholders")),
            "shares": shares,
            "pct_reported": _num(fi.get("ShareholdingAsAPercentageOfTotalNumberOfShares")),
            "context": cid,
        })

    return {"quarter_end": d, "taxonomy": taxonomy, "file": path.name, "members": members, "details": details}


# --------------------------------------------------------------------------- bucket logic
def bucketize(filing):
    m = filing["members"]

    def g(k, field="shares"):
        v = m.get(k, {}).get(field)
        return v or 0

    total = g("shareholdingpattern")
    total_h = g("shareholdingpattern", "holders")
    out = {}
    out["promoter"] = (g("shareholdingofpromoterandpromotergroup"), g("shareholdingofpromoterandpromotergroup", "holders"))
    out["others"] = (g("sharesheldbynonpromoternonpublicshareholders"), g("sharesheldbynonpromoternonpublicshareholders", "holders"))

    if "institutionsforeign" in m:
        # SEBI format effective Sep-2022 quarter onwards: explicit domestic/foreign/KMP split
        fmt = "2022+"
        out["fii"] = (g("institutionsforeign"), g("institutionsforeign", "holders"))
        out["dii"] = (g("institutionsdomestic"), g("institutionsdomestic", "holders"))
        out["government"] = (g("governments"), g("governments", "holders"))
        out["kmp"] = (g("keymanagerialpersonnel"), g("keymanagerialpersonnel", "holders"))
        out["public"] = (g("noninstitutions") - out["kmp"][0], g("noninstitutions", "holders") - out["kmp"][1])
        kmp_disclosed = True
    else:
        # Pre-Sep-2022 format: 'Institutions' mixes foreign & domestic; NBFCs sit under non-institutions;
        # no KMP category exists. Foreign share of 'Other institutions' is taken from its detail table
        # (rows whose sub-category is a foreign type such as Overseas Corporate Bodies).
        fmt = "pre-2022"
        foreign_keys = ["institutionsforeignportfolioinvestor", "foreignventurecapitalinvestors", "overseasdepositories"]
        oth_foreign = sum((r["shares"] or 0) for r in filing["details"]
                          if r["table"].startswith("DetailsOfSharesHeldByOtherInstitutions")
                          and r["sub_category"].lower() != "other" and r["name"] == r["sub_category"])
        oth_foreign_h = sum((r["holders"] or 0) for r in filing["details"]
                            if r["table"].startswith("DetailsOfSharesHeldByOtherInstitutions")
                            and r["sub_category"].lower() != "other" and r["name"] == r["sub_category"])
        fii = sum(g(k) for k in foreign_keys) + oth_foreign
        fii_h = sum(g(k, "holders") for k in foreign_keys) + oth_foreign_h
        nbfc, nbfc_h = g("nbfcsregisteredwithrbi"), g("nbfcsregisteredwithrbi", "holders")
        out["fii"] = (fii, fii_h)
        out["dii"] = (g("institutions") - fii + nbfc, g("institutions", "holders") - fii_h + nbfc_h)
        out["government"] = (g("centralgovernmentorstategovernmentsorpresidentofindia"),
                             g("centralgovernmentorstategovernmentsorpresidentofindia", "holders"))
        out["kmp"] = (None, None)
        out["public"] = (g("noninstitutions") - nbfc, g("noninstitutions", "holders") - nbfc_h)
        kmp_disclosed = False

    check = sum((out[b][0] or 0) for b in BUCKETS)
    if check != total:
        raise AssertionError(f"{filing['file']}: buckets sum to {check}, filing total is {total}")

    row = {"quarter_end": filing["quarter_end"], "total_shares": total, "total_holders": total_h,
           "kmp_disclosed": "yes" if kmp_disclosed else "no", "format": fmt}
    for b in BUCKETS:
        sh, h = out[b]
        row[f"{b}_shares"] = sh
        row[f"{b}_pct"] = round(sh / total * 100, 4) if sh is not None and total else None
        row[f"{b}_holders"] = h
    return row


# --------------------------------------------------------------------------- build
def build():
    files = sorted(RAW.glob("SHP_*.xml"), key=lambda p: datetime.strptime(p.stem[4:], "%d-%b-%Y"))
    if not files:
        sys.exit("No XBRL files in data/raw_xbrl. Run with --refresh.")
    master = {}
    if MASTER_JSON.exists():
        for rec in json.loads(MASTER_JSON.read_text()):
            master[datetime.strptime(rec["date"], "%d-%b-%Y").date()] = rec

    filings, summary, cats, named = [], [], [], []
    for p in files:
        f = parse_filing(p)
        row = bucketize(f)
        qe = f["quarter_end"]
        is_qe = (qe.month, qe.day) in [(3, 31), (6, 30), (9, 30), (12, 31)]
        rec = master.get(qe, {})
        filings.append({
            "quarter_end": qe, "filing_type": "quarterly" if is_qe else "event-based",
            "nse_broadcast_date": rec.get("broadcastDate", ""), "sebi_taxonomy_version": f["taxonomy"],
            "total_shares": row["total_shares"], "kmp_disclosed": row["kmp_disclosed"],
            "xbrl_url": rec.get("xbrl", ""), "raw_file": f["file"],
        })
        summary.append(row)
        total = row["total_shares"]
        for key, mv in f["members"].items():
            cats.append({"quarter_end": qe, "category_member": mv["member"], "category_key": key,
                         "holders": mv["holders"], "shares": mv["shares"],
                         "pct_of_total": round(mv["shares"] / total * 100, 4) if total else None,
                         "pct_as_reported": mv["pct_reported"], "demat_shares": mv["demat_shares"]})
        for r in f["details"]:
            named.append({"quarter_end": qe, "table": r["table"], "shareholder_name": r["name"],
                          "sub_category": r["sub_category"], "pac_names": r["pac_names"],
                          "holders": r["holders"], "shares": r["shares"],
                          "pct_of_total": round(r["shares"] / total * 100, 4) if (r["shares"] and total) else None,
                          "pct_as_reported": r["pct_reported"]})

    df_summary = pd.DataFrame(summary)
    df_filings = pd.DataFrame(filings)
    df_cats = pd.DataFrame(cats)
    df_named = pd.DataFrame(named)

    df_insider = pd.DataFrame()
    if INSIDER_JSON.exists():
        raw = json.loads(INSIDER_JSON.read_text()).get("data", [])
        cols = ["date", "acqName", "personCategory", "secType", "acqMode", "tdpTransactionType", "secAcq", "secVal",
                "befAcqSharesNo", "befAcqSharesPer", "afterAcqSharesNo", "afterAcqSharesPer",
                "acqfromDt", "acqtoDt", "intimDt", "anex", "exchange", "remarks", "xbrl"]
        df_insider = pd.DataFrame(raw)[[c for c in cols if raw and c in raw[0]]].rename(columns={
            "date": "broadcast_date", "acqName": "person_name", "personCategory": "person_category",
            "secType": "security_type", "acqMode": "mode", "tdpTransactionType": "transaction_type",
            "secAcq": "securities_transacted", "secVal": "value_inr", "befAcqSharesNo": "shares_before",
            "befAcqSharesPer": "pct_before", "afterAcqSharesNo": "shares_after", "afterAcqSharesPer": "pct_after",
            "acqfromDt": "transaction_from", "acqtoDt": "transaction_to", "intimDt": "intimated_to_company",
            "anex": "regulation", "xbrl": "xbrl_url"})

    OUT.mkdir(parents=True, exist_ok=True)
    df_summary.to_csv(OUT / "iex_shareholding_summary.csv", index=False)
    df_filings.to_csv(OUT / "iex_filings.csv", index=False)
    df_cats.to_csv(OUT / "iex_shareholding_categories_long.csv", index=False)
    df_named.to_csv(OUT / "iex_named_holders.csv", index=False)
    df_insider.to_csv(OUT / "iex_insider_disclosures.csv", index=False)

    # SQLite
    db = OUT / "iex_shareholding.sqlite"
    if db.exists():
        db.unlink()
    con = sqlite3.connect(db)
    for name, df in [("summary", df_summary), ("filings", df_filings), ("categories", df_cats),
                     ("named_holders", df_named), ("insider_disclosures", df_insider)]:
        d2 = df.copy()
        for c in d2.columns:
            if d2[c].dtype == object and len(d2) and isinstance(d2[c].iloc[0], date):
                d2[c] = d2[c].astype(str)
        d2.to_sql(name, con, index=False)
    con.execute("""CREATE VIEW summary_pct AS SELECT quarter_end, total_shares,
        promoter_pct, fii_pct, dii_pct, government_pct, kmp_pct, public_pct, others_pct FROM summary""")
    con.commit(); con.close()

    # Excel
    pct_cols = ["quarter_end", "total_shares"] + [f"{b}_pct" for b in BUCKETS]
    sh_cols = ["quarter_end", "total_shares"] + [f"{b}_shares" for b in BUCKETS]
    h_cols = ["quarter_end", "total_holders"] + [f"{b}_holders" for b in BUCKETS]
    notes = pd.DataFrame({"note": [
        "Source: SEBI Reg. 31 shareholding-pattern XBRL filings by Indian Energy Exchange Ltd, downloaded from NSE archives.",
        "Percentages are recomputed as shares / total shares * 100 (the as-reported field changed from percent to fraction in late 2025).",
        "KMP is reported only as an aggregate in SEBI filings. The category did not exist before the Sep-2022 quarter: kmp is blank there and included within public.",
        "Pre-Sep-2022 filings: NBFCs are reclassified from non-institutions to DII, and Overseas Corporate Bodies from 'Other institutions' to FII, to match the later SEBI format.",
        "public = Non-institutions minus KMP (resident individuals, NRIs, bodies corporate incl. the Dalmia group, HUFs, trusts, clearing members, IEPF, directors & relatives).",
        "others = non-promoter non-public holders (IEX employee benefit trust; DR holders are nil).",
        "The 08-Dec-2021 filing is event-based (post 2:1 bonus issue), not a quarter end.",
        "Named-holder rows reproduce the filing's detail tables; in pre-Sep-2022 filings they contain sub-category header rows as well as named entities.",
        "Insider disclosures are PIT Regulation 7 filings relayed by NSE; they cover transactions only, not point-in-time holdings of every KMP.",
    ] + [f"{b}: {BUCKET_LABELS[b]}" for b in BUCKETS]})
    with pd.ExcelWriter(OUT / "iex_shareholding.xlsx", engine="openpyxl") as xw:
        df_summary[pct_cols].to_excel(xw, sheet_name="Summary_pct", index=False)
        df_summary[sh_cols].to_excel(xw, sheet_name="Summary_shares", index=False)
        df_summary[h_cols].to_excel(xw, sheet_name="Summary_holders", index=False)
        df_cats.to_excel(xw, sheet_name="Categories_long", index=False)
        df_named.to_excel(xw, sheet_name="Named_holders", index=False)
        df_insider.to_excel(xw, sheet_name="Insider_disclosures", index=False)
        df_filings.to_excel(xw, sheet_name="Filings", index=False)
        notes.to_excel(xw, sheet_name="Notes", index=False)
        for ws in xw.book.worksheets:
            for col in ws.columns:
                width = max(len(str(c.value)) if c.value is not None else 0 for c in col)
                ws.column_dimensions[col[0].column_letter].width = min(max(10, width + 2), 60)
            ws.freeze_panes = "B2"

    print(f"Built {len(df_summary)} filings -> {OUT}")
    print(df_summary[pct_cols].to_string(index=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true", help="download new filings from NSE before building")
    a = ap.parse_args()
    if a.refresh:
        refresh_from_nse()
    build()
