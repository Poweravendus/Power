"""Pasupati Acrylon Ltd (BSE 500456 / NSE PASUPTAC) - document inputs for the model.
Annual figures in Rs. LAKH as printed (builder converts to Rs. crore = lakh / 100). Quarterly figures in Rs. CRORE as printed.
Basis: standalone (the company has no subsidiary, associate or JV - AR FY26 p.13 / Res Q2FY27 note 4). FY = April-March.
Each series: (values FY17..FY26, source text). Printed page numbers: AR FY17-FY24 printed = PDF - 3; AR FY25-FY26 printed = PDF - 4.
FY17 is the Ind AS restated comparative in AR FY18 (the FY17 AR itself was Indian GAAP, revenue net of excise 46,086.62).
"""
YRS = ['FY17', 'FY18', 'FY19', 'FY20', 'FY21', 'FY22', 'FY23', 'FY24', 'FY25', 'FY26']

SRC_PL = {'FY17': 'AR FY18 p.37 (Ind AS comparative)', 'FY18': 'AR FY18 p.37', 'FY19': 'AR FY19 p.46', 'FY20': 'AR FY20 p.51',
          'FY21': 'AR FY21 p.49', 'FY22': 'AR FY22 p.59', 'FY23': 'AR FY23 p.53', 'FY24': 'AR FY24 p.60', 'FY25': 'AR FY25 p.59', 'FY26': 'AR FY26 p.54'}
SRC_BS = {'FY17': 'AR FY18 p.36', 'FY18': 'AR FY18 p.36', 'FY19': 'AR FY19 p.45', 'FY20': 'AR FY20 p.50', 'FY21': 'AR FY21 p.48',
          'FY22': 'AR FY22 p.58', 'FY23': 'AR FY23 p.52', 'FY24': 'AR FY24 p.59', 'FY25': 'AR FY25 p.58', 'FY26': 'AR FY26 p.53'}
SRC_CF = {'FY17': 'AR FY18 p.38', 'FY18': 'AR FY18 p.38', 'FY19': 'AR FY19 p.47', 'FY20': 'AR FY20 p.52', 'FY21': 'AR FY21 p.50',
          'FY22': 'AR FY22 p.60', 'FY23': 'AR FY23 p.54', 'FY24': 'AR FY24 p.61', 'FY25': 'AR FY25 p.60', 'FY26': 'AR FY26 p.55'}

# ---------------- P&L (Rs. lakh) ----------------
PL = {
    'rev_gross': [50203.48, 57949.01, 82531.12, 66364.36, 50544.66, 77553.75, 82796.06, 57522.82, 62143.18, 101015.78],
    'excise': [3774.72, 943.51, 0, 0, 0, 0, 0, 0, 0, 0],          # inside other expenses pre-GST (AR FY18 p.58)
    'rm': [31599.41, 41772.49, 65155.81, 54589.67, 33269.58, 59752.73, 63102.06, 43464.97, 47771.83, 67336.78],
    'purch': [19.48, 21.89, 16.91, 4.30, 9.36, 22.16, 0, 7.48, 0, 19.87],
    'inv': [-1587.38, 224.71, 811.97, -2926.25, 1919.53, 201.09, -1259.14, 1271.78, -2188.87, 3567.50],
    'emp': [1937.70, 2217.63, 2434.73, 2307.87, 2253.29, 2399.18, 2491.85, 2488.86, 2856.73, 3498.93],
    'oth_tot': [11919.57, 8173.45, 9341.54, 9829.19, 7114.60, 8930.63, 13483.11, 8681.75, 9220.30, 15480.82],
    'pf': [3448.32, 4199.76, 5623.96, 5200.73, 3945.52, 5590.67, 9239.82, 5372.88, 5271.50, 8294.11],
    'fin': [573.42, 464.32, 816.83, 498.96, 377.65, 316.77, 360.93, 257.73, 249.62, 1237.39],
    'dep': [686.23, 524.34, 575.97, 665.54, 625.56, 621.09, 614.50, 586.99, 598.60, 1248.76],
    'oi': [791.78, 469.26, 934.74, 644.39, 878.08, 873.41, 841.86, 1076.95, 1136.90, 867.26],
    'exc': [541.10, 651.14, 0, 0, 0, 0, 0, 0, 0, 56.89],
    'tax': [1883.42, 1567.71, 1574.24, 734.49, 1548.32, 1593.85, 1253.56, 521.22, 1233.75, 2444.69],
    'pbt_rep': [5305.73, 4368.30, 4312.10, 2039.46, 5853.17, 6183.51, 4844.61, 1840.21, 4771.87, 9436.10],
    'pat_rep': [3422.31, 2800.59, 2737.86, 1304.96, 4304.85, 4589.66, 3591.05, 1318.99, 3538.12, 6991.41],
    'eps_rep': [3.84, 3.14, 3.07, 1.46, 4.83, 5.15, 4.03, 1.48, 3.97, 7.84],
}
PL_SRC_EXTRA = {
    'excise': 'Excise duty inside other expenses: AR FY18 p.58 (3,774.72 FY17; 943.51 Apr-Jun 2017 before GST). Revenue shown net of it.',
    'pf': 'Power & fuel (note "Other expenses"): AR FY18 p.58, FY19 p.67, FY20 p.72, FY21 p.69, FY22 p.80, FY23 p.74, FY24 p.81, FY25 p.81, FY26 p.76.',
    'exc': 'FY17-FY18: CDR exit recompense to lenders (AR FY18 p.59); FY26: new labour codes past service cost (AR FY26 p.74).',
}
SHARES = 8.9133121   # crore shares (8,91,33,121; AR FY26 p.67)

