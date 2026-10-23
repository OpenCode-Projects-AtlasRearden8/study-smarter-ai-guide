# Study Smarter with AI

*A beginner-friendly manual for using AI to actually learn — not copy.*

Written in the style of Dylan Asdale's *The Massive AI Manual* and the hub site
[dylanasdale.github.io](https://dylanasdale.github.io): plain English, step by
step, never condescending — like a friend explaining it over coffee.

## What this is

A complete guide for students and lifelong learners who want AI as a study
partner instead of a copy machine. Inside, in `docs/`:

| Chapter | File | What it does |
|---|---|---|
| How to Use This Guide | `docs/00-how-to-use-this-guide.md` | Orientation + chapter map |
| 1. Notes Into Quizzes | `docs/01-notes-into-quizzes.md` | An AI quiz master built from your own class notes |
| 2. Explain It Back | `docs/02-explain-it-back.md` | The highest-value technique: close the source, teach it back |
| 3. Spaced Review | `docs/03-spaced-review.md` | A simple day 0 / 2 / 7 / 21 schedule that fights the forgetting curve |
| 4. Catching Hallucinations | `docs/04-catching-hallucinations.md` | Spotting confident AI errors, and five checking habits |
| 5. Citation Honesty | `docs/05-citation-honesty.md` | Green light / red light use, honesty without the anxiety |
| 6. Free Tools | `docs/06-free-tools.md` | An honest map of what you can do for $0 |
| 7. Worked Example | `docs/07-worked-example.md` | The full playbook run on a mock textbook chapter |
| Glossary | `docs/glossary.md` | Every term in zero-jargon plain English |

Plus `build.py`, a dependency-free Python script that turns the docs into a
small static HTML website in `site/`.

## How to run it

You need Python 3.8+ and nothing else.

```bash
python3 build.py          # build the site into site/
python3 build.py --check  # build + verify structure, links, anchors, content
```

Then either open `site/index.html` directly in a browser, or serve it:

```bash
python3 -m http.server 8377 --directory site
# visit http://localhost:8377
```

Rebuilding is safe — the script wipes and regenerates `site/` each run.

## Quick taste of the content

The core idea, chapter 2 in one line: after you study something, close the
source and explain it back to the AI in your own words — and have the AI
question you about the gaps, *without* rescuing you mid-explanation. Sketch:

```
I just studied [topic]. I'm going to explain it back to you in my own
words. Do NOT fill in gaps for me while I talk — let me finish. Then
tell me what I got right, what I glossed over, and ask me 2 questions
that would catch shallow understanding.
```

That deficit you feel while explaining? That's the learning happening.

## Design choices

- **Local-first and offline-friendly.** Build the site once, read it anywhere.
- **Zero dependencies.** The build script uses only the Python standard
  library, so it runs on anything with `python3`.
- **No secrets, no API keys, no personal data.** Nothing in this repo phones
  home; the site is plain static HTML.
- **Warm, never condescending.** Every chapter ends with a small, ten-minute
  "Try it today" step. Education only — this guide never hands out medical,
  legal, or financial advice.
- **Beginner-tested structure.** Worked example first-timers can follow end
  to end, and a glossary that assumes zero prior jargon.

## Verification

Run the built-in check, which verifies page structure, internal links,
in-page anchor targets, the copyright footer, and spot-checks expected
content on key pages:

```bash
python3 build.py --check
```

`STATUS.md` records the latest verification results and any known gaps.

## Credits and license

Built and maintained by **Asdale Dynamics, LLC** — the LLC behind
*The Massive AI Manual* by Dylan Asdale (dylanasdale.github.io), which
explains AI like a friend would for beginners, small businesses, and
healthcare workers (education only, never medical advice).

Licensed under the MIT License — see [LICENSE](LICENSE).

Copyright (c) 2026 Asdale Dynamics, LLC
