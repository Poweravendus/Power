#!/usr/bin/env python3
"""Annual, player-wise analysis of DAM sold / purchased volumes.

Reads dam_volumes.csv (monthly, entity names as printed by CERC), maps the
printed names onto consistent player names (CERC renamed many entities,
especially at the Aug-2024 report redesign), sums by year, and writes
dam_annual_analysis.xlsx with:

  README                      method, assumptions, caveats
  Entity_Mapping              every printed name -> player -> group (audit / override here)
  Sold_Annual_CY              player x calendar year, all players
  Purchased_Annual_CY
  Sold_Top15_CY               top 15 players (by total over the period) + Others + Total, MU and % share
  Purchased_Top15_CY
  Sold_Top15_ByYear_CY        each year's own top 15 + Others
  Purchased_Top15_ByYear_CY
  Sold_Top15_Group_CY         same as Top15 but at parent-group level (Adani Green SPVs, NTPC plants, ... rolled up)
  Purchased_Top15_Group_CY
  *_FY                        the same tables on an April-March fiscal-year basis
"""
import os, re
import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__))

# --- 1. printed name -> player (first matching pattern wins) -----------------
# Player = clean company / state name. Plants, stages and SPVs of the same company
# are merged. Renames were identified from non-overlapping active periods in the
# data (old label's last month is immediately followed by the new label's first).
ENTITY_ALIASES = [
    # states and UTs
    (r"^MP$|^MADHYA PRADESH$", "Madhya Pradesh"),
    (r"^J ?& ?K$|^JAMMU ?(&|AND)? ?KASHMIR$", "Jammu & Kashmir"),
    (r"^CHANDIGARH", "Chandigarh"),
    (r"^GOA( WR| SR)?$", "Goa"),
    (r"^PONDICHERRY|^PUDUCHERRY", "Puducherry"),
    (r"^DD ?& ?DNH$|^DADRA & NAGAR HAVELI$|^DAMAN AND DIU|^DAMAN & DIU", "DNH & Daman Diu (UT)"),
    (r"^GOVERNMENT OF HIMACHAL PRADESH|^HIMACHAL PRADESH$", "Himachal Pradesh"),   # state free-power shares listed separately from Aug-2024
    (r"^UTTAR PRADESH$", "Uttar Pradesh"), (r"^WEST BENGAL$", "West Bengal"), (r"^TAMIL NADU$", "Tamil Nadu"),
    (r"^ANDHRA PRADESH$", "Andhra Pradesh"), (r"^ARUNACHAL PRADESH$", "Arunachal Pradesh"),
    (r"^DADRA|^DAMAN", "DNH & Daman Diu (UT)"),
    # cross-border
    (r"^NEPAL|^NEA\b|^NEP$", "Nepal (NEA / NVVN)"),
    (r"DGPCL|DRUK GREEN|BASOCHHU", "Druk Green Power (Bhutan)"),
    # generators / traders / consumers
    (r"^SEMBCORP|^SEIL ENERGY|^THERMAL POWERTECH", "SEIL Energy (ex-Sembcorp)"),
    (r"^TEESTA (STG ?3|HEP)|TEESTA URJA|TEESTA.?III", "Teesta Urja"),
    (r"^JAYPEE NIGRIE", "Jaypee Nigrie"),
    (r"^JINDAL STAGE-II|^JINDAL POWER$|^JINDAL POWER LIMITED", "Jindal Power"),
    (r"^ESSAR POWER|^MAHAN ENERGEN", "Mahan Energen (ex-Essar Power MP)"),
    (r"^JITPL|^JINDAL INDIA (THERMAL )?POWER", "Jindal India Thermal Power"),
    (r"^DCPP$|JINDAL STEEL & POWER", "Jindal Steel & Power"),
    (r"^DB POWER|^D B POWER", "DB Power"),
    (r"^GMR CHATT?ISGARH|^RPREL|^ARTPP|^REGL$|^RAIGARH_ADANI|^ADANI POWER", "Adani Power"),
    (r"ADANI (GREEN|RENEWABLE|SOLAR|WIND|HYBRID)|^ADANI_|^ASEJTL", "Adani Green Energy"),
    (r"^ADANI PORTS", "Adani Ports & SEZ"),
    (r"^AMBUJA", "Ambuja Cements"),
    (r"^MB POWER", "MB Power"),
    (r"^ACBIL|^ACB \(INDIA\)", "ACB India"),
    (r"^RKM POWER|^R\.?K\.?M POWERGEN", "RKM Powergen"),
    (r"^KARCHAM WANGTOO|^BASPA", "JSW Hydro (Karcham Wangtoo)"),
    (r"^AD HYDRO", "AD Hydro Power"),
    (r"^NTPC|^SIMHADRI (FSP|FLOATING)|^RAMAGUNDAM FLOATING|^NPGC|^NABINAGAR POWER|^NTPP BRBCL|^BRBCL|^KANTI BIJLEE|^IGSTPS|^NTECL|^BONGAIGAON", "NTPC"),
    (r"^NEEPCO|^KAMENG HYDRO|^AGARTALA GAS|^ASSAM GAS BASED", "NEEPCO"),
    (r"^NLC$|^NLC INDIA|^NTPL$|^NLC TAMIL ?NADU", "NLC India"),
    (r"^SKS POWER", "SKS Power"),
    (r"^MARUTI (COAL|CLEAN)", "Maruti Clean Coal"),
    (r"^DIKCHU", "Dikchu HEP"),
    (r"^SHREE CEMENT", "Shree Cement"),
    (r"^SIMHAPURI", "Simhapuri Energy"),
    (r"^COASTGEN|^COASTAL ENERGEN", "Coastal Energen"),
    (r"^EMCO$|^GMR WARORA", "GMR Warora (ex-EMCO)"),
    (r"^GMR KAMALANGA", "GMR Kamalanga"),
    (r"^BALCO|^BHARAT ALUMINIUM", "BALCO"),
    (r"^JHABUA POWER", "Jhabua Power"),
    (r"^IL&FS", "ITPCL (IL&FS Tamil Nadu)"),
    (r"^DHARIWAL", "Dhariwal Infrastructure"),
    (r"^ONGC PALATANA|^PALATANA", "OTPC Palatana"),
    (r"^RENEW|^RENEW_", "ReNew Power"),
    (r"^ADEPT", "Adept Renewable"),
    (r"^AMPS HAZIRA|^AMNSIL|^ARCELORMITTAL|^ESSAR STEEL", "AM/NS India (Hazira)"),
    (r"^NCR ALLAHABAD|^NORTH CENTRAL RAILWAY|^RAIL$", "Indian Railways"),
    (r"^MEENAKSHI", "Meenakshi Energy"),
    (r"^GREENKO|BUDHIL", "Greenko"),
    (r"^IND BARATH ENERGY UTKAL|^JSW ENERGY \(UTKAL\)", "JSW Energy (Utkal, ex-Ind Barath)"),
    (r"^KSK MAHANADI", "KSK Mahanadi"),
    (r"^ADHUNIK", "Adhunik Power"),
    (r"^DVC$|^DAMODAR VALLEY", "DVC"),
    (r"^DGEN", "Torrent Power (DGEN)"),
    (r"^SPECTRUM", "Spectrum Power"),
    (r"^JUNIPER", "Juniper Green Energy"),
    (r"^AMP ENERGY", "Amp Energy"),
    (r"^SERENTICA", "Serentica Renewables"),
    (r"^SPRNG", "Sprng Energy"),
    (r"^TP SAURYA|^TATA POWER", "Tata Power"),
    (r"^SJVN", "SJVN"), (r"^NHPC", "NHPC"), (r"^AVAADA", "Avaada"), (r"^ACME", "ACME"),
    (r"^AZURE", "Azure Power"), (r"^HERO", "Hero Future Energies"),
    (r"^SAINJ", "Sainj HEP"), (r"^SINGOLI", "Singoli Bhatwari HEP"), (r"^SORANG", "Sorang HEP"),
    (r"^JORETHANG", "Jorethang HEP"), (r"^TASHIDENG", "Tashiding HEP"), (r"^CHUZACHEN", "Chuzachen HEP"),
    (r"^RGPPL", "RGPPL (Dabhol)"),
    (r"^HVDC", "HVDC Raigarh"),
    (r"^KAPP", "KAPP 3&4 (NPCIL)"),
    (r"^TRN ENERGY", "TRN Energy"),
    (r"^IBEUL", "IBEUL"),
    (r"VEDANTA", "Vedanta (Chhattisgarh)"),
    (r"^RELIANCE INDUSTRIES", "Reliance Industries (Jamnagar)"),
    (r"^TEHRI", "THDC (Tehri PSP)"),
]

