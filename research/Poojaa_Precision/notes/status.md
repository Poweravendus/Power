# Poojaa Precision Engg. Ltd (BSE SME: 544844, PPEL) - research status

**Updated:** 11-Nov-2026 (base reset). **Stage:** v1 (historicals) and v2 (forecasts, scenarios, valuation, note) built. Next: cross-check against the investor's ACE dump, then the step-by-step business discussion. Next results: 2HFY27 / FY27 (board around May 2027). The investor wrote "Pooja precision engineering": this is the company (formerly Pooja Castings Pvt Ltd, inc. 12-Aug-1992).

## Where we are
1. Document pack: scratchpad packs/poojaa/build/Poojaa-Precision-Investor-Docs (50 PDFs + price csv + 26 TXT; zip in packs/poojaa/out). Page map in FINANCIAL_SOURCES.md.
2. Model v1 (POOJAA_Model_v1.xlsx): standalone FY23 (DRHP restated), FY24-FY25 (Prospectus restated), FY26 (audited AR) P&L / BS / CF / working capital / ratios; restated-vs-audited memo; cost memo (job work, contract labour, power, directors' pay, promoter-group purchases); Half-yearly sheet (1HFY26, 2HFY26, 1HFY27, restated 1HFY26 stub; half-year BS and CF; tonnes and Rs/kg); Segments (sector, sub-sector, geography, states, top-10 customers, capacity and production by plant, raw materials, people, order book, WC certificate, inventory mix, IPO use, directors' pay); Valuations; Sources with 12 conflicts.
3. Checks: every P&L, BS and CF check row is ~0 (largest 0.0003 cr). The one red "TEST" row (Half-yearly D76 = 25.06) is the company's 1HFY27 cash-flow error, kept visible on purpose. Recalc v1: 460 formulas, 0 errors; v2: 1,139 formulas, 0 errors.
4. Verified from documents: BSE 544844 / PPEL; price band Rs.285-301 (Prospectus p.107); issue Rs.15,983.10 lakh, 53,10,000 fresh shares (cover, p.49); bid 28-30 Jul-2026 (cover); anchors 14,99,600 shares at Rs.301 = Rs.45.14 cr (p.49, BoA ad); listed 4-Aug-2026 (results note 7). NOT verified: listing open "around Rs.470" (aggregators only; first close in the price feed Rs.493.50).

## Decisions
- 10-Nov-2026: Standalone basis (no subsidiaries exist).
- 10-Nov-2026: FY26 = audited AR (PAT Rs.33.45 cr), as instructed (audited wins). Restated FY26 PAT Rs.30.90 cr kept as a memo. FY23-FY25 = restated. This mixes bases at the FY25/FY26 join: FY25 restated PAT is Rs.1.49 cr above audited and FY26 audited is Rs.2.55 cr above restated, so FY26 growth on the model (+40%) is flattered vs restated (+29%).
- 10-Nov-2026: Half-years use the results version of 1HFY26 (PAT Rs.13.29 cr) so that 1H + 2H = audited FY26; the restated stub (Rs.10.26 cr) sits next to it.
- 10-Nov-2026: EBITDA before other income; no exceptional items in any year.
- 10-Nov-2026: Revenue engine = casting tonnes (capacity x utilisation, Units 1+2 and Unit 3 separately) x realisation per kg; realisation = aluminium (passed through, with an explicit same-year pass-through %) + other materials + value added. Starting point = 1HFY27 per-kg economics (Rs.811 price, Rs.384 materials, Rs.192 job work and labour).
- 10-Nov-2026: Valuation 26x FY28E EPS (bear 18x, bull 32x); EV/EBITDA cross-check 15x (11x / 18x). CMP Rs.924.90 = BSE close 9-Nov-2026 per Screener.

