#!/bin/bash
# Download Pasupati Acrylon documents listed in a "name url" file into OUT; resume with -C -; dedupe by md5.
# Usage: fetch_docs.sh <out_dir> <list_file>
OUT=$1; LIST=$2
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
mkdir -p "$OUT"
while read -r n u; do
  [ -z "$n" ] && continue
  if [ -s "$OUT/$n" ] && file -b "$OUT/$n" | grep -q PDF; then echo "have $n"; continue; fi
  curl -s -C - -m 600 -A "$UA" -e "https://www.bseindia.com/" -L -o "$OUT/$n" "$u" || echo "FAIL $n $u"
  echo "$n $(stat -c %s "$OUT/$n" 2>/dev/null) $(file -b "$OUT/$n" | cut -c1-25)"
done < "$LIST"
md5sum "$OUT"/*.pdf 2>/dev/null | sort | awk '{if($1==p){print "DUP",$2}else{p=$1}}'
