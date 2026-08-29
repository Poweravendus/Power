# POWERGRID TBCB SPVs — Tariff & Capex Verification

Verification run 29 August 2026. Workbook: `PGCIL_TBCB_Tariff_Capex_Verification.xlsx`

## Sources

- **Capex** — CEA, *Monthly Progress Report of Under Construction Transmission Projects
  awarded through TBCB Route*, July 2026. Project cost column (Rs. Cr), PGCIL section,
  serial numbers 1–44.
- **Tariff** — CERC orders under Section 63 of the Electricity Act, 2003 adopting the single
  annual transmission charge discovered through e-reverse auction. All 200 published `/AT/`
  orders for 2021–2026 were downloaded from cercind.gov.in and the adopting paragraph read
  in each.
- **Pending status** — CERC active-petitions list as on 31 July 2026.

Orders were matched on the **bid-stage SPV name** (the petitioner) and the scheme scope,
cross-checked against the SPV name and scope in the CEA report. Bid-stage names differ from
the post-transfer POWERGRID names — e.g. *Khavda V-A Power Transmission Ltd* is now
*POWERGRID West Central Transmission Ltd*.

## Result

| | Count |
|---|---|
| Capex figures matching the CEA report exactly | 44 of 44 |
| Tariffs matching the adopted tariff to the rupee | 32 |
| Tariffs contradicted by the adoption order | 7 |
| Tariffs with no adoption order yet (unverifiable) | 10 |

The 44 CEA project costs sum to Rs 128,118 Cr against the report's own summary of
Rs 128,119 Cr (Re 1 Cr rounding). Every listed capex equals the CEA figure × 10.

## Tariff exceptions (Rs. million per annum)

| # | SPV | Listed | Adopted | Diff | CERC order |
|---|---|---:|---:|---:|---|
| 1 | POWERGRID Ramgarh II Transmission Ltd | 1,809 | 1,615.05 | +193.95 | 365/AT/2023, 27-Mar-2024 |
| 6 | POWERGRID Bidar Transmission Ltd | 2,741 | 2,368.09 | +372.91 | 117/AT/2024, 27-May-2024 |
| 7 | POWERGRID Sikar Khetri Transmission Ltd | 2,400 | 2,147.30 | +252.70 | 115/AT/2024, 28-May-2024 |
| 8 | POWERGRID Khavda IV-E2 Power Transmission Ltd | 815 | 932.07 | −117.07 | 234/AT/2024, 18-Nov-2024 |
| 14 | POWERGRID Jam Khambaliya Transmission Ltd | 395 | 446.04 | −51.04 | 490/AT/2024, 11-Mar-2025 |
| 29 | POWERGRID Kurnool-IV Transmission Ltd | 1,010 | 6,451.06 | −5,441.06 | 471/AT/2025, 30-Jun-2025 |
| 36 | POWERGRID Mandsaur Augmentation Transmission Ltd | 538 | 446.99 | +91.01 | 870/AT/2025, 02-Feb-2026 |

Notes:

- **Row 29 (Kurnool-IV)** is the material one. The adopted charge is Rs 6,451.06 mn/yr
  against Rs 1,010 listed — an understatement of Rs 5,441 mn/yr. The listed figure is also
  implausible on its face at 1.8% of a Rs 55,500 mn capex, against a ~11–13% norm.
- **Row 36 (Mandsaur Augmentation)**: the listed 538 is close to Rs 537.70 mn, the tariff
  adopted in 345/AT/2024 for *Tumkur-II REZ Power Transmission Ltd* — a GR Infra project,
  not this one. Likely a value taken from the wrong row.
- Rows 1, 6, 7 and 8 have no counterpart anywhere in their own adoption orders: the listed
  values match neither the initial price offer nor the CERC levelised estimate.

## Tariffs that cannot be verified yet

| # | SPV / Scheme | Status as on 31-Jul-2026 |
|---|---|---|
| 34 | POWERGRID Mahan Rewa Transmission Ltd (MEL Power Transmission Ltd) | Petition 690/AT/2025 — order reserved |
| 41 | POWERGRID Tumkur-II Transmission Ltd (Tumkur II RE Transmission Ltd) | Petition 328/AT/2026 — in hearing |
| 42 | WR-ER Inter-Regional Network Expansion Scheme Part-A | No AT petition on file |
| 43 | Kakinada Green Hydrogen / Green Ammonia Ph-I | No AT petition on file |
| 44 | Bhadla-III, Ramgarh PS & Kanpur Augmentation | No AT petition on file |
| 45 | POWERGRID West Maharashtra Transmission Ltd | Not in the CEA under-construction list; no figures supplied |
| 46 | POWERGRID Krishnagiri REZ Transmission Ltd | SPV acquired 3-Aug-2026, after the CEA report cut-off |
| 47 | POWERGRID Fatehgarh II Transmission Ltd (SynCon) | No AT petition traced |
| 48 | Robertsganj Power Transmission Ltd | SPV transfer pending; no AT petition traced |
| 49 | Humnabad Power Transmission Ltd | InSTS project — outside the CERC/CEA ISTS ambit |

## Placeholder figures to be aware of

Seven rows carry a tariff that is exactly 12.0% of the stated capex, which points to a
12%-of-capex proxy rather than a sourced figure: rows 14, 34, 41, 46, 47, 48 and 49. Row 14
is now disproved — the adopted tariff is Rs 446.04 mn, i.e. 13.6% of capex. For rows 46–49
there is no CEA capex either, so on those four the capex and the tariff are not independent
of one another and neither is independently sourced.

## One source-document caveat

CERC order 72/AT/2025 (row 19, West Central) prints the estimated project cost as
"Rs. 24610.94 million". The magnitude is crore — Rs 2,461 Cr would be under a tenth of the
adopted annual charge of Rs 40,829 mn. The CEA figure of Rs 24,819 Cr is consistent with the
tariff and is the one used here.
