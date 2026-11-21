#!/bin/bash
# PreToolUse(Edit|Write|MultiEdit): 완성본 HTML·릴리스 zip 직접 수정 차단 → 패치 스크립트로만 변경
f=$(python3 -c 'import json,sys;print(json.load(sys.stdin).get("tool_input",{}).get("file_path",""))')
case "$f" in
  *_Lite.html|*_Full.html|*/releases/*)
    echo "차단: $f 는 직접 고치지 않습니다. patch/patch_vXXXXX.py 를 만들어 빌드하세요(/new-patch)." >&2
    exit 2;;
esac
exit 0
