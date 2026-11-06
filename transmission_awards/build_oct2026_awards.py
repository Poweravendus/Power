#!/usr/bin/env python3
"""Transmission projects (TBCB) awarded in October 2026 - compiled from public sources on 6 Nov 2026."""
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter as L

BOLD = Font(bold=True); HEAD = PatternFill("solid", fgColor="DDEBF7"); LINK = Font(color="0563C1", underline="single")
wb = Workbook(); wb.remove(wb.active)

def sheet(name, headers, rows, widths, link_cols):
    ws = wb.create_sheet(name)
    for j, h in enumerate(headers, 1):
        c = ws.cell(row=1, column=j, value=h); c.font = BOLD; c.fill = HEAD
        c.alignment = Alignment(wrap_text=True, vertical="top")
    for i, r in enumerate(rows, 2):
        for j, v in enumerate(r, 1):
            c = ws.cell(row=i, column=j, value=v)
            c.alignment = Alignment(wrap_text=True, vertical="top")
            if j in link_cols and isinstance(v, str) and v.startswith("http"):
                c.hyperlink = v; c.font = LINK
    for j, w in enumerate(widths, 1):
        ws.column_dimensions[L(j)].width = w
    ws.freeze_panes = "A2"
    return ws

H = ["Date (LoI issued)", "Transmission scheme name", "Won by", "Estimated cost", "Tariff (quoted annual transmission charges)",
     "Source 1 (primary)", "Source 2", "Source 3", "Type", "State", "Bid process coordinator", "Scope / notes", "Competing bidders"]
awarded = [[
    "16-Oct-2026",
    "Establishment of 765kV GIS Pune West (District: Pune) - intra-state transmission system on BOOT basis. SPV: Pune West Power Transmission Ltd",
    "Power Grid Corporation of India Ltd (POWERGRID)",
    "Not disclosed in the exchange filing or press coverage (only the annual charge is public)",
    "Rs 199.55 crore per annum",
    "https://www.bseindia.com/xml-data/corpfiling/AttachLive/2a0b1af1-86e1-4796-94ed-7679292699ea.pdf",
    "https://www.tndindia.com/pgcil-wins-765kv-pune-west-intrastate-tbcb-scheme-in-maharashtra-receives-letter-of-intent/",
    "https://www.tradingview.com/news/cnbctv:5bc80bbc7094b:0/",
    "InSTS (intra-state, TBCB)", "Maharashtra", "PFC Consulting Ltd (for MSETCL / Maharashtra STU)",
    "New 765/400kV GIS substation at Pune West (2x1500 MVA); 400kV D/C line to MSETCL Hinjewadi; LILO of 765kV D/C Pune-III to South Kalamb (ISTS) line. 24 months from SPV transfer. POWERGRID's 10th TBCB win of FY27 (cumulative ATC Rs 7,863.63 crore).",
    "Adani Energy Solutions, Resonia (per T&D India, 17 Aug 2026)",
]]
sheet("Awarded_Oct2026", H, awarded, [14, 55, 30, 32, 28, 45, 45, 45, 18, 14, 30, 70, 35], {6, 7, 8})

H2 = ["Status as of 6-Nov-2026", "Date of L1 / status report", "Transmission scheme name", "L1 / likely winner", "Estimated cost / value",
      "Tariff", "Source 1", "Source 2", "Type", "State", "Bid process coordinator", "Notes"]