# ---------------- Balance sheet (Rs. lakh) ----------------
BS = {
    'ppe': [3077.11, 6122.34, 8507.31, 8017.91, 8462.60, 8077.29, 7712.13, 7520.02, 25021.51, 24858.57],
    'cwip': [3227.94, 310.61, 0, 43.78, 0, 0, 55.29, 7741.42, 3.71, 24.25],
    'onca': [674.55, 1799.13, 598.32, 711.64, 589.91, 405.76, 525.34, 2012.60, 1089.59, 2139.62],   # other fin. assets NC + DTA + other NCA + inv. property
    'invy': [10069.58, 11691.54, 9066.91, 11142.33, 11220.39, 14355.89, 19435.80, 11594.22, 13519.27, 10339.94],
    'cinv': [3333.42, 4096.54, 3054.48, 0, 2544.37, 0, 7469.55, 8517.19, 8035.70, 8780.35],
    'recv': [3218.85, 4691.68, 6753.99, 3492.09, 5498.78, 7782.44, 5088.73, 5592.77, 4978.36, 7782.74],
    'cash': [789.38, 2751.96, 6426.44, 8610.60, 6475.72, 7269.61, 2173.99, 3486.55, 2165.76, 4259.95],
    'bank': [0, 0, 0, 0, 0, 3273.86, 1528.20, 1654.45, 1475.74, 1958.20],   # other bank balances (FY17-FY21 inside other current financial assets)
    'oca': [3101.50, 1622.35, 2334.69, 3897.72, 2289.86, 1362.53, 1854.32, 1783.90, 3246.94, 3618.69],
    'scap': [8914.10, 8914.10, 8914.10, 8914.10, 8914.10, 8914.10, 8914.10, 8914.10, 8914.10, 8913.31],
    'oeq': [3261.50, 6041.94, 8756.08, 10080.59, 14432.26, 19037.92, 22654.57, 23962.82, 27499.91, 34629.40],
    'ltb': [214.72, 70.88, 40.46, 7.54, 1.12, 0, 0, 4355.56, 10142.02, 9638.64],
    'stb': [2813.88, 610.33, 358.96, 1131.18, 425.59, 5.87, 12.96, 67.42, 632.73, 1071.60],   # incl. current maturities / other fin. liabilities (FY17-FY21)
    'tp': [9048.77, 14111.98, 14745.98, 11589.25, 10746.98, 11449.11, 12175.42, 10148.55, 9015.05, 5711.74],
    'ncl': [263.97, 461.51, 795.26, 916.94, 888.81, 941.22, 975.01, 1160.76, 2035.19, 1943.62],     # NC provisions + DTL + other NCL
    'ocl': [2975.39, 2875.41, 3131.30, 3276.47, 1672.78, 2179.16, 1111.29, 1293.91, 1297.58, 1854.00],  # other current liabilities + provisions + current tax
    'ta_rep': [27492.33, 33086.15, 36742.14, 35916.07, 37081.64, 42527.38, 45843.35, 49903.12, 59536.58, 63762.31],
}
BS_NOTE = ('Grouping of reported lines: other non-current assets = other financial assets + deferred tax asset + other NCA + investment property; '
           'other current assets = other current financial assets + current tax assets + other current assets; short-term borrowings include '
           'current maturities and (FY17-FY21) other current financial liabilities; non-current liabilities other = NC provisions + deferred tax + other NCL; '
           'other current liabilities = other CL + current provisions + current tax liabilities. FY17 = Ind AS opening comparative in AR FY18 p.36.')

