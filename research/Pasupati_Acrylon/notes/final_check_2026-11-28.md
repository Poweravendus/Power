# Pasupati Acrylon (PASUPTAC) - final check, 28-Nov-2026

Reviewer: independent final check per `_briefs/FINAL_CHECK_BRIEF.md`. Files checked: `PASUPTAC_Model_v2.xlsx`, `Pasupati_Acrylon_Note_v1.docx`.
Backups of the files as received: scratchpad `fc/bak/`. Scripts written: `scripts/fc_dump.py`, `fc_scenarios.py`, `fc_note_dump.py`, `fc_note_fix.py`, `fc_note_trim.py`, `fc_model_fix.py`.

## What was checked
- Recalc (LibreOffice): 0 formula errors before and after the fixes (1,882 formulas after).
- Selector Drivers!C3 run on copies at 1 bear, 2 base, 3 bull, 4 floor. Every CHECK row on every sheet (177 cells after the fix, 145 before) is exactly 0 in all four. Selector left at 2 (base).
- Pasted scenario table (Valuations rows 28-39) and the pasted bull/floor rows on Drivers (rows 93-96): equal to live output in all four scenarios (difference 0.000). No re-paste needed.
- Logic: floor 53.8 <= base 77.0 <= bull 115.4 (bear 14.6 sits below the floor, see lead items); same 7.5x P/E in all cases (one cell); chance in price = (67.95 - 76.98) / (115.43 - 76.98) = -23.5%, correct; rating HOLD at +13.3% on the base target, correct (1.7 pts from BUY); net debt for EV cross-check = FY27E (year before FY28E), correct; EPS on 8,91,33,121 shares (AR FY26 p.67), correct; all Rs. crore; FY = April-March throughout; base below bull (proxy for guidance; the company gives none) on revenue and margin in every year.
- Per-kg spread: realisation - ACN consumed per kg produced; implied ACN = cost per kg / 0.889 gives Rs.97.4 FY21 and Rs.171.5 FY22 vs CARE Rs.97.47 / 171.57 (CARE Aug-2022 p.2). Recomputes.
- Mid-cycle: 10-yr average EBITDA margin 7.99% (FY17-FY26); FY28E PAT at that margin Rs.58.4 crore; x 7.5 / 8.913 crore shares = Rs.49.2. Recomputes.
- Historical spot-checks against the pack (all tie): FY26 revenue 1,01,015.78 lakh, materials, inventory change, employees, finance cost, depreciation, other expenses, exceptional 56.89, tax, PAT 6,991.41, EPS 7.84, CFO 5,150.22, capex 1,604.41 (AR FY26 p.53-55); FY26 BS lines incl. borrowings 9,638.64 + 1,071.60, cash 4,259.95, MF 8,780.35 (p.53); segments FY24, FY25, FY26 revenue / result / depreciation / assets (AR FY24 p.85, AR FY26 p.81); FY17 revenue 50,203.48 incl. excise and PAT 3,422.31, FY18 PAT, CFO 6,726.58, inventory (AR FY18); FY20 revenue 66,364.36, PAT, CFO (181.26), cash (AR FY20); FY22 revenue 77,553.75, PAT, CFO, inventory, fibre segment revenue, CPP result (AR FY22); FY23 inventory, PAT, power (AR FY23); FY24 LT borrowings 4,355.56, CWIP, CFO (AR FY24); FY25 LT borrowings, ACN, fibre sales 33,850 t, MD pay (AR FY25); Q2FY27, Q1FY27, Q2FY26, H1 P&L and segments, Sep-26 balance sheet (Res Q2FY27 p.2-4); Q3FY26 / Q4FY26 PAT and fibre results (Res Q3FY26, Q4FY26).
- Note: every number in the title, snapshot and 16 tables tied to the model or the source (list of exceptions below). Rendered to PDF and every page viewed.
- Latest price: Screener page 28-Nov-2026 shows Rs.68.0 (= 27-Nov close Rs.67.95; 28-Nov is a Saturday), mcap Rs.606 crore, P/E 5.42. CMP not changed. Screener 52-week high/low (intraday) Rs.86.4 / 40.4 vs note's closing range Rs.40.9-84.3 (now labelled "closes").

## Issues found