# --- 2. player -> parent group (only where a group is obvious from the name) --
GROUP_RULES = [
    (r"^Adani Power|^Mahan Energen", "Adani Power (incl. Mahan Energen)"),
    (r"^JSW|^KSK Mahanadi", "JSW Energy (incl. Utkal, Hydro, KSK Mahanadi)"),
    (r"^GMR", "GMR Energy"),
    (r"^Jindal Power|^Jindal Steel", "Jindal Power + JSPL"),
]

ACRONYMS = {"NTPC", "NLC", "DVC", "JSW", "SJVN", "NHPC", "HEP", "TPP", "STPP", "UT", "GMR", "SKS", "RKM", "DB", "MB",
            "ACB", "SEIL", "KSK", "OTPC", "BALCO", "NEEPCO", "NPGC", "BRBCL", "ITPCL", "JITPL", "JSPL", "IREP", "PSP",
            "DCPP", "ONGC", "NEA", "NVVN", "PSS", "BESS", "II", "III", "IV", "AP", "MP", "HP", "UP", "CTU", "STU", "ISTS",
            "SEZ", "LLP", "TPS", "FSP", "MW", "HPD", "DNH", "DD", "PH2", "U1", "U2", "WR", "ER", "NR", "SR", "NER", "JV"}


def clean_default(norm):
    """Fallback for unmapped names: drop corporate suffixes, title-case, keep acronyms."""
    s = re.sub(r"\b(PRIVATE|PVT\.?|LIMITED|LTD\.?|COMPANY|CO\.?)\b\.?", " ", norm)
    s = re.sub(r"\s+", " ", s).strip(" ,._-")
    words = []
    for w in s.split(" "):
        core = re.sub(r"[^A-Z0-9&/]", "", w)
        words.append(w if core in ACRONYMS else w.title())
    return " ".join(words)


