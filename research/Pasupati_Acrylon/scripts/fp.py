"""Find which PDF pages of a pdftotext file match a regex. Usage: python3 -I fp.py <txtfile> <regex>"""
import sys, re
t = open(sys.argv[1], errors='replace').read().split('\f')
rx = re.compile(sys.argv[2], re.I)
for i, pg in enumerate(t):
    for line in pg.splitlines():
        if rx.search(line): print(f'p{i+1}: {line.strip()[:180]}')
