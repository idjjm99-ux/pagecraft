---
name: release
description: PageCraft 릴리스 — 회귀 시험·옛/새 판 비교·결과 기록·Lite/Source zip·커밋. 사용법 /release 12.49.0
disable-model-invocation: true
---

# 릴리스

인자: `$ARGUMENTS` = 새 버전. 새 판 `build/PageCraft_v<새>_Lite.html`, 직전 판은 `bash tools/unpack.sh`로 준비.

1. **회귀 시험**(약 10분 → Bash `run_in_background`): `bash tests/run.sh build/PageCraft_v<새>_Lite.html`
   - python t_v40~44·chart_audit + node t_v*.js 전부. 마지막 줄 `실패한 시험 묶음: 0`이어야 함
2. **비교 시험**: `regression-comparer` 에이전트에 직전 판·새 판 경로 → keytest·keyseq·cssdump 차이 요약.
   의도한 변경 외 차이가 있으면 멈추고 사용자에게 보고
3. **결과 기록** `tests/result_v<새>.txt`: 기존 형식(통과 수·차이·미검증). 실패는 그대로 적기
4. **CHANGELOG·README**: `docs/CHANGELOG.md` 줄 다듬기, README의 '최신'·계보 갱신
5. **묶기**: `bash tools/pack.sh <새>` → `releases/v<새>/` Lite·Source zip
6. **커밋·푸시**: 사용자가 요청했을 때만. 실패한 시험이 있으면 커밋 전에 확인받기