# ---------------- Cash flow (Rs. lakh) ----------------
CF = {
    'cfo': [4138.25, 6726.58, 5900.08, -181.26, 1349.50, -1316.84, 3002.35, 7271.22, 671.41, 5150.22],
    'capex': [-2463.72, -1561.22, -2650.33, -467.65, -827.82, -235.78, -411.63, -9450.12, -8925.03, -1604.41],  # PPE + capital advances + inv. property
    'int_paid': [-573.42, -464.32, -816.83, -498.96, -377.65, -316.77, -360.93, -257.73, -183.23, -1241.51],
    'net_borr': [813.34, -2115.53, -365.77, -18.35, 54.30, -83.00, 7.09, 4462.25, 6345.63, -70.66],
    'div': [0] * 10,
    'cfi': [-3912.30, -2184.15, -1042.99, 2882.74, -3161.03, 2510.49, -7744.13, -10163.17, -8154.66, -1743.86],
    'cff': [239.92, -2579.85, -1182.61, -517.32, -323.35, -399.77, -353.84, 4204.52, 6162.40, -1312.17],
    'net': [465.87, 1962.58, 3674.49, 2184.16, -2134.88, 793.88, -5095.62, 1312.56, -1320.79, 2094.19],
}

# ---------------- Segments (Rs. lakh) ----------------
SEG = {
    'rev_fib': [46428.76, 56178.88, 78387.93, 60998.15, 45621.31, 67565.13, 71928.27, 49743.47, 53810.27, 58703.05],   # FY17-FY18 net of excise
    'rev_cpp': [0, 826.62, 4143.19, 5366.21, 4923.36, 9988.62, 10867.79, 7779.35, 8066.67, 9890.46],
    'rev_eth': [0, 0, 0, 0, 0, 0, 0, 0, 266.24, 32422.27],
    'res_fib': [6420.25, 5528.32, 5100.82, 2264.76, 5800.73, 5648.45, 5911.98, 2510.22, 5047.77, 6596.39],   # FY17 = company EBIT incl. OI (single segment)
    'res_cpp': [0, -44.55, 28.11, 273.66, 430.10, 851.82, -706.44, -412.28, -30.62, 763.44],
    'res_eth': [0, 0, 0, 0, 0, 0, 0, 0, 4.34, 3370.55],
    'dep_fib': [None, None, None, None, 421.07, 373.20, 354.49, 311.08, 310.82, 347.82],
    'dep_cpp': [None, None, None, None, 204.49, 247.88, 260.01, 275.91, 275.91, 276.16],
    'dep_eth': [None, None, None, None, 0, 0, 0, 0, 11.87, 624.78],
    'ass_fib': [None, 28071.04, 29741.75, 29352.67, 28838.04, 32483.46, 37623.22, 33487.73, 31140.37, 30361.49],
    'ass_cpp': [None, 5015.11, 7000.39, 6563.40, 8243.60, 10043.93, 8220.13, 7122.95, 7473.08, 8273.55],
    'ass_eth': [None, None, None, None, None, None, None, 9292.44, 20923.13, 25127.27],
    'geo_in': [None, None, None, None, None, None, 73056.64, 52884.81, 56513.08, 97824.34],
    'geo_out': [None, None, None, None, None, None, 9739.42, 4638.01, 5630.10, 3191.44],
}
SEG_SRC = {'FY17': 'single segment; AR FY18 p.37 (EBIT = PBT before exceptional + finance cost)', 'FY18': 'AR FY18 p.65', 'FY19': 'AR FY19 p.70',
           'FY20': 'AR FY20 p.76', 'FY21': 'AR FY21 p.73', 'FY22': 'AR FY22 p.84', 'FY23': 'AR FY23 p.78', 'FY24': 'AR FY24 p.85-86',
           'FY25': 'AR FY25 p.85', 'FY26': 'AR FY26 p.81'}

