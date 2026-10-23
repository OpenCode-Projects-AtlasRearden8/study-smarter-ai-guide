# STATUS.md — Study Smarter with AI

Last updated: 2026-10-23

## What was built

**Study Smarter with AI** — a beginner-friendly manual for students and life-
long learners on using AI to actually learn rather than copy. Written in the
plain-English, never-condescending style of Asdale Dynamics, LLC
(*The Massive AI Manual*, dylanasdale.github.io).

### Contents

- `docs/` — 9 markdown source files:
  - How to Use This Guide (orientation + chapter map)
  - Ch. 1 — Turning Your Notes Into Quizzes (quiz-master prompt recipe)
  - Ch. 2 — Explain It Back (Feynman-style technique, three levels)
  - Ch. 3 — Spaced Review (day 0/2/7/21 schedule, AI-generated plans)
  - Ch. 4 — Catching Hallucinations (five checking habits)
  - Ch. 5 — Citation Honesty (green light / red light disclosures)
  - Ch. 6 — Free Study Tools (honest $0 map: free AI chats, Anki, Quizlet,
    libraries, GitHub)
  - Ch. 7 — Worked Example (full five-step playbook on a mock textbook
    chapter, "The Science of Memory")
  - Glossary (zero-jargon, alphabetical, every term defined plainly)
- `build.py` — dependency-free (stdlib-only) static site generator.
- `site/` — the built static HTML site (10 pages, `index.html` entry point,
  shared styling, prev/next navigation, responsive layout).
- `README.md`, `LICENSE` (MIT), `.gitignore`.

Every chapter ends with a ten-minute "Try it today" step. Education only:
the guide contains no medical, legal, or financial advice.

## How to run it

```bash
python3 build.py          # build the site into site/
python3 build.py --check  # build + automated verification
python3 -m http.server 8377 --directory site   # optional local preview
```

Requires Python 3.8+ only — no packages to install.

## Verification results

- `python3 build.py --check` — **PASS** (2026-10-23). Builds 10 pages and
  verifies: valid html wrapper on every page, the copyright line
  ("Asdale Dynamics, LLC") in the footer of every page, all internal
  `.html` links resolve to built pages, all in-page `#anchor` links have
  matching `id` targets, and spot-checks confirm expected content on the
  explain-it-back chapter and glossary.
- Manual HTML parser check — **PASS**. Every built page was parsed with
  `html.parser` and all tags balanced (no unclosed/mismatched elements).
- Local server check — **PASS**. `http.server` on the built site returns
  HTTP 200 for the index and chapter pages.
- Output inspection — the quiz prompts render in `<pre><code>` blocks,
  tables render as `<table>`, and the glossary paragraph anchors
  (`#hallucination` etc.) resolve.

## Known gaps

- The built-in markdown support in `build.py` is a deliberate small subset
  (headings, paragraphs, bold/italic/code/links, flat lists, blockquotes,
  tables, fenced code). Nested lists and other extensions are not supported
  — not needed by these docs. For richer needs, the site generator can be
  swapped for a full markdown package later.
- Chapter 6 deliberately avoids naming specific AI products/pricing; service
  names and limits change fast, so it teaches how to evaluate free tiers
  instead. Expect that chapter to age gently.
- No tests beyond the `--check` verification; zero external dependencies
  means there is nothing to linting- or CI-integrate out of the box.
- `site/` is committed for convenience; it regenerates fully from `docs/`
  via `build.py`, so it can safely be removed from the repo later.

## Notes

- No secrets, API keys, or personal data are included anywhere in this repo.
- License: MIT — Copyright (c) 2026 Asdale Dynamics, LLC.
- Built and maintained by Asdale Dynamics, LLC.
