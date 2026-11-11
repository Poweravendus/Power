# Qualiance International (NSE SME: QUALIANCE) - research status

**Updated:** 11-Nov-2026 (base reset). **Stage:** 2 (forecast model v2 + note v2) built; ACE cross-check still pending.

## Where we are
1. Document pack (35 PDFs) sent: scratchpad packs/qualiance/out/Qualiance-International-Investor-Docs.zip.
2. Model v1: FY23-FY26 restated; half-yearly (1HFY26 restated and audited, 2HFY26, FY26 audited, 1HFY27); segments (country, woven/knitted, concentration, capacity, realisation per piece, employees, other income detail); price check.
3. Correction recorded: the company was wrongly described as an NBFC from an aggregator site; it is a garment exporter (RHP p.102).

## Decisions
- 8-Nov-2026: Restated used for full years; audited for half-years (only basis available). Indian GAAP (SME).
- 8-Nov-2026: Manufacturing engine applies (capacity x utilisation x realisation), not a lending model.

## First questions the numbers raise
- Revenue fell 19% and PAT 29% in 1HFY27, the first half after listing (Rs.31.0 cr vs 38.5 cr). Management blames Swiss inspection timing (~Rs.6 cr awaiting inspection).
- One customer (Swiss government departments) = 57% of FY26 sales; Switzerland 81%; top 10 = 99.7%; no order book, no long-term contracts.
- FY26 realisation per piece +29% (Rs.1,502 to 1,936) while volume +12%: mix or price? Needed to judge margin durability (EBITDA margin 15% to 22%).
- Other income is 25-32% of PBT; FY26 FX gain Rs.3.2 cr. Core PBT ex other income Rs.12.0 cr.
- Promoter Vipul Badani borrowed Rs.3.76 cr from the company (Mar-26) while the company had Rs.28.5 cr of bank debt; interest Rs.0.30 cr; repaid in 1HFY27. FY24 rights issue of 84 lakh shares at Rs.10 settled against directors' loans.
- Working capital: NWC ~206 days of revenue; cumulative FY23-FY26 PAT Rs.21.2 cr vs FCF Rs.2.9 cr.
- IPO costs 13.1% of the Rs.45.1 cr raised. Expansion to 2.4x capacity (10.8 lakh pieces) on Rs.39.1 cr: who fills it, given 99.7% top-10 concentration?
- Attrition 30-64% a year on a 283-person workforce.

## v2 forecast and note (8-Nov-2026)
- Model v2: Drivers (scenario selector C3: 1 bear / 2 base / 3 bull), TAM, FY27E-FY30E P&L/BS/CF, valuation (12x FY28E EPS; 7x EV/EBITDA cross-check). Built by scratchpad scripts/add_qualiance_v2.py; scenarios run by qual_scen.py. All check rows ~0 in all three scenarios.
- Base: FY27E rev Rs.71.7 cr / PAT 9.1 cr; FY28E rev 100.7 / PAT 11.7 / EPS 8.67. Targets: bear Rs.32, base Rs.104 (SELL, -24%), bull Rs.240.
- Decisions: base fills the new unit at 12/25/40% (mgmt 30/60/90%); realisation held ~Rs.1,950 (FY26 jump = mix + inventory timing + FX); FX gain at 1% of exports; SME/concentration discount 50% to S P Apparels' 23.2x.
- New facts found: Swiss customs order Rs.13.8 cr FY26 (0.7 cr FY25); family salaries Rs.2.31 cr FY26 vs 0.84 cr; promoter group sold 13.37 lakh shares at Rs.127 pre-IPO; RHP said RCC building + COD Mar-2027, now PEB + Jul-2027; headcount 255 on PPT vs 283.
- Note: Qualiance_International_Note_v1.docx (6 pages).

