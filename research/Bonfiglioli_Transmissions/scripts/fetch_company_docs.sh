#!/bin/bash
# Download every PDF linked from bonfiglioli.in Investor_Relations subpages (urls.txt), resume with -C -, dedupe by md5.
OUT=$1; LIST=$2
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
mkdir -p "$OUT"
while read -r u; do
  n=$(python3 -I -c "import sys,urllib.parse;print(urllib.parse.unquote(sys.argv[1].rsplit('/',1)[1]).replace(' ','_').replace(',','').replace('(','').replace(')','').replace(\"'\",''))" "$u")
  curl -s -C - -m 600 -A "$UA" -L -o "$OUT/$n" "$u" || echo "FAIL $u"
  echo "$n $(stat -c %s "$OUT/$n") $(file -b "$OUT/$n" | cut -c1-20)"
done < "$LIST"
md5sum "$OUT"/* | sort | awk '{if($1==p){print "DUP",$2}else{p=$1}}'