pipeline = [
    ["L1 declared; LoI not reported", "21-Sep-2026",
     "Establishment of 400kV GIS Solapur/Paranda Switching Station (Dist. Dharashiv). SPV: Dharashiv Power Transmission Ltd",
     "Dilip Buildcon Ltd", "Rs 1,265 crore (EPC business opportunity, ex-GST, per DBL filing)", "Not disclosed",
     "https://www.bseindia.com/xml-data/corpfiling/AttachHis/60148df3-458e-48a2-b394-a32856fb57e8.pdf",
     "https://www.tndindia.com/pgcil-wins-765kv-pune-west-intrastate-tbcb-scheme-in-maharashtra-receives-letter-of-intent/",
     "InSTS", "Maharashtra", "RECPDCL", "T&D India (16 Oct) said LoI expected 'in the coming weeks'. No LoI filing found by 6 Nov 2026."],
    ["L1 declared; LoI not reported", "28-Sep-2026",
     "Establishment of 400kV AIS Yavatmal (Babhulgaon) (Dist. Yavatmal). SPV: Yavatmal Power Transmission Ltd",
     "Dilip Buildcon Ltd", "About Rs 1,151 crore (per SolarQuarter / DBL filing)", "Not disclosed",
     "https://www.bseindia.com/xml-data/corpfiling/AttachLive/9eafc14f-b5c9-47d0-b3f9-8ae030bd30ab.pdf",
     "https://solarquarter.com/2026/09/29/dilip-buildcon-emerges-l-1-for-inr-1151-crore-400-kv-yavatmal-transmission-project-in-maharashtra/",
     "InSTS", "Maharashtra", "RECPDCL", "Same as above: LoI pending per T&D India 16 Oct; none found by 6 Nov 2026."],
    ["L1 declared; LoI not reported", "24-Sep-2026",
     "Establishment of 765kV AIS Parli (District: Beed). SPV: Beed Parli Power Transmission Ltd",
     "Resonia Ltd", "Not disclosed", "Not disclosed",
     "https://www.tndindia.com/flash-news-resonia-close-to-winning-beed-parli-intrastate-tbcb-scheme-in-maharashtra/",
     "https://www.tndindia.com/three-intrastate-tbcb-schemes-in-maharashtra-transferred-to-winning-developers-big-names-score-first-wins/",
     "InSTS", "Maharashtra", "RECPDCL", "T&D India: Resonia L1, LoI pending issuance (24 Sep); still 'expected' on 16 Oct. No LoI found by 6 Nov 2026."],
    ["Bids opened; AESL reported 'set to win'", "19-Oct-2026",
     "Intra-state transmission system for evacuation of power from 3x800 MW Pirpainti STPP (Bhagalpur) - Bihar's first InSTS-TBCB scheme. SPV: Vikramshila Power Transmission Ltd",
     "Adani Energy Solutions Ltd (reported likely winner)", "Not disclosed", "Not disclosed",
     "https://www.tndindia.com/adani-energy-set-to-win-bihars-first-intrastate-transmission-scheme-under-tbcb/",
     "https://powerpeakdigest.com/adani-resonia-shivalaya-pirpainti-transmission/",
     "InSTS", "Bihar", "RECPDCL (notified BPC by Govt of Bihar, 7 May 2026)",
     "Qualified bidders: AESL, Resonia, Shivalaya Construction. Four new GIS substations, 400kV/220kV D/C lines, LILO at Jhanjharpur; BOOT. No LoI found by 6 Nov 2026."],
]
sheet("L1_pending_LoI", H2, pipeline, [26, 14, 55, 30, 34, 16, 45, 45, 10, 13, 30, 60], {7, 8})

H3 = ["SPV transfer date (Oct 2026)", "Original award (LoI) date", "Transmission scheme / SPV", "Won by", "Estimated cost", "Tariff (annual transmission charges)",
      "Source 1", "Source 2", "Type", "State", "Bid process coordinator", "Notes"]