## Base reset, 11-Nov-2026 (base = most likely; old base kept as the floor)
- Why: the old base counted only what was committed (slow new-unit fill). Investor asked for a "most likely" base built from industry growth plus shown share gain, below management guidance.
- Old base (now the floor; memo on Valuations rows 57-65, pasted): revenue FY27E-FY30E Rs.71.7 / 100.7 / 128.3 / 160.1 cr; PAT 9.1 / 11.7 / 15.1 / 21.1 cr; FY28E EPS Rs.8.67; target Rs.104 (-24%), SELL.
- New base: revenue Rs.73.5 / 123.4 / 172.9 / 215.9 cr; EBITDA margin 19.4 / 19.7 / 20.3 / 20.8%; PAT 9.5 / 15.9 / 23.0 / 30.5 cr; FY28E EPS Rs.11.85; target Rs.142 (+4%), HOLD. Nearest line is SELL (8.7 points away; SELL above a CMP of Rs.150).
- Base drivers changed (Drivers base rows only, reasons in the merged source cells): existing-plant utilisation FY27 80% to 82%; new-unit fill 12/25/40% to 22/45/65%; price Rs.1,975 flat (floor Rs.1,950 from FY28); employee cost per piece Rs.445/465/480 (floor 420/435/450) for new-tailor ramp-up, which holds margins near the company's own record.
- Industry numbers used (Drivers block H, rows 122-159): global apparel 4.1% CAGR 2026-34, global textile and apparel trade 4% to 2030, India PPE 10.4% CAGR 2025-33, RMG export target 12-13% (not used, aspirational), ICRA 9-11% FY26 (RHP p.94-99; IBEF-sourced, no paid industry report). Actuals: India textile and garment exports FY26 -2.2% (US$35.8 bn), garments -1.4% (GTRI); garments to the EU +2.4% (US$4.66 bn); garments Apr-Sep 2026 -6.2% (CITI). Market ~0%, so growth = share gain: company FY23-26 CAGR 29.5% vs flat exports; base FY26-30 CAGR 29.4% (same pace), guidance-implied 36.7%, bull 40.6%.
- Position: base revenue 33% / 42% / 43% / 40% of the way from floor to bull (low end of the 40-75% range: short, poor delivery record - plant date slipped Mar-27 to Jul-27, 1HFY27 sales -19% - and top 10 = 99.7%). Base below guidance-implied revenue every year (-4% / -15% / -15% / -20%) and below the 21.7% margin guidance every year.
- Guidance: FY27 Rs.76-77 cr at FY26 margin (call p.6); new unit 30-35/60/90% fill, peak Rs.180 cr (call p.7, p.14); same combined margin later (call p.11). Bull broadly equals it on fill and margin but adds +3% a year price and 88% on the old plant, so bull FY30E Rs.301 cr vs ~Rs.269 cr guidance-implied. Not rebuilt.
- Chance of management's plan already in the price: (137.10 - 142) / (240 - 142) = -5%: the price sits just under the new base. Bear Rs.32 and bull Rs.240 unchanged; one P/E (12x FY28E) for all scenarios; peer multiples still pending from Bloomberg.
- Base needs ~Rs.6 cr of extra borrowing in FY28-FY29 (revolver) as working capital grows with sales.
- Checks: 0 formula errors; all check rows ~0 (<=0.0002) in bear, base and bull; selector back to 2. Sensitivities re-run (qual_sens_v2.json): mgmt fill Rs.176, floor fill Rs.100, no new customer Rs.49.
- Files: model updated in place (QUALIANCE_Model_v2.xlsx); note Qualiance_International_Note_v2.docx (8 pages; v1 untouched). Scripts: qual_base_reset.py, qual_scen.py, qual_sens_v2.py, build_qualiance_note_v2.js.

## Open questions
- Swiss contract structure (tenders? framework agreements? duration?), inspection process and payment terms.
- Restated vs audited differences each year (Rs.1.2 cr in FY26): what was re-allocated?
- Revaluation of land/building (reserve Rs.9.9 cr): when and by whom.

## File versions
- Model: QUALIANCE_Model_v1.xlsx (8-Nov-2026, historicals, untouched); QUALIANCE_Model_v2.xlsx (8-Nov-2026, forecasts); notes: Qualiance_International_Note_v1.docx (8-Nov-2026), Qualiance_International_Note_v2.docx (11-Nov-2026, base reset); evidence: notes/evidence.md
