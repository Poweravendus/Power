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
# Renames were identified from non-overlapping active periods in the data
# (old label's last month is immediately followed by the new label's first).
ENTITY_ALIASES = [
    (r"^MP$", "MADHYA PRADESH"),
    (r"^J ?& ?K$|^JAMMU ?(&|AND)? ?KASHMIR$", "JAMMU & KASHMIR"),
    (r"^CHANDIGARH", "CHANDIGARH"),
    (r"^GOA( WR)?$", "GOA"),
    (r"^PONDICHERRY|^PUDUCHERRY", "PUDUCHERRY"),
    (r"^DD ?& ?DNH$|^DADRA & NAGAR HAVELI$|^DAMAN AND DIU|^DAMAN & DIU", "DNH & DD (UT)"),
    (r"^DVC$|^DAMODAR VALLEY", "DVC"),
    (r"^GOVERNMENT OF HIMACHAL PRADESH", "HIMACHAL PRADESH"),   # state free-power shares, listed separately from Aug-2024
    (r"^NEPAL|^NEA\b|^NEP$", "NEPAL (NEA / NVVN)"),
    (r"DGPCL|DRUK GREEN|BASOCHHU", "DRUK GREEN POWER (BHUTAN)"),
    (r"^SEMBCORP|^SEIL ENERGY|^THERMAL POWERTECH", "SEIL ENERGY INDIA (EX-SEMBCORP)"),
    (r"^TEESTA (STG ?3|HEP)|TEESTA URJA|TEESTA.?III", "TEESTA URJA (TEESTA-III HEP)"),
    (r"^JAYPEE NIGRIE", "JAYPEE NIGRIE STPP"),
    (r"^JINDAL STAGE-II|^JINDAL POWER LIMITED ?, ?STAGE-2", "JINDAL POWER LTD - STAGE 2"),
    (r"^JINDAL POWER$|^JINDAL POWER LIMITED ?, ?STAGE-1", "JINDAL POWER LTD - STAGE 1"),
    (r"^ESSAR POWER|^MAHAN ENERGEN", "MAHAN ENERGEN (EX-ESSAR POWER MP)"),
    (r"^JITPL|^JINDAL INDIA (THERMAL )?POWER", "JINDAL INDIA THERMAL POWER (JITPL)"),
    (r"^DB POWER|^D B POWER", "DB POWER"),
    (r"^GMR CHATT?ISGARH|^RPREL|^ARTPP|RAIPUR TPP", "ADANI POWER - RAIPUR TPP (EX-GMR CHHATTISGARH)"),
    (r"^REGL$|^RAIGARH_ADANI|RAIGARH TPP", "ADANI POWER - RAIGARH TPP (EX-REGL)"),
    (r"^MB POWER", "MB POWER (MP)"),
    (r"^ACBIL|^ACB \(INDIA\)", "ACB (INDIA)"),
    (r"^RKM POWER|^R\.?K\.?M POWERGEN", "RKM POWERGEN"),
    (r"^KARCHAM WANGTOO", "KARCHAM WANGTOO HEP"),
    (r"^AD HYDRO", "AD HYDRO POWER"),
    (r"^DCPP$|JINDAL STEEL & POWER.*DCPP", "JSPL - DCPP"),
    (r"^NTPC STATIONS|^NTPC\b|^SIMHADRI (FSP|FLOATING)|^RAMAGUNDAM FLOATING", "NTPC STATIONS"),
    (r"^NPGC|^NABINAGAR POWER", "NPGC NABINAGAR"),
    (r"^NTPP BRBCL|^BRBCL", "BRBCL NABINAGAR"),
    (r"^NEEPCO|^KAMENG HYDRO|^AGARTALA GAS|^ASSAM GAS BASED", "NEEPCO STATIONS"),
    (r"^SKS POWER", "SKS POWER"),
    (r"^MARUTI (COAL|CLEAN)", "MARUTI CLEAN COAL & POWER"),
    (r"^DIKCHU", "DIKCHU HEP"),
    (r"^SHREE CEMENT", "SHREE CEMENT"),
    (r"^SIMHAPURI", "SIMHAPURI ENERGY"),
    (r"^COASTGEN|^COASTAL ENERGEN", "COASTAL ENERGEN"),
    (r"^EMCO$|^GMR WARORA", "GMR WARORA (EX-EMCO)"),
    (r"^GMR KAMALANGA", "GMR KAMALANGA"),
    (r"^BALCO|^BHARAT ALUMINIUM", "BALCO"),
    (r"^JHABUA POWER", "JHABUA POWER"),
    (r"^IL&FS", "ITPCL (IL&FS TAMIL NADU)"),
    (r"^DHARIWAL", "DHARIWAL INFRASTRUCTURE"),
    (r"^ONGC PALATANA|^PALATANA", "OTPC PALATANA"),
    (r"^NLC$|^NLC INDIA", "NLC INDIA"),
    (r"^NTPL$|^NLC TAMIL ?NADU", "NTPL (NLC TAMIL NADU POWER)"),
    (r"^RENEW_SPRATAP|^RENEW SURYA PRATAP", "RENEW SURYA PRATAP"),
    (r"^RENEW_SR_SLR|^RENEW SURYA RAVI", "RENEW SURYA RAVI"),
    (r"^ASEJTL|^ADANI SOLAR ENERGY JAISALMER TWO", "ADANI SOLAR ENERGY JAISALMER TWO"),
    (r"^ADANI_4RE|^ADANI RENEWABLE ENERGY HOLDING FOUR", "ADANI RENEWABLE ENERGY HOLDING FOUR"),
    (r"^ADEPT", "ADEPT RENEWABLE TECHNOLOGIES"),
    (r"^AMPS HAZIRA|^AMNSIL|^ARCELORMITTAL|^ESSAR STEEL", "AM/NS INDIA (HAZIRA)"),
    (r"^NCR ALLAHABAD|^NORTH CENTRAL RAILWAY|^RAIL$", "INDIAN RAILWAYS (NCR)"),
    (r"^MEENAKSHI", "MEENAKSHI ENERGY"),
    (r"^GREENKO AP01", "GREENKO AP01 IREP (PSP)"),
    (r"^IND BARATH ENERGY UTKAL|^JSW ENERGY \(UTKAL\)", "JSW ENERGY UTKAL (EX-IND BARATH)"),
    (r"^ADHUNIK", "ADHUNIK POWER"),
    (r"^KSK MAHANADI", "KSK MAHANADI"),
]

