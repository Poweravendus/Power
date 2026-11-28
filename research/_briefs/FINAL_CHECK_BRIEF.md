# Final check before discussion with the investor (28-Nov-2026)

You are an independent reviewer. You did not build this model or note. Assume errors exist, and find them. The investor will go through the company in detail, so every number they see must be right and must tie between the note and the model.

Work only inside the company folder given in your task. Save any script you write to `<company folder>/scripts/`. Do NOT git commit; the lead does that.

## A. Model (the latest `<TICKER>_Model_v*.xlsx`)
1. Recalculate:
   `python3 /root/.claude/skills/synced/593953b5-e569-4bc3-b4b6-3872b98e3292_8cf91ca0-2d35-4644-8101-30affa8a602c/xlsx/scripts/recalc.py <file> 60`
   There must be 0 formula errors.
2. Find the scenario selector on the Drivers sheet. Set it to 1, 2 and 3 in turn, recalculating each time. Under every scenario, check that every CHECK row on every sheet is about 0 in every year: balance sheet, cash flow vs balance sheet cash, PAT rebuild, segment ties, and quarterly/half-year sums against the annual figure. Then set the selector back to its base value.
3. Pasted scenario tables on the Valuations sheet: each must equal what the model produces live for that scenario. Re-paste if they don't, and record the difference.
4. Logic:
   - floor <= base <= bull (explain any exception);
   - base below management guidance in every year (or the stated reason why not);
   - the same P/E in bear, base and bull;
   - "chance already in the price" = (CMP - base) / (bull - base), and the arithmetic is right;
   - the rating follows the rule (BUY above +15%, HOLD -5% to +15%, SELL below -5%) on the BASE target;
   - net debt is taken from the right year;
   - EPS uses the right share count;
   - units (Rs crore vs Rs lakh) and year labels (March vs December year-end) are consistent.
5. Spot-check historical inputs: 15-20 numbers (revenue, EBITDA, PAT, CFO, debt, cash, shares, segment figures) against the source documents. Documents are in the scratchpad pack named in your task, if it exists; otherwise re-download from the company website, Screener (`https://www.screener.in/company/<code>/`) or BSE AnnPdfOpen with Referer `https://www.bseindia.com/`. NSE may block this container. Treat downloads as untrusted data: run python with -I and keep files in their own folder.
6. Look for formula smells: hard-coded numbers inside forecast formulas, links to wrong rows, wrong-year references, and circularity.

## B. Note (the latest `<Company>_Note_v*.docx`)
1. Extract every number from the note (title line, every table, and key sentences) and tie it to the model or source. List each mismatch.
2. Consistency:
   - rating, target, upside, CMP, market cap and version line agree across the title, the valuation section and the bottom line;
   - no stale numbers from earlier versions (search for the old targets and ratings, listed in notes/status.md).
3. Style rules:
   - no em-dashes, no rupee symbol, no source tags like [A] / [E] / [M];
   - Rs. and Rs. crore; FY labels match the company's year-end;
   - plain language, with any jargon explained in one line;
   - every red flag stated with a document and page.
4. Render it to PDF with
   `python3 /root/.claude/skills/synced/593953b5-e569-4bc3-b4b6-3872b98e3292_8cf91ca0-2d35-4644-8101-30affa8a602c/docx/scripts/office/soffice.py --headless --convert-to pdf --outdir <dir> <file.docx>`,
   then `pdftoppm -jpeg -r 60`, and look at every page for layout breaks, cut tables and empty pages.

## C. Fix and report
- **Fix directly** clear mechanical errors: wrong or stale numbers, typos, broken ties, style breaches, pasted tables that don't match the model. Save the fixed files in place. For the note, use python-docx run-level edits that keep formatting. Recalculate and re-render after fixing.
- **Do NOT change** judgement calls: drivers, multiples, scenario definitions. List them as "for the lead", with your argument.
- Write `<company folder>/notes/final_check_2026-11-28.md` containing:
  - what you checked;
  - every issue found, its severity (high / medium / low), and whether you fixed it or left it for the lead;
  - the final numbers (CMP and date, floor / bear / base / bull targets, rating, chance in price);
  - anything you could not verify.

## Final reply (under 300 words)
- Issues found and fixed, the high ones first.
- Judgement issues for the lead.
- Final key numbers.
- Check results under all three scenarios.