transfers = [
    ["06-Oct-2026", "26-Aug-2026 (win announced)",
     "Satara Power Transmission Ltd - 765/400kV substation at Satara and 765kV Kolhapur-Satara line; evacuation of 4,500 MW RE and pumped storage",
     "Adani Energy Solutions Ltd", "About Rs 4,700 crore (capex, per AESL release)", "Not disclosed",
     "https://www.bseindia.com/xml-data/corpfiling/AttachHis/249b80bb-fe73-435e-ae62-a18c01e83369.pdf",
     "https://www.tndindia.com/adani-energy-solutions-acquires-project-spv-satara-power-transmission-ltd/",
     "InSTS", "Maharashtra", "PFC Consulting Ltd", "SPA with PFCCL executed 6 Oct 2026; consideration Rs 19.01 crore."],
    ["12-Oct-2026", "03-Sep-2026",
     "Lakadia II Power Transmission Ltd - transmission system for Lakadia REZ Phase-II (7.5 GW), Gujarat",
     "Power Grid Corporation of India Ltd", "Not disclosed", "Rs 1,152.49 crore per annum",
     "https://www.tndindia.com/all-five-project-spvs-of-gujarat-14-gw-re-scheme-transferred-to-winning-developers/",
     "https://powerpeakdigest.com/powergrid-lakadia-ii-transmission-project-gujarat/",
     "ISTS", "Gujarat", "PFC Consulting Ltd", "One of five SPVs of the Gujarat 14 GW RE evacuation plan transferred on 12 Oct 2026."],
    ["12-Oct-2026", "25-Sep-2026",
     "Lakadia C Power Transmission Ltd - Common transmission system for Lakadia (Ph-II 7.5 GW), Jam Khambhaliya (Ph-II 5.5 GW), Jamnagar (Ph-I 1 GW) - Part C",
     "Power Grid Corporation of India Ltd", "Not disclosed", "Rs 430.67 crore per annum",
     "https://www.tndindia.com/pgcil-receives-letter-of-intent-for-lakadia-c-interstate-tbcb-scheme/",
     "https://www.tndindia.com/all-five-project-spvs-of-gujarat-14-gw-re-scheme-transferred-to-winning-developers/",
     "ISTS", "Gujarat", "PFC Consulting Ltd", "Acquired for Rs 19.94 crore (press reports)."],
    ["12-Oct-2026", "21-Aug-2026",
     "Transmission system for Jam Khambhaliya REZ Phase-II (5.5 GW) and Jamnagar Phase-I (1 GW), Gujarat",
     "Power Grid Corporation of India Ltd", "Not disclosed", "Rs 822.91 crore per annum",
     "https://www.tndindia.com/pgcil-wins-jam-khambhaliya-rez-interstate-tbcb-scheme-receives-letter-of-intent/",
     "https://www.psuconnect.in/psu-news/powergrid-wins-major-inter-state-transmission-project-under-tbcb",
     "ISTS", "Gujarat", "RECPDCL", "Part of the same five-SPV transfer on 12 Oct 2026."],
    ["12-Oct-2026", "03-Sep-2026 (approx.)",
     "Jam Khambhaliya Jamnagar Power Transmission Ltd - Common transmission system (Lakadia/Jam Khambhaliya/Jamnagar) - Part B: 765/400kV AIS substation and about 300 km of lines",
     "Ceigall India Ltd", "About Rs 5,300 crore (per Ceigall release)", "Rs 608.67 crore per annum",
     "https://www.bseindia.com/xml-data/corpfiling/AttachHis/15560d68-9e6c-439a-854c-e97d811d14d5.pdf",
     "https://www.business-standard.com/industry/news/ceigall-india-secures-5-300-cr-order-for-transmission-project-in-gujarat-126090301365_1.html",
     "ISTS", "Gujarat", "RECPDCL", "SPA with RECPDCL signed 12 Oct 2026; TSA with CTUIL executed 19 Oct 2026. Ceigall's first TBCB development project."],
    ["12-Oct-2026", "Aug-2026 (e-RA 6-7 Aug; LoI reported 21 Aug)",
     "Lakadia A Power Transmission Ltd - Common transmission system - Part A: about 270 km 765kV D/C Halvad-Vadodara line and substation augmentation",
     "AnantGrid Projects One Pvt Ltd (Bajel Projects 26% / NIIF 74%)", "Rs 2,252 crore (estimated, per Power Peak Digest)", "About Rs 370 crore per annum (e-RA quote, per T&D India; LoI figure not disclosed)",
     "https://www.tndindia.com/bajel-projects-associate-anantgrid-receives-loi-for-lakadia-a-interstate-tbcb-scheme/",
     "https://powerpeakdigest.com/anantgrid-wins-lakadia-transmission-line/",
     "ISTS", "Gujarat", "PFC Consulting Ltd", "Bajel subsequently received about Rs 1,500 crore EPC order from the SPV (27 Oct 2026)."],
    ["16-Oct-2026", "30-Sep-2026",
     "Nawada Durgapur Power Transmission Ltd - ERES-47: Nawada (Bihar)-Durgapur-Jeerat (New) (West Bengal) 765kV corridor",
     "Shivalaya Construction Ltd", "Rs 5,270 crore (estimated)", "Rs 585.7 crore per annum (L1; L2 was Rs 720 crore)",
     "https://www.tndindia.com/shivalaya-construction-acquires-project-spv-of-eres-47-interstate-tbcb-scheme/",
     "https://powerpeakdigest.com/power-sector-news-roundup-for-october-16-2026/",
     "ISTS", "Bihar / West Bengal", "RECPDCL", "Envisaged completion March 2029."],
]
sheet("SPV_transfers_Oct2026", H3, transfers, [16, 22, 60, 32, 30, 32, 45, 45, 8, 16, 22, 55], {7, 8})