# --- 2. player -> parent group (only where a group is obvious from the name) --
GROUP_RULES = [
    (r"ADANI (GREEN|RENEWABLE|SOLAR|WIND|HYBRID)|^ADANI_", "ADANI GREEN ENERGY (ALL SPVs)"),
    (r"ADANI POWER|MAHAN ENERGEN", "ADANI POWER (ALL PLANTS)"),
    (r"ADANI PORTS", "ADANI PORTS & SEZ"),
    (r"NTPC|NPGC|BRBCL|KANTI BIJLEE|IGSTPS|NTECL", "NTPC GROUP"),
    (r"^RENEW", "RENEW POWER (ALL SPVs)"),
    (r"GREENKO|BUDHIL", "GREENKO GROUP"),
    (r"^JINDAL POWER LTD", "JINDAL POWER LTD (BOTH STAGES)"),
    (r"^JSPL", "JSPL"),
    (r"JSW ENERGY|KSK MAHANADI", "JSW ENERGY (INCL. KSK MAHANADI)"),
    (r"NLC INDIA|^NTPL", "NLC INDIA GROUP"),
    (r"^GMR", "GMR ENERGY"),
    (r"^JUNIPER", "JUNIPER GREEN ENERGY"),
    (r"^AMP ENERGY", "AMP ENERGY"),
    (r"^AMBUJA", "AMBUJA CEMENTS"),
    (r"^SERENTICA", "SERENTICA RENEWABLES"),
    (r"^SPRNG", "SPRNG ENERGY"),
    (r"^TP SAURYA|^TATA POWER", "TATA POWER"),
    (r"^SJVN", "SJVN"),
    (r"^NHPC", "NHPC"),
    (r"^AVAADA", "AVAADA"),
    (r"^ACME", "ACME"),
    (r"^AZURE", "AZURE POWER"),
    (r"^HERO", "HERO FUTURE ENERGIES"),
    (r"^SEMBCORP|SEIL ENERGY", "SEIL ENERGY INDIA"),
]


def normalize(name):
    s = re.sub(r"\s+", " ", str(name).upper()).strip()
    s = re.sub(r"\s+,", ",", s)
    return s


def player_of(norm):
    for pat, canon in ENTITY_ALIASES:
        if re.search(pat, norm):
            return canon
    return norm


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
