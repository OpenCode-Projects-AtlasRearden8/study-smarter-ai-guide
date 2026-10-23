#!/usr/bin/env python3
"""Build script for Study Smarter with AI.

Converts docs/*.md into a small static website in site/.
Zero dependencies: Python 3 standard library only.

Usage:
    python3 build.py            # build the site
    python3 build.py --check    # build + verify output (exit 1 on failure)
"""

import html
import re
import sys
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
SITE = ROOT / "site"

TITLE = "Study Smarter with AI"
SUBTITLE = "Turn AI into a study partner — learn, don't copy."
VERSION = "1.0.0"

NAV = [
    ("00-how-to-use-this-guide", "How to Use This Guide"),
    ("01-notes-into-quizzes", "1. Notes Into Quizzes"),
    ("02-explain-it-back", "2. Explain It Back"),
    ("03-spaced-review", "3. Spaced Review"),
    ("04-catching-hallucinations", "4. Catching Hallucinations"),
    ("05-citation-honesty", "5. Citation Honesty"),
    ("06-free-tools", "6. Free Tools"),
    ("07-worked-example", "7. Worked Example"),
    ("glossary", "Glossary"),
]


# --------------------------------------------------------------- markdown

def md_inline(text: str) -> str:
    """Inline markdown: code, bold, italic, links."""
    text = html.escape(text, quote=False)
    # inline code first so its content isn't further processed
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)\s]+)\)",
        lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>',
        text,
    )
    return text


