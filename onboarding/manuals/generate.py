#!/usr/bin/env python
"""
Manual PDF Generator — NIB Online Portal

Renders each markdown source under manuals/source/*.md into a styled PDF
under manuals/pdf/*.pdf using Python-Markdown + WeasyPrint.

Each source file must start with YAML-style front matter:

    ---
    title: User Manual
    subtitle: NIB Online Portal
    audience: For Bahamian Citizens
    version: 1.0
    date: 2026-05-20
    ---

Usage:
    python generate.py                  # render all sources
    python generate.py USER-MANUAL      # render one (case-insensitive prefix match)
"""
import re
import sys
from pathlib import Path

import markdown
from weasyprint import HTML, CSS

ROOT = Path(__file__).resolve().parent
SOURCE_DIR = ROOT / "source"
PDF_DIR = ROOT / "pdf"
STYLE = ROOT / "styles" / "manual.css"

# The docs and images sit two levels up (onboarding/).
ONBOARDING_DIR = ROOT.parent

MD_EXTENSIONS = [
    "tables",
    "fenced_code",
    "toc",
    "attr_list",
    "sane_lists",
    "smarty",
]

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title} — {subtitle}</title>
</head>
<body data-manual-title="{title}">

<section class="cover">
  <img src="styles/nib-logo.png" class="logo" alt="NIB" />
  <h1>{title}</h1>
  <div class="subtitle">{subtitle}</div>
  <div class="accent-line"></div>
  <div class="audience">{audience}</div>
  <div class="meta">
    <strong>Version {version}</strong>  •  {date}<br>
    National Insurance Board of The Bahamas
  </div>
</section>

<section class="toc">
<h2>Contents</h2>
{toc}
</section>

<article>
{body}
</article>

</body>
</html>
"""


def parse_front_matter(text: str) -> tuple[dict, str]:
    """Parse simple YAML-style front matter (no nested keys)."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end < 0:
        return {}, text
    block = text[3:end].strip()
    body = text[end + 4 :].lstrip("\n")

    meta = {}
    for line in block.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta, body


def render(source_path: Path) -> Path:
    """Render one markdown source into a PDF."""
    raw = source_path.read_text(encoding="utf-8")
    meta, body_md = parse_front_matter(raw)

    md = markdown.Markdown(extensions=MD_EXTENSIONS)
    body_html = md.convert(body_md)
    toc_html = md.toc

    full_html = HTML_TEMPLATE.format(
        title=meta.get("title", source_path.stem),
        subtitle=meta.get("subtitle", "NIB Online Portal"),
        audience=meta.get("audience", ""),
        version=meta.get("version", "1.0"),
        date=meta.get("date", ""),
        toc=toc_html,
        body=body_html,
    )

    out_path = PDF_DIR / f"{source_path.stem}.pdf"
    PDF_DIR.mkdir(exist_ok=True)

    # base_url so relative image paths (../images/citizen/foo.png) resolve
    # against the onboarding/ dir.
    HTML(string=full_html, base_url=str(ONBOARDING_DIR)).write_pdf(
        target=str(out_path),
        stylesheets=[CSS(filename=str(STYLE))],
    )
    return out_path


def main():
    filter_arg = sys.argv[1].lower() if len(sys.argv) > 1 else None
    sources = sorted(SOURCE_DIR.glob("*.md"))
    if filter_arg:
        sources = [s for s in sources if filter_arg in s.stem.lower()]
    if not sources:
        print(f"No matching sources in {SOURCE_DIR}")
        sys.exit(1)

    for src in sources:
        print(f">> rendering {src.name}")
        out = render(src)
        size_kb = out.stat().st_size / 1024
        print(f"  OK{out.relative_to(ROOT)}  ({size_kb:,.0f} KB)")


if __name__ == "__main__":
    main()