notes = """TRANSMISSION PROJECTS AWARDED IN OCTOBER 2026 (India, tariff-based competitive bidding) - compiled 6 November 2026

DEFINITION USED
'Awarded' = Letter of Intent (LoI) issued by the bid process coordinator (PFC Consulting or RECPDCL) to the successful bidder. That is the formal award step under TBCB; being declared L1 or winning the e-reverse auction is not yet an award, and the later SPV share transfer is closure of an earlier award.

RESULT
Only ONE LoI was issued in October 2026 that could be found: POWERGRID, 765kV GIS Pune West (Maharashtra, intra-state), LoI 16 Oct 2026, Rs 199.55 crore p.a. (sheet Awarded_Oct2026).
Sheet L1_pending_LoI lists four schemes where a winner was declared or widely reported in Sep-Oct 2026 but no LoI had surfaced by 6 Nov 2026.
Sheet SPV_transfers_Oct2026 lists seven earlier awards (Aug-Sep 2026 LoIs) whose project SPVs were handed over to the winners during October 2026. These are often reported as 'wins' in October but the award itself predates the month.

COVERAGE CHECKED
- T&D India (tndindia.com) tag archives for interstate-TBCB and intrastate-TBCB, which carry an article per LoI; homepage to 6 Nov 2026.
- Mercom India grid and tenders/auctions categories; Power Peak Digest; Power Line; Business Standard; CNBC-TV18.
- BSE filings of POWERGRID, Adani Energy Solutions, Dilip Buildcon, Ceigall (PDFs read directly).
- PFC Consulting and RECPDCL websites (no award/LoI listing for the period on their public pages).
- Company-specific searches: Tata Power, Torrent, IndiGrid, Apraava, GR Infra, Techno Electric, HG Infra, Shivalaya, Megha, KEC, Resonia, Adani, POWERGRID.

LIMITS
- BSE's announcement API blocks automated access, so company filing lists for late October could not be scanned exhaustively; a late-October LoI disclosed only via an exchange filing and not covered by the trade press could be missed. The most likely such items are the three Maharashtra schemes in L1_pending_LoI.
- 'Estimated cost' is rarely in the LoI announcement. Where given it is the figure the company or press reported (capex or EPC value, as labelled); POWERGRID discloses only annual charges.
- Resonia's Balsane SPV (Maharashtra) was transferred on 26-28 Sep 2026 and reported on 7 Oct 2026; it is excluded from the October transfer sheet as the transfer predates October.
"""
ws = wb.create_sheet("README")
for i, line in enumerate(notes.strip().split("\n"), 1):
    ws.cell(row=i, column=1, value=line)
ws.column_dimensions["A"].width = 150
wb._sheets = [wb["README"], wb["Awarded_Oct2026"], wb["L1_pending_LoI"], wb["SPV_transfers_Oct2026"]]
wb.save("transmission_awards_oct2026.xlsx")
print("ok")
