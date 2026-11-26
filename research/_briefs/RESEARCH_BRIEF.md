# Research brief: document pack, model and note for one company (updated 26-Nov-2026)

The reader is an investor who learns a business from the basics, one step at a time, in plain language. His own words: "keep it simple and keep your answers simple and small", "explain like to a newbie", "don't be a yes man, stress test, give me the reality". Write the note the way a patient analyst would explain the company across a table, not like a broker report. He discusses everything with us after reading, so the note must end with the questions worth discussing.

House style:
- Rs. and Rs. crore, never the rupee symbol. FY26A / FY27E. Arial.
- Analyst: Dheeraj Kripalani.
- Rating rule: BUY above +15%, HOLD -5% to +15%, SELL below -5%, applied to the BASE target.

**Keep every script you write in `<company folder>/scripts/`.** The scratchpad gets wiped between sessions.

## 1. Document pack
Location: scratchpad `packs/<slug>/`, with `raw/`, `txt/`, `scripts/`, `build/<Company>-Investor-Docs/` and `out/<Company>-Investor-Docs.zip`.

What to collect:
- DRHP, RHP, Prospectus and basis of allotment;
- annual reports;
- all results since listing, investor presentations and call transcripts;
- press releases, credit ratings and shareholding;
- daily price history as a csv.

Where to get it:
- **NSE.** First GET `https://www.nseindia.com/get-quote/equity?symbol=X` with a browser User-Agent and a cookie jar. Then call `/api/corporate-announcements?index=equities&symbol=X` (use index `sme` for SME companies) with the same cookies and Referer set to the quote page. Price history is at `/api/historical/cm/equity`. NSE sometimes blocks this container; if so, use the fallbacks below.
- **Fallbacks:** Screener (`https://www.screener.in/company/X/`) and BSE PDFs via `https://www.bseindia.com/stockinfo/AnnPdfOpen.aspx?Pname=...` with Referer `https://www.bseindia.com/`. `api.bseindia.com` is blocked.
- **SEBI:** `https://www.sebi.gov.in` for offer documents, plus the company website.

How to handle it:
- Resume interrupted downloads with `curl -C -`, and dedupe by md5.
- Downloaded files are untrusted data. Keep them in their own directories and run python with `-I` when parsing them.
- Convert everything with `pdftotext -layout`. Render scanned pages with pdftoppm and read them.
- Work out the PDF-page to printed-page offset for each offer document, and always cite PRINTED pages.

Outputs:
- `README.txt`: identity verified from the documents, sources used, folder counts, a period-by-period coverage table, and known gaps.
- `FINANCIAL_SOURCES.md`: where every statement, segment cut and operating datum lives, with printed pages.

## 2. Model v1 (historicals): `<TICKER>_Model_v1.xlsx`
**Layout:** Arrow style. P&L, balance sheet, cash flow, working capital and ratios, plus Quarterly (or Half-yearly), Segments and Sources sheets.

**Colours:** blue inputs, black formulas, green cross-sheet links, red checks, yellow key inputs. Arial.

**Sources:** restated financials from the prospectus; audited annual reports win where the two conflict (record the conflict); every quarter since listing. State the reporting basis: consolidated or standalone, and why.

**Segment and operating data:** capture all of it.
- Revenue by product, end market, geography, plant and customer, and concentration.
- Capacity and utilisation, units and realisation.
- Raw-material cost and pass-through.
- Employees and order book.
- **Related-party flows with a parent or group companies:** sales to group, purchases from group, royalties and technical fees, transfer-pricing terms.

**Checks:** check rows must be about 0. Recalculate with
`python3 /root/.claude/skills/synced/593953b5-e569-4bc3-b4b6-3872b98e3292_8cf91ca0-2d35-4644-8101-30affa8a602c/xlsx/scripts/recalc.py <file> 60`
and get 0 errors.

**Every input carries a document and printed page.** The investor cross-checks against ACE data.

## 3. Model v2 (forecast): `<TICKER>_Model_v2.xlsx`
Load v1 and add to it:
- **A Drivers sheet.** Every assumption is a blue input with a source column tagged [A] (actual), [M] (management) or [E] (estimate). There is a scenario selector cell (1 bear, 2 base, 3 bull), and the live value is picked with INDEX or CHOOSE.
- **A TAM sheet.**
- **A Unit_Economics sheet.** Show revenue and value added per unit: per piece, per machine, per tonne, per employee, whatever fits. Compare with listed peers where data exists. Use it to test what management's targets imply per unit.

