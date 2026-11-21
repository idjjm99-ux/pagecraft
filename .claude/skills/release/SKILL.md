---
name: release
description: PageCraft 릴리스 — 회귀 시험·옛/새 판 비교·결과 기록·Lite/Source zip·커밋. 사용법 /release 12.46.0
disable-model-invocation: true
---

# 릴리스

인자: `$ARGUMENTS` = 새 버전(예 12.46.0). 새 판 `build/PageCraft_v<새>_Lite.html`, 직전 판은 `bash tools/unpack.sh` 로 준비.

1. **회귀 시험**(오래 걸림 → Bash `run_in_background`):
   `cd tests && bash run.sh ../build/PageCraft_v<새>_Lite.html v<새>` — 새 t_vXX.py도 함께 실행
   - 회귀 시험의 버전 검사가 옛 버전 문자열을 요구하면 README 지침대로 버전 문자열만 바꿔 실행
2. **비교 시험**: `regression-comparer` 에이전트에 직전 판·새 판 경로를 넘겨 keytest·keyseq·cssdump 비교 요약을 받음.
   의도한 변경 외 차이가 있으면 멈추고 사용자에게 보고
3. **결과 기록** `tests/result_v<새>.txt`: 기존 result 파일 형식(통과 수·차이 0·미검증 항목)을 따름. 실패는 숨기지 말고 그대로
4. **묶기**:
   - `releases/v<새>/PageCraft_v<새>_Lite.zip` ← Lite html 하나
   - `releases/v<새>/PageCraft_v<새>_Source.zip` ← README.md, patch/, tests/ (`__pycache__`·`out_*` 제외)
5. **커밋·푸시**: 사용자가 요청했을 때만. 실패한 시험이 있으면 커밋 전에 확인받기
