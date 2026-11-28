# Qualiance International - final check, 28-Nov-2026

Reviewer: independent final check per `_briefs/FINAL_CHECK_BRIEF.md`.
Files checked: `QUALIANCE_Model_v2.xlsx` and `Qualiance_International_Note_v3.docx`. v1 and v2 files were not touched.
Scripts added in `scripts/`: `fc_scen_check.py` (three scenarios on a copy, all CHECK rows, pasted-table and live comparison), `fc_sens_floor.py` (re-runs the sensitivities and rebuilds the floor), `fc_fix_model.py` and `fc_fix_note.py` (the fixes below).

## What was checked
- Model: recalculated with 0 formula errors (1,116 formulas). Ran selector 1, 2 and 3 on a copy, recalculating each time. Read every CHECK row on every sheet. Compared the live results with the pasted scenario table (Valuations rows 51-53) and the pasted bull revenue (Drivers row 146). Rebuilt the re-based floor (Valuations rows 57-65) and re-ran the five sensitivities (rows 90-95). Logic tests: floor <= base <= bull, base vs guidance, one P/E, chance-in-price formula, rating rule, net-debt year, share count, units and year labels. Looked for formula smells.
- Note: tied every number in the title, all 17 tables and the key sentences to the model or source. Checked style rules (no em-dashes, rupee symbols or [A]/[E]/[M] tags; comments and footnotes are empty), stale targets (Rs.104 and Rs.142 appear only as history), and red-flag page citations. Rendered to PDF (9 pages) and looked at every page.
- Sources re-downloaded (kept outside the repo, in the scratchpad): the RHP from the company website (299 pages; printed page = PDF page - 3, confirmed), the 1HFY27 results filing, the 1HFY27 presentation and the call transcript from NSE archives (via Screener links), and the Screener price history.

## Check results under all three scenarios (after fixes)
| Check | Bear (1) | Base (2) | Bull (3) |
|---|---|---|---|
| Formula errors | 0 | 0 | 0 |
| Balance sheet (P&L row 73) | <=0.0001 | <=0.0001 | <=0.0001 |
| Cash flow vs BS cash (row 98) | <=0.0001 | <=0.0001 | <=0.0001 |
| PAT rebuild / reported (row 30) | <=0.0001 | <=0.0001 | <=0.0001 |
| Segment ties (Segments rows 10, 18, 44) | <=0.0001 | <=0.0001 | <=0.0001 |
| Half-year PAT and 1H+2H=FY (Half-yearly rows 21-22) | <=0.0002 | <=0.0002 | <=0.0002 |
| Live target vs pasted (Valuations row 54) | 0 | 0 | 0 |
| Pasted table C:I vs live | match | match | match |
| Pasted EV/EBITDA value (col J) vs live | was 36.8 vs 31.0 (fixed) | was 124.6 vs 88.1 (fixed) | was 191.8 vs 172.5 (fixed) |

TAM row 26 is labelled "Cross-check" but is a value (MBAS programme Rs.500 cr a year), not a zero check. All other 1H+2H=FY lines tie when added by hand (other income, materials, stock change, staff, other costs, depreciation, interest, tax, PAT). The selector is back at 2 (base).

The floor rebuild reproduces Valuations rows 59-63 exactly: existing plant 80% FY27 then 82%, Rs.1,975 a piece; new unit 0/12/25/40% at Rs.1,100; base costs. The sensitivities reproduce: FY28E EPS 8.72 / 9.31 / 10.37 / 9.38; targets Rs.104.67 / 111.71 / 124.40 / 112.60; Rs.181.99 at 23.2x.

