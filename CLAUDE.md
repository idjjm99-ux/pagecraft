# PageCraft (페이지공방)

단일 HTML 앱(문서·발표 편집기). 구조·사용법은 README.md.

## 새 대화 시작 시 (먼저 할 것)
- 최신판 = `releases/` 안 가장 높은 버전 폴더(`ls releases | sort -V | tail -1`). README의 "최신" 줄과 맞는지 확인
- `bash tools/unpack.sh` → `build/PageCraft_v<최신>_Lite.html` 을 기준본으로 작업
- `main` = 항상 최신 릴리스. 새 판은 작업 브랜치에서 만들고, 사용자 허락을 받은 뒤 `main`에 합침
- 판마다 태그 `v<버전>` (예: `v12.50.0`). 이전 판은 `releases/v*/` 와 태그에 그대로 남음 → 되돌릴 때 사용
- 되돌리기: 기록 강제 덮어쓰기(force push) 금지. `git revert`로 되돌림 커밋을 남김

## 작업 흐름
`/new-patch <버전> "<요약>"` → 패치·시험 작성 → 빌드 → `/release <버전>`

## 규칙
- 완성본 HTML·`releases/`는 직접 고치지 않음 — 항상 패치 스크립트로(훅이 차단)
- 패치 교체는 `R(old,new,n)`: 횟수 검사로 실패를 바로 드러냄. 기준 버전·'이미 적용' assert 필수
- 버전 문자열 2곳: `BUILD_VERSION`, 하단 서명 `Jungmin Jo · PageCraft v…` (`<title>`은 v12.46부터 문서 제목)
- 저장 데이터 불변: 새 필드는 기본값일 때 저장하지 않음(예: `rotation`, `lineArrow`) → 옛 문서 그대로
- CSS: `<style id="pc-ui-css">` 안 해당 구역 규칙을 직접 고침. 맨 아래 덧붙이기·`!important` 덧칠 금지
- 단축키: `PC_KEYS` / 표 `PC_KEYMAP` 한 곳에서
- 시험: 새 판은 `tests/t_vXX.js`(node Playwright). 버전 검사는 `pcVer`(파일 이름 기준)로 — 판 올려도 안 깨지게
- 파이썬은 `python3 -I`로 실행(시험 파일은 `pcenv.py`로 자기 폴더·크롬 경로를 잡음)
- 화면 크기: 폭은 t_v49(1024~1920), 높이는 t_v50(Windows 배율 125·150% → 1093×491·1280×597 등). 낮은 화면 규칙은 `@media(max-height:660px)`
- 결과 기록 `tests/result_v<버전>.txt`: 통과 수·비교 차이·미검증 항목. 실패는 숨기지 않음

## 환경
- 크롬: `PC_CHROME` → `/usr/bin/google-chrome` → `/opt/pw-browsers/chromium`
- Python Playwright 필요: `pip install playwright` (브라우저 설치 불필요). node playwright는 전역에 있음
- 시험은 길다 → 백그라운드 실행
