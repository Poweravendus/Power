**Subject: POWERGRID TBCB model — 17 SPVs were double-counted; corrected**

Hi,

Flagging a material error we found in the POWERGRID TBCB model, and what we've changed.

**What happened**

The MCA sanctioned two schemes of amalgamation by orders dated **27 January 2026**, appointed date **1 April 2024**, effective **1 March 2026**:

- **12 SPVs merged into POWERGRID Khavda II-C** — Khavda II-B, Khavda RE, KPS2, KPS3, ERWR, Raipur Pool Dhamtari, Dharamjaigarh, Bhadla Sikar, Ananthpuram Kurnool, Koppal Gadag, Neemrana Bareilly, Bidar
- **5 SPVs merged into POWERGRID Vataman** — Bhadla III, Beawar Dausa, Ramgarh II, Bikaner Neemrana, Sikar Khetri

**The error**

Our model carried all 17 transferors as separate forecast blocks *alongside* the two transferees — whose FY26 balance sheets had already been restated as the merged entities. So Khavda II-C was running interest on 13 SPVs' debt against 1 SPV's tariff. Its PAT turned negative from FY27 and its IRR was meaningless. The five transferors into Vataman have no FY26 accounts at all and never will, so that block was heading for the same fault at the next update.

Two related problems surfaced:

- Khavda II-C's project cost of 96,628 was a plug — it equalled the merged FY26 PPE + CWIP. Its CERC-adopted tariff of Rs 2.82bn implied a 2.9% annuity, which is not a real bid. Replaced with the CEA estimate of 28,104.
- Depreciation and O&M were charged on full project cost rather than gross block, so assets still under construction were being depreciated.

**What we changed**

- Blanked the 17 transferor blocks from FY24 (the appointed date), retaining name, project cost, tariff and COD as reference, with notes on TBCB, TBCBsum, Subsidaries and Sheet1
- Restated FY24–FY26 for both transferees to the filed merged accounts — every line ties (Khavda II-C FY26: revenue 3,087, interest 2,043, PAT 526, CWIP 78,622, debt 129,887, equity 29,513)
- Khavda II-C: project cost 189,307, merged tariff 18,985 flat; Vataman: 147,575 and 13,565
- Re-phased remaining capex off the capital commitments disclosed in the FY26 accounts
- Depreciation and O&M now run off gross block
- Extended IRR/NPV ranges that were stopping short of the final year — Khavda II-C's IRR was dropping a 39,957 terminal cash flow

**Effect**

FY27 PAT turns positive in both blocks (Khavda II-C −25 → +923; Vataman −2,336 → +840). Group project costs and tariffs were verified against source — PGCIL's Q3 FY24 TBCB wins aggregate to Rs 20,479 crore of investment and Rs 1,636 crore of annual tariff, and the six relevant blocks sum to exactly those figures.

**Sources**

- POWERGRID Khavda II-C FY26 financial statements, Note 51 (Ind AS 103) — names all 12 transferors:
  https://www.powergrid.in/sites/default/files/financial_results/FS%20for%20PKIICTL.pdf
- POWERGRID Vataman FY26 financial statements, Note 49 — names all 5 transferors:
  https://www.powergrid.in/sites/default/files/financial_results/PVTL_0.pdf
- Press coverage of the MCA orders:
  https://psuwatch.com/newsupdates/mca-approves-merger-of-17-power-grid-subsidiaries-into-two-units
  https://www.tndindia.com/pgcil-completes-first-phase-of-consolidating-tbcb-subsidiaries/

Note: a second phase covering 28 further SPVs into POWERGRID Ghiror and POWERGRID South Olpad is pending regulatory approval and is **not** reflected in FY26 or in the model.

Happy to walk through the changes.
