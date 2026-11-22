---
name: new-patch
description: PageCraft 새 버전 패치·시험 뼈대 만들기(기준 버전 검사·버전 문자열·CHANGELOG 한 줄). 사용법 /new-patch 12.49.0 "한 줄 요약"
disable-model-invocation: true
---

# 새 패치 만들기

인자: `$ARGUMENTS` = `<새 버전> "<한 줄 요약>"`

1. 기준본: `bash tools/unpack.sh` → `build/PageCraft_v<직전>_Lite.html` (이 세션에서 직전 판을 빌드했다면 그 파일)
2. 뼈대: `python3 -I tools/new_patch.py <기준.html> <새 버전> "<요약>"`
   → `patch/patch_vXXXXX.py` · `tests/t_vXX.js` · `docs/CHANGELOG.md` 한 줄
3. 패치 규칙
   - 모든 교체는 `R(old, new, n)` — old는 유일한 문자열로
   - CSS: `pc-ui-css` 안 해당 구역을 직접 고침. 덧붙이기·`!important` 금지
   - 새 JS에는 `/*pc-vXXXXX*/` 표시('이미 적용' 검사용)
   - 새 저장 필드는 기본값이면 저장하지 않기(옛 문서 데이터 불변)
4. 빌드: `python3 -I patch/patch_vXXXXX.py build/<직전>.html build/PageCraft_v<새>_Lite.html`
5. 시험: `tests/t_vXX.js`에 `ok(조건, 이름)` 추가 → `node tests/t_vXX.js build/...`
6. 다음: `/release <새 버전>`
