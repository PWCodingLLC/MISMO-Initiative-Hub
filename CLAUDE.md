# MISMO Initiative Hub — Project Context

This file exists so a new Claude Code session (or a fresh `opusplan` planning pass)
can pick this project up without re-deriving conventions that were already worked
out, sometimes the hard way, across many earlier sessions in Claude.ai.

## What this is

A set of static HTML dashboards tracking MISMO workgroup initiatives — built,
tested, and deployed entirely through hand-written HTML/CSS/vanilla JS (no
build step, no framework, no backend yet).

- **Live site:** https://pwcodingllc.github.io/MISMO-Initiative-Hub/
- **Repo:** https://github.com/PWCodingLLC/MISMO-Initiative-Hub
- **Hosting:** GitHub Pages, served directly from the `main` branch

## File structure

| File | What it is |
|---|---|
| `index.html` | The hub homepage — domain tiles, tabs, links out to each dashboard |
| `mcd-dashboard.html`, `lbds-dashboard.html`, `ccs-dashboard.html`, `tpa-dashboard.html` | The four live, real workgroup dashboards |
| `calendar.html` | Meeting calendar with a workgroup filter dropdown |
| `_dev/dashboard-template.html` | Starting point for building a **new** dashboard — see below |
| `_dev/validate_nesting.py` | HTML nesting validator used before every deploy |

There is no build/deploy directory distinction in the repo itself, but during
development a `gh-deploy/` copy is kept in sync with `template-work/` before
each push — see **Deployment workflow** below.

**Why `_dev/`:** this repo has no `.nojekyll` file, so GitHub Pages runs Jekyll,
which excludes underscore-prefixed directories from the published site. Dev-only
files live there so they stay version-controlled and available to you, without
being served at the public URL — an unfilled template rendering a page full of
`{{WORKGROUP_NAME}}` placeholders isn't something a visitor should stumble onto.
If a `.nojekyll` file is ever added, `_dev/` becomes publicly served; nothing in
it is sensitive, but it would look unpolished.

## `dashboard-template.html` — how it works, and its history

This file is a `{{TOKEN}}`-based starting point: duplicate it, find-and-replace
the ~100 `{{PLACEHOLDER}}` tokens with real content for a new workgroup, and
you have a new dashboard consistent with the other four.

**Important history:** this template silently drifted out of sync with the
four real dashboards for an extended stretch — new bug fixes kept landing on
the four real files but were never back-ported to the template, so it
accumulated real, confirmed bugs (a broken anchor-scroll ROI toggle instead of
the working button toggle, a missing dark-mode fix, stale copy, etc.). It was
brought back in sync as of this handoff by systematically diffing it against
the four live files, section by section, and patching each confirmed
divergence — not by rebuilding it from scratch, specifically to preserve its
existing token system intact.

**The lesson, and the ask:** if you fix something on the four real dashboards
that's structural/CSS/JS (not dashboard-specific content), also apply it to
`dashboard-template.html` in the same turn, or explicitly flag it as deferred.
Otherwise this exact drift will happen again.

One known, accepted limitation from this sync: the deliverables table's first
row no longer has its own `.deliv-date-label` span (its label lives in the
`<th>` instead, so it lines up visually with the other column headers). This
means the JS that dynamically flips a row's label between "Completed" and
"Expected Publication Date" based on its status dropdown no longer applies to
that first row specifically. This is documented inline in the template's JS
comments, and it's the same tradeoff already live on all four real dashboards
— not a new limitation introduced by the sync.

## Architecture conventions (load-bearing — don't casually change these)

- **CSS variables, light/dark mode:** `--bar-bg` is a *fixed-role* color
  (`#101B33`) that stays dark navy in both themes — used for buttons, tabs,
  chips, lock-button-when-locked. `--header-bg` / `--header-text` *flip*
  between themes. Don't casually swap one for the other; a past bug (savings
  bar invisible in dark mode) came from `.savings-fill` using `--bar-bg`
  without a dark-mode override, since a fixed-dark color blends into a
  fixed-dark background. Fixed with a scoped
  `html[data-theme="dark"] .savings-fill{background:#fff;}` — don't just
  change `--bar-bg` itself, since that would affect the lock button and other
  intentionally-fixed-dark elements too.
- **Default theme is light.** A FOUC-prevention inline `<script>` sits at the
  very top of `<head>`, before any stylesheet, reading a per-dashboard
  localStorage key and setting `data-theme` before first paint.
- **Per-dashboard localStorage keys**, all namespaced by dashboard ID (e.g.
  `mcd-`, `lbds-`): `{id}-dashboard-theme`, `{id}-roster-data-v1`,
  `{id}-lane-data-v1`, `{id}-dashboard-snapshot`.
