# Final check - Bonfiglioli Transmissions (BONFIG) - 28-Nov-2026

Files checked: BONFIG_Model_v2.xlsx, Bonfiglioli_Transmissions_Note_v1.docx (both fixed in place; pre-check copies in scratchpad fc_bonfig/bak).
Scripts added: scripts/fc_scenarios_2026-11-28.py (scenario and check runner on copies), scripts/fc_fix_model_2026-11-28.py, scripts/fc_fix_note_2026-11-28.py (run-level docx edits).

## What was checked
- Model recalc (LibreOffice): 0 formula errors (1,136 formulas), before and after fixes.
- Scenarios 1/2/3 (Drivers!C3), recalculated each time, every CHECK row on every sheet: P&L EBITDA and PBT vs reported, balance sheet, total assets vs reported, closing cash vs balance sheet, Quarterly (Q1+Q2 = H1, Q4 + 9M = FY25), Segments verticals vs P&L, geography, channel, Valuations live vs pasted. All 0 in all three scenarios except a 0.001 rounding in the H1FY25 channel table (source rounding). Selector left at 2 (Base).
- Extra tie: H1FY26 + Q3FY26 = 9MFY26 holds for revenue, PBT, PAT; other expenses and other income each differ by Rs.0.6 crore (Prospectus H1 vs results classification; Q1FY26 derived lines carry it). Not a model error.
- Pasted tables (Valuations rows 47-49 and floor memo rows 54-60): re-ran brun.py logic on a copy; live minus pasted = 0.000 for every cell. No re-paste needed.
- Logic: bear 589 < floor 676 < base 757 < bull 810 (floor <= base <= bull holds; bear sits below the floor by design: wind falls and materials 64.6%). Base below guidance every year (revenue -0.2% FY26 to -15.9% FY30; margin -0.3 to -0.5 points). Same 45x P/E in all cases. Chance in price = (803.25 - 756.89) / (809.58 - 756.89) = 88.0%, correct. Rating rule on base target: -5.8% -> SELL, correct (borderline, 0.8 points). EV cross-check uses FY26E net cash (year before valuation year), consistent. EPS on 18.7996 crore shares (187,995,834, Pros p.63/p.97; OFS added none). Units Rs. crore throughout; December-year labels consistent (TAM sheet uses March market years and says so).
- Historical spot-check (~30 numbers) against Prospectus p.284-286, 207-209 and results p.1: revenue, other income, raw materials, employee, finance, D&A, other expenses, PBT, tax, PAT continuing and discontinued (FY23-25), EBITDA (p.209), CFO 1,876.81/1,883.50/1,982.28 mn, capex, dividends, buyback, net change in cash, PPE, inventories, receivables, cash, total assets, equity, FY23 borrowings, I&A/wind/others revenue, dealer sales, all of Q3FY26, Q2FY26, Q3FY25, 9MFY26, 9MFY25 lines, EPS 4.63/3.99/3.35/12.54/8.91/12.65. All match.
- Formula smells: none material. Group_vs_ThirdParty F98 uses IF(0=0,...) constants to switch the 77% (works, cosmetic). Floor memo FY27 growth is 6.6% not 7% because "others" revenue moves to 2% of verticals (memo only).
- Note: every number in title, tables and key sentences tied to model or source (list of mismatches below). Style scan after fixes: no em/en-dashes, no rupee symbol, no [A]/[E]/[M] tags, no "cr". Rendered to PDF (7 pages) and checked every page.

