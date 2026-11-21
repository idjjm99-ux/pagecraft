# PageCraft v12.22.0 (매끄러운 이동 + Lite 글꼴 3종)
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
