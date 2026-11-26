# Bonfiglioli Transmissions Ltd (NSE: BONFIG, BSE: 544996) - historical inputs.
# All amounts Rs. million as printed in the documents (the model converts to Rs. crore = /10).
# Fiscal year = calendar year (1-Jan to 31-Dec). FY25 = year ended 31-Dec-2025.
# Page references are PRINTED pages of the Prospectus dated 19-Oct-2026 (PDF page = printed + 5),
# unless another document is named.  Abbreviations:
#   Pros   = Prospectus 19-Oct-2026 (same text as RHP 9-Oct-2026 except offer price/size fields)
#   DRHP   = Draft Red Herring Prospectus filed with SEBI Feb-2026
#   Res    = Unaudited results for quarter and nine months ended 30-Sep-2026 (board 12-Nov-2026), PDF page
#   PPT    = Q3CY26 investor presentation (12-Nov-2026), slide number
#   Call   = Q3CY26 earnings call transcript (13-Nov-2026), page
#   PR     = Q3 and 9M CY26 earnings release (12-Nov-2026), page
#   LicAgr = License for Limited Scope Manufacturing Agreement with Bonfiglioli S.p.A. dated 1-Jun-2021, page

YEARS = ['FY23A', 'FY24A', 'FY25A']          # years to 31-Dec-2023 / 2024 / 2025

# ---------------- Profit and loss (restated, continuing operations) ----------------
PL = {
 'rev':      ([16873.30, 18541.83, 20135.26], 'Pros p.285 (restated P&L)'),
 'rm':       ([11104.93, 11854.27, 11967.18], 'Pros p.285; note 25 p.317'),
 'inv_chg':  ([-268.86, -64.11, 542.53],      'Pros p.285; note 26 p.317 (+ = stock release)'),
 'emp':      ([896.70, 982.19, 1062.70],      'Pros p.285; note 27 p.317'),
 'royalty':  ([752.35, 822.09, 895.87],       'Pros note 30 p.318 (royalty in other expenses)'),
 'prof':     ([474.84, 453.06, 475.67],       'Pros note 30 p.318 (professional fees, mostly BSPA cost-sharing)'),
 'oth_tot':  ([2701.62, 2818.74, 2855.15],    'Pros p.285; note 30 p.318'),
 'dep':      ([370.99, 466.29, 478.23],       'Pros p.285; note 28 p.317'),
 'oi':       ([144.71, 69.72, 100.63],        'Pros p.285; note 24 p.316'),
 'fin':      ([130.92, 104.18, 77.77],        'Pros p.285; note 29 p.317'),
 'pbt':      ([2081.71, 2449.99, 3252.33],    'Pros p.285'),
 'tax':      ([615.06, 534.01, 873.59],       'Pros p.285'),
 'pat_cont': ([1466.65, 1915.98, 2378.74],    'Pros p.285'),
 'pat_disc': ([18.27, 35.66, 0.0],            'Pros p.285 (IT/R&D unit transferred to BTSPL 30-Sep-2024, p.376)'),
 'ebitda_rep': ([2438.91, 2950.74, 3707.70],  'Pros p.209 (EBITDA excl. other income, company definition)'),
 'tp_secadj': ([0.0, 140.63, 80.32],          'Pros note 23 p.316 (one-off transfer-pricing secondary adjustment in revenue)'),
 'grant':    ([102.13, 145.62, 127.90],       'Pros note 23 p.316 (income from government grant, in revenue)'),
 'warranty': ([100.62, 82.25, 60.85],         'Pros note 30 p.318'),
 'csr':      ([55.30, 44.91, 67.03],          'Pros note 30 p.318'),
 'subcon':   ([420.13, 430.80, 356.19],       'Pros note 30 p.318'),
}
# audited (statutory) PAT and equity, for the conflict log (Pros Annexure VII p.345)
AUDITED = {'pat': [1495.25, 1946.89, 2378.74], 'equity': [8053.44, 8530.92, 9929.93]}
# DRHP restated FY22 (not pooled for the BDSPL business, memo only) DRHP restated P&L p.262 (PDF p.267)
FY22_DRHP = {'rev': 15588.01, 'pat': 1714.49, 'pat_cont': 1687.53}

