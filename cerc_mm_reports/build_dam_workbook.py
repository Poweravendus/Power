#!/usr/bin/env python3
"""Build dam_volumes.xlsx from dam_volumes.csv.

Sheets:
  Sold_long / Purchased_long  - one row per (month, entity) as printed in the report
  Sold_pivot / Purchased_pivot - entity x month matrix of volume (MU)
  Monthly_totals              - sum of each table per month
  Validation                  - per-table reconciliation against the printed total
Entity names in the pivots are upper-cased and whitespace-collapsed so that
case changes between report eras (TELANGANA / Telangana) line up. Genuine
renames (MP vs Madhya Pradesh, J&K vs Jammu Kashmir) are NOT merged.
"""
import os, re
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(HERE, "dam_volumes.csv"))
val = pd.read_csv(os.path.join(HERE, "dam_volumes_validation.csv"))
df["entity_norm"] = df["entity"].str.upper().str.replace(r"\s+", " ", regex=True).str.strip()

with pd.ExcelWriter(os.path.join(HERE, "dam_volumes.xlsx"), engine="openpyxl") as xw:
    for kind in ("sold", "purchased"):
        sub = df[df["table"] == kind]
        sub[["month", "entity", "volume_mu", "pct_of_volume"]].to_excel(
            xw, sheet_name=f"{kind.title()}_long", index=False)
        piv = sub.pivot_table(index="entity_norm", columns="month", values="volume_mu",
                              aggfunc="sum")
        piv["TOTAL_MU"] = piv.sum(axis=1)
        piv = piv.sort_values("TOTAL_MU", ascending=False)
        piv.index.name = "entity"
        piv.to_excel(xw, sheet_name=f"{kind.title()}_pivot")
    tot = df.pivot_table(index="month", columns="table", values="volume_mu", aggfunc="sum")
    tot.columns = [f"{c}_total_mu" for c in tot.columns]
    tot.to_excel(xw, sheet_name="Monthly_totals")
    val.to_excel(xw, sheet_name="Validation", index=False)

    for ws in xw.book.worksheets:
        ws.freeze_panes = "B2"
        for col in ws.columns:
            width = max(len(str(c.value)) if c.value is not None else 0 for c in col[:200])
            ws.column_dimensions[col[0].column_letter].width = min(max(10, width + 2), 60)
print("wrote dam_volumes.xlsx")