## First questions the numbers raise (for the discussion)
- **The value per kg jumped 39% in one half.** Revenue per kg of castings went from Rs.582 (FY26) and Rs.574 (2HFY26) to Rs.811 (1HFY27) while tonnes fell (2,589 t vs 2,942 t in 2HFY26). Management: 8-9% metal, the rest bigger parts (50-80 kg). Our base holds Rs.811; a 5% lower value added cuts the target 15%. If it was mix plus one-off die or tooling sales, the base case is too high.
- **Cash conversion is weak and the latest cash-flow statement is wrong.** FY23-FY26 CFO was 76% of PAT and free cash flow was Rs.-35 cr. The 1HFY27 statement adds taxes paid (Rs.12.5 cr) instead of deducting: its own lines give CFO Rs.5.6 cr, not the Rs.30.6 cr reported (and repeated in the PPT). Debt repayment shown (Rs.45.9 cr) does not match the Rs.17.4 cr fall in borrowings.
- **One customer and one vehicle type.** Customer 1 = 31.7% of FY26 sales (46% in FY23); top five 75%; commercial vehicles 51% of sales. A truck down-cycle or a lost part is the bear case.
- **The money trail is busy.** Promoter-group firms supplied ~24% of materials (G K Founders, a steel foundry, Rs.18.5 cr; G K Alloys Rs.6.4 cr; Jayshree Pistons Rs.10.5 cr). Directors took Rs.8.8 cr (19% of PBT; Chairman 103x the median). The CFO's father's CA firm bills Rs.1.44 cr a year. Promoters sold 9.15 lakh shares at Rs.271-301 on 13-14 Jul-2026, two weeks before the IPO. Bank stock statements differed from the books every quarter FY24-FY26.
- **The new plant is the whole case.** Unit 3 (6,600 t) doubles casting capacity; 1,500 t runs since 30-Aug-2026. Full date has drifted from Jun-2027 (Prospectus) to Sep-2027 (PPT). Management's Rs.1,000 cr by FY30 needs ~98% of 12,600 t at today's Rs/kg. The order book (Rs.1,180 cr to FY29) covers roughly the current run-rate.
- **Accounting judgement sits in inventory.** The restatement wrote off obsolete casting dies (Rs.3.27 cr) and moved Rs.2.55 cr of profit out of FY26. Inventory went from 33 to 63 days of sales in two years, dies from Rs.4.6 cr to Rs.17.4 cr.

## Management guidance vs our cases
| Item | Management guidance (source) | Bull | Base | Reality check |
|---|---|---|---|---|
| FY27 revenue | ~50% growth = ~Rs.440 cr (PPT slide 5; call PDF 5, 15) | Rs.455 cr (+55%) | Rs.427 cr (+45%) | 1HFY27 already Rs.210 cr (+68%); 2HFY27 needs ~Rs.230 cr vs Rs.169 cr in 2HFY26. Achievable on tonnes if Rs/kg holds |
| FY28 revenue | Rs.630-640 cr (call PDF 5) | Rs.652 cr | Rs.531 cr | Needs Unit 3 largely full in its first full year |
| FY29 / FY30 revenue | Rs.800-820 cr / ~Rs.1,000 cr; 30-35% CAGR (call PDF 5, 15-16) | Rs.866 / 970 cr | Rs.679 / 745 cr | Rs.1,000 cr needs ~12,300 t = ~98% of capacity |
| EBITDA margin | "always remain higher"; Unit 3 fixed costs "already absorbed" (call PDF 11-12) | 21.6% FY28E | 19.2% FY28E | Gross margin fell 61% -> 53% in 1HFY27; restated FY26 EBITDA margin 17.7% |
| Casting capacity | 12,600 t by Sep-2027 (PPT) / FY28 (call); full by Jun-2027 (Prospectus p.101) | full from Jul-2027 | full from Oct-2027 | 1,500 t running since 30-Aug-2026 (PPT counts 1,320 t) |
| Capex | Rs.110.4 cr Unit 3 + solar; "no additional capacity required" for Rs.1,000 cr (call PDF 16) | as base | Rs.87.6 cr more project capex FY27-28 + Rs.12-18 cr a year | Unit 4 (magnesium, aerospace) unbudgeted; CRISIL talks of a "major debt-funded capex plan" |
| Debt | repay "the entire loan by this second quarter" (call PDF 17) | near zero | Rs.5 cr at FY27E end | Borrowings Rs.23.7 cr at 30-Sep-2026; CRISIL rated Rs.73.5 cr term loans to 2032 |
| Mix | 50:50 auto / non-auto in 2-3 years; 40-45% auto by 2030 (call PDF 7, 10) | not modelled by sector | not modelled by sector | Non-auto 17.6% of FY26, 25% of 1HFY27 (PPT); PPT 1HFY26 base understates restated non-auto by Rs.8 cr |

