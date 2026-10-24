# ACME Solar model – historical data update (Oct 2026)

File: `ACME_solar_historicals_updated.xlsx` (built from the uploaded `ACME_solar.xlsx`). Only the `Qtry` tab and the historical columns of `Consolidated` were changed; `Key_New`, `Assumptions`, the forecast columns (FY27E onward), the QIP table on `Valuation` and all charts, external links and other sheets are untouched. The workbook was edited at XML level (not re-saved through a spreadsheet library), so charts, external-link caches, comments and styles are preserved byte-for-byte outside the edited areas.

## What was done

### Task 1 – `Qtry` rebuilt
Columns D–P = 1QFY24 … 1QFY27 (same column positions as before, so the `IPRU` tab's column references still line up). Eight blocks, each with a cell note on its header cell (column B) naming the source document and page:

| Block | Rows | Content |
|---|---|---|
| A | 5–25 | Consolidated P&L, INR mn, as first reported in the exchange results filings (Q1FY24 from the RHP) |
| B | 27–47 | Standalone P&L (in-house EPC), same filings |
| C | 49–57 | Generation, CUF, plant/grid availability, Rajasthan and wind CUF with the contracted MW each refers to |
| D | 59–66 | Operational MW by technology, MW commissioned in the quarter, commissioned BESS MWh |
| E | 68–78 | BESS revenue, cost of power, EBITDA/margin, capitalised cost per MWh, RTE, DoD, short-term vs merchant split |
| F | 80–89 | Gross block, CWIP, asset base, gross debt, cash, net debt (operational / under-construction), net worth |
| G | 91–99 | Net debt/TTM EBITDA, TTM EBITDA, net debt/net worth, cash RoE, DSO (two bases), weighted average tariff, weighted average cost of debt |
| H | 101–107 | Shares outstanding, basic/diluted EPS, cash EPS, BVPS, dividend declared |

`IPRU` formulas that pointed at the old `Qtry` rows were re-pointed to the same line items in the new layout (45 formulas; the "Profit of associate" links now point at an empty spacer row, as the company reports no associates). No other formula was changed.

### Task 2 – `Consolidated` extended to FY18
Four columns (FY18–FY21) inserted before the old column D. Every formula in the workbook that referenced `Consolidated` (in `Consolidated` itself, `Valuation`, `DCF`, `Charts`, `IPRU`) was shifted by four columns so it points at the same cells as before; a LibreOffice recalculation of the original and the updated file shows identical values on every sheet. The one deliberate exception is the FY22 working-capital-days rows (now H220:H223): their `AVERAGE(prior year, current year)` ranges now include the FY21 column that previously did not exist, so they read the actual two-year average instead of a single year.

Reported line items are hard-coded (black, Arial 9, format `#,##0;(#,##0);"–"`); sub-total and ratio rows keep the sheet's existing formulas, translated to the new columns. Sum-of-two-notes cells follow the sheet's existing `=a+b` convention (e.g. cash + bank balances).

## Sources
* Annual reports FY19–FY26 and all quarterly presentations/transcripts: `ACME Solar/` folder in this repo (downloaded from acmesolar.in).
* RHP dated 29 Oct 2024 and Prospectus dated 9 Nov 2024 (acmesolar.in). The DRHP covers the same fiscal years (FY22–FY24) as the RHP and adds nothing further back, so it was not used.
* Exchange results filings Q2FY25–Q1FY27 (acmesolar.in, "Quarterly Results"). FY24 quarters come from the comparative columns of these filings; Q1FY24 from the RHP.
* Annual reports FY19, FY20, FY21 are scanned images; the statement and note pages were read visually (page numbers in the cell notes: AR19 p.121-124, 144, 146; AR20 p.39-41, 52, 62, 64; AR21 p.110-112, 122, 132, 134). The FY2017-18 annual report is not published on the company site, so FY18 is taken from the FY19 comparatives.

## Restatement flags
* **FY22–FY24 (existing columns)** agree to the RHP *restated* consolidated financials (e.g. FY22 revenue 14,879.02), not to the as-originally-reported annual reports. Left as found.
* **FY20**: AR 2020-21 regrouped the FY20 comparatives (other income 820.31 vs 776.58 as reported; D&A 7,044.48 vs 7,000.80; total assets 154,851.88 vs 154,341.28; PBT/PAT unchanged). The as-originally-reported AR 2019-20 figures are used.
* **FY19**: AR 2019-20 comparatives are identical to AR 2018-19 as reported.
* **FY18**: only available as FY19 comparatives (no restatement visible).
* **FY24 quarterly operating metrics**: the company discloses FY24 only on a like-for-like basis (369 MW divested in Jan-24 excluded) and only cumulatively (H1/9M/FY), so FY24 quarters in block C are left as dashes. FY24 net debt and ratio comparatives in block F/G are on that adjusted basis (noted).
* Later presentations restate earlier quarters' ratios on a TTM basis (e.g. Q2FY25 cash RoE 15.5% annualised at the time vs 13.1% TTM later); the originally reported figure is used.

## Gaps (shown as "–")
* Q1FY24 standalone P&L; Q1FY24 total expenses/EBITDA on the filing basis (RHP shows total expense including finance cost and D&A).
* Sep-23 and Dec-23 quarter-end capacity; FY24 quarterly generation/CUF/availability.
* BESS financials before Q1FY27 (only Q4FY26 RTE 88–90% exists); cash EPS (never disclosed); BVPS after Jun-24 (RHP NAV only); weighted average tariff before Q3FY25; weighted average cost of debt before Q3FY26.
* Gross debt and cash for Dec-25, Mar-26, Jun-26 (presentations show net debt only).

## Deviations from the stated conventions, flagged
* Percentages use `0%;(0%);"–"` as instructed, which displays CUF 25.6% as 26%; the underlying values keep one decimal.
* Per-share figures, tariffs (INR/kWh) and multiples (x) use the workbook's existing `0.00;(0.00);"–"` format rather than the integer format, because an EPS of 2.16 or a 4.4x multiple would otherwise display as 2 and 4.
* Block F figures are the presentation numbers in INR Cr converted to INR mn (×10), because the company's asset-base/net-debt definitions are only published that way; statutory balance sheets in INR mn exist only for Mar/Jun/Sep dates and are cited in the note.
* Shares outstanding = paid-up capital ÷ INR 2 face value (a unit conversion, not a derivation); FY18–FY21 shares shown on the current INR 2 basis (522.21 mn).
* Cash PAT in blocks A/B is the company's own definition (PAT + D&A ∓ exceptional items) applied to the reported lines.
* "Not disclosed" cells carry a zero so they render as the en-dash required by the format; the block notes list which items are undisclosed.
* The workbook is set to recalculate on open (`fullCalcOnLoad`) because new formula cells were written without cached values.
