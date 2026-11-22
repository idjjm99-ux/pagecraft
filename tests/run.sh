#!/bin/bash
# 회귀 시험 전부: python(t_v40~44·chart_audit) + node(t_v46 이후 t_v*.js 자동)
# usage: bash tests/run.sh <Lite.html> [tag]   → 결과 tests/out_<tag>/*.txt, 마지막 줄 합계
# 필요: pip install playwright (브라우저 설치 불필요, pcenv.py가 크롬을 찾음), node + playwright
H=$(realpath -e "$1" 2>/dev/null) || { echo "없음: $1"; exit 1; }
cd "$(dirname "$0")"
T=${2:-$(basename "$H" .html)}; O=out_$T; mkdir -p "$O"
bad=0
line() { # $1=이름 $2=출력파일
  # 요약 줄 형식: '== n/m 통과'(js) · 'TOTAL n / m'(py) · 'CHARTS n BAD m'(chart_audit)
  local s f; s=$(grep -E '^(== |TOTAL |CHARTS )' "$2" | tail -1); f=$(grep -cE '^FAIL' "$2")
  [[ "$s" =~ BAD\ ([0-9]+) ]] && f=$((f+BASH_REMATCH[1]))
  [[ "$s" =~ TOTAL\ ([0-9]+)\ /\ ([0-9]+) ]] && [ "${BASH_REMATCH[1]}" != "${BASH_REMATCH[2]}" ] && [ "$f" = 0 ] && f=1
  printf '%-12s %-18s fails=%s\n' "$1" "${s:-'(요약 없음)'}" "$f"
  [ "$f" = 0 ] && [ -n "$s" ] || bad=$((bad+1))
}
for t in t_v40 t_v41 t_v42 t_v43 t_v44 chart_audit; do
  timeout 900 python3 -I $t.py "$H" > "$O/$t.txt" 2>&1; line $t "$O/$t.txt"
done
for t in $(ls t_v*.js | sort -V); do
  n=${t%.js}; timeout 900 node $t "$H" > "$O/$n.txt" 2>&1; line $n "$O/$n.txt"
done
echo "== 실패한 시험 묶음: $bad"
exit $bad