# ---------------- Balance sheet (restated) Pros p.284 ----------------
BS = {
 'ppe':    [2561.45, 2639.82, 2691.52], 'cwip': [202.57, 137.32, 123.46], 'intang': [23.18, 3.04, 3.38],
 'iaud':   [0.0, 9.46, 0.0], 'rou': [381.04, 343.07, 306.97],
 'inv_nc': [1.13, 1.13, 1.13], 'loan_nc': [0.0, 92.40, 69.30], 'ofa_nc': [54.59, 55.56, 38.30],
 'dta':    [175.08, 161.80, 174.08], 'nctax': [26.93, 4.92, 4.92], 'onca': [71.89, 74.39, 78.31],
 'inventory': [3322.79, 3214.17, 3192.13], 'recv': [4101.43, 4061.92, 5177.39],
 'cash':   [905.32, 1446.67, 1531.81], 'bank': [1700.12, 0.94, 100.15],
 'loan_c': [0.0, 126.11, 49.95], 'ofa_c': [65.59, 147.87, 138.13], 'ctax_a': [92.53, 82.30, 0.0],
 'oca':    [461.51, 387.87, 713.65],
 'total_assets': [14147.15, 12990.76, 14394.58],
 'sharecap': [1311.23, 1253.31, 1253.31], 'oeq': [6702.40, 7356.20, 8676.62],
 'lease_nc': [60.10, 28.09, 3.88], 'ofl_nc': [20.31, 1.82, 22.11], 'prov_nc': [107.59, 106.35, 121.30],
 'contract': [31.33, 50.40, 56.43], 'borrow': [1107.86, 0.0, 0.0], 'lease_c': [36.56, 37.48, 24.24],
 'tp_msme': [595.84, 382.72, 516.43], 'tp_oth': [3224.42, 2702.79, 2785.69], 'ofl_c': [499.15, 662.18, 438.70],
 'ctax_l': [0.0, 0.0, 30.59], 'ocl': [135.81, 201.90, 209.16], 'prov_c': [314.55, 207.52, 256.12],
}
BS_SRC = 'Pros p.284 (restated statement of assets and liabilities)'

# ---------------- Cash flow (restated) Pros p.286 ----------------
CF = {
 'cfo':      ([1982.28, 1883.50, 1876.81], 'Pros p.286'),
 'op_pre_wc':([2567.07, 3026.63, 3764.77], 'Pros p.286'),
 'wc_chg':   ([-9.79, -619.82, -1128.88],  'Pros p.286 (cash generated less operating profit before WC)'),
 'tax_paid': ([-616.90, -567.90, -759.08], 'Pros p.286'),
 'capex':    ([-1201.21, -430.77, -539.77],'Pros p.286 (purchase of PPE and intangibles)'),
 'cfi':      ([-999.23, 1093.95, -523.79], 'Pros p.286'),
 'div':      ([-655.60, -463.72, -1153.05],'Pros p.286 (dividend paid)'),
 'buyback':  ([0.0, -720.00, 0.0],         'Pros p.286 (buyback 9-May-2024 at Rs.124.30, p.122)'),
 'net_borrow': ([-329.60, -1107.86, 0.0],  'Pros p.286 (proceeds less repayments)'),
 'cff':      ([-1164.44, -2436.10, -1267.88], 'Pros p.286'),
 'net_chg':  ([-181.39, 541.35, 85.14],    'Pros p.286'),
 'cash_close': ([905.32, 1446.67, 1531.81], 'Pros p.286'),
}