def normalize(name):
    s = re.sub(r"\s+", " ", str(name).upper()).strip()
    s = re.sub(r"\s+,", ",", s)
    return s


def player_of(norm):
    for pat, canon in ENTITY_ALIASES:
        if re.search(pat, norm):
            return canon
    return clean_default(norm)


def group_of(player):
    for pat, grp in GROUP_RULES:
        if re.search(pat, player):
            return grp
    return player


# --- 3. load and label ------------------------------------------------------
    df = pd.read_csv(os.path.join(HERE, "dam_volumes.csv"))
    df["norm"] = df["entity"].map(normalize)
    df["player"] = df["norm"].map(player_of)
    df["group"] = df["player"].map(group_of)
    df["cy"] = df["month"].str[:4]
    yr, mo = df["month"].str[:4].astype(int), df["month"].str[5:7].astype(int)
    fy_start = yr.where(mo >= 4, yr - 1)
    df["fy"] = "FY" + fy_start.astype(str) + "-" + ((fy_start + 1) % 100).astype(str).str.zfill(2)

    first, last = df["month"].min(), df["month"].max()
    CY_LABEL = {y: (f"{y} (Jan-Mar)" if y == last[:4] and last[5:] != "12" else y)
                for y in sorted(df["cy"].unique())}
    FY_LABEL = {}
    for f in sorted(df["fy"].unique()):
        months = sorted(df.loc[df["fy"] == f, "month"].unique())
        FY_LABEL[f] = f if len(months) == 12 else f"{f} ({months[0]} to {months[-1]} only)"

    mapping = (df.groupby(["entity", "norm", "player", "group"])
                 .agg(tables=("table", lambda s: "/".join(sorted(set(s)))),
                      first_month=("month", "min"), last_month=("month", "max"),
                      months=("month", "count"), total_mu=("volume_mu", "sum"))
                 .reset_index().sort_values("total_mu", ascending=False))
    mapping["renamed"] = (mapping["norm"] != mapping["player"]).map({True: "yes", False: ""})


    # --- 4. table builders ------------------------------------------------------
    def annual(sub, key, period, labels):
        piv = sub.pivot_table(index=key, columns=period, values="volume_mu", aggfunc="sum").fillna(0)
        piv = piv.rename(columns=labels)
        piv["TOTAL"] = piv.sum(axis=1)
        piv = piv.sort_values("TOTAL", ascending=False).round(2)
        piv.index.name = key
        return piv


    def top15_fixed(piv, n=15):
        """Top n by total over the whole period; everything else -> Others."""
        top = piv.head(n).copy()
        others = piv.iloc[n:].sum()
        total = piv.sum()
        top.loc[f"OTHERS ({len(piv) - n} players)"] = others
        top.loc["TOTAL"] = total
        share = (top.div(total, axis=1) * 100).round(2)
        return top.round(2), share


    def top15_by_year(piv, n=15):
        """Each period's own top n + Others, stacked vertically."""
        blocks = []
        for col in [c for c in piv.columns if c != "TOTAL"]:
            s = piv[col][piv[col] > 0].sort_values(ascending=False)
            total = s.sum()
            rows = [(col, i + 1, name, v, v / total * 100) for i, (name, v) in enumerate(s.head(n).items())]
            rows.append((col, "", f"OTHERS ({max(len(s) - n, 0)} players)", s.iloc[n:].sum(), s.iloc[n:].sum() / total * 100))
            rows.append((col, "", "TOTAL", total, 100.0))
            blocks.append(pd.DataFrame(rows, columns=["period", "rank", "player", "volume_mu", "share_pct"]))
        return pd.concat(blocks, ignore_index=True).round(2)


    # --- 5. write workbook ------------------------------------------------------
    README = f"""DAM (Day Ahead Market) volumes sold and purchased through power exchanges, by player and year.
    Source: CERC Market Monitoring monthly reports, {first} to {last}, tables 'Volume of Electricity Sold / Purchased in Day Ahead Market through Power Exchanges'.
    Units: MU (million units = GWh). Shares are % of that period's table total.

    PERIODS
    - CY sheets: calendar years. {CY_LABEL[last[:4]]} is partial.
    - FY sheets: Indian fiscal years (April-March). {list(FY_LABEL.values())[0]} is partial.

    PLAYER NAMES
    - CERC prints inconsistent names across report eras (e.g. 'MP' then 'Madhya Pradesh'; 'RPREL' -> 'ARTPP' -> 'Adani Power Limited-Raipur TPP').
      Renames were merged where the old label stops exactly when the new one starts. See Entity_Mapping (column 'renamed') for every merge; the raw printed name is kept there so any merge can be undone.
    - 'Government of Himachal Pradesh_<plant>' rows (state free-power shares, listed separately from Aug-2024) are folded into HIMACHAL PRADESH; before Aug-2024 they were inside the single state row.
    - Inferred, not certain: AMPS HAZIRA = AM/NS India (Hazira); RENEW_SR_SLR = ReNew Surya Ravi; ADANI_4RE = Adani Renewable Energy Holding Four. Each follows the stop/start timing rule but the acronyms are not expanded in the reports.
    - NOT merged: plant-level rows CERC introduced from Aug-2024 (dozens of Adani Green SPVs, individual NTPC stations, ReNew SPVs). These stay separate players in the Top15 sheets. The *_Group_* sheets roll them up to a parent group so you can see e.g. Adani Green as one seller.
    - KSK Mahanadi is grouped under JSW Energy (acquired 2025) only in the Group sheets.

    TOP 15
    - Top15_* sheets rank by total volume over the whole period, then show each year; the same 15 players in every column. Good for trend reading, but a player that only appeared in 2025-26 can rank low.
    - Top15_ByYear_* sheets give each year's own top 15, so new entrants show up.

    A player can be both a seller and a buyer (states especially), so Sold and Purchased lists are independent.
    """

    out = os.path.join(HERE, "dam_annual_analysis.xlsx")
    with pd.ExcelWriter(out, engine="openpyxl") as xw:
        pd.DataFrame({"README": README.strip().split("\n")}).to_excel(xw, sheet_name="README", index=False)
        mapping.to_excel(xw, sheet_name="Entity_Mapping", index=False)
        for basis, period, labels in (("CY", "cy", CY_LABEL), ("FY", "fy", FY_LABEL)):
            for kind in ("sold", "purchased"):
                sub = df[df["table"] == kind]
                K = kind.title()
                piv = annual(sub, "player", period, labels)
                piv.to_excel(xw, sheet_name=f"{K}_Annual_{basis}")
                top, share = top15_fixed(piv)
                sh = f"{K}_Top15_{basis}"
                top.to_excel(xw, sheet_name=sh, startrow=1)
                share.to_excel(xw, sheet_name=sh, startrow=len(top) + 5)
                ws = xw.book[sh]
                ws.cell(row=1, column=1, value=f"{K.upper()} in DAM - top 15 players by total {basis} volume (MU)").font = Font(bold=True)
                ws.cell(row=len(top) + 5, column=1, value="Share of total (%)").font = Font(bold=True)
                top15_by_year(piv).to_excel(xw, sheet_name=f"{K}_Top15_ByYear_{basis}", index=False)
                gpiv = annual(sub, "group", period, labels)
                gtop, gshare = top15_fixed(gpiv)
                sh = f"{K}_Top15_Group_{basis}"
                gtop.to_excel(xw, sheet_name=sh, startrow=1)
                gshare.to_excel(xw, sheet_name=sh, startrow=len(gtop) + 5)
                ws = xw.book[sh]
                ws.cell(row=1, column=1, value=f"{K.upper()} in DAM - top 15 parent groups by total {basis} volume (MU)").font = Font(bold=True)
                ws.cell(row=len(gtop) + 5, column=1, value="Share of total (%)").font = Font(bold=True)

        # formatting
        bold = Font(bold=True)
        for ws in xw.book.worksheets:
            ws.freeze_panes = "B2" if ws.title not in ("README",) else None
            for col in ws.columns:
                width = max((len(str(c.value)) for c in col[:300] if c.value is not None), default=8)
                ws.column_dimensions[get_column_letter(col[0].column)].width = min(max(10, width + 2), 70)
                for c in col:
                    if isinstance(c.value, float):
                        c.number_format = "#,##0.00"
            for row in ws.iter_rows():
                if row[0].value is not None and str(row[0].value).startswith(("TOTAL", "OTHERS")):
                    for c in row:
                        c.font = bold
    print("wrote", out)
    print("players:", df.groupby("table")["player"].nunique().to_dict(),
          " raw names:", df.groupby("table")["entity"].nunique().to_dict())


if __name__ == "__main__":
    main()