| # | Severity | Where | Issue | Action |
|---|---|---|---|---|
| 1 | High | Note s.6 red flags | Red flags were not each stated with document + page; four of the six known flags (H1FY27 fibre margin jump, distillery sales fall, anti-dumping duty not notified, distillery on promoter-leased land) were not in the red-flag list. Each re-verified against the pack | Fixed: list rewritten (a)-(g), each with doc + page |
| 2 | Medium | Note s.7 floor text | Said floor uses mid-cycle Rs.15/kg fibre and Rs.12.5/kg film and "nothing assumed after October 2027"; the model (and the note's own FY28E table) uses Rs.16.4 and Rs.11.3, and repeats the allocated ethanol volume in FY29E-FY30E | Fixed text to describe the model; driver left for lead (item L2) |
| 3 | Medium | Note Q7 | "MD's commission rose 90%": total pay rose 89.7%; commission went from Rs.1.30 crore to Rs.3.55 crore (+173%) (AR FY25 p.41, AR FY26 p.36) | Fixed |
| 4 | Medium | Note s.6 | "promoted in 1982 by Vineet Jain": company set up 1982, production from 1990; Vineet Jain born 1969, on the board since 1994 (CARE Jun-2026 p.2; postal ballot p.15) | Fixed |
| 5 | Medium | Note s.5 / Q3 | Anti-dumping: Indian Acrylics AR FY26 does not date the DGTR recommendation and names "Thailand, China & France"; note said "never notified ... August 2025" | Fixed wording to "still not notified in September 2026 (Indian Acrylics AR FY26 PDF p.13, 21)"; country mismatch for lead (L5) |
| 6 | Medium | Model Quarterly | No check that quarters add to the annual figure or half-years to reported H1 | Fixed: rows 44-52 (revenue, PAT, 3 segment revenues, 3 segment results; FY25, FY26, H1FY26, H1FY27); all 0 |
| 7 | Low | Note s.1 | "Mills pay in 15-30 days" not in any document; CARE says advance payments or discounted LCs | Fixed (CARE Jun-2026 p.3) |
| 8 | Low | Note s.4 | H1FY27 CFO was negative Rs.35 crore (Res Q2FY27 p.5): material, not mentioned | Added to working-capital paragraph and red flag (c) |
| 9 | Low | Note s.6 | CDR recompense "paid in FY18-FY19": provided by FY18, paid in FY19 (AR FY18 p.7, AR FY19 p.7); film assets "Rs.75-100 crore" are Rs.50-100 crore over FY18-FY26 | Fixed |
| 10 | Low | Note T7 | Q2FY26 EBITDA 27.15 shown as 27.1 (model shows 27.2) | Fixed |
| 11 | Low | Note style | Jargon unexplained (EBITDA, PBIT, CFO, CWIP, BOPP, DGTR, CBIC, ESY, EV/EBITDA); "a 18.3%"; "Rs.606cr" / "cr" in header, snapshot and two tables | Fixed (one-line explanations, "crore") |
| 12 | Low | Note layout | After the edits section 6's sources line spilled onto a near-empty page (8 pages) | Fixed by trimming wording; back to 7 pages, no cut tables |
| 13 | Low | Model | Hard-coded 0.889 in Segments!B40:K40 (not linked to Drivers!C21); share count hard-coded in Quarterly EPS; raw-material values typed inside Segments row 53/64 formulas (history only) | Left (history only, no forecast effect) |
| 14 | Low | Model BS | Forecast balance-sheet check is 0 by construction (cash is the plug); the real test is the CF closing-cash check, which is 0 | Left, noted |
| 15 | Low | Model Segments row 62 | Label says production/capacity; forecast years use sales | Left |
| 16 | Low | Scripts | `pal_build_model.py` / `pal_note_v1.py` do not contain these fixes; a rebuild would undo them | For lead: port fc_model_fix.py / fc_note_fix.py / fc_note_trim.py or stop rebuilding |

No em-dashes, rupee symbols or [A]/[E]/[M] tags in the note. No stale targets (first priced version; status.md lists none). Title, valuation section and bottom line agree: CMP Rs.67.95, mcap Rs.606 crore, HOLD (borderline), Rs.77, +13.3%, Version 1 (28-Nov-2026).

## For the lead (judgement, not changed)
- L1. "Floor" Rs.54 is 3.7x the bear Rs.15. A floor above the bear will confuse the investor; rename it (e.g. "visible-earnings memo") or define it as a true floor.
- L2. Floor fibre EBITDA is Rs.16.4-17.4/kg in FY28-30E against the stated mid-cycle Rs.15 (10-yr available-year average Rs.14.7). At Rs.15 the floor falls by about Rs.5 crore EBITDA, to roughly Rs.50 a share. Floor FY29-30E ethanol repeats the ESY27 volume although the definition says nothing after Oct-2027.
- L3. Base FY28E is 38% of the way from floor to bull (17-21% in FY29-30E), below the 40-75% rule of thumb; the stated reason (unapproved 240 KLPD in bull) is reasonable but should be said to the investor.
- L4. HOLD is 1.7 points from BUY; small driver changes flip the rating.
- L5. Anti-dumping: press (KNN, tpm, Aug/Sep-2025) says China, Peru, Thailand; the Indian Acrylics AR says "Thailand, China & France". A web search on 28-Nov-2026 found no Finance Ministry/CBIC notification, but the primary CBIC list was not checked.
- L6. Peer P/Es (Vardhman 7.1x, Gulshan 5.8x, Cosmo 15.5x) are Screener trailing multiples on different points of their cycles; check on Bloomberg before relying on 7.5x.

## Final numbers (base, selector 2)
CMP Rs.67.95 (27-Nov-2026 close; Screener Rs.68.0 on 28-Nov) | Mcap Rs.606 crore | FY28E EPS Rs.10.26 | P/E 7.5x
Floor Rs.54 (memo) | Bear Rs.15 | Base Rs.77 | Bull Rs.115 | Upside +13.3% | Rating HOLD (borderline) | Chance in price -23% | Mid-cycle value Rs.49 | EV/EBITDA cross-check Rs.80.

## Could not verify
- CBIC notification status of the acrylic fibre anti-dumping duty (primary source not checked).
- Peer multiples and peer capacities (Screener only).
- ESY 2025-26 ethanol allocation; 240 KLPD plan beyond CARE; fire loss and insurance.
- Quarterly figures are read from scanned PDFs (OCR is noisy); all tie to H1 and annual totals, which is strong evidence they are right.
