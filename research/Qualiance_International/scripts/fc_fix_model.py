"""Final check 28-Nov-2026: mechanical fixes to QUALIANCE_Model_v2.xlsx (no driver, multiple or scenario changes).
1) Valuations J51:J53 EV/EBITDA value per share re-pasted from the live runs (C36 under selector 1/2/3).
2) Valuations C90:C95 sensitivity targets pasted unrounded (upsides in D now exact).
3) Valuations C14 price/book linked to Half-yearly!D33 instead of a typed 77.2782.
4) Valuations J59 floor description corrected (it described the 8-Nov old base, not the re-based floor).
5) Drivers C155 memo: new-unit FY30E revenue used the old-plant price (row 29); now row 174 x (1 + row 34).
6) Drivers G148 note updated: base is 22-32% of the way floor-to-bull, not 40%.
7) Unit_Economics C30:D32 use Drivers capacity (C13) and machine count (C175) instead of typed 10.8 / 600.
Usage: fc_fix_model.py <model.xlsx> <scen_results.json> <sens_floor.json>"""
import openpyxl, json, sys
F, SJ, FJ = sys.argv[1:4]
sc = json.load(open(SJ)); se = json.load(open(FJ))
wb = openpyxl.load_workbook(F); v = wb['Valuations']; d = wb['Drivers']; u = wb['Unit_Economics']
for s in ('1', '2', '3'):
    v[f'J{50 + int(s)}'] = round(sc[s]['ev_val'], 4)
for r, k in ((90, 'base'), (91, 'price1400'), (92, 'price1600'), (93, 'price1960_brandcost'), (94, 'mgmt_fill_1100')):
    v[f'C{r}'] = se[k]['tp']
v['C95'] = round(23.21 * se['base']['eps'][1], 2)
v['B49'] = v['B49'].value + ' EV/EBITDA column re-pasted 28-Nov-2026 (final check).'
v['C14'] = "=C5/'Half-yearly'!D33"
v['J59'] = ("Re-based floor (24-Nov-2026): existing plant 80% FY27 then 82%, Rs.1,975 a piece; new unit filled 0/12/25/40% "
            "at Rs.1,100 a piece with 54% material and 22% labour; existing-plant labour Rs.400/420/435/450 a piece; other drivers as base. "
            "Re-run 28-Nov-2026 reproduces rows 59-63. What is visible today with no new customer won faster than a trickle.")
d['C155'] = '=F174*(1+F34)'
d['G148'] = ("Rule of thumb 40-75%. 24-Nov-2026: with the bull now at management's new-unit price, the base is only 22-32% "
             "of the way from floor to bull (FY27E 32%, FY28E-FY30E 22-24%), below the rule: no brand volume signed and listed peers price "
             "brand work at Rs.640-830 a piece. For the lead to confirm.")
for r in (30, 31, 32):
    u[f'C{r}'] = f'=Drivers!$C$13*B{r}/100'
    u[f'D{r}'] = f'=C{r}*100/Drivers!$C$175'
wb.save(F); print('saved')