# ---------------- Operating data ----------------
OPS = {
    'fib_cap': [42000] * 10,          # MTPA; AR FY24 p.15, FY25 p.16, FY26 p.11; CARE 2022-2026. AR FY23 p.10 says 45,000 (conflict)
    'fib_prod': [38918, 37429, 43462, 41250, 29826, 29652, 36425, 31534, 35198, 35212],
    'fib_sale': [37515, 38811, 44505, 38771, 31335, 30918, 35260, 31685, 33850, 37878],
    'fib_exp': [14187, 9300, 12379, 12062, 6549, 1415, None, None, 2604, 741],
    'cpp_cap': [0, 2917, 5014, 10000, 10000, 10000, 10000, 10000, 10000, 10000],   # 5,000 from 1-Sep-2017 (7/12 of year in FY18), +5,000 from 26-Mar-2019
    'cpp_prod': [None, None, None, 4531, 3757, 6348, 7663, 6463, 6343, 7545],
    'cpp_sale': [None, None, None, 4420, 3868, 6210, 7640, 6476, 6409, 7621],
    'eth_cap_kl': [0, 0, 0, 0, 0, 0, 0, 0, 7 * 150, 150 * 330],   # KL/yr: 150 KLPD from 25-Mar-2025 (7 days in FY25); FY26 at 330 days
    'eth_prod': [0, 0, 0, 0, 0, 0, 0, 0, 790, 41923],
    'eth_sale': [0, 0, 0, 0, 0, 0, 0, 0, 440, 41162],
    'acn': [27404.67, 36839.65, 55801.23, 44729.25, 25819.48, 45206.45, 44068.13, 31796.76, 35649.84, 32649.14],   # Rs lakh consumed
    'vam': [1896.81, 1849.47, 2969.09, 2231.21, 1733.91, 3339.18, 2332.21, 2289.76, 2227.85, 2205.18],
    'homo': [None, None, None, None, 2202.11, 5429.07, 6411.20, 4378.50, 4520.06, 5001.83],
    'grain': [0, 0, 0, 0, 0, 0, 0, 0, 573.81, 22388.64],
    'emp_no': [487, 492, 481, 465, 439, 442, 424, 433, 514, 540],
    'top10': [None, None, None, None, None, 0.55, 0.6057, 0.5899, 0.59, 0.41],
}
OPS_SRC = {
    'fib_prod': 'Board report / MD&A: AR FY17 p.8, FY18 p.7, FY19 p.7, FY20 p.10, FY21 p.10, FY22 p.19, FY23 p.10, FY24 p.15, FY25 p.16, FY26 p.11',
    'fib_sale': 'Same pages. FY18 sale 38,811 MT in AR FY18 p.7 but 38,590 MT in AR FY19 p.7 (conflict; FY18 AR used). FY21 31,335 MT (CARE says 31,361).',
    'fib_exp': 'AR FY17 p.12, FY18 p.12, FY19 p.17, FY20 p.22, FY21 p.24, FY22 p.19, FY25-FY26 AR FY26 p.9 (MT; FY23-FY24 tonnes not given)',
    'cpp': 'CPP commercial production 1-Sep-2017 (AR FY18 p.7), 10,000 MT from 26-Mar-2019 (AR FY19 p.7); volumes AR FY20 p.11, FY21 p.11, FY22 p.19, FY23 p.10, FY24 p.16, FY25 p.16, FY26 p.11 (FY18-FY19 volumes not disclosed)',
    'eth': '150 KLPD grain distillery, COD 24/25-Mar-2025 (BSE 24-Mar-2025; AR FY26 p.82 note 45); consents for 180 KLPD received (AR FY26 p.11); volumes AR FY25 p.16, FY26 p.11',
    'acn': 'Raw materials consumed, major heads: AR FY18 p.55, FY19 p.64, FY20 p.69, FY21 p.66, FY22 p.77, FY23 p.71, FY24 p.78, FY25 p.78, FY26 p.73',
    'emp_no': 'Permanent employees on rolls (FY17-FY24: AR FY17 p.16, FY18 p.16, FY19 p.25, FY20 p.30, FY21 p.25, FY22 p.33, FY23 p.26, FY24 p.32); FY25 rolls 514 (AR FY25 p.31); FY26 average 540 (AR FY26 p.12)',
    'top10': 'Top-10 customers share of sales: CARE Aug-2022 p.1 (FY22), Aug-2023 p.2 (FY23), Jul-2024 p.2 (FY24), Jul-2025 p.2 (FY25), Jun-2026 p.2 (FY26)',
}
# CARE-reported per kg figures (cross-check of our derived numbers)
CARE_KG = {
    'acn_price': {'FY21': 97.47, 'FY22': 171.57},            # Rs/kg, CARE Aug-2022 p.2
    'asf_real': {'FY21': 145.47, 'FY22': 218.53, 'FY23': 205.12, 'FY24': 157.0},   # CARE Aug-2022 p.2, Aug-2023 p.2, Jul-2024 p.2
    'cpp_real': {'FY21': 126.3, 'FY22': 160.85, 'FY23': 143.42, 'FY24': 120.12},
    'acn_usd': 'ACN ~USD 1,700/t Jan-Feb 2022, 1,400-1,500 till Mar-2023, low USD 900/t Jun-2023 (CARE Aug-2023 p.2); USD 1,250-1,350/t in H2FY24 (CARE Jul-2024 p.2)',
}
ACN_FACTOR = 0.889   # kg ACN per kg fibre produced: ACN cost / (CARE ACN price x production) = 0.888 FY21, 0.889 FY22 [E, calibrated]

