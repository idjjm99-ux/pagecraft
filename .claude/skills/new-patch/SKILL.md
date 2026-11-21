---
name: new-patch
description: PageCraft 새 버전 패치 뼈대 만들기(기준 버전 검사·버전 문자열 3곳·README 한 줄). 사용법 /new-patch 12.46.0 "한 줄 요약"
disable-model-invocation: true
---

# 새 패치 만들기

인자: `$ARGUMENTS` = `<새 버전> "<한 줄 요약>"`

1. 기준본 준비: `bash tools/unpack.sh` → 출력된 `build/PageCraft_v<직전>_Lite.html` 경로 사용
   (직전 버전을 이미 이 세션에서 빌드했다면 그 파일을 기준으로)
2. 뼈대 생성: `python3 -I tools/new_patch.py <기준.html> <새 버전> "<요약>"`
   → `patch/patch_vXXXXX.py` + README 한 줄
3. 패치 본문 작성 규칙
   - 모든 교체는 `R(old, new, n)` — 횟수가 다르면 실패하므로 old는 유일한 문자열로
   - CSS: `<style id="pc-ui-css">` 안 해당 구역 규칙을 직접 고침. 맨 아래 새 블록 덧붙이기·`!important` 덧칠 금지
   - 새 JS에는 `/*pc-vXXXXX*/` 표시를 넣어 '이미 적용' 검사가 작동하게
   - 완성본 HTML은 절대 직접 수정하지 않음(훅이 차단)
4. 빌드: `python3 -I patch/patch_vXXXXX.py build/<직전>.html build/PageCraft_v<새>_Lite.html`
5. 시험 `tests/t_vXX.py` 작성(`from h import H` 패턴, `OK`/`FAIL` 줄 + 마지막 `== n/m 통과`)
6. 다음 단계는 `/release <새 버전>`
