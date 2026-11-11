# Shankesh Jewellers (NSE: SHANKESH, BSE: 544882) - research status

**Updated:** 11-Nov-2026 (base reset). **Stage:** 1 (Historicals) built; waiting for the investor's ACE dump to cross-check, then the step-by-step business discussion.

## Where we are
1. Document pack built (25 documents): scratchpad packs/shankesh/out/Shankesh-Jewellers-Investor-Docs.zip (sent to investor).
2. Model v1: FY22 (IGAAP memo) + FY23-FY26 restated, quarterly 1QFY26-2QFY27 (3QFY26 derived), half-year BS/CF, segment sheet (karat, customer type, state, concentration, volume, customers, karigars, returns, purchases), "what the price implies".
3. No management numeric guidance exists (call 1QFY27 deflected on margins); forecasts deferred to discussion.

## Decisions
- 8-Nov-2026: Standalone = whole entity (no subsidiaries, RHP p.228, 258).
- 8-Nov-2026: Restated figures used over statutory; quarter figures taken from page images, not the filer's text layer.
- 8-Nov-2026: FY22 kept as a memo column only (IGAAP; labour charges in other expenses).

## First questions the numbers raise (for the discussion)
- FY26 revenue +16% with gold processed -28% (1,936 kg to 1,397 kg): growth was gold price, volume fell. Revenue per gram Rs.7,188 to Rs.11,571 (+61%).
- Gross margin 5.6% to 11.1% in FY26 on unhedged inventory of Rs.240 cr while gold rose ~44%: how much of FY26 profit is inventory gain? At FY25's gross margin, FY26 PAT would be ~Rs.40 cr, not Rs.107 cr.
- Cash: cumulative FY23-FY26 PAT Rs.170 cr vs CFO Rs.(29) cr and FCF Rs.(46) cr; 1HFY27 CFO Rs.(132) cr as receivables doubled to Rs.260 cr.
- Directors' (promoters') pay Rs.12.2 cr in FY26 = 81% of employee cost.
- Hedging: management says no hedge; FY26 BS has Rs.15.5 cr margin with a bullion-hedging broker.
- Non-corporate customers fell 6% in FY26; new customers 166 to 84; karigar attrition 3% to 17%; returns 5.2% to 7.2% of revenue.

## v2 decisions (8-Nov-2026)
- Gold price series: CareEdge Chart 26 (CMIE) quarterly readings taken from the vector chart (CareEdge PDF p.35); Sep-26 level = placeholder Rs.1,52,600 (replace from Bloomberg/IBJA).
- Margin split: inventory gain = gold move x opening inventory; residual making margin 2.6-3.1% FY23-FY26; base karat margins 22K 2.5% / 18K 5.0% / job work 30% reproduce each year within Rs.3 cr.
- 1HFY27 gross profit is Rs.77 cr above the making margin with gold roughly flat: kept in FY27E as booked, flagged as unexplained.
- Valuation: 12x FY28E EPS (peers Shanti Gold 10.0x, Sky Gold 34.9x per RHP p.125), EV/EBITDA 8x cross-check.

## Base reset (11-Nov-2026): "committed only" -> "most likely"
- **Old base (now the floor memo, Valuations rows 82-90):** revenue FY27E-FY30E Rs.2,148 / 2,321 / 2,497 / 2,692 cr; EBITDA Rs.124 / 51 / 56 / 61 cr; PAT Rs.86 / 36 / 42 / 45 cr; EPS Rs.5.85 / 2.48 / 2.83 / 3.08; target Rs.29.7 (12x FY28E), -68%, SELL.
- **New base (most likely):** identical numbers. The industry build (Drivers block 8, rows 115-183) lands on the old drivers: kg +5% FY27 (1HFY27 ~+3% derived; 2H needs ~+7%) and +8% a year FY28-FY30; making margin 22K 2.5% / 18K 5.0% (FY23-FY26 history); gold flat. Target Rs.30, -68%, SELL; HOLD line (-5%) is 63 pp away (needs Rs.87, FY28E EPS Rs.7.28 = about the bull).
- **Industry numbers used:** India jewellery tonnes 610.9 CY21 / 600.6 CY22 / 563.4 CY24 / 430.5 CY25 (WGC via CareEdge, Prospectus p.158); tonnes fall ~0.5% per 1% gold rise (CY25 -24% on +44%, p.155; Jul-Sep 2026 -20% on +45%, WGC Q3 2026) -> price-free market trend 4.2% (CY21-CY24) to 5.6% (CY22-CY24). Organised wholesale makers 15.4% vs total jewellery 11.4% CAGR CY25-CY30P (p.175, p.155) -> 3.6% a year share gain; wholesale market 13.1% (p.171). Shankesh share gain vs tonnes 1.8% a year FY23-FY26, ~6% to Sep-26 (1HFY27 kg ~+3% vs market -18%, WGC). Range 6-12%; 40% point (poor plan record) = 8.3% -> 8%.
- **Guidance ceiling:** only the IPO working-capital plan, FY27 revenue ~Rs.2,100 cr (Prospectus p.118). Base is 2% above it: guidance below the evidence (plan set before gold's rise; needs only ~1,434 kg, +3%). No guidance after FY27 (call p.10); reference ceiling = plan grown at 13.1% (Rs.2,375 / 2,686 / 3,038 cr), base 2-11% below. Delivery record: DRHP FY26 plan Rs.1,591 cr met in rupees only via gold; kg -28%; stock/credit days 54/28 vs 45/20 planned.
- **Bull** (Rs.90, -2%) is a gold-price case (+10% a year, 4%/7% making margin, kg +10-15%), not management guidance; unchanged. Chance of the plan already in the price = (91.95 - 29.7) / (90.4 - 29.7) = 103%. Bear Rs.9 unchanged. Same 12x P/E in all cases; peer multiples still pending from Bloomberg.
- **Memos:** base drivers with the bull gold path (+10% a year) = Rs.54 (-42%); kg +12% a year (top of range) = Rs.31.
- Checks ~0 under bear, base and bull (BS, CF, equity, segment, quarterly ties; max 0.002 rounding); 0 formula errors; selector at 2.
- Scripts: scratchpad scripts/update_shankesh_base.py (one-off, already applied), run_scen_shankesh_v2.py (in place), dump_shankesh_note_v2.py, build_note_shankesh_v2.js.

## Open questions
- Gold price series (FY23-1HFY27) to split price vs volume vs inventory gain; KPI definition of "gold processed".
- Credit terms with corporate chains; why receivable days rose to ~49 in 1HFY27.
- What the CWIP / new corporate office cost (Rs.12.5 cr) and its ownership.
- Use of IPO proceeds vs plan (Rs.274 cr fresh issue).

## File versions
- Model: SHANKESH_Model_v1.xlsx (8-Nov-2026); SHANKESH_Model_v2.xlsx (8-Nov-2026: Drivers with bear/base/bull selector, TAM, FY27E-FY30E, valuation)
- Note: Shankesh_Jewellers_Note_v1.docx (8-Nov-2026): SELL, target Rs.30 (12x FY28E EPS Rs.2.48); bear Rs.9, bull Rs.90 vs CMP Rs.91.95
- Note: Shankesh_Jewellers_Note_v2.docx (11-Nov-2026): base reset to most likely; SELL, target Rs.30 unchanged; floor Rs.30; bull Rs.90; chance in price 103%
- Model v2 updated in place 11-Nov-2026: floor memo + reset block (Valuations rows 82-107), industry block 8 (Drivers rows 115-183)
- Evidence: notes/evidence.md
