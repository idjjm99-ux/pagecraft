# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

PageCraft (페이지공방) is a slide/page editor shipped as **one self-contained HTML file** (`app/PageCraft_v<ver>_Lite.html`, ~4 MB: all JS, CSS and embedded fonts inline; no build system, no package manager). Docs, comments and commit text are in Korean.

## Development model: patch chain

The app is never edited directly. Each version is produced by a Python patch script that transforms the previous version's HTML:

```bash
python3 -I patch/patch_v12450.py app/PageCraft_v12.44.0_Lite.html app/PageCraft_v12.45.0_Lite.html
```

- A patch asserts the exact input `BUILD_VERSION='PageCraft v…'` string and refuses already-patched input. It uses `R(old, new, n)` (exact string replace with an occurrence-count assert) and `cut(a, b)` (remove a unique span). Follow the same style for new patches (`patch/patch_vXXXX0.py`). Bump `BUILD_VERSION` and `<title>`.
- `README.md` is the changelog. Add one line per version with the patch command, a summary and the test file. Older patches and tests (≤ v12.39) live in earlier Source zips and are not in this repo.
- Releases go in `releases/v<ver>/` as `PageCraft_v<ver>_Lite.zip` (the HTML) and `PageCraft_v<ver>_Source.zip` (README, patch/, tests/).

## App architecture (inside the HTML)

- Global API `window.Revival`: `getProject()` → `{pages:[{templateId, themeId, objects:[…]}]}`, `keymap()`, `keyHandlers()`. Tests drive the app through it via `page.evaluate`.
- CSS: one UI block `<style id="pc-ui-css">` (merged in v12.45 from 37 blocks; each section has a comment naming its original block). Only the startup block (`rv-startup-no-editor-flash`) and the font blocks (`pc-step3-00_embedded-fonts`, `rv-v12220-fonts`) are separate. **To change CSS, edit the rule in its section of `pc-ui-css`. Never append a new block at the end, and never override with `!important`.**
- Keyboard: all editor shortcuts go through `PC_KEYS` (capture phase 1, bubble phase 2, order matters). The shortcut table is `PC_KEYMAP`.
- Templates (61) × themes (~50). Theme colors are derived at runtime (accent/secondary/rule colors with contrast fallbacks). Saved project data must stay unchanged by visual fixes.

## Tests

Headless Chrome via Python Playwright (`pip install playwright`; tests launch `/usr/bin/google-chrome`). The scripts hard-code `/home/claude/tests`, so link it once per container:

```bash
mkdir -p /home/claude && ln -sfn "$PWD/tests" /home/claude/tests
```

- Single test: `cd tests && python3 -I t_v44.py <abs path to html>`. The output ends with `== N/N 통과`, and failures start with `FAIL`.
- Regression suite: `cd tests && bash run.sh <abs html> <tag>` (t_v40–t_v44 + chart_audit; output in `out_<tag>/`).
- Behavior-equivalence checks for refactors run the old and new HTML with identical inputs and diff the results:
  - `keytest.py` (13 states × 25 keys) and `keyseq.py` (26 sequences) → compare the JSON outputs.
  - `cssdump.py <html> <out.json> quick` (computed style/position hashes across states, templates × themes, present and print) → `cmpdump.py a.json b.json`.
  - `keyreg.py` checks listener registration order.
- Expected results per version: `tests/result_v<ver>.txt` (v12.45.0: t_v40 17/17, t_v41 16/16, t_v42 29/29, t_v43 13/13, t_v44 18/18, chart_audit BAD 0).
- Some tests rewrite reference JSON in `tests/` (`rail_colors_v43.json`, `sep_colors_v44.json`). Check `git diff` after running them.
- `patch/css45_build.py` regenerates `patch/valid45.json` (Chrome `CSS.supports` results used by the v12.45 patch).

## Skill routing (overlapping skills)

- Small or mechanical tasks (single fix, rename, test run): skip `superpowers:brainstorming`. Use it only for new features or design changes.
- Code review: use `/code-review`. Do not use `superpowers:requesting-code-review` unless it is asked for by name.
- Bugs: `superpowers:systematic-debugging` first, then verify with the tests above before claiming a fix.