## Issues found
| # | Severity | Where | Issue | Action |
|---|---|---|---|---|
| 1 | High | Note, Key drivers table | Old-plant labour per piece FY28E shown as Rs.435 for floor and base; the model uses Rs.420 (Drivers D52; floor rebuild confirms 420). 435 is the FY29E value. | Fixed: 420 / 420 |
| 2 | Medium | Model, Valuations J51:J53 | Pasted EV/EBITDA values were stale (36.8 / 124.6 / 191.8 vs live 31.0 / 88.1 / 172.5). The note already showed the live values. | Fixed: re-pasted |
| 3 | Medium | Note, red flags | None of the six red flags cited a document and page (brief rule). | Fixed: added RHP p.182, 189 (loan); p.61-62, 158 (rights issue); p.189-190 (family pay); p.63, 65-66, 83 (pre-IPO sale); results filing and Prospectus p.69 (issue costs); p.156, 166, 56, 151 (restatement, auditors). Every RHP page was checked against the download. |
| 4 | Medium | Note, "Can they deliver" and Questions | The note said the presentation's 255 staff conflicted with 283. The RHP itself (p.114) gives 255 payroll staff excluding management at June 2026; 283 at March 2026 includes management. | Fixed the wording in both places |
| 5 | Medium | Model, Drivers C155 | The memo for new-unit FY30E revenue used the old-plant price (Rs.139.8 cr base vs actual Rs.77.8 cr), a stale link from before the 24-Nov split. Memo only; the note had the right figure. | Fixed: =F174*(1+F34) |
| 6 | Low | Note, unit table | Depreciation and interest per piece: 123, should be 124 (Rs.4.87 cr / 3,94,044). The column now adds to 301. | Fixed |
| 7 | Low | Note, base table | FY29E net debt: 11.2, should be 11.3 (11.25). | Fixed |
| 8 | Low | Note sensitivity table; Valuations C90:C95 | Upside was worked out on rounded targets: -23% / -18% / -10%; on the model targets it is -24% / -19% / -9%. | Fixed in the note; pasted unrounded targets in the model |
| 9 | Low | Model text | Valuations J59 described the old 8-Nov base, not the re-based floor. Drivers G148 said 40% when the base is 22-32% of the way. | Fixed the text |
| 10 | Low | Model formulas | Valuations C14 used typed equity 77.2782; Unit_Economics C30:D32 used typed 10.8 and 600. | Linked to Half-yearly!D33 and Drivers C13 / C175 (same values) |
| 11 | Low | Note p.7-8 | The source line under "What the price is paying for" falls to the top of page 8. | Left as is (cosmetic) |
| 12 | Low | Note | Rs.1,240 (peer table) vs Rs.1,241 (capacity table) for the FY24 price per piece: rounding of the inputs. | Left as is |

## For the lead (judgement, not changed)
1. **Position of the base.** The base is 22-32% of the way from floor to bull, below the house rule of 40-75%. The note says so, but the rule is broken in every year. Either restate the rule now that the bull uses management's new-unit price, or lift the base.
2. **Stale CMP and stale disclosure.** The 27-Nov close is Rs.126.00, 8% below the Rs.137.10 in the files. The base is still SELL at that price (-25%) and the chance in the price falls to about 27%. Replace it with Bloomberg as planned.
3. **New fact for the governance section.** RHP p.67 states that no promoter or promoter-group shares were bought or sold in the six months before filing. But p.65-66 and p.83 show promoter-group sales at Rs.127 on 29-Aug-2026, two days before the RHP. Consider adding this to the pre-IPO selling red flag.
4. **Year of net debt in the EV/EBITDA cross-check.** FY28E EBITDA is paired with FY27E-end net debt (Rs.2.3 cr). With FY28E-end net debt the base value is Rs.81 instead of Rs.88. This is only a cross-check, and the convention is stated in the note.
5. **FY27E EPS.** It uses year-end shares (1.345 cr) although the IPO came in September 2026, which slightly understates FY27E EPS and overstates FY27E P/E. The FY28E target is not affected.
6. **Multiple.** The same 12x is used in all scenarios. At the peer's 23.2x the base is Rs.182 (BUY). Peer multiples are still pending from Bloomberg.

