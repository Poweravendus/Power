"""Qualiance v2 update (24-Nov-2026): split new-unit economics from the existing plant.
New unit = private-label performance wear (management meeting Nov-2026), so its price per piece,
material share and labour share get their own drivers. Adds Drivers rows 161-190 and rewires rows 22-23,30,50,55.
Also adds a 'Unit_Economics' sheet with the investor's per-piece and per-machine peer table."""
import sys
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

F = sys.argv[1]
wb = openpyxl.load_workbook(F)
d = wb['Drivers']
A = 'Arial'
BLUE = Font(name=A, size=9, color='0000FF'); BLK = Font(name=A, size=9); BOLD = Font(name=A, size=9, bold=True)
GRN = Font(name=A, size=9, color='008000'); NOTE = Font(name=A, size=8)
YEL = PatternFill('solid', fgColor='FFFF00'); HDR = PatternFill('solid', fgColor='D9D9D9')
C = 'CDEF'  # FY27E..FY30E

def setnote(ref, text, append=False):
    cell = d[ref]
    for mr in d.merged_cells.ranges:
        if ref in mr:
            cell = d.cell(mr.min_row, mr.min_col); break
    cell.value = ((cell.value or '') + ' ' + text) if append else text

def block(r, label, unit, vals, note, fmt='#,##0'):
    d.cell(r, 1, label).font = BLK; d.cell(r, 2, unit).font = BLK
    for c in C:
        x = d[f'{c}{r}']; x.value = f'=CHOOSE($C$3,{c}{r+1},{c}{r+2},{c}{r+3})'; x.font = BLK; x.number_format = fmt
    d.cell(r, 7, note).font = NOTE
    for j, (lab, vv) in enumerate(zip(('Bear', 'Base', 'Bull'), vals)):
        rr = r + 1 + j
        d.cell(rr, 1, f'   {label} - {lab}').font = BLK; d.cell(rr, 2, unit).font = BLK
        for k, c in enumerate(C):
            x = d[f'{c}{rr}']; x.value = vv[k]; x.font = BLUE; x.number_format = fmt
            if j == 1: x.fill = YEL

r0 = 161
d.cell(r0, 1, 'I. New unit economics (added 24-Nov-2026 after the management meeting): private-label performance wear, priced and costed separately from the Swiss technical business').font = BOLD
block(162, 'New unit price per piece', 'Rs.',
      [(800, 800, 800, 800), (1100, 1100, 1100, 1100), (1960, 1960, 1960, 1960)],
      '[M/A/E] Meeting Nov-2026: the new unit is for "larger private-label performance-wear programmes" (Agilitas, Skechers trials), not the Swiss tenders, '
      'which management calls "relatively mature". Peer price per piece FY26 (investor\'s table, company disclosures): Pearl Global Rs.643, Gokaldas legacy India Rs.765, '
      'Banswara garments Rs.831; Qualiance Swiss mix Rs.1,936. Base Rs.1,100: performance outerwear above commodity peers, well below military jackets. '
      'Bull Rs.1,960 = management\'s Rs.180 cr peak at 80-85% of 10.8 lakh pieces (call p.14). Bear Rs.800 = peer level. Cross-check: base at full use = '
      'Rs.119 cr = Rs.20 lakh a machine on 600 machines, between S P Apparels Rs.17.3 lakh and Young Brand Rs.23.2 lakh (FY25).', '#,##0')
block(166, 'New unit material cost', '% of new-unit revenue',
      [(0.56, 0.56, 0.56, 0.56), (0.54, 0.54, 0.54, 0.54), (0.46, 0.46, 0.46, 0.46)],
      '[E] Brand programmes carry less design and testing value than certified Swiss garments, and inputs shift to the Far East (meeting). Existing plant 40-46% (rows 46-49). '
      'Base 54%, bear 56%; bull = existing-plant level (management expects the same combined margin, call p.11). Peer material shares to be checked against annual reports / Bloomberg.', '0.0%')
block(170, 'New unit labour cost', '% of new-unit revenue',
      [(0.25, 0.25, 0.25, 0.25), (0.22, 0.22, 0.22, 0.22), (0.24, 0.24, 0.24, 0.24)],
      '[M/E] ~1,000 new workers on top of ~340 (meeting). Base 22%: at full use (Rs.119 cr) that is ~Rs.26 cr, ~Rs.2.6 lakh a worker. Bull 24% = existing plant (Rs.470 on a Rs.1,960 piece). '
      'Staff hired ahead of output sit in the fixed overheads (rows 58-62).', '0.0%')
