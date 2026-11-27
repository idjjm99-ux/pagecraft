# 변경 기록 (v12.22.0 ~)
판마다 패치 명령과 바뀐 내용. 옛 줄의 run_all.sh·/home/claude 경로는 당시 기록 그대로(지금 시험은 README 참고)

- v12.22.0 (매끄러운 이동 + Lite 글꼴 3종)
2단계 빌드: v12.21.0 완성본 위에 적용
- python3 -I patch/patch_v12220.py PageCraft_v12.21.0_Lite.html PageCraft_v12.22.0_Lite.html
- 적용 내용·시험 결과: PageCraft_v12.22.0_인계서.md 참고
- Full판에는 5)글꼴 단계를 빼고 적용할 것(이미 전체 글꼴 내장) — 미시험
- v12.23.0: python3 -I patch/patch_v12230.py PageCraft_v12.22.0_Lite.html PageCraft_v12.23.0_Lite.html (내 글꼴 추가)
- v12.24.0: python3 -I patch/patch_v12240.py PageCraft_v12.23.0_Lite.html PageCraft_v12.24.0_Lite.html (설정 찾기·이동 보완)
- v12.25.0: python3 -I patch/patch_v12250.py PageCraft_v12.24.0_Lite.html PageCraft_v12.25.0_Lite.html (정렬 안내선 정리)
- v12.26.0: python3 -I patch/patch_v12260.py PageCraft_v12.25.0_Lite.html PageCraft_v12.26.0_Lite.html (회사 테마 공식 색·테마 이름·양식 창 고정·글씨 대비·표/이미지/영상 설정 열기·사용법 13단계)
- 시험: tests/run_all.sh <html> <tag>. 옛 시험 파일(t_repro 등)은 PageCraft_v12.21.0_Source.zip에 있음 → 이 tests 폴더의 h.py·t_v21.py(v12.26용 수정본)로 덮어써서 사용
- v12.27.0: python3 -I patch/patch_v12270.py PageCraft_v12.26.0_Lite.html PageCraft_v12.27.0_Lite.html (조용한 정렬 안내선: 축마다 얇은 선 1개, 이름표·점·점선상자 제거). 시험 t_v27.py (t_v25.py 대체)
- v12.28.0: python3 -I patch/patch_v12280.py PageCraft_v12.27.0_Lite.html PageCraft_v12.28.0_Lite.html (페이지별 양식 장식선 숨기기). 시험 t_v28.py
- v12.29.0: python3 -I patch/patch_v12290.py PageCraft_v12.28.0_Lite.html PageCraft_v12.29.0_Lite.html (발표·인쇄·PPT에서 양식 글씨 맞춤 적용 → 잘림 수정). 시험 t_v29.py, 전 양식 검사 scan_clip.py
- v12.30.0: python3 -I patch/patch_v12300.py PageCraft_v12.29.0_Lite.html PageCraft_v12.30.0_Lite.html (예시 글씨 줄배치: 한 줄 상자 한 줄 유지·단어 안 쪼갬·인쇄 측정 수정·Ctrl+P). 시험 t_v30.py(글꼴 3종 가정)
- v12.31.0: python3 -I patch/patch_v12310.py PageCraft_v12.30.0_Lite.html PageCraft_v12.31.0_Lite.html (Lite 예시·기본 글꼴 → 내장 글꼴: 프리텐다드·고운바탕·나눔스퀘어). 시험 t_v31.py
- v12.32.0: python3 -I patch/patch_v12320.py PageCraft_v12.31.0_Lite.html PageCraft_v12.32.0_Lite.html (인쇄: 용지·여백 무관 빈 쪽 없음, 인쇄 가능 영역에 맞춰 축소·가운데). 시험 t_v32.py
- v12.33.0: python3 -I patch/patch_v12330.py PageCraft_v12.32.0_Lite.html PageCraft_v12.33.0_Lite.html (목차·타임라인·순환 단계: 간편편집바 ＋/－, 처음 한 번 안내). 시험 t_v33.py
- v12.34.0: python3 -I patch/patch_v12340.py PageCraft_v12.33.0_Lite.html PageCraft_v12.34.0_Lite.html (영상 자리 재생 단추·장식 ▶ 중복·큰 제목 대비·선그래프 썸네일·양식 107 띠). 시험 t_v34.py, 점검 audit_layout.py
- v12.35.0: python3 -I patch/patch_v12350.py PageCraft_v12.34.0_Lite.html PageCraft_v12.35.0_Lite.html (단계 ＋/－ 간편편집바·선택 제자리, [⇄ 배치] 2열/1열 다시 고르기). 시험 t_v35.py
- v12.36.0: python3 -I patch/patch_v12360.py PageCraft_v12.35.0_Lite.html PageCraft_v12.36.0_Lite.html (접힌 설정 칸 길잡이: 제목/탭 강조 + 4초 말풍선). 시험 t_v36.py
- v12.37.0: python3 -I patch/patch_v12370.py PageCraft_v12.36.0_Lite.html PageCraft_v12.37.0_Lite.html (엑셀 Ctrl+V 붙여넣기·자동 확장·숫자 형식, 흐름도 클릭 효과, 설정 칸 색 구분·펼침 애니메이션, 표 배경 안내, 양식 고르기 속도, 순환 분할 제거, 타임라인 2열 간격, 예시 문구 중복 제거, 주석형 핀, 예시 문서 한 주제 10장). 재료 ux37.js·ui37.css·starter37.json. 시험 t_v37.py
- v12.38.0: python3 -I patch/patch_v12380.py PageCraft_v12.37.0_Lite.html PageCraft_v12.38.0_Lite.html (글씨색 고르기 창 확인·취소, 빠른 색 즉시, 편집 중 고른 색 표시, 배치 잠금 작은 창·잠긴 개수, 마무리 화살표 삭제, 무채색 보조색 띠). 재료 ux38.js·ui38.css. 시험 t_v38.py
- v12.39.0: python3 -I patch/patch_v12390.py PageCraft_v12.38.0_Lite.html PageCraft_v12.39.0_Lite.html (남은 문제 정리: 편집 중 상자 색 유지, 표 셀 글자·배경색 색 창, 크기 조절 안내선·가려진 손잡이 잡기, 글꼴 내장/PC 묶음·표 칸 글꼴, 드문 한글 대체 글꼴, 잠금 숫자 회색+잠긴 개체 끌면 안내, 엑셀·시트 붙여넣기 서식, 인쇄 그라데이션 가는 선, 장식선 숨기기에 양식 틀 띠 포함, 좁은 그래프 글씨, G마켓 산스 OFL 표기). 재료 ux39.js·ui39.css. 시험 t_v39.py (t_v22 크기 조절 허용 오차 ±9)
- v12.40.0: python3 -I patch/patch_v12400.py PageCraft_v12.39.0_Lite.html PageCraft_v12.40.0_Lite.html (닌텐도 테마 빨강 #E70012·하양만, 좁은 세로 그래프 항목 8개 초과 시 이름 45° 기울이기·건너뛰기, 가로형 항목 많으면 이름 건너뛰기, 원·도넛 6개까지·나머지 '기타'). 시험 t_v40.py, 그래프 점검 tests/chart_audit.py(9종×5크기×항목 5/8/12/16/20×이름 2종=450개, 회전 고려 겹침 검사)
- v12.41.0: python3 -I patch/patch_v12410.py PageCraft_v12.40.0_Lite.html PageCraft_v12.41.0_Lite.html (양식 04·07 목차 칸 고정 파스텔 → 테마별 칸 모양(윗선/전체 테두리/왼쪽선 + 모서리), 05·07·16 상단 띠). 시험 tests/t_v41.py
- v12.42.0: python3 -I patch/patch_v12420.py PageCraft_v12.41.0_Lite.html PageCraft_v12.42.0_Lite.html (05·06 목차 칸·16 타임라인 단계 → 테마 바탕 면, Ctrl+V 개체 붙여넣기 고침(v12.37~ 오류), 마우스 위치에 붙이기·넘치면 안쪽으로, 복사한 칸도 테마 칸 유지). 시험 tests/t_v42.py
- 주의: 이 zip의 tests/h.py는 같은 인터페이스로 새로 쓴 대체본(원본은 v12.40.0 Source). 옛 시험 전체(run_all.sh)는 v12.40 Source와 합쳐서 사용
- v12.43.0: python3 -I patch/patch_v12430.py PageCraft_v12.42.0_Lite.html PageCraft_v12.43.0_Lite.html (양식 06 세로 레일 목차: 레일 선·점 고정 파랑 #356A99 → 테마색. 강조색→보조색 중 바탕 대비 3 이상, 없으면 강조색을 글자색 쪽으로 섞음. 기본 파랑일 때만, 저장 데이터 불변, 복사·Ctrl+D한 점·선도 유지). 시험 tests/t_v43.py, 육안 tests/shots_v43.py·shots_v43.png, 테마별 색 rail_colors_v43.json
- 주의(갈래): v12.43.0은 두 판이 있음. ① 17:10 판 = 위 patch_v12430(레일 테마색) ② 18:00 판 = 영상 칸 장식 ▶ 없앰(패치·시험은 드라이브 18:00 Source zip id 1MvPhbCwG1r7dyBGEvD9pA5bUaKNtX8A7). v12.44.0은 ② Lite 위에 ①을 이식해 합침
- v12.44.0: python3 -I patch/patch_v12440.py PageCraft_v12.43.0_Lite.html(18:00 판) PageCraft_v12.44.0_Lite.html (레일 선·점 테마색 이식, 05 목차 구분선 고정 회색 #97A8B8·#C2CAD4 → 테마 구분선색 rule(대비<1.5면 글자색 쪽 보정), 크래프톤 테마 원 도형 원형 유지(.rv-shape[data-shape-type=circle]), 복사·Ctrl+D 구분선 역할 유지). 시험 tests/t_v44.py, 육안 tests/shots_v44.py·shots_v44.png, 테마별 색 sep_colors_v44.json. 회귀 시험은 버전 문자열만 v12.44.0으로 바꿔 실행
- v12.45.0: python3 -I patch/patch_v12450.py PageCraft_v12.44.0_Lite.html PageCraft_v12.45.0_Lite.html (코드 정리 B안 · 보이는 동작 그대로)
  · CSS 한 곳: 화면 CSS 블록 37개 → <style id="pc-ui-css"> 1개(원래 순서, 구역마다 원래 블록 이름 주석), 완전히 덮여 안 쓰이던 선언 233개 제거. 시작 화면·글꼴 블록 3개는 제자리
    도구 patch/css45.py(범위 스캐너·죽은 선언 판정), patch/valid45.json(이기는 쪽 값 크롬 CSS.supports 결과, 패치 입력)
  · 단축키 한 곳: 흐름도 칸 키·방향키 이동·편집기 단축키 → PC_KEYS(캡처 1·버블 2, 순서 동일) + 단축키 표 PC_KEYMAP, Revival.keymap()·keyHandlers()
  · 시험(동작 비교형, 옛 판과 새 판을 같은 조건으로 돌려 결과 비교):
    tests/keytest.py(13상태×25키=325경우) · tests/keyseq.py(연속 동작 26가지) → json 두 개 비교
    tests/cssdump.py <html> <out.json> quick(모든 요소의 계산된 스타일·위치 해시, 화면 크기 2종·UI 상태·양식 61종×테마 6종·발표·인쇄) → tests/cmpdump.py a.json b.json
    tests/keyreg.py(키 리스너 등록 순서 확인)
  · 앞으로 CSS 수정: 맨 아래 새 블록 덧붙이기·!important 덧칠 금지. pc-ui-css 안 해당 구역 규칙을 직접 고칠 것
- v12.46.0: python3 -I patch/patch_v12460.py PageCraft_v12.45.0_Lite.html PageCraft_v12.46.0_Lite.html (쓰기 편하게)
  · 탭 제목 = 문서 제목(저장본에도), 화면 아래 서명 버전은 BUILD_VERSION에서 자동(v12.44.0으로 남아 있던 것 고침)
  · 첫 안내 '괜찮아요'/Esc → 바로 닫힘 + [? 사용법] 3초 깜빡임(두 번째 막는 창 없앰)
  · 머리줄 저장 단추 4개 + 리본 '임시저장 복구' → [저장 ▾] 메뉴 하나(단추를 옮겨 data-action·id·이벤트 유지, 저장본 다시 열 때 중복 정리)
  · 폭 1439px 이하: 테마 칸·지우개 '크기' 글자 줄여 도구줄 3줄→2줄 (1366×768 편집 배율 49%→55%)
  · 시험: node tests/t_v46.js <html> (31개), 회귀 run.sh, keytest/keyseq 비교 → tests/result_v12.46.0.txt
- v12.47.0: python3 -I patch/patch_v12470.py PageCraft_v12.46.0_Lite.html PageCraft_v12.47.0_Lite.html (기본 기능 4가지, 추천 순서 1·2·4·3. 기준 v12.46.0 = 브랜치 claude/keen-shannon-uczmhn 판)
  · 1 글자 맞춤: 도구줄 [글자 맞춤] 단추 3개(왼쪽·가운데·오른쪽) + 간편편집바 3개 + Ctrl+L·E·R(글 편집 중 포함, 고른 글상자·도형 없으면 브라우저 기본 그대로). 여러 개 한꺼번에, Ctrl+Z 한 번. 저장값 style.textAlign(기존 필드)
    폭 1499px 이하: 글꼴 칸 150→128·두께 칸·투명도 칸 줄여 도구줄 줄 수 v12.46 그대로(1366×768 2줄 55%)
  · 2 캡처 그림 Ctrl+V: 클립보드에 그림만 있으면 그림 개체(원래 비율, 페이지 60% 안, 마우스 위치 가운데). 그림 칸 하나 골라 두면 그 그림 교체. 글 편집 중이면 편집 마치고 넣음
    붙여넣기 갈래 pcPasteRoute(paste 이벤트): 그림 → 그림 / 앱 복사 표시 글자 → 개체 / 그 밖 → 기존 그대로(표·그래프 엑셀 칸 붙여넣기 포함). 앱 Ctrl+C는 클립보드에 '[페이지공방 개체 n개 복사 …]' 글자를 남김
  · 4 선 화살표: lineArrow = end·start·both (없으면 필드 없음 → 기존 문서 데이터 불변). 상세 설정 '화살표' 칸, 간편편집바 '화살표', 도형 고르기 '화살표'. 화살촉은 선 색·두께에 맞춘 삼각형(화면·썸네일·발표·인쇄·PPT 같은 그림)
  · 3 페이지 끌기: 왼쪽 목록 썸네일을 위아래로 끌기(6px 넘게 움직이면 끌기, 파란 선 = 놓을 자리, 목록 끝 자동 스크롤, Esc 취소, Ctrl+Z). ↑↓ 단추 그대로
  · 시험: node tests/t_v47.js <html> (72개) · 회귀 run.sh · keytest/keyseq·cssdump v12.46↔v12.47 비교 → tests/result_v12.47.0.txt
- v12.48.0: python3 -I patch/patch_v12480.py PageCraft_v12.47.0_Lite.html PageCraft_v12.48.0_Lite.html (지난 표 6·5번. 기준 v12.47.0 = 브랜치 ccr-d0973cf5-o0uei2 판)
  · 6 개체 회전: 글상자·도형·그림·선. 고른 개체 아래 동그란 손잡이를 끌어 돌리기(Shift 15° 단위, 0·±90·180° 근처 ±3°는 붙음, Esc 취소), 상세 설정 '배치와 위치' 회전 칸(숫자·↺90°·↻90°·0°), Ctrl+Z
    저장값 rotation(도, -180~180, 0.1 단위) — 돌리지 않은 개체엔 필드 없음(기존 문서 데이터 불변). 표·그래프·영상·흐름도는 회전 없음(불러올 때 빠짐)
    화면·썸네일·발표·인쇄는 같은 그리기 함수에서 CSS rotate 속성(transform과 별개). 돌린 개체 크기 조절은 잡은 쪽 반대편 고정, 지우개 위치도 회전 반영
    PPT: 글자·그림은 회전을 뺀 자리에서 재서 PowerPoint 회전값(rot)과 개체 가운데 기준 위치로, 상자 꾸밈은 돌린 그대로 그림
    손잡이는 간편편집바와 겹치면 반대쪽으로(편집바 자리는 v12.47 그대로)
  · 5 발표자 보기: 발표 도구줄 [발표자 보기] → 새 창(같은 출처 빈 창에 앱의 그리기 함수로 그림): 지금 화면·다음 페이지(계층 문서는 고를 번호 목록)·발표 메모·지난 시간(멈춤·0부터)·지금 시각·메모 글씨 크기
    새 창 키: → ← ↑ ↓·Space·PageUp/Down·1~9·0, Esc = 발표 끝. 발표 끝내면 새 창도 닫힘. 영상·소리는 새 창에서 재생 안 함(대표 그림)
    팝업이 막히면 발표 화면 아래 메모 칸(✕로 닫기)
  · 시험: node tests/t_v48.js <html> (89개) · 회귀 run.sh · t_v46/t_v47.js · keytest/keyseq·cssdump v12.47↔v12.48 비교 → tests/result_v12.48.0.txt
- v12.49.0: python3 -I patch/patch_v12490.py PageCraft_v12.48.0_Lite.html PageCraft_v12.49.0_Lite.html (좁은 화면 잘림. 기준 v12.48.0 = 브랜치 claude/sleepy-gates-8juflm 판)
  · 곁가지 claude/zealous-mendel-3moh1n v12.46.0의 잘림 수정을 본류로 옮김 + 새로 찾은 겹침 목록 1건. CSS만(pc-ui-css 안 기존 구역 직접 수정), 저장 데이터·동작 변화 없음
  · 머리줄: 1101~1240px에서 저장 상태 글씨가 길면 [▶ 발표]가 화면 밖(최대 76px) → ≤1240에서 상태 글씨·부제 숨김
  · 페이지 설정 [페이지에 적용]·[문서 전체 적용]: ≤1100px 칸 밖 29px → 글꼴 고르기 아래 줄, 오른쪽 맞춤
  · 설정 탭 작은 글씨: ≤1350px 탭 좌우 여백 0·10px, ≤1100px 9px(1024에서 '배경·글꼴·전환' 잘림)
  · 겹침·순서 목록: 이름이 모든 폭에서 2~3글자('1년 …'), ≤1350px에선 0글자 → 첫 줄 이름(칸 폭 전부) + 둘째 줄 [종류][겹침 n]. ≤1100px 단추·표 여백 줄임
  · 곁가지의 ≤1100 머리줄 단추 여백 12→8px은 v12.46 [저장 ▾] 메뉴로 필요 없어 빼냄
  · 시험: node tests/t_v49.js <html> (88개, 9개 폭 1024~1920) · 회귀 run.sh · keytest/keyseq·cssdump v12.48↔v12.49 비교 → tests/result_v12.49.0.txt
- v12.50.0: python3 -I patch/patch_v12500.py PageCraft_v12.49.0_Lite.html PageCraft_v12.50.0_Lite.html (배율 화면·겹침 이름·CSS 우선순위 정리). 시험 node tests/t_v50.js
  · Windows 배율 화면(1366×768@125% → 보이는 칸 약 1093×491 등): 높이 ≤660px에서 머리줄 65→50, 도구 단추 아이콘·글자 가로(도구줄 229→156px), 페이지 막대 53→38, 상태줄 한 줄(서명은 온전히), 설정 칸 머리 설명 숨김. #app 최소 높이 640→460(화면 전체 스크롤 없앰). [맞춤]·축소 하한 28/30%→15%
  · 1101~1350px: 왼쪽 '페이지' 머리·[페이지에 적용]·[문서 전체 적용] 줄바꿈 배치(≤1100과 같게)
  · 겹침·순서 목록 이름: 8글자 줄임 없앰 → 칸 폭만큼, 넘칠 때만 '…'
  · v12.37 구역 !important 34개 중 28개 뺌(계산된 스타일 그대로인 것만, 남은 6개는 다른 구역 !important와 겨룸). 전체 1058→1030
  · Source 묶음: tools/pack.sh가 시험 부산물(tests/*.png·*.pptx·out_*) 제외, 100KB 넘는 파일 알림
- v12.51.0: python3 -I patch/patch_v12510.py PageCraft_v12.50.0_Lite.html PageCraft_v12.51.0_Lite.html (CSS 우선순위 정리 2). 시험 node tests/t_v51.js
  · !important 2차 정리(보이는 동작 그대로): @media 없는 구역 4묶음(rv-lock-state-visual-v12171 · rv-v12176~12179 · rv-v12260-themes · rv-v12330~12340) 원문 206개 중 62개 뺌. 전체 1030→968
  · 판정: tools/imp_check.js를 1500x950·1024x600 두 화면에서 돌려 둘 다 FREE인 것만. 원문 선언이 여러 세부 속성으로 펼쳐지면 모두 FREE일 때만. :hover 등 상태 선택자·테마 지정 선택자는 남김
  · tools/imp_check.js: 화면 크기 인자(5번째), 상태 선택자 UNMATCHED 처리, 낮은 화면에서 탭 hover 가려짐 건너뜀
  · 시험 t_v48 '계속 → 다시 흐름': 1.2초 고정 대기 → 조건 대기(0.5초 간격 갱신이라 v12.50에서도 2/3 실패하던 타이밍 문제)