## Final numbers (unchanged by this check)
- CMP Rs.137.10 (NSE close 8-Nov-2026, matches the Screener history). Market cap Rs.184 crore.
- Targets at 12x FY28E EPS: floor Rs.71 (-48%), bear Rs.24 (-82%), base Rs.94 (-31%), bull Rs.214 (+56%).
- Rating on the base: SELL. HOLD would need a price below Rs.99.
- Chance of management's plan already in the price: (137.10 - 94.09) / (213.99 - 94.09) = 36%.
- Logic holds: floor (71) <= base (94) <= bull (214). The bear (24) is below the floor by design: the bear is a loss of Swiss volume, the floor is the committed-only case. The base is below guidance-implied revenue every year (-4% / -30% / -36% / -43%) and below the 21.7% margin guidance every year. FY28E EPS uses the post-IPO 1,34,52,000 shares. All figures are in Rs. crore with March year-end FY labels.
- Latest close (Screener): **Rs.126.00 on 27-Nov-2026**, 8.1% below the model's CMP. At Rs.126: market cap Rs.169.5 crore, base -25% (SELL), floor -44%, bull +70%, chance in price about 27%. The CMP in the model and note was not changed.

## Verified against source documents
- RHP restated statements (p.154, 156, 157): FY24-FY26 revenue, other income, materials, stock change, staff cost, other expenses, depreciation, finance cost, PBT, tax, PAT (11.87 / 4.90 / 2.84), EPS 11.99, share capital, reserves, long and short-term debt, payables, provisions, PPE, DTA, promoter loan 3.76 / 2.21, inventory, receivables, cash, CFO 7.84 / (4.45) / 2.85, capex, opening cash.
- RHP operating data: country split (p.103), Swiss buyer split incl. customs 13.84 (p.105), woven 71.55% and top 1/5/10 (p.19), capacity, production and utilisation (p.112), employees and attrition (p.114), 600-machine quote (p.72), RCC building and March 2027 date (p.71, 75), peer P/E 60.84x / 23.21x (p.80), family pay, reimbursements and promoter-loan interest (p.189-190), rights issue (p.61-62, 158), auditor change (p.56, 151), restatement reconciliation incl. audited PAT 10.67 / 5.88 / 3.71 (p.166), GST sales Rs.14.5 cr (p.211), promoter holding 63.66% post-issue (p.67).
- 1HFY27 results filing (PDF p.3-5): all half-year P&L lines for 1HFY27, 2HFY26, 1HFY26 audited and FY26 audited; the Sep-26 balance sheet (equity 77.28, debt 16.80, cash 37.90, inventory, receivables, PPE); the cash flow (CFO 8.91, capex 2.43, IPO 45.11 less 5.91, net debt repaid 11.70, promoter loan 3.76).
- Presentation: project cost Rs.39.14 cr, 600 machines, 10.8 lakh pieces, 255 employees, July 2027 start, promoters 63.7%. Call: Rs.6 cr awaiting inspection, Rs.76-77 cr FY27, 30-35/60/90% fill, Rs.180 cr peak, Rs.30 cr visibility, "upwards of Rs.2,500", no hedging, steel pre-engineered building, Q1FY28 start.
- Investor inputs: the meeting notes (60/20/20 split, Rs.40-60 cr, 25-30% of Rs.200 cr, 60/40 tender scoring, 2032 and 2028, 600 machines and 1,000 workers on 340, March and July 2027, 80% imports, 8-9 days, HEM 131/24 and 202/40) and the revenue-per-piece workbook (peer figures) match the note.
- Price: 8-Nov-2026 close Rs.137.10 and listing-day close Rs.236.10 (Screener history).

## Not verified (checked only against our own notes)
- Prospectus figures: the issue-expense estimate of Rs.7.09 cr (15.7%), the fee breakdown, and the Prospectus p.69 page cited in the note. The Prospectus was not downloaded.
- DRHP figures: FY23 restated and 1HFY26 restated; the DRHP was not downloaded.
- Post-listing events: Krupa Badani's resignation ten days after listing, the company secretary's resignation, Dhriti Drolia's link to Silvertraq, and the ICRA A4 rating of July 2022. The RHP board-change table (p.138) does not parse cleanly.
- Swiss Army census and MBAS web data (TAM sheet); GTRI, CITI and Apparel Resources export data.
- Peer revenue per machine and machine counts in the investor table, and the 240-machine count posted on X.
