---
name: equity-pitch
description: Produce an institutional-quality equity research note (Word doc) plus a matching pitch deck (PPTX) on a listed company, in the analyst's fixed 15-section format - researching the company website for annual reports, earnings call transcripts, and investor presentations first. Use whenever the user asks for a pitch, research note, initiating-coverage note, stock analysis, company analysis, investment thesis, or says "analyse <company>" or "make a pitch on <company>" for any listed company, even if they don't say "research note" or name a format.
argument-hint: [company name / ticker] [CMP]
---

# Equity Research Pitch

Write a buy-side research note the way an experienced Indian small/mid-cap analyst
would: every claim carries a number and a source, negatives are stated plainly, and
the rating falls out of the valuation math rather than the narrative. The user is an
equity research analyst - the output is their work product, so accuracy and
verifiability matter more than polish.

## Step 0 - Gather inputs (ask before researching)

Confirm with the user before starting deep work:

1. **Company + ticker + CMP.** If CMP (current market price) is not given, fetch the
   latest close from NSE/BSE and confirm it with the user - the title block, market
   cap, implied multiples, and upside all depend on it.
2. **Financial model.** Ask the user for their financial model (usually xlsx). If
   they provide one, use its estimates exactly - do not silently override them.
   Only if they explicitly say "proceed without a model", build your own estimates
   (3-4 forward years) with conservative, clearly stated assumptions, labelled
   "analyst estimates" in every table footnote.

Do not ask about output format or rating - those are fixed: always produce **both**
the .docx note and the .pptx deck, and **derive the Rating and Target Price yourself**
from the valuation scenarios (the user edits afterwards).

## Step 1 - Research

Primary sources first, in this order:

1. **Company website - Investor Relations section**: annual reports for the *full
   listed history* (the Business Cycles section needs the early years, not just the
   recent ones), earnings call transcripts for the last 8-12 quarters, latest
   investor presentation(s), shareholding pattern.
   If the company holds no earnings calls, record that explicitly - it goes in the
   Corporate Governance table as a finding, not a gap in your work.
2. **Exchange filings** (BSE/NSE): outcomes of board meetings, credit ratings,
   corporate actions the ARs haven't caught up with.
3. **Aggregators** (screener.in etc.) only to cross-check, never as the sole source
   for a number that appears in the note.
4. **Demand-side context** from the actual regulator or industry body (e.g. RBI
   annual report for banknote printing spend, ministry data for sector volumes).
   The thesis is only as strong as the demand numbers behind it.

Cross-check every figure against audited financials. Cite sources inline for key
claims ("per FY25 AR", "RBI FY26 AR"). Where segments changed names or the company
restated, say so rather than splicing series silently.

Use parallel subagents for the document sweep where available (one on ARs, one on
transcripts/presentations, one on price history and shareholding) - the reading load
is large and independent.

## Step 2 - Write the note

Follow the section-by-section specification in
[references/format.md](references/format.md) - read it in full before writing.
It defines all 16 sections (title block through disclaimer), the required tables,
and worked examples of the expected voice taken from a real note.

Style rules that apply everywhere:

- Rs. crore throughout: `Rs.243cr`, `36.4% margin`, `9.1x FY28E EV/EBITDA`.
- Every strong claim carries a number and a source. Delete filler adjectives.
- Say the negative things (thin board, no concalls, capital sinks, unverifiable
  concentration). The governance and risk sections are where credibility is earned.
- Year-labelling: `FY26A` for actuals, `FY27E` for estimates, and footnote whose
  estimates they are.
- The tagline in the title is thematic, not promotional ("The Invisible Thread",
  not "A Great Buying Opportunity").

## Step 3 - Produce both deliverables

Always both, every time:

1. **Word document (.docx)** - the full note. Use the docx skill's guidance
   (docx-js for creation). Real tables with `WidthType.DXA` widths, styled
   headings, prominent single-line title block, footer disclaimer.
2. **Pitch deck (.pptx)** - built from the same content using the pptx skill.
   Slide mapping and per-slide content limits are in
   [references/format.md](references/format.md) under "Pitch deck mapping".

Render both to PDF/images and visually inspect before delivering - broken tables
and overflowing slides are the most common failure. Deliver both files to the user.

## Fallback

If a step fails (site unreachable, document behind a viewer, model file corrupt),
say exactly what you could not get and what you substituted - never fill a gap
with an invented number. [references/standalone-prompt.md](references/standalone-prompt.md)
contains the self-contained prompt version of this workflow; keep it in sync if
the format ever changes.
