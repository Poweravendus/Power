import sys,re
# usage: fp.py file offset "phrase" -> printed pages containing phrase (whitespace-insensitive)
f,off=sys.argv[1],int(sys.argv[2]); pages=open(f).read().split('\f')
for ph in sys.argv[3:]:
    pat=re.compile(r'\s+'.join(map(re.escape,ph.split())),re.I)
    print(ph,'->',[i+1-off for i,p in enumerate(pages) if pat.search(p)][:12])
