# JSW Energy — institutional research note, July 2026

Produced by applying the *Equity Research Note Master Prompt v1.2* (26 sections)
to JSW Energy Limited, using the attached financial model (`JSW_Energy_2.xlsx`)
exactly as given for all estimates, verified against primary sources.

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

The build is real — 13.45GW at FY26A to 25,905MW by FY30E, EBITDA Rs.10,064cr to
Rs.23,536cr, 92% of the growth from renewables, 14GW under construction fully
tied under PPAs and Rs.24,184cr of capex contractually committed. The equity is a
thin, geared claim on it: net debt of Rs.75,038cr at FY27E-end is 4.7x FY28E
EBITDA, so the equity is 29% of enterprise value and every 1.0x of EV/EBITDA is
Rs.87 per share. An asset-based SOTP of Rs.510 and a forward-multiple target of
Rs.625 bracket the current price.

## Primary sources used

- **FY26 Integrated Annual Report**, consolidated financial statements — audited
  by Deloitte Haskins & Sells LLP, unmodified opinion, one key audit matter
  (tariff disputes with customers). Source for contingent liabilities
  (Rs.2,519.61cr of claims, ~Rs.4,506cr in aggregate, ~15% of net worth), capital
  commitments (Rs.24,184cr), related-party transactions (~Rs.804cr of power
  sales, 4.3% of revenue), customer concentration (one customer at 10.4% of
  revenue), the JSW Steel holding (7.00cr shares at Rs.7,861.80cr), and the
  Supreme Court's 18% Himachal free-power ruling.
- **Q4FY26 earnings call transcript**, 11 May 2026 — source for FY27 guidance
  (~3GW, ~Rs.20,000cr capex), the Rs.75 lakh/MW steady-state renewable EBITDA
  benchmark, the KSK Rs.2,700cr steady state, the KSK 26% call option, the
  deferred-tax explanation, cost of debt (8.36%), debtor days (62), curtailment
  (Rs.50cr in FY26A) and the 2030 leverage target (~5.0–5.5x).
- **Q1FY27 results and call**, 22 July 2026 — the completed Rs.10,150cr capital
  raise and 4.95x post-raise leverage.

## What the primary sources changed

Three corrections to what the model alone would have produced: Ind-Barath is not
an uncontracted merchant plant (400MW on a 25-year PPA at Rs.5.78/unit plus 115MW
to Assam); the CFO is Chandrasekaran Prabhakaran, not Pritesh Vinay; and the
collapse in modelled minority interest is explained by a served call option on
KSK Mahanadi's 26%, not an unexplained assumption. Three material additions: the
Supreme Court free-power ruling (permanent, ~287 million units a year, absent
from the forecast), the completed funding programme, and management's own
Rs.0.75cr/MW renewable benchmark against the model's implied Rs.1.02cr/MW.

## Reproducing

```bash
pip install openpyxl python-docx python-pptx matplotlib
cd scripts
python charts.py       # writes the seven exhibit PNGs
python build_docx.py   # writes the note
python build_pptx.py   # writes the deck
```

`jswdata.py` holds every figure lifted from the model, in Rs. crore, with the
source sheet noted per block.

## Remaining disclosed gaps

Promoter-level share pledge (disclosed in the quarterly shareholding filing, not
the annual report); the quantum of the KSK minority consideration (management
expects a number by end-Q2FY27); and like-for-like peer growth, margin and ROCE —
the peer multiples in Section 20 are trailing secondary-source figures, not
reconciled to audited accounts.

---

*Strictly Confidential — for internal circulation only. This note is for
informational purposes and does not constitute investment advice.*
