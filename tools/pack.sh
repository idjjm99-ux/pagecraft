#!/bin/bash
# 릴리스 zip 2개 만들기: Lite(완성본 html 하나) · Source(README·CLAUDE.md·docs·patch·tests·tools)
# usage: bash tools/pack.sh 12.49.0   (build/PageCraft_v12.49.0_Lite.html 필요)
set -e
cd "$(dirname "$0")/.."
V=$1; [ -n "$V" ] || { echo "usage: tools/pack.sh <버전>"; exit 1; }
H=build/PageCraft_v${V}_Lite.html; [ -f "$H" ] || { echo "없음: $H"; exit 1; }
D=releases/v$V; [ -e "$D" ] && { echo "이미 있음: $D (덮어쓰지 않음)"; exit 1; }
mkdir -p "$D"
(cd build && zip -q -X "../$D/PageCraft_v${V}_Lite.zip" "PageCraft_v${V}_Lite.html")
# 시험 부산물(캡처 그림·PPT 출력·결과 폴더)은 빼고 넣음 — .gitignore와 같은 기준
zip -q -X -r "$D/PageCraft_v${V}_Source.zip" README.md CLAUDE.md docs patch tests tools \
  -x '*/__pycache__/*' '*.pyc' 'tests/out_*' 'tests/out_*/*' '*/node_modules/*' 'tests/*.png' 'tests/*.pptx'
ls -la "$D"
# 점검: Source 안 큰 파일(100KB 넘음)이 있으면 알림
unzip -Z1 "$D/PageCraft_v${V}_Source.zip" >/dev/null && unzip -l "$D/PageCraft_v${V}_Source.zip" | awk '$1 ~ /^[0-9]+$/ && $4!="" && $1>102400{print "  큰 파일 확인:",$1,$4; n++} END{if(!n)print "  Source: 100KB 넘는 파일 없음"}'
