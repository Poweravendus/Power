# JSW Energy — institutional research note, July 2026

Produced by applying the *Equity Research Note Master Prompt v1.2* (26 sections)
to JSW Energy Limited, using the attached financial model (`JSW_Energy_2.xlsx`)
exactly as given for all estimates.

## Deliverables

| File | What it is |
|---|---|
| `JSW_Energy_Equity_Research_Note_July2026.docx` | The note — 18 pages, 26 sections, 7 embedded exhibits |
| `JSW_Energy_Pitch_Deck_July2026.pptx` | 18-slide companion deck, same content, one idea per slide |
| `*.pdf` | Rendered copies for review without Office |
| `exhibits/` | The seven exhibit PNGs |
| `scripts/` | Reproducible generation: data → charts → documents |

## The call

**HOLD · CMP Rs.561 (17 Jul 2026) · Base TP Rs.625 (+11.4%) · Mkt cap Rs.98,584cr**

Base target = 11.9x FY28E EV/EBITDA less FY27E-end net debt on 1,833mn post-QIP
shares — the same construction the model carries. Bear Rs.286 (8.0x), bull
Rs.839 (11.9x FY29E), mean-reversion to the 16-year multiple average Rs.373.

The build is real — 13,454MW at FY26A to 25,905MW by FY30E, EBITDA Rs.10,064cr
to Rs.23,536cr, 92% of the growth from renewables. The equity is a thin, geared
claim on it: net debt of Rs.75,038cr at FY27E-end is 4.7x FY28E EBITDA, so the
equity is 29% of enterprise value and every 1.0x of EV/EBITDA is Rs.87 per
share. An asset-based SOTP of Rs.510 and a forward-multiple target of Rs.625
bracket the current price.

## Reproducing

```bash
pip install openpyxl python-docx python-pptx matplotlib
cd scripts
python charts.py       # writes the seven exhibit PNGs
python build_docx.py   # writes the note
python build_pptx.py   # writes the deck
```

`jswdata.py` holds every figure lifted from the model, in Rs. crore, with the
source sheet noted per block. Change a number there and both documents rebuild
consistently.

## Disclosed gaps

Per the prompt's rule against filling a gap with an estimate presented as fact,
the following could not be verified and are stated as unverified in place:
contingent liabilities and litigation, auditor opinion and key audit matters,
board composition, promoter pledge, related-party transaction quantum,
entity-level PAT, top-5/top-10 customer concentration, plant-level capex for the
renewable pipeline, a monthly closing-price series, and like-for-like peer
growth/margin/ROCE. Peer multiples are trailing secondary-source figures, not
reconciled to audited accounts.

---

*Strictly Confidential — for internal circulation only. This note is for
informational purposes and does not constitute investment advice.*