def slugify(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^a-z0-9 _-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-")


def md_to_html(md_text: str) -> str:
    """A tiny, dependency-free markdown subset -> HTML.

    Supports: fences, headings, hr, blockquotes, flat lists, tables,
    paragraphs, and md_inline formatting. Flat lists only (no nesting),
    which is all this guide's docs use.
    """
    lines = md_text.splitlines()
    out: list[str] = []
    in_code = False
    code_buf: list[str] = []
    open_list: str | None = None  # "ul" or "ol"
    list_needs_close = False
    para_buf: list[str] = []

    def close_para():
        if para_buf:
            out.append("<p>" + md_inline(" ".join(para_buf)) + "</p>")
            para_buf.clear()

    def close_list():
        nonlocal open_list, list_needs_close
        if list_needs_close and open_list:
            out.append("</li></" + open_list + ">")
        elif open_list:
            out.append("</" + open_list + ">")
        open_list = None
        list_needs_close = False

    i = 0
    while i < len(lines):
        line = lines[i]

        # fenced code block
        if line.strip().startswith("```"):
            if in_code:
                out.append("<pre><code>" + html.escape("\n".join(code_buf)) + "</code></pre>")
                code_buf = []
                in_code = False
            else:
                close_para()
                close_list()
                in_code = True
            i += 1
            continue
        if in_code:
            code_buf.append(line)
            i += 1
            continue

        # blank line
        if not line.strip():
            close_para()
            i += 1
            continue

        # heading
        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            close_para()
            close_list()
            level = len(m.group(1))
            out.append(f"<h{level}>{md_inline(m.group(2))}</h{level}>")
            i += 1
            continue

        # horizontal rule
        if re.match(r"^\s*(-{3,}|\*{3,})\s*$", line):
            close_para()
            close_list()
            out.append("<hr>")
            i += 1
            continue

        # blockquote
        if line.lstrip().startswith(">"):
            close_para()
            close_list()
            quote: list[str] = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                quote.append(lines[i].lstrip()[1:].lstrip())
                i += 1
            out.append("<blockquote>" + md_to_html("\n".join(quote)) + "</blockquote>")
            continue

        # unordered list
        m = re.match(r"^[-*]\s+(.*)$", line.strip())
        if m:
            close_para()
            item = m.group(1)
            if open_list != "ul":
                close_list()
                out.append("<ul>")
                open_list = "ul"
            elif list_needs_close:
                out.append("</li>")
            out.append(f"<li>{md_inline(item)}")
            list_needs_close = True
            i += 1
            continue

        # ordered list
        m = re.match(r"^\d+\.\s+(.*)$", line.strip())
        if m:
            close_para()
            item = m.group(1)
            if open_list != "ol":
                close_list()
                out.append("<ol>")
                open_list = "ol"
            elif list_needs_close:
                out.append("</li>")
            out.append(f"<li>{md_inline(item)}")
            list_needs_close = True
            i += 1
            continue

        # table row
        if line.strip().startswith("|") and "|" in line.strip()[1:]:
            # collect the table block
            tbl: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                tbl.append(lines[i].strip())
                i += 1
            close_para()
            close_list()
            out.append(md_table(tbl))
            continue

        # paragraph text (continued lines)
        close_list()
        para_buf.append(line.strip())
        i += 1

    close_para()
    close_list()
    return "\n".join(out)


def md_table(rows: list[str]) -> str:
    """Render a small markdown table."""
    parsed: list[list[str]] = []
    for row in rows:
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if cells and all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
            continue  # separator row
        parsed.append(cells)
    if not parsed:
        return ""
    head, *body = parsed

    def cols(row):
        return row + [""] * max(0, len(head) - len(row))

    html_rows = ["<table>", "<thead><tr>"]
    html_rows += [f"<th>{md_inline(c)}</th>" for c in head]
    html_rows.append("</tr></thead><tbody>")
    for r in body:
        html_rows.append("<tr>" + "".join(f"<td>{md_inline(c)}</td>" for c in cols(r)) + "</tr>")
    html_rows.append("</tbody></table>")
    return "".join(html_rows)


def extract_title(md_text: str) -> str:
    for line in md_text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return TITLE


def add_para_ids(body: str) -> str:
    """Give <p> blocks that start with bold text an id derived from it.

    Lets glossary-style entries be targets for in-page (#term) anchors.
    """
    def repl(m):
        term = m.group(1)
        return f'<p id="{slugify(term)}">{m.group(0)[3:]}'

    return re.sub(r"<p><strong>([^<]+)</strong>", repl, body)


# --------------------------------------------------------------- templates

CSS = """\
:root {
  --ink: #2a2a35; --muted: #6b6b78; --paper: #fdfbf7; --card: #ffffff;
  --accent: #7c5cff; --accent-soft: #efeaff; --line: #e8e4dc;
}
* { box-sizing: border-box; }
body {
  margin: 0; padding: 0; background: var(--paper); color: var(--ink);
  font-family: Georgia, "Times New Roman", serif;
  line-height: 1.7; font-size: 18px;
}
header.site {
  background: var(--accent-soft); border-bottom: 3px solid var(--accent);
  padding: 2.2rem 1rem 1.4rem; text-align: center;
}
header.site h1 { margin: 0 0 .3rem; font-size: 1.9rem; font-weight: bold; }
header.site p { margin: 0; color: var(--muted); font-style: italic; }
nav { text-align: center; padding: .9rem 1rem; border-bottom: 1px solid var(--line);
  background: var(--card); font-size: .92rem; }
nav a { margin: .25rem .55rem; display: inline-block; color: var(--accent);
  text-decoration: none; }
nav a:hover { text-decoration: underline; }
main { max-width: 46rem; margin: 0 auto; padding: 2rem 1.25rem 3rem; }
h1, h2, h3 { line-height: 1.25; }
h2 { margin-top: 2.1rem; border-bottom: 1px solid var(--line); padding-bottom: .3rem; }
h3 { margin-top: 1.6rem; }
a { color: var(--accent); }
pre {
  background: #2d2d3a; color: #e8e8f2; padding: 1rem 1.1rem;
  border-radius: 10px; overflow-x: auto; font-size: .86rem;
  font-family: "Courier New", monospace; line-height: 1.5;
}
code { font-family: "Courier New", monospace; font-size: .9em;
  background: var(--accent-soft); padding: .1em .4em; border-radius: 4px; }
pre code { background: none; padding: 0; }
blockquote {
  margin: 1.2rem 0; padding: .8rem 1.2rem; border-left: 4px solid var(--accent);
  background: var(--card); border-radius: 0 10px 10px 0; font-style: italic;
}
table { border-collapse: collapse; width: 100%; margin: 1.2rem 0;
  font-size: .95rem; background: var(--card); }
th, td { text-align: left; padding: .55rem .8rem; border: 1px solid var(--line); }
th { background: var(--accent-soft); }
footer { text-align: center; color: var(--muted); font-size: .85rem;
  padding: 1.5rem 1rem 2.5rem; border-top: 1px solid var(--line); }
.nextprev { display: flex; justify-content: space-between; gap: 1rem;
  margin: 2.6rem 0 0; }
.nextprev a { text-decoration: none; background: var(--accent-soft);
  padding: .6rem 1rem; border-radius: 10px; }
.nextprev a:hover { text-decoration: underline; }
@media (max-width: 600px) { body { font-size: 16.5px; } }
"""


def page(title: str, body: str, current: str) -> str:
    nav_items = []
    for slug, label in NAV:
        cls = f' class="current"' if slug == current else ""
        nav_items.append(f'<a href="{slug}.html"{cls}>{html.escape(label)}</a>')
    nav_html = "\n".join(nav_items)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{html.escape(SUBTITLE)}">
<title>{html.escape(title)} — {TITLE}</title>
<style>{CSS}</style>
</head>
<body>
<header class="site"><h1>{TITLE}</h1><p>{SUBTITLE}</p></header>
<nav>
{nav_html}
</nav>
<main>
{body}
<div class="nextprev">{nextprev_links(current)}</div>
</main>
<footer>
Built from the docs/ markdown source by <code>build.py</code> ·
{TITLE} · © 2026 Asdale Dynamics, LLC · MIT licensed
</footer>
</body>
</html>
"""


def nextprev_links(current: str) -> str:
    slugs = [s for s, _ in NAV]
    parts: list[str] = []
    idx = slugs.index(current) if current in slugs else -1
    if idx > 0:
        prev_slug, prev_label = NAV[idx - 1]
        parts.append(f'<a href="{prev_slug}.html">← {html.escape(prev_label)}</a>')
    else:
        parts.append("<span></span>")
    if idx != -1 and idx + 1 < len(NAV):
        next_slug, next_label = NAV[idx + 1]
        parts.append(f'<a href="{next_slug}.html">{html.escape(next_label)} →</a>')
    else:
        parts.append("<span></span>")
    return "".join(parts)


# --------------------------------------------------------------- build

def build() -> list[Path]:
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()

    md_files = sorted(DOCS.glob("*.md"))
    if not md_files:
        raise SystemExit("No markdown files found in docs/")

    built: list[Path] = []
    for md_file in md_files:
        slug = md_file.stem
        md_text = md_file.read_text(encoding="utf-8")
        body = add_para_ids(md_to_html(md_text))
        title = extract_title(md_text)
        out_path = SITE / f"{slug}.html"
        out_path.write_text(page(title, body, slug), encoding="utf-8")
        built.append(out_path)

    # a little index page so site/index.html is the entry point
    toc = ["<ul>"]
    for slug, label in NAV:
        toc.append(f'<li><a href="{slug}.html">{html.escape(label)}</a></li>')
    toc.append("</ul>")
    index_body = "<h2>All chapters</h2>\n" + "\n".join(toc) + (
        "\n<blockquote>Start anywhere. New here? "
        '<a href="00-how-to-use-this-guide.html">Read "How to Use This Guide" first</a>. '
        "This site is static HTML — open it locally, share it, host it anywhere.</blockquote>"
    )
    out_path = SITE / "index.html"
    out_path.write_text(page(TITLE, index_body, ""), encoding="utf-8")
    built.append(out_path)
    return built


def verify(built: list[Path]) -> list[str]:
    errors: list[str] = []
    for path in built:
        text = path.read_text(encoding="utf-8")
        if "<html" not in text or "</html>" not in text:
            errors.append(f"{path.name}: missing html wrapper")
        if "Asdale Dynamics, LLC" not in text:
            errors.append(f"{path.name}: missing copyright line")
        # every internal link must resolve
        for target in re.findall(r'href="([a-z0-9-]+\.html)"', text):
            if not (SITE / target).exists():
                errors.append(f"{path.name}: dead link -> {target}")
        for anchor in re.findall(r'href="#([a-z0-9-]+)"', text):
            if f'id="{anchor}"' not in text:
                errors.append(f"{path.name}: dead anchor -> #{anchor}")
    # spot checks that rendered content includes real chapter text
    spot = SITE / "02-explain-it-back.html"
    if spot.exists():
        if "explain it back" not in spot.read_text(encoding="utf-8").lower():
            errors.append("02-explain-it-back.html: expected content missing")
    spot = SITE / "glossary.html"
    if spot.exists():
        if "hallucination" not in spot.read_text(encoding="utf-8").lower():
            errors.append("glossary.html: expected content missing")
    if len(built) < len(NAV):
        errors.append(f"built only {len(built)} pages, expected at least {len(NAV)}")
    return errors


def main() -> int:
    built = build()
    print(f"Built {len(built)} pages -> {SITE.relative_to(ROOT)}/")
    for p in built:
        print(f"  {p.name}")
    if not any(a == "--check" for a in sys.argv[1:]):
        return 0
    errors = verify(built)
    if errors:
        print("CHECK FAILED:")
        for e in errors:
            print("  -", e)
        return 1
    print("Check passed: structure, links, footer, and content verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