## Open questions
- Who is Customer 1, what share of its wallet does Poojaa hold, and what price-down terms apply?
- What drove Rs/kg from Rs.582 to Rs.811: part mix, die/tooling sales, metal? What is revenue per kg excluding dies?
- What is the corrected 1HFY27 cash-flow statement?
- Why does a steel foundry (G K Founders) supply Rs.18.5 cr a year of materials? How are related-party prices benchmarked?
- Is the Unit 1 land (owned by Anil Kulkarni, mortgaged to SBI) rented to the company, and is any of the Rs.2.9 cr rent paid to promoters?
- Why did promoters sell at Rs.271 just before the IPO, and to whom (Gracious Advisors LLP, GMT Advisors LLP, Accent Agencies, Upsurge Investment)?
- Order book definition (firm POs or lifetime schedules)? How many Unit 3 tonnes have customer approval?
- Debt and capex: CRISIL's "major debt-funded capex plan" vs "repay the entire loan"; Unit 4 budget?
- Why did bank stock statements differ from the books every quarter?

## v2 (10-Nov-2026): forecasts, valuation, note
- Model v2 = v1 plus Drivers (selector D3: 1 bear / 2 base / 3 bull), TAM (bottom-up from vehicle volumes x kg x Rs/kg; volumes and kg are estimates to verify), FY27E-FY30E in every P&L/BS/CF/WC/ratio row, valuation on Valuations rows 26-74.
- Base: revenue Rs.426.7 / 530.6 / 679.2 / 745.4 cr; EBITDA Rs.79.4 / 101.8 / 132.8 / 142.4 cr (18.6-19.5%); PAT Rs.50.6 / 66.6 / 87.9 / 98.1 cr; EPS Rs.25.35 / 33.37 / 44.08 / 49.18 (FY27E-FY30E; 1.9945 cr shares).
- Valuation: 26x FY28E EPS = Rs.868, -6.2% vs CMP Rs.924.90 => SELL (narrowly; HOLD from 26.3x). Bear Rs.191 (-79%), bull Rs.1,541 (+67%). EV/EBITDA cross-check Rs.254 / 797 / 1,306. Reverse check: CMP needs FY28E PAT Rs.71.0 cr at 26x vs base Rs.66.6 cr.
- Most sensitive: value added per kg (-5% => target -15%), Unit 3 utilisation (-10 pts => -9.5%), the multiple (24x / 28x => Rs.801 / 934), Units 1+2 utilisation (-5 pts => -7%).
- All check rows ~0 under bear, base and bull (P&L PAT, BS, CF cash, Drivers revenue tie, Segments, Half-yearly); selector left at 2.
- Scripts: scratchpad scripts/build_poojaa.py, add_forecast_poojaa.py, run_scen_poojaa.py, build_note_poojaa.js; pack scripts in packs/poojaa/scripts.