d.cell(174, 1, 'New unit revenue').font = BOLD; d.cell(174, 2, 'Rs cr').font = BLK
d.cell(175, 1, 'New unit sewing machines').font = BLK; d.cell(175, 2, 'no.').font = BLK
d.cell(176, 1, 'memo: new unit revenue per machine at this year\'s fill').font = BLK; d.cell(176, 2, 'Rs lakh').font = BLK
d.cell(177, 1, 'memo: new unit revenue per machine at full use').font = BLK; d.cell(177, 2, 'Rs lakh').font = BLK
d.cell(178, 1, 'Existing plant garment sales').font = BLK; d.cell(178, 2, 'Rs cr').font = BLK
d.cell(179, 1, 'memo: existing plant revenue per machine (240 machines, analyst count, unverified)').font = BLK; d.cell(179, 2, 'Rs lakh').font = BLK
d.cell(180, 1, 'New unit share of garment sales').font = BLK; d.cell(180, 2, '%').font = BLK
for c in C:
    d[f'{c}174'] = f'={c}22*{c}163/100'.replace('163', '162'); d[f'{c}174'].font = BLK; d[f'{c}174'].number_format = '#,##0.0'
    d[f'{c}175'] = 600; d[f'{c}175'].font = BLUE
    d[f'{c}176'] = f'=IFERROR({c}174*100/{c}175,0)'; d[f'{c}176'].number_format = '0.0'
    d[f'{c}177'] = f'={c}13*{c}162/{c}175'; d[f'{c}177'].number_format = '0.0'
    d[f'{c}178'] = f'={c}12*{c}29/100'; d[f'{c}178'].number_format = '#,##0.0'
    d[f'{c}179'] = f'={c}178*100/240'; d[f'{c}179'].number_format = '0.0'
    d[f'{c}180'] = f'=IFERROR({c}174/{c}30,0)'; d[f'{c}180'].number_format = '0%'
d.cell(175, 7, '[A] 600 sewing machines (RHP Objects p.71-72; PPT 1HFY27 slide 19; meeting).').font = NOTE
d.cell(177, 7, 'Full-use capacity (10.8 lakh pieces) x price / machines. Management\'s Rs.180 cr at 80-85% needs ~Rs.36 lakh a machine; listed peers earn Rs.9.8-23.2 lakh (investor table).').font = NOTE
d.cell(179, 7, '[E] 240 machines is an analyst count posted on X, not a company disclosure. RHP employees: 302 / 284 / 283 (FY24-26); meeting: ~340 workers.').font = NOTE

# ---- rewire the engine ----
for c in C:
    d[f'{c}30'] = f'={c}178+{c}174'                       # garment sales = existing + new unit
    d[f'{c}50'] = f'=({c}178+{c}178*{c}34)*{c}49+({c}174+{c}174*{c}34)*{c}166'   # material on each unit's revenue (incl. other op revenue)
    d[f'{c}55'] = f'={c}12*{c}54/100+{c}174*{c}170'        # existing: per piece; new unit: % of its revenue
setnote('G30', 'Existing plant (row 178: pieces x row 29 price) + new unit (row 174: pieces x row 162 price). Split 24-Nov-2026.')
setnote('G50', 'Existing-plant revenue x row 49 + new-unit revenue x row 166 (each incl. its share of other operating revenue).')
setnote('G55', 'Existing plant: pieces x cost per piece (row 54); new unit: revenue x row 170. Split 24-Nov-2026.')
# existing-plant labour per piece: the new-tailor premium now sits in the new unit -> base back to wage-inflation path
for c, v in zip('DEF', (420, 435, 450)):
    d[f'{c}52'] = v
setnote('G51', '24-Nov-2026: base back to Rs.420/435/450 for the existing plant; the new unit labour is now row 170.', True)
setnote('G26', 'From 24-Nov-2026 this price applies to the existing plant only. Risk: management says Swiss institutions run ~Rs.40-60 cr a year (~Rs.50 cr typical) vs Rs.61.5 cr in FY26, so FY26 may be a peak mix (meeting Nov-2026).', True)

# ---- Unit_Economics sheet ----
if 'Unit_Economics' in wb.sheetnames:
    del wb['Unit_Economics']
u = wb.create_sheet('Unit_Economics', index=wb.sheetnames.index('Segments') + 1)
u['A1'] = 'Revenue per piece and per machine: Qualiance vs listed garment makers (investor table, Nov-2026) and what it means for the new unit'
u['A1'].font = Font(name=A, size=11, bold=True)
u['A2'] = 'Blue = input (investor\'s table from company disclosures; machine counts from annual reports / presentations), black = formula, green = link.'
u['A2'].font = NOTE
hdr = ['Company', 'Period', 'Scope', 'Revenue (Rs cr)', 'Pieces (mn)', 'Rs per piece', 'Sewing machines', 'Rs lakh per machine', 'Pieces per machine']
for j, h in enumerate(hdr):
    x = u.cell(4, 1 + j, h); x.font = BOLD; x.fill = HDR
