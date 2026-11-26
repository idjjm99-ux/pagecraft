# 시험 공통 환경: 이 폴더 경로(HERE)와 크롬 실행 파일(CHROME) 한 곳에서 정함
# 크롬 찾는 순서: 환경변수 PC_CHROME → /usr/bin/google-chrome → /opt/pw-browsers/chromium → PATH
import os, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
def _find():
    for c in (os.environ.get('PC_CHROME'), '/usr/bin/google-chrome', '/opt/pw-browsers/chromium'):
        if c and os.path.exists(c): return c
    return shutil.which('google-chrome') or shutil.which('chromium')
CHROME = _find()
# 버전 검사: 파일 이름의 버전(v12.50.0 등)과 앱 BUILD_VERSION이 같은지. 이름에 버전이 없으면 PageCraft v12.x면 통과
def ver_ok(bv, path=None):
    import re, sys
    m = re.search(r'v(\d+\.\d+\.\d+)', os.path.basename(path or sys.argv[1]))
    return bv.startswith('PageCraft v' + m.group(1) + ' ') if m else bv.startswith('PageCraft v12.')
