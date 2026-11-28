# Pasupati Acrylon Ltd (BSE 500456 | NSE PASUPTAC) - status

## Files (versions)
- PASUPTAC_Model_v1.xlsx - historicals FY17A-FY26A + 12 quarters (Q3FY24-Q2FY27), segments, sources. Recalc: 0 errors. 28-Nov-2026.
- PASUPTAC_Model_v2.xlsx - adds Drivers (selector C3: 1 bear, 2 base, 3 bull, 4 floor memo), TAM, Unit_Economics, Valuations; FY27E-FY30E. Recalc: 0 errors; all checks 0 in floor/bear/base/bull; selector left at 2.
- Pasupati_Acrylon_Note_v1.docx - 7 pages. 28-Nov-2026.
- exhibits/exhibit1_fibre_and_segments.png
- scripts/: fetch_docs.sh, list_*.txt, price_csv.py, pg.py, fp.py, pal_data.py, pal_build_model.py, pal_run.py, pal_exhibit.py, pal_note_v1.py, model_map.json, run_results_28Nov2026.json
- Pack: scratchpad packs/pasupati/out/Pasupati-Acrylon-Investor-Docs.zip

## Rebuild
python3 scripts/pal_build_model.py . both && python3 scripts/pal_run.py PASUPTAC_Model_v2.xlsx scripts/model_map.json scripts/run_results_28Nov2026.json && python3 scripts/pal_exhibit.py PASUPTAC_Model_v2.xlsx exhibits && python3 scripts/pal_note_v1.py

## Decisions (dated)
- 28-Nov-2026: Business lines verified from documents: acrylic staple fibre/tow/tops (42,000 MTPA), CPP film only (10,000 MTPA; no BOPP), and a THIRD segment the brief did not mention - 150 KLPD grain ethanol distillery (COD 24/25-Mar-2025; consents for 180 KLPD). Ethanol is 32% of FY26 revenue, so it is modelled as its own engine.
- 28-Nov-2026: Promoter is Vineet Jain family (not Jindal). PICUP (UP state corporation) 5.03% is classed as promoter.
- 28-Nov-2026: Standalone basis (no subsidiaries). FY17 = Ind AS comparative in AR FY18. Revenue shown net of excise for FY17-FY18.
- 28-Nov-2026: ACN per kg is derived: ACN consumed / fibre produced; implied ACN price uses 0.889 kg ACN per kg fibre, calibrated to the two CARE ACN prices (FY21 Rs.97.47, FY22 Rs.171.57) - matches to 0.1 Rs/kg.
- 28-Nov-2026: Segment EBITDA = segment result + segment depreciation - other income allocated on revenue (segment results include other income).
- 28-Nov-2026: No management numeric guidance exists (no calls/presentations). Bull = stated capacities at target utilisation (fibre/CPP 95%, ethanol 180 KLPD, 240 KLPD from FY29 per CARE "envisaged") with today's spreads held.
- 28-Nov-2026: Floor = FY26 volumes at mid-cycle per-kg margins + only the allocated ethanol (ESY27 50,745 KL; nothing after Oct-2027).
- 28-Nov-2026: P/E 7.5x FY28E for all scenarios (Vardhman Acrylics 7.1x, Gulshan Polyols 5.8x, Cosmo First 15.5x; PAL own median 7.6x). Peer P/E from Screener - to be checked on Bloomberg.
- 28-Nov-2026: Anti-dumping duty: DGTR final findings 18-Aug-2025 recommended duty (PAL co-applicant); NOT notified by the Finance Ministry (Indian Acrylics AR FY26, Sep-2026). Treated as NOT in force in base; bull assumes today's spreads hold (duty or tight supply); bear = imports rise.
- 28-Nov-2026: Base FY28E sits 38% of the way from floor to bull on EBITDA (FY27E 33%, FY29-30E ~17-21% because bull adds an unapproved 240 KLPD). Kept: we do not price capacity no one has approved.

## Result (base, 28-Nov-2026)
CMP Rs.67.95 (27-Nov close) | Mcap Rs.606 cr | FY28E EPS Rs.10.26 | TP Rs.77 at 7.5x | +13.3% | HOLD (borderline, 1.7 pts from BUY) | Bear Rs.15 | Bull Rs.115 | Floor Rs.54 | Chance in price -23%.

## First questions the numbers raise
1. Fibre PBIT margin 18.3% in H1FY27 vs 8.9% 10-yr average: why?
2. Inventory Rs.103 cr (Mar-26) -> Rs.195 cr (Sep-26).
3. Distillery revenue H1FY27 Rs.133 cr vs Rs.171 cr H1FY26 despite 180 KLPD consents.
4. MD pay Rs.4.76 cr (+90%), commission up to 5% of profit, postal ballot to exceed Rs.5 cr; zero dividends.

## Open questions / gaps
- No investor presentations or call transcripts exist (company does not hold them).
- NSE API blocked from container (301 redirect); BSE api blocked; used company website + BSE AnnPdfOpen + Screener.
- Daily prices only for the last 12 months (Screener); weekly before that.
- CPP volumes FY18-FY19 not disclosed; fibre exports FY23-FY24 tonnes not disclosed; quarterly volumes never disclosed.
- ESY 2025-26 ethanol allocation not found; 240 KLPD plan has no board disclosure.
- Anti-dumping status after Aug-2025 to be checked on CBIC.
- Peer volumes (films) and peer multiples: to be checked on Bloomberg.