# ---------------- Quarterly (Rs. crore) Q3FY24 .. Q2FY27 ----------------
Q = ['Q3FY24', 'Q4FY24', 'Q1FY25', 'Q2FY25', 'Q3FY25', 'Q4FY25', 'Q1FY26', 'Q2FY26', 'Q3FY26', 'Q4FY26', 'Q1FY27', 'Q2FY27']
QD = {  # rev, oi, rm, inv, emp, fin, dep, oth, exc, pbt_rep, tax, pat_rep, fib, cpp, eth, r_fib, r_cpp, r_eth
    'Q3FY24': [156.06, 2.35, 116.17, -0.81, 6.48, 0.58, 1.55, 21.75, 0, 12.69, 3.60, 9.09, 136.49, 19.57, 0, 14.53, -1.26, 0],
    'Q4FY24': [176.77, 2.83, 122.08, 11.61, 6.39, 0.61, 1.53, 20.35, 0, 17.03, 4.52, 12.51, 154.43, 22.34, 0, 17.91, -0.27, 0],
    'Q1FY25': [154.80, 3.07, 126.04, -12.12, 7.17, 0.46, 1.44, 19.78, 0, 15.10, 3.85, 11.25, 133.27, 21.53, 0, 16.99, -1.43, 0],
    'Q2FY25': [124.44, 2.09, 90.50, 1.96, 6.63, 0.55, 1.48, 21.69, 0, 3.72, 0.99, 2.73, 106.13, 18.31, 0, 4.18, 0.09, 0],
    'Q3FY25': [173.87, 2.52, 121.85, 8.46, 7.28, 0.65, 1.49, 23.01, 0, 13.65, 3.52, 10.13, 152.93, 20.94, 0, 13.91, 0.39, 0],
    'Q4FY25': [168.32, 3.69, 139.33, -20.19, 7.49, 0.84, 1.58, 27.71, 0, 15.25, 3.98, 11.27, 145.77, 19.89, 2.66, 15.41, 0.64, 0.04],
    'Q1FY26': [216.05, 2.69, 154.96, 11.34, 7.79, 3.32, 2.99, 35.94, 0, 2.40, 0.65, 1.75, 137.12, 23.12, 55.81, 6.37, -0.30, -0.35],
    'Q2FY26': [280.25, 1.35, 194.60, 4.89, 8.45, 3.63, 3.11, 45.16, 0, 21.76, 5.56, 16.20, 137.98, 26.77, 115.50, 10.66, 1.63, 13.10],
    'Q3FY26': [269.23, 2.32, 188.79, -9.10, 9.35, 3.43, 3.20, 40.99, 0.57, 34.32, 8.63, 25.69, 145.60, 25.44, 98.19, 21.15, 2.52, 14.65],
    'Q4FY26': [244.63, 2.31, 135.22, 28.55, 9.40, 1.99, 3.19, 32.71, 0, 35.88, 9.60, 26.28, 166.34, 23.57, 54.72, 27.78, 3.78, 6.31],
    'Q1FY27': [238.26, 3.07, 202.43, -50.42, 9.84, 2.26, 3.15, 37.38, 0, 36.69, 9.30, 27.39, 143.66, 31.65, 62.95, 28.79, 3.52, 6.64],
    'Q2FY27': [274.74, 1.80, 176.71, 6.10, 10.34, 1.64, 3.25, 36.02, 0, 42.48, 10.47, 32.01, 170.71, 33.65, 70.38, 28.78, 4.42, 10.92],
}
QSRC = {'Q3FY24': 'Res Q4FY24 p.1-2', 'Q4FY24': 'Res Q4FY24 p.1-2', 'Q1FY25': 'Res Q1FY26 p.1-2', 'Q2FY25': 'Res Q2FY25 p.1-2',
        'Q3FY25': 'Res Q3FY26 p.1-2', 'Q4FY25': 'Res Q4FY26 p.1-2', 'Q1FY26': 'Res Q1FY26 p.1-2', 'Q2FY26': 'Res Q2FY27 p.2-3',
        'Q3FY26': 'Res Q3FY26 p.1-2', 'Q4FY26': 'Res Q4FY26 p.1-2', 'Q1FY27': 'Res Q2FY27 p.2-3', 'Q2FY27': 'Res Q2FY27 p.2-3'}
