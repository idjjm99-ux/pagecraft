# PageCraft (페이지공방)

문서·발표 편집기. 결과물은 HTML 한 파일(`PageCraft_v<버전>_Lite.html`, 약 4MB, 오프라인 동작).

**최신: v12.51.0** (CSS 우선순위 정리 2 · 보이는 동작 그대로) — `releases/v12.51.0/`

## 폴더
| 경로 | 내용 |
|---|---|
| `releases/v*/` | 배포본 zip. Lite = 완성본 HTML, Source = 이 저장소의 패치·시험 |
| `patch/patch_vXXXXX.py` | 버전마다 하나. 직전 판 HTML → 문자열 교체 → 다음 판 |
| `tests/` | 시험. `run.sh` = 회귀 전부, `t_vXX.js/py` = 버전별, `keytest·keyseq·cssdump` = 옛/새 판 비교 |
| `tools/` | `unpack.sh`(기준본 풀기) · `new_patch.py`(새 패치·시험 뼈대) · `pack.sh`(릴리스 zip) |
| `docs/CHANGELOG.md` | v12.22 이후 판마다 바뀐 내용 |

## 빠른 사용
```bash
pip install playwright                      # 브라우저 설치는 불필요 (tests/pcenv.py가 크롬을 찾음)
bash tools/unpack.sh                         # → build/PageCraft_v12.51.0_Lite.html
python3 -I tools/new_patch.py build/PageCraft_v12.51.0_Lite.html 12.52.0 "요약"
python3 -I patch/patch_v12520.py build/PageCraft_v12.51.0_Lite.html build/PageCraft_v12.52.0_Lite.html
bash tests/run.sh build/PageCraft_v12.51.0_Lite.html     # 회귀 전부 (약 10분)
bash tools/pack.sh 12.51.0                   # releases/v12.51.0/ zip 2개 (시험 그림·PPT는 자동 제외)
```

## 판 계보 (브랜치)
v12.45.0 `main` → v12.46.0 `claude/keen-shannon-uczmhn` → v12.47.0 `ccr-d0973cf5-o0uei2` → v12.48.0 `ccr-989f8055-6s2ujq`(소스 풀림 `claude/sleepy-gates-8juflm`) → v12.49.0(사용자 업로드본) → v12.50.0 `ccr-033fa78f-2aq5ny` → v12.51.0 `ccr-44790727-4lx6dd`

- 다른 갈래: `claude/zealous-mendel-3moh1n`의 v12.46.0(서명·1024 잘림). 서명 수정은 본류에도 있고,
  상세 설정 잘림 수정은 v12.49.0에서 본류에 반영함(머리줄 단추 여백만 빼냄)