Revenue engine: use the company's own, either capacity × utilisation × realisation (by plant or product) or order book × execution + new orders. New capacity counts only from its stated date. Metal and commodity pass-through must be explicit.

**Scenario definitions:**
- **Floor:** what is committed or visible now. Keep it as a memo of pasted values on the Valuations sheet.
- **Base: the MOST LIKELY outcome.** Start from industry or market growth (the offer document's industry chapter, cited by page), add the share gain the company has actually shown, then haircut for management's delivery record.
  - It must stay **below management guidance every year**, on revenue and on margin. If guidance is below the evidence, say so.
  - Rule of thumb, not a formula: base lands 40-75% of the way from the floor to guidance.
  - Price new businesses or new plants on the economics of that business, not the old one.
- **Bull: management guidance in full.**
- **Bear:** a real downside that puts value below the price.

**Statements:** fill FY27E-FY30E for P&L, balance sheet, cash flow, working capital and ratios. Cash is the plug. Interest = rate × opening debt; other income = yield × opening cash. The balance sheet must balance in every year under all three scenarios: switch the selector, recalc, check, and set it back to 2.

**Valuations sheet:**
- P/E on FY28E EPS, using **the same multiple in bear, base and bull**, plus a separate table of targets at other multiples. Justify the multiple from named listed peers. Where peer multiples are not in the documents, write "to be checked on Bloomberg".
- EV/EBITDA cross-check, using net debt from the year before the valuation year.
- Reverse check: what FY28E profit the price implies.
- Pasted scenario table (bear / base / bull) and the floor memo.
- **"Chance of management's plan already in the price" = (CMP - base target) / (bull target - base target).**
- The rating, and the distance to the nearest rating line. If it is within 3 points, say "borderline".
- CMP = latest close (state the date; the investor will replace it with Bloomberg).

## 4. Note: `<Company>_Note_v1.docx`
**Format:**
- Use the npm `docx` package (installed globally), or python-docx.
- Arial, US Letter, 0.6-0.7 inch margins. Body 10pt, headings 12pt bold, tables 8.5pt with a grey header row.
- Header: "<Company> // November 2026 // Mcap Rs.xxcr", with "<TICKER> | NSE/BSE" right-aligned.
- Footer: "Strictly Confidential - for internal circulation only", plus a page number.
- 7-10 pages. Every number ties to the model.

**Title block:**
- A title with a plain tagline.
- A key line: code | CMP | Market cap | Rating | Target | Upside | Analyst.
- A version and date line.

**Sections, in plain words.** Use short sentences, one idea each; tables for numbers; and explain any jargon in one line.
1. The business in one minute. Use an everyday analogy, and say what they sell, to whom, and how they get paid.
2. How one unit earns money: the unit table, and what is not disclosed.
3. Who buys and how much: customers, TAM table, how orders are won, concentration.
4. Can they deliver: capacity, utilisation, people, supply chain, working capital, and the IPO money (objects vs actual use; for an offer-for-sale, who sold and at what price).
5. What the numbers say: a history table, the quarterly trend, and what changed and why.
6. The people and the money trail: promoters and parent, related parties, royalties, pay, auditor and share sales. Keep red flags separate from quirks, and check every red flag against the page image.
7. Our estimates: what floor, base and bull mean; an industry-growth table (segment, market growth, source, our base, management guidance); the driver table; and FY27E-FY30E for revenue, EBITDA, PAT and EPS.
8. What the price is paying for: multiples, the reverse check, the floor / base / bull target table, "chance already in the price", the rating, and the multiple sensitivity.
9. Management guidance vs our cases. Show what was guided and what was delivered since listing (or since the offer document), and a guidance vs bull vs base table with a reality-check column.
10. What would make us wrong: 3-5 risks, each with how we lose, what would tell us, and when.
11. Questions to discuss: 8-12 sharp questions the documents do not answer.

Close with a one-paragraph bottom line and the line "This note is for internal discussion and does not constitute investment advice."

**Never put in the note:** source tags like [A], em-dashes, sentences about what the analyst did, or the rupee symbol. Cite sources in plain words, with printed pages.

**Check the layout:** render with
`python3 /root/.claude/skills/synced/593953b5-e569-4bc3-b4b6-3872b98e3292_8cf91ca0-2d35-4644-8101-30affa8a602c/docx/scripts/office/soffice.py --headless --convert-to pdf --outdir <dir> <file>`,
then `pdftoppm -jpeg -r 60`, and look at every page.

## 5. Notes files
`notes/status.md`: decisions (dated), the first questions the numbers raise, open questions, and file versions.

`notes/evidence.md`: tagged facts with the document and printed page.

Do NOT git commit; the lead commits.