# Sep-2026 balance sheet (Rs crore), Res Q2FY27 p.4
BS_SEP26 = {'ppe': 244.66, 'cwip': 17.53, 'onca': 17.11, 'invy': 194.88, 'cinv': 53.03, 'recv': 105.45, 'cash': 21.31, 'bank': 18.02, 'oca': 46.91,
            'scap': 89.13, 'oeq': 405.73, 'ltb': 90.18, 'stb': 11.93, 'tp': 79.23, 'ncl': 22.03, 'ocl': 20.67, 'ta': 718.90}

# ---------------- Market ----------------
CMP = 67.95            # Rs, close 27-Nov-2026 (Screener price series; investor to replace with Bloomberg)
CMP_DATE = '27-Nov-2026'
HI52, LO52 = 84.28, 40.89
PEERS = [  # name, segment, mcap Rs cr, P/E (Screener 27/28-Nov-2026), FY26 sales, FY26 OPM, note
    ('Vardhman Acrylics', 'Acrylic fibre', 319, 7.07, 319, 0.05, '21,000 TPA (Screener key insight); net cash'),
    ('Indian Acrylics', 'Acrylic fibre', 68.2, None, 352, -0.003, 'loss-making; 45,000 TPA, ~31% utilisation (Screener)'),
    ('Cosmo First', 'Films (BOPP/CPP/BOPET)', 2098, 15.5, 3356, 0.09, ''),
    ('Jindal Poly Films', 'Films', 2725, None, 697, -0.81, 'not meaningful (losses)'),
    ('Polyplex Corp', 'Films (PET)', 3292, 50.6, 1497, 0.05, 'trough earnings'),
    ('Uflex', 'Films + packaging', 4242, 22.9, 7778, 0.11, ''),
    ('Gulshan Polyols', 'Grain ethanol + chemicals', 987, 5.78, 2312, 0.10, ''),
    ('Globus Spirits', 'Grain ethanol + alcohol', 2327, 24.4, 2708, 0.10, 'consumer alcohol brands lift the multiple'),
]