## Company-specific points
- Year labels: FY25 = Jan-Dec 2025 in both files; FY27E = Dec-2027 stated in the note version line and now explained in the valuation section.
- Quarter labels: the company calls the quarters Q2CY26 / Q3CY26 / 9MCY26 (BSE cover letters 13-Nov-2026, earnings release, presentation, call title); the statutory results say "quarter ended September 30, 2026". The note and model use Q3 FY26 for the same Jul-Sep 2026 quarter (same period, different label). Added a one-line definition to the note and to the Quarterly sheet so no one reads Q3 FY26 as Oct-Dec 2025.
- Royalty: 6% of yearly net sales, sales to Bonfiglioli S.p.A. excluded, net of discounts and incentives - Pros p.253 (also p.25, p.232); licence clause 5.2 (licence p.4). Effective 4.4-4.5% of sales - call p.14 (model cited p.13; fixed).
- Territory: India, Pakistan, Bangladesh, Sri Lanka, Nepal; any other country with BSPA consent - Pros p.25, p.232, p.253. The licence itself (clause 7.2, p.5) is narrower: outside the territory only to group companies, with consent. Note now cites both.
- Renewal: one-year term, automatic yearly renewal, either party may end with notice at least three months before 31-Dec - Pros p.25, p.253; clause 9.2 licence p.6.
- OFS: 43,239,042 shares by Bonfiglioli S.p.A. at Rs.586 = Rs.25,336.63 mn (after Rs.29 employee discount) - Pros cover (PDF p.1), p.106. No fresh issue; shares unchanged at 187,995,834 (p.63).
- Parent cost: weighted average Rs.6.77 per share - Pros cover, p.51.
- Post-IPO parent holding: 144,756,792 shares = 77.00% - Pros p.97, p.104.
- Common control (note 46, Pros p.341; also p.252, p.345; results note 7): BTA 15-Dec-2025 with group company Bonfiglioli Drive Solutions Pvt Ltd (BDSPL); BTL bought its gear-components manufacturing business (movable assets, contracts, employees, liabilities) as a slump sale for Rs.214.40 mn at fair value (valuer report 17-Dec-2025); pooling-of-interest under Ind AS 103 Appendix C, comparatives restated. Audited vs restated PAT: FY23 149.53 vs 148.49 cr, FY24 194.69 vs 195.16 cr, FY25 equal (p.345). The note mentioned the BDSPL restatement but not what/when/price; added.
- Latest close (Screener): Rs.803.00 on 27-Nov-2026 (Mcap Rs.15,096 crore on Screener). CMP in model and note left at Rs.803.25 (26-Nov) as instructed. At Rs.803.00: base -5.7% (SELL, still borderline), chance in price 87.5%.

## Issues found
| # | Severity | Where | Issue | Action |
|---|---|---|---|---|
| 1 | High | Note, peer table (p.1) | Elecon and Shanthi Gears values swapped in four rows: revenue, EBITDA margin, ROCE, sales/fixed assets (Pros p.119: Elecon Rs.2,366 cr, 22.1%, 19%, 3.9x; Shanthi Rs.519 cr, 20.0%, 25%, 4.2x) | Fixed |
| 2 | Medium | Note, Capacity | "would need about 90% of today's hours by FY28 without that expansion" does not tie: model shows 107% of FY25 hours without expansion (Unit_Economics D27), 91% with the assumed machine additions (Drivers bull FY28) | Fixed (both numbers stated) |
| 3 | Medium | Note, price section | "risen ... most of it after the September-quarter results": Rs.574.50 -> 722.35 came before results (12-Nov), only 722.35 -> 803.25 after (about a third) | Fixed |
| 4 | Medium | Note, layout | Scenario table (Floor/Bear/Base/Bull) split across pages 5-6 | Fixed (rows kept together; re-rendered) |
| 5 | Medium | Note | Common-control BDSPL acquisition not described (what, when, price) | Added with pages |
| 6 | Medium | Note | Royalty described as "6% of sales of licensed products" without the exclusion of sales to the parent | Fixed, Pros p.253 |
| 7 | Low | Note, licence red flag | Clause references without document page; licence 7.2 vs prospectus "any other country" difference not shown | Fixed (licence p.5/p.6, Pros p.25/p.253) |
| 8 | Low | Note | Quarter labels Q3 FY26 differ from company's Q3CY26 naming; no definition | Definition added (also Quarterly!A1) |
| 9 | Low | Note | Valuation year choice (FY27E) not explained in the valuation section | Added one line |
| 10 | Low | Note, history table | PAT row is reported (incl. discontinued Rs.1.8/3.6 cr FY23/24) while EPS and source line say continuing | Row relabelled "PAT (reported)", source line explains |
| 11 | Low | Note, quarterly table | Q1 FY26 PAT 73.500 shown as 73 | Fixed to 74 |
| 12 | Low | Note | Local sourcing "64% to 71%" mixes two prospectus bases (p.209 64.12% purchases vs p.237 65.39%-71.10% consumed) | Fixed to 65% to 71%, p.237 |
| 13 | Low | Note, market table | Global wind drives growth "~5%"; USD 1.0 -> 1.4 bn CY25-31 = 5.8% | Fixed to ~6% |
| 14 | Low | Note, drivers table | "Materials, % of sales" shows the core-revenue driver (FY30 62.1% vs 62.2% of total) | Relabelled "% of core sales" |
| 15 | Low | Note | "FY27E EPS about 9% higher" at 19.7% margin; model gives 9.5% | Fixed |
| 16 | Low | Note, questions | "interim dividend weeks before the IPO" vs red flag "months before"; dividend was declared and paid in H1 2026 (p.280, p.311), IPO opened 15-Oct | Fixed to "months" |
| 17 | Low | Note | "cr" abbreviations (header Mcap, market table headers, capex cells) | Fixed to "crore" |
| 18 | Low | Note + model | Royalty quote cited call p.13; it is p.14 | Fixed (note table source, Drivers!H54, Group_vs_ThirdParty!G51) |
| 19 | Low | Model, Valuations!A1 | Said FY27E is "the same 12-month window" as FY28E for March companies; it overlaps 9 of 12 months | Text fixed |
| 20 | Low | Model, Unit_Economics!H27 | Text said "~95-100%" of FY25 hours by FY28; cells show 107% bull, 97% base | Text fixed |
| 21 | Info | Quarterly | Rs.0.6 cr other expense / other income classification gap between Prospectus H1FY26 and results 9M less Q3 | Left (not a model error) |

