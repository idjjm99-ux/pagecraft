#!/bin/bash
# 최신(또는 지정) 릴리스의 Lite HTML을 build/에 풀어 패치 기준본으로 준비
# usage: tools/unpack.sh [버전, 예: 12.45.0]
set -e
cd "$(dirname "$0")/.."
V=${1:-$(ls releases | sed 's/^v//' | sort -V | tail -1)}
Z=releases/v$V/PageCraft_v${V}_Lite.zip
[ -f "$Z" ] || { echo "없음: $Z"; exit 1; }
mkdir -p build && unzip -q -o "$Z" -d build
echo "build/PageCraft_v${V}_Lite.html"