rows = [
    ('SP Apparels', 'FY25', 'Garment exports', 853.83, 63.5, 4950),
    ('SP Apparels', 'FY26', 'Garment exports', 955.43, 70.5, None),
    ('S.P. / Young Brand', 'FY25', 'Intimate apparel', 325, None, 1400),
    ('Banswara Syntex', 'FY26', 'Garment division', 324, 3.9, None),
    ('Pearl Global', 'FY26', 'Consolidated', 5025, 78.1, None),
    ('KPR Mill', 'FY26', 'Garment division', 3179, 181.45, None),
    ('Gokaldas Exports', 'FY26', 'Legacy India', 2572.47, 33.63, None),
    ('Maral Overseas', 'FY26', 'Garment division', 190.07, None, 1948),
    ('Qualiance', 'FY24', 'Garments made', 36.91, 0.297548, 240),
    ('Qualiance', 'FY25', 'Garments made', 52.82, 0.351698, 240),
    ('Qualiance', 'FY26', 'Garments made', 76.29, 0.394044, 240),
]
r = 5
for row in rows:
    for j, val in enumerate(row):
        col = 1 + j if j < 5 else 7
        x = u.cell(r, col, val); x.font = BLUE if j >= 3 and val is not None else BLK
    u.cell(r, 6, f'=IF(E{r}="","",D{r}*10/E{r})').number_format = '#,##0'
    u.cell(r, 8, f'=IF(G{r}="","",D{r}*100/G{r})').number_format = '0.0'
    u.cell(r, 9, f'=IF(OR(E{r}="",G{r}=""),"",E{r}*1000000/G{r})').number_format = '#,##0'
    r += 1
u.cell(r, 1, 'Qualiance pieces use the RHP chartered-engineer production figures (2,97,548 / 3,51,698 / 3,94,044). The 240 machines are an analyst count on X, not disclosed; RHP employees 302 / 284 / 283.').font = NOTE
r += 2
u.cell(r, 1, 'Qualiance: is the higher price per piece real value or pass-through?').font = BOLD; r += 1
for j, h in enumerate(['Item', 'FY24', 'FY25', 'FY26', 'FY24-26 change']):
    x = u.cell(r, 1 + j, h); x.font = BOLD; x.fill = HDR
r += 1
base = r
u.cell(r, 1, 'Price per piece (Rs)')
for j, c in enumerate('BCD'):
    u.cell(r, 2 + j, f'=Segments!{c}32').font = GRN
u.cell(r + 1, 1, 'Gross margin (P&L)')
for j, c in enumerate('CDE'):
    u.cell(r + 1, 2 + j, f"='P&L'!{c}10").font = GRN
u.cell(r + 2, 1, 'Value added per piece (price x gross margin, Rs)')
u.cell(r + 3, 1, 'EBITDA per piece (Rs)')
u.cell(r + 4, 1, 'Switzerland share of garment sales')
for j, (c, pc) in enumerate(zip('BCD', 'CDE')):
    u.cell(r + 2, 2 + j, f'={c}{r}*{c}{r+1}').number_format = '#,##0'
    u.cell(r + 3, 2 + j, f"='P&L'!{pc}15*10000000/Segments!{c}30").number_format = '#,##0'
    u.cell(r + 4, 2 + j, f'=Segments!{c}11').number_format = '0%'
    u.cell(r, 2 + j).number_format = '#,##0'; u.cell(r + 1, 2 + j).number_format = '0.0%'
for k in range(5):
    u.cell(r + k, 5, f'=IFERROR(D{r+k}/B{r+k}-1,"")').number_format = '0%'
u.cell(r + 5, 1, 'Reading: value added per piece rose about as fast as the price, so FY24-26 was a real mix shift to Swiss technical garments, not metal-style pass-through. '
       'But Swiss sales were Rs.61.5 cr in FY26 against the Rs.40-60 cr (~Rs.50 cr) management calls typical, so FY26 may be the peak mix.').font = NOTE
r += 8
u.cell(r, 1, 'New unit: what each price assumption means per machine (600 machines, 10.8 lakh pieces at full use)').font = BOLD; r += 1
for j, h in enumerate(['Case', 'Rs per piece', 'Revenue at full use (Rs cr)', 'Rs lakh per machine', 'vs Qualiance FY26 per machine', 'vs S P Apparels FY25 per machine']):
    x = u.cell(r, 1 + j, h); x.font = BOLD; x.fill = HDR
r += 1
for lab, ref in (('Bear', 'Drivers!C163'), ('Base', 'Drivers!C164'), ('Bull (management Rs.180 cr peak)', 'Drivers!C165')):
    u.cell(r, 1, lab)
    x = u.cell(r, 2, f'={ref}'); x.font = GRN; x.number_format = '#,##0'
    u.cell(r, 3, f'=10.8*B{r}/100').number_format = '#,##0'
    u.cell(r, 4, f'=C{r}*100/600').number_format = '0.0'
    u.cell(r, 5, f'=D{r}/H15-1').number_format = '0%'
    u.cell(r, 6, f'=D{r}/H5-1').number_format = '0%'
    r += 1
u.cell(r, 1, 'Management\'s Rs.180 cr needs each new machine to earn more than today\'s Swiss machines and 1.5-3.5x what listed peers earn, on private-label work that peers price at Rs.640-830 a piece.').font = NOTE
u.column_dimensions['A'].width = 46
for col in 'BCDEFGHI':
    u.column_dimensions[col].width = 15
u.sheet_view.showGridLines = False
for row in u.iter_rows():
    for x in row:
        if x.font is None or x.font.name != A:
            x.font = Font(name=A, size=9, bold=x.font.bold if x.font else False, color=x.font.color if x.font else None)
wb.save(F)
print('ok')
