# IEX shareholding history database

Full historical shareholding database for **Indian Energy Exchange Ltd (NSE: IEX, BSE: 540750)**,
built from the company's own SEBI Regulation 31 shareholding-pattern filings (XBRL), as disseminated by NSE.

Coverage: every filing from **30-Sep-2021 to 30-Sep-2026** (21 quarter-ends plus the 08-Dec-2021 post-bonus filing).

## Buckets

| bucket | definition |
|---|---|
| `promoter` | Promoter & promoter group (IEX has none, always 0) |
| `fii` | Foreign institutions: FPI category I & II, foreign VC, overseas depositories, overseas corporate bodies |
| `dii` | Domestic institutions: mutual funds, AIFs, banks, insurance companies, NBFCs, pension funds, other domestic institutions |
| `government` | Central / state government and government-promoted companies |
| `kmp` | Key Managerial Personnel (aggregate, as SEBI requires; disclosed only from the Sep-2022 quarter) |
| `public` | Non-institutional holders excluding KMP: resident individuals, NRIs, bodies corporate (incl. Dalmia group), HUFs, trusts, clearing members, IEPF, directors & relatives |
| `others` | Non-promoter non-public: employee benefit trust (DR holders are nil) |

The seven buckets always sum to the filing's total share count; the build asserts this for every filing.

## Outputs (`output/`)

| file | content |
|---|---|
| `iex_shareholding_summary.csv` | one row per filing: shares, % of total and number of holders for each bucket |
| `iex_shareholding_categories_long.csv` | every SEBI category / sub-category line in every filing (long format) |
| `iex_named_holders.csv` | named holders above 1 % and other detail-table rows per filing (LIC, SBI MF, MIT, Dalmia entities, ...) |
| `iex_insider_disclosures.csv` | PIT Regulation 7 insider-trading disclosures relayed by NSE (named employees / designated persons, ESOP allotments, Dalmia sales) |
| `iex_filings.csv` | filing metadata: NSE broadcast date, SEBI taxonomy version, source XBRL URL |
| `iex_shareholding.sqlite` | all of the above as tables (`summary`, `categories`, `named_holders`, `insider_disclosures`, `filings`) plus a `summary_pct` view |
| `iex_shareholding.xlsx` | same data as an Excel workbook, one sheet per table plus `Notes` |

## Rebuild / refresh

```bash
python3 build_database.py            # rebuild from cached filings in data/
python3 build_database.py --refresh  # pull any new quarterly filing + insider data from NSE, then rebuild
```

Raw XBRL files are kept in `data/raw_xbrl/` so the database can be rebuilt offline.

## Caveats

- Percentages are recomputed from share counts. The as-reported percentage field switched from percent to fraction when SEBI's taxonomy changed in late 2025, so it is unreliable across time.
- KMP is an aggregate line in SEBI filings; there are no names. Before the Sep-2022 quarter the category did not exist, so `kmp` is blank and any KMP holding sits inside `public`.
- For pre-Sep-2022 filings, NBFCs are moved from non-institutions to `dii` and Overseas Corporate Bodies from "Other institutions" to `fii`, to keep the buckets consistent with the later SEBI format.
- Named-holder rows for pre-Sep-2022 filings include sub-category header rows (e.g. "Bodies Corporate") alongside named entities, exactly as filed.
- Insider disclosures record transactions, not a point-in-time list of every KMP's holding. Named KMP holdings as of a year end are in the annual report's corporate governance section, which is not part of this dataset.