## For the lead (judgement, not changed)
1. Rating is borderline on the multiple, not the business: base -5.8% is 0.8 points past the SELL line; at Rs.803.00 it is -5.7%. 47x instead of 45x (peer average 51.6x divided by 1.10 rather than 1.15) would make it HOLD. The 1.15 roll-forward divisor (~8% a year over 1.75 years) is a choice worth defending in the meeting.
2. Bear (Rs.589) sits below the floor (Rs.676). Defensible (bear assumes wind falls and margin to ~16%), but the note calls the floor "what is visible now"; the investor may ask why a case is below it.
3. Bull = guidance gives only +0.8%, so even full delivery does not support HOLD with upside; the note says this. Consider whether bull should also carry the 19.7% margin evidence (note's "what would make us wrong" gives Rs.869).
4. 9MFY25 base: the note says reported 40.7% nine-month PAT growth is on a low base (32% on Prospectus H1 + results Q3). Results note 5 says Q3FY25 is a balancing figure after subsequent-event adjustments, so the audited 9M (Rs.167.5 crore) may be the right base; consider softening.
5. "The first quarter as a listed company was its best ever" (bottom line): Q3 (Jul-Sep) ended before the 23-Oct listing; it was the first result reported as a listed company.
6. status.md still says the interim dividend was paid "weeks" before the IPO; the prospectus supports "months" (H1 2026).

## Final numbers (unchanged by this check)
- CMP Rs.803.25 (close 26-Nov-2026; Screener latest Rs.803.00 on 27-Nov-2026, not applied). Market cap Rs.15,101 crore.
- Targets at 45x FY27E EPS (year to Dec-2027): floor Rs.676 (-15.8%), bear Rs.589 (-26.7%), base Rs.757 (-5.8%), bull Rs.810 (+0.8%).
- Rating SELL (borderline). Chance of management's plan in the price: 88%.
- EV/EBITDA cross-check (29x FY27E + FY26E net cash): Rs.755.

## Could not verify
- Current peer multiples (Bloomberg items flagged in the note); NSE price (blocked; Screener used).
- Subscription, anchor book, basis of allotment (not in pack).
- Licence clause 7.2 vs prospectus wording: which governs in practice (the amendments to the licence referred to on p.253 are not in the pack).
- Vertical quarterly figures (PPT slides 7-8, rounded in Rs. mn) beyond the totals.