## Base reset (11-Nov-2026): base = most likely, old base kept as a floor
- **Why:** the old base counted only committed capacity (Unit 3 to 60% by FY30, Rs/kg held). The investor asked for a base built from industry growth plus shown share gain, below management guidance. Brief: scratchpad brief/BASE_RESET_BRIEF.md.
- **Old base (floor, memo on Valuations rows 78-86):** revenue Rs.426.7 / 530.6 / 679.2 / 745.4 cr; PAT Rs.50.6 / 66.6 / 87.9 / 98.1 cr; FY28E EPS Rs.33.37; target Rs.868 at 26x (-6.2%, SELL). Old bear Rs.191 at 18x, old bull Rs.1,541 at 32x.
- **New base:** revenue Rs.432.9 / 577.1 / 738.9 / 856.5 cr (44-46% of the way from floor to guidance each year); EBITDA margin 18.7 / 18.3 / 18.5 / 18.3%; PAT Rs.51.8 / 69.3 / 90.6 / 108.3 cr; EPS Rs.25.95 / 34.75 / 45.43 / 54.30. Target Rs.903 at 26x FY28E, -2.3% vs CMP Rs.924.90 => HOLD, 2.7 pts above the SELL line (SELL below 25.3x, BUY above 30.6x).
- **One multiple:** bear and bull now 26x too (EV/EBITDA cross-check 15x for all). Bear Rs.276 (-70%), bull Rs.1,252 (+35%). P/E sensitivity table 18-32x on Valuations rows 101-107. Peer multiples still pending from Bloomberg.
- **Chance of management's plan already in the price** = (CMP - base) / (bull - base) = 6%.
- **Industry growth used (TAM rows 24-44):** CV 8% (ICRA: CV volumes +12.6% FY26, +4-6% FY27, https://www.icra.in/Research/ViewResearchReport/6946; + ~3% content/price [E]); cars/2W/dies 10% (ACMA +12.7% FY26, AR p.88; IBEF 14% CAGR FY20-25, Prospectus p.128); EV 20% [E] (EV sales >20 lakh FY25, p.127; 30% target 2030, p.129); energy 11% (switchgear 7.12% to 2029, electrical equipment 14.3% FY24-28, p.126; transformers ~7.5%, p.127); farm/other 5% (agri equipment 5.24%, p.126). Weighted 9.7%. Company FY24-FY26 30.1% (+20 pts share gain); FY23-FY26 21.6% (+9 pts). Base FY27-FY30 25.5% = market + ~16 pts; guidance 31.4%.
- **Driver changes (base rows only, notes tagged "Base reset 11-Nov-2026"):** Units 1+2 utilisation 82% (was 80%; call PDF 10, 13); Unit 3 utilisation 45 / 60 / 66 / 86% (was 50 / 40 / 50 / 60%); staff cost growth 30 / 17 / 13 / 11% (was 30 / 15 / 12 / 10%); new per-kg mix factor (Drivers rows 107-111, rewires rows 49 and 56) 1.00 in FY27 then 0.95 (bear and bull 1.00).
- **Revenue per kg choice:** FY27 keeps the 1HFY27 Rs.811 (half the year is actual; Sep-2026 ~Rs.875 = Rs.42 cr on ~480 t, call PDF 8, 13). From FY28 base takes 5% off (~Rs.40/kg, a fifth of the mix gain): Unit 3 fills with newly approved parts (the company's own Unit 3 first-line estimate = Rs.75 cr from 1,500 t = Rs.500/kg), dies lumpy, FY24-FY26 ran Rs.576-662. Most of the gain kept: energy Rs.48 cr in 1HFY27 vs Rs.31 cr in all FY26. Factor scales materials and value added together, so gross margin holds and EBITDA margin falls ~0.6-1.2 pts vs the floor.
- **FY27 note:** Sep-2026 run-rate would give ~Rs.460 cr, above the ~Rs.440 cr guided; base stays just below guidance (Rs.433 cr) because one month is not a trend.
- **Bull vs guidance:** bull Rs.455 / 652 / 866 / 970 cr vs guidance ~441 / 635 / 810 / 1,000: close to guidance (above in FY27-FY29, 3% below in FY30). Left unchanged, as is the bear.
- **Checks:** recalc 0 errors (1,219 formulas). Under bear, base and bull every check row is ~0 (P&L max 0.0003, Drivers revenue tie 0, Segments 0.0001, Half-yearly 0.0003); Valuations C63 = 0; TAM row 42 base-between-floor-and-guidance = 1 each year. Selector back at 2.
- **Not sourced:** no die-casting or aluminium-casting market size or CAGR in the documents (IBEF-based chapter, no commissioned report); no CV forecast CAGR in the documents (ICRA used for FY26-FY27 only); EV market growth and the CV content/price add-on are our estimates; management's 29-30% energy-sector growth has no source.
- **Scripts (scratchpad scripts/):** update_poojaa_base_reset.py, valuation_reset_poojaa.py, run_scen_poojaa.py (updated: mix row), tam_industry_block_poojaa.py, dump_reset_poojaa.py, build_note_poojaa_v2.js. Pre-reset model copy and results in scratchpad pjreset/.

## File versions
- Model: POOJAA_Model_v1.xlsx (10-Nov-2026); POOJAA_Model_v2.xlsx (10-Nov-2026)
- Model: POOJAA_Model_v2.xlsx updated in place 11-Nov-2026 (base reset; git holds the pre-reset version)
- Note: Poojaa_Precision_Note_v1.docx (6 pages, rendered and checked); Poojaa_Precision_Note_v2.docx (11-Nov-2026, base reset, 7 pages, rendered and checked)
- Evidence: notes/evidence.md
