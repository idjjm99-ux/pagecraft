#!/bin/bash
# usage: run.sh <html> <tag>
H=$1; T=$2; mkdir -p out_$T
for t in t_v40 t_v41 t_v42 t_v43 t_v44 chart_audit; do
  timeout 900 python3 -I $t.py "$H" > out_$T/$t.txt 2>&1; echo "$t: $(grep -E '^== ' out_$T/$t.txt | tail -1) fails=$(grep -c '^FAIL' out_$T/$t.txt)"
done