- **Save/Restore system** serializes the actual JS data model (`rosterData`,
  `laneData`, plus every other editable field's live value) to localStorage —
  it does **not** snapshot rendered HTML. This matters because a `<select>`'s
  or `<input type="date">`'s current value is never reflected in its
  `outerHTML` once a user changes it, so an HTML-snapshot approach would
  silently lose edits.
- **Locked vs. unlocked mode:** dashboards load locked (read-only) by default.
  `body.locked` disables interaction on editable `<select>`s/`<input>`s via
  `pointer-events:none` — but a plain `<select>` still shows its native
  browser dropdown arrow regardless of `pointer-events`, which is misleading
  once it's actually disabled. Fixed with a scoped
  `appearance:none` rule under `body.locked`, restored to normal the instant
  it's unlocked.
- **Never use `<a href="#...">` for an in-page toggle.** The ROI/savings
  breakdown used to be an anchor that scrolled to a `#why-card` anchor — this
  looked like it worked but actually navigated the page. It's now a real
  `<button type="button">` with a click handler that toggles a `.roi-detail`
  panel open/closed. If you ever see a toggle built as an anchor tag, that's
  a bug, not a stylistic choice.
- **Table headers should be real column headers, not row-local labels.**
  The deliverables table's 4th column header used to just say "Date" even
  though every row has its own more specific label ("Published",
  "Completed", "Expected Publication Date"). Fixed by moving the *first*
  row's specific label into the actual `<th>` (see the limitation noted
  above), removing the generic placeholder header entirely.
- **`vertical-align:top`** is set explicitly on `.deliverables-table td`,
  since the browser default (`middle`) looks fine on short rows but visibly
  misaligns content whenever a row's first cell wraps to two lines.

## Testing workflow (follow this before every deploy)

1. Edit the file in `/home/claude/template-work/` (or wherever your working
   copy lives).
2. **Validate HTML nesting** — run `python3 _dev/validate_nesting.py {file}.html`
   (in this repo). It's a stack-based
   checker that catches real mismatched open/close `<div>` tags, not just
   whether total open/close counts happen to match (which can coincidentally
   line up despite a real bug).
3. **Check JS syntax** — extract `<script>` blocks and run `node --check` on
   each. Note: `dashboard-template.html` will *never* pass this directly,
   since its `{{TOKEN}}` placeholders (especially numeric ones like
   `{{LEADERBOARD_SCORE_1}}`) aren't valid JS syntax until filled in. To test
   it, regex-replace every `{{TOKEN}}` with a safe dummy value first (numeric
   tokens → `1`, everything else → a short string), check syntax on *that*
   copy, and discard it afterward.
4. **Real-browser test with Playwright**, not just static inspection. This
   project uses a real headless Chromium at
   `~/.cache/puppeteer/chrome/linux-131.0.6778.204/chrome-linux64/chrome`.
   Confirm interactive elements actually work (toggles open/close, selects
   have the right option count, no `pageerror` events), not just that the
   markup looks plausible.
5. **Screenshot and visually confirm** anything involving layout, alignment,
   or color — several bugs in this project's history looked correct from the
   code alone but were visibly wrong once rendered (a fixed pixel offset that
   worked for one dashboard's row height and broke on a shorter row is a
   good example of why "looks right in the diff" isn't sufficient).
6. Only after all of the above passes, copy to the deploy location and `git
   push`.

## Deployment workflow

```bash
cp template-work/{file}.html gh-deploy/{file}.html
cd gh-deploy
git add {file}.html
git commit -m "<what changed and why, verified how>"
git push origin main
```

Write commit messages that explain *what changed, why, and how it was
verified* — this project's history relies on being able to reconstruct
reasoning from commit messages alone, since context resets between sessions.

## GitHub access

The repo is public: https://github.com/PWCodingLLC/MISMO-Initiative-Hub

For push access, authenticate properly rather than reusing a hardcoded
personal access token in a plaintext file:

- **From Claude Code:** run `gh auth login` once per environment, or connect
  GitHub through Claude Code's native GitHub integration (`/web-setup` from
  the CLI, or via claude.ai settings for cloud/web sessions).
- **A prior personal access token was used** during the Claude.ai chat-based
  sessions that built this project (visible repeatedly in that conversation
  history, and already flagged there for rotation). Don't reuse it — if
  you're the project owner, revoke it in GitHub's token settings and
  authenticate fresh via one of the methods above instead. Continuing to
  copy a live credential from document to document only increases exposure.

## Known deferred / pending items

Carried forward from earlier sessions, still outstanding as of this handoff:

- LBDS's resource links are placeholders — need real URLs.
- LBDS's meeting-tracker leaderboard shows names carried over from MCD —
  needs LBDS's own real names.
- A `window.storage` dead-code path exists in at least one dashboard and
  hasn't been decided on (remove vs. actually wire up).
- The hub's brand color (`--brand: #2A4DFF`) doesn't match the four
  dashboards' brand color (`#125DAB`) — never reconciled.
- The calendar page (`calendar.html`) doesn't have full dark-mode styling.
- TPA's Governance section leadership tag was left blank deliberately —
  workgroup hasn't started meeting yet, no real leadership to show.

## What's next for this project

The person building this is planning to add a backend and other more complex
elements. See this project's conversation history in Claude.ai for the
reasoning already discussed on model/effort selection (Sonnet for day-to-day
work, Opus/Fable for architecture decisions, `opusplan` to combine both) and
using the advisor tool or an adversarial review subagent as a second check on
non-trivial changes before they ship.
