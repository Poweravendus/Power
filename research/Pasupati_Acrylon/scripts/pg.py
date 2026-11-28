"""Print PDF pages of a pdftotext -layout file. Usage: python3 -I pg.py <txtfile> <p1>[-p2] [width]  (1-based PDF page)"""
import sys
t = open(sys.argv[1], errors='replace').read().split('\f')
a = sys.argv[2]; w = int(sys.argv[3]) if len(sys.argv) > 3 else 200
p1, p2 = (map(int, a.split('-')) if '-' in a else (int(a), int(a)))
for p in range(p1, p2 + 1):
    print(f'=================== PDF page {p} ===================')
    for line in t[p - 1].splitlines():
        if line.strip(): print(line[:w])
