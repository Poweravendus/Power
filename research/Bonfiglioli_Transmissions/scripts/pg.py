import sys
# usage: pg.py file offset printed_page [n_pages]
f,off,p=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]); n=int(sys.argv[4]) if len(sys.argv)>4 else 1
pages=open(f).read().split('\f')
for q in range(p,p+n):
    print(f'######## printed {q} (pdf {q+off})'); print(pages[q+off-1])