# ---------------- Half-year restated (Pros p.284-286) ----------------
H1 = {  # H1CY25, H1CY26
 'rev': [9603.55, 11318.69], 'oi': [61.42, 72.99], 'rm': [5977.36, 7541.76], 'inv_chg': [34.41, -633.04],
 'emp': [492.28, 589.61], 'fin': [36.56, 40.72], 'dep': [234.02, 271.87], 'oth': [1335.22, 1581.62],
 'pbt': [1555.12, 1999.14], 'tax': [405.43, 513.33], 'pat': [1149.69, 1485.81], 'ebitda_rep': [1764.28, 2238.74],
 'royalty': [430.33, 507.36], 'prof': [228.18, 284.05], 'cfo': [686.53, 1298.96], 'capex': [-247.99, -409.22],
 'div': [0.0, -1099.78],
}
# ---------------- Quarterly / nine-month (Res p.1, unaudited; Q3CY25 and 9MCY25 restated for BDSPL) ----------
Q = {  # columns: Q3CY25, Q2CY26, Q3CY26, 9MCY25, 9MCY26
 'rev': [5069.09, 5616.13, 6601.71, 14592.33, 17920.40],
 'oi':  [18.08, 63.77, 38.36, 77.80, 105.20],
 'rm':  [3034.99, 3760.45, 3926.47, 9015.40, 11468.23],
 'inv_chg': [89.40, -343.20, 118.63, 123.81, -514.41],
 'emp': [258.34, 297.22, 316.34, 750.62, 905.94],
 'fin': [22.19, 26.11, 23.22, 57.93, 63.94],
 'dep': [119.82, 137.50, 130.90, 353.84, 402.51],
 'oth': [752.54, 792.52, 951.27, 2127.02, 2527.00],
 'pbt': [809.89, 1009.30, 1173.24, 2241.51, 3172.39],
 'tax': [179.51, 258.49, 302.21, 566.25, 815.54],
 'pat': [630.38, 750.81, 871.03, 1675.26, 2356.85],
 'eps': [3.35, 3.99, 4.63, 8.91, 12.54],
}
# vertical revenue by period (PPT slides 7-8; Pros p.207)  Rs mn
VERT = {
 #            FY23      FY24      FY25      H1CY25   H1CY26   9MCY25  9MCY26  Q3CY25  Q3CY26
 'ia':   [7270.46, 7648.89, 8244.39, 3902.36, 4813.28, 5984, 7530, 2081, 2717],
 'ohm':  [4257.93, 4357.92, 5070.48, 2349.51, 3203.78, 3679, 5262, 1329, 2058],
 'wind': [5009.58, 5994.29, 6347.70, 3092.33, 3096.46, 4666, 4796, 1574, 1700],
 'oth':  [335.33, 540.73, 472.69, 259.35, 205.17, None, None, None, None],
}
VERT_SRC = 'Pros p.207 (FY23-FY25, H1); PPT slides 7-8 (9M and Q3, rounded Rs mn)'
# I&A split: low/medium-duty gear motors vs heavy-duty gearboxes (Pros p.222)
IA_SPLIT = {'lmd': [6487.40, 6885.25, 7346.77, 3523.78, 4272.25], 'hd': [783.06, 763.64, 897.62, 378.58, 541.03]}
# Product (Pros note 36 p.322)
PRODUCT = {'gearbox': [9615.62, 11072.63, 12056.19, 5698.01, 7100.96], 'gearmotor': [5231.89, 5366.21, 5825.12, 2802.28, 2856.94],
           'others': [1841.64, 1722.46, 1945.64, 920.70, 1227.33]}
# Geography: revenue from contracts with customers (Pros p.227-228; note 36 p.322)
GEO = {'India': [12709.58, 13546.37, 14372.84, 6981.67, 7833.67], 'USA': [1577.45, 2405.17, 3077.40, 1451.28, 1591.60],
       'Italy': [371.31, 373.18, 607.63, 252.15, 342.68], 'Germany': [589.16, 642.25, 435.33, 194.49, 322.47],
       'China': [592.70, 411.43, 186.70, 94.17, 108.15], 'Other': [848.95, 782.90, 1147.05, 447.23, 986.66]}
