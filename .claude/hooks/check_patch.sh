#!/bin/bash
# PostToolUse(Edit|Write|MultiEdit): patch/·tests/ 파이썬 문법 검사 + 패치에 !important 새로 추가 시 경고
read -r -d '' IN
f=$(printf '%s' "$IN" | python3 -c 'import json,sys;print(json.load(sys.stdin).get("tool_input",{}).get("file_path",""))')
case "$f" in
  */patch/*.py|*/tests/*.py)
    out=$(python3 -m py_compile "$f" 2>&1) || { echo "문법 오류: $out" >&2; exit 2; }
    rm -rf "$(dirname "$f")/__pycache__"
    if [[ "$f" == */patch/patch_v*.py ]]; then
      # 이번 수정에서 늘어난 !important 개수(Edit: new-old, MultiEdit: 합, Write: 파일 전체 - old 문자열 R("...") 안 것도 포함되므로 참고용)
      added=$(printf '%s' "$IN" | python3 -c '
import json,sys
t=json.load(sys.stdin).get("tool_input",{}); k="!important"
eds=t.get("edits") or ([t] if "new_string" in t else [])
print(sum(e.get("new_string","").count(k)-e.get("old_string","").count(k) for e in eds) if eds else 0)')
      if [ "${added:-0}" -gt 0 ]; then
        echo "경고: $f 에 !important 가 ${added}개 새로 들어갔습니다. 규칙: 덧칠 금지, pc-ui-css 안 해당 구역 규칙을 직접 고칠 것. 꼭 필요하면 이유를 사용자에게 설명하세요." >&2
        exit 2
      fi
    fi;;
esac
exit 0
