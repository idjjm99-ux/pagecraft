# PageCraft (페이지공방)

단일 HTML 앱(문서·발표 편집기). 결과물은 `PageCraft_v<버전>_Lite.html` 한 파일(약 4MB).

## 구조
- `releases/v*/` — 배포본 zip (Lite = 완성본 HTML, Source = README·patch·tests). 직접 수정 금지
- `patch/patch_vXXXXX.py` — 버전마다 하나. 직전 판 HTML을 읽어 문자열 교체로 다음 판을 만듦
- `tests/` — Python Playwright(async). `h.py`(도우미), `t_vXX.py`(버전별), `run.sh`(회귀 묶음),
  `keytest.py`·`keyseq.py`·`cssdump.py`→`cmpdump.py`(옛/새 판 비교형)
- `tools/unpack.sh [버전]` — 릴리스 Lite를 `build/`에 풂(build/는 git 제외)
- `tools/new_patch.py` — 새 패치 뼈대 생성(`/new-patch`)

## 작업 흐름
`/new-patch <버전> "<요약>"` → 패치 작성·빌드 → `t_vXX.py` → `/release <버전>`

## 규칙
- 완성본 HTML은 직접 고치지 않음 — 항상 패치 스크립트로(훅이 차단)
- 패치 교체는 `R(old,new,n)`: 횟수 검사로 실패를 바로 드러냄. 기준 버전·'이미 적용' assert 필수
- 버전 문자열 3곳: `BUILD_VERSION`, `<title>`, 하단 서명 `Jungmin Jo · PageCraft v…`
- CSS: `<style id="pc-ui-css">` 안 해당 구역 규칙을 직접 고침. 맨 아래 덧붙이기·`!important` 덧칠 금지
- 단축키: `PC_KEYS` / 표 `PC_KEYMAP` 한 곳에서
- 파이썬은 `python3 -I`로 실행(시험 파일은 자기 폴더를 sys.path에 직접 추가함)

## 환경
- 크롬: 환경변수 `PC_CHROME` → `/usr/bin/google-chrome` → `/opt/pw-browsers/chromium` 순으로 찾음
- Python Playwright 필요: `pip install playwright` (브라우저 설치는 불필요)
- 시험은 길다(시험당 최대 15분) → 백그라운드 실행