GEO_TOT = [16689.15, 18161.30, 19826.95, 9420.99, 11185.23]
# Channel (Pros p.208 and p.228) - FY24 inter-company: p.208 prints 2,755.09, p.228 prints 2,775.09; only 2,775.09 adds to revenue 18,541.83, so used
CHANNEL = {'dealer': [3333.07, 3535.58, 3909.41, 1865.11, 2145.72], 'direct': [10556.18, 11756.65, 12746.32, 6210.11, 6741.06],
           'interco': [2722.21, 2775.09, 3064.77, 1294.75, 2263.99], 'others': [261.84, 474.51, 414.76, 233.59, 167.92]}
# Group sales by entity FY25 (Pros RPT summary p.73-75), Rs mn
GROUP_SALES_FY25 = [('Bonfiglioli U.S.A. Inc.', 785.25), ('Bonfiglioli Riduttori S.p.A. (Italy)', 471.86),
    ('Bonfiglioli Deutschland GmbH', 435.33), ('Bonfiglioli (U.K) Ltd', 338.19), ('Bonfiglioli Redutores do Brasil', 198.64),
    ('Tecnotrans Bonfiglioli SA (Spain)', 195.75), ('Bonfiglioli Drives (Shanghai)', 143.83), ('Bonfiglioli Transmission (Aust.) - Australia', 112.43),
    ('Bonfiglioli Vietnam', 91.99), ('Bonfiglioli Transmission S.A.S (France)', 87.15), ('Bonfiglioli Trading (Shanghai)', 39.22),
    ('Bonfiglioli South East Asia', 36.74), ('Bonfiglioli Slovakia', 22.74), ('Bonfiglioli Transmission (Aust.) - New Zealand', 22.41),
    ('Bonfiglioli Turkey', 19.62), ('Bonfiglioli South Africa', 5.89)]
# Payments to / receipts from group (Pros RPT p.73-82) FY23, FY24, FY25, H1CY25, H1CY26
RPT = {
 'royalty_bspa': [741.26, 813.32, 888.08, 425.92, 505.43],      # p.82
 'prof_bspa':    [441.21, 420.33, 427.76, 207.51, 262.57],      # p.79
 'purch_riduttori': [2303.32, 1985.81, 1856.50, 998.90, 1163.34],# p.79
 'purch_group_total_pct': [20.91, 17.90, 15.68, 17.37, 15.79], # % of RM purchases from related parties, p.21
 'sales_commission_usa': [25.14, 36.39, 46.17, 21.78, 19.40],   # p.80
 'dividend_bspa': [639.71, 689.30, 927.45, 927.45, 1099.78],    # p.82 (paid/payable)
 'buyback_group': [0.0, 720.00, 0.0, 0.0, 0.0],                 # p.82 (BSPA 324.50 + Vectron 395.50)
 'tp_secadj_recv': [0.0, 140.63, 80.32, 80.32, 0.0],            # p.78
 'loan_to_btspl_out': [0.0, 218.51, 119.25, 151.81, 130.21],    # p.330 balance
 'income_rp_pct': [17.70, 17.66, 15.59, 14.29, 19.91],          # p.25
 'exp_rp_pct': [28.66, 25.20, 24.83, 32.38, 32.71],             # p.25-26
}
# Group receivables / payables at period end (Pros note 38 p.330) Dec-23, Dec-24, Dec-25, Jun-25, Jun-26
GROUP_RECV = [1055.48, 831.51, 1267.62, 845.10, 1598.00]   # holding + fellow subsidiaries (sum of lines, Pros p.330; excl. B.R.T.)
GROUP_PAY  = [1405.03, 990.43, 1077.66, 952.71, 1079.22]   # holding + fellow subsidiaries trade payables (sum of lines, Pros p.330)

# ---------------- Operating data ----------------
CAP = {  # hours; Pros p.233 (FY23, FY24, FY25, H1CY25, H1CY26)
 'tmv_ms_av': [594332, 629657, 687348, 322658, 353304], 'tmv_ms_ut': [443805, 500737, 556670, 261661, 285262],
 'tmv_as_av': [312570, 312570, 323411, 163080, 167184], 'tmv_as_ut': [151406, 162655, 181709, 88634, 102746],
 'man_as_av': [112368, 48320, 54040, 24468, 35938],     'man_as_ut': [65039, 35463, 41913, 18001, 27997],
 'man_ms_av': [0, 0, 0, 0, 5663],                       'man_ms_ut': [0, 0, 0, 0, 4118],
 'tal_as_av': [91482, 129105, 140950, 66818, 86146],    'tal_as_ut': [52905, 92456, 108522, 51168, 66319],
}
AGG_UTIL = [0.6422, None, 0.7371, None, 0.7504]   # Pros p.216
UNITS_FY25 = 341133            # gear motors and gearboxes manufactured FY25, Pros p.209
SKUS = {'produced': [9959, 11517, 11857, 8014, 8780]}   # Pros p.233
EMP = {'onroll': [752, 601, 604, 597, 627], 'headcount': [None, 968, 987, 943, 1032]}  # Pros p.239; p.373; p.370
TOP10_CUST = [28.61, 32.48, 35.58, 36.28, 31.72]   # % of revenue from customers, Pros p.230
TOP1_CUST = [7.48, 9.92, 11.43, 11.60, 9.40]       # Pros p.27/229 (largest customer, GE per Call p.11)
DOMESTIC_PURCH = [65.39, 70.00, 71.10, 69.64, 70.70]  # % of RM consumed from domestic suppliers, Pros p.237
DEALERS = 44
CAPEX_GUIDE = {'FY26': 1000.0, 'FY27': 1500.0}   # Call p.8, p.13 (Rs.100 cr CY26, Rs.150 cr CY27)

# ---------------- Offer / share data ----------------
SHARES_POST = 187995834       # Pros p.287 (after 1:2 bonus allotted 25-Jan-2026); OFS creates no new shares
OFS_SHARES = 43239042         # Pros cover p.2
OFS_PRICE = 586.0             # Pros cover p.2; band Rs.558-586 (p.110)
OFS_AMOUNT_MN = 25336.63      # Pros cover p.2
OFS_PCT = 0.23                # 23.00% of post-offer capital, Pros cover p.2
WACA = 6.77                   # promoter average cost per share, Pros p.51
NAV_JUN26 = 55.02             # Pros p.111
OFFER_PE = 46.32              # on FY25 diluted EPS, Pros p.110
OFFER_EV_EBITDA = 29.71       # Pros p.51
OFFER_EXPENSES_MN = 1213.16   # borne by the selling shareholder, Pros p.106-107
LISTING_DATE = '23-Oct-2026'  # PPT slide 3; Res p.2 note 4
LISTING_CLOSE = 574.50        # Screener daily close 23-Oct-2026 (exchange data via Screener)
CMP = 803.25                  # close 26-Nov-2026 (Screener daily price series); replace with Bloomberg
CMP_DATE = '26-Nov-2026'
PEERS = [  # Pros p.112 (price 28-Sep-2026, NSE), p.119 KPIs
 ('Elecon Engineering', 23660.50, 31.63, 22.11, 15.85, 19.28),
 ('Shanthi Gears', 5187.20, 63.39, 20.03, 18.19, 24.85),
 ('Schaeffler India', 96858.50, 53.74, 18.20, 20.21, 26.08),
 ('Timken India', 34780.29, 57.66, 18.18, 14.28, 19.00),
]
PEER_PE_AVG = 51.61           # Pros p.110
