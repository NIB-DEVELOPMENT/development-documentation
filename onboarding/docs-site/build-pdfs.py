#!/usr/bin/env python
"""
NIB Docs Site — PDF builder.

Renders each *-print.html under docs/ into a real text-searchable PDF
under pdf/ using WeasyPrint. This replaces the client-side html2canvas
+ jsPDF approach (which produces image-based, non-searchable PDFs).

Output naming follows the design system convention:
    docs/user-manual-print.html       -> pdf/NIB-User-Manual-v1.0.pdf
    docs/admin-manual-print.html      -> pdf/NIB-Admin-Manual-v1.0.pdf
    docs/supervisor-manual-print.html -> pdf/NIB-Supervisor-Manual-v1.0.pdf
    docs/storage-brief-print.html     -> pdf/NIB-Document-Storage-Brief-v1.0.pdf
    docs/index-print.html             -> pdf/NIB-Docs-Index-v1.0.pdf

Usage:
    python build-pdfs.py             # render all
    python build-pdfs.py admin       # render just admin
"""
import sys
from pathlib import Path
from weasyprint import HTML

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
PDF_DIR = ROOT / "pdf"

# Map print-html stem -> output PDF filename
TARGETS = {
    "user-manual-print":       "NIB-User-Manual-v1.0.pdf",
    "admin-manual-print":      "NIB-Admin-Manual-v1.0.pdf",
    "supervisor-manual-print": "NIB-Supervisor-Manual-v1.0.pdf",
    "storage-brief-print":     "NIB-Document-Storage-Brief-v1.0.pdf",
    "index-print":             "NIB-Docs-Index-v1.0.pdf",
}


def render(stem: str, out_name: str) -> Path:
    src = DOCS / f"{stem}.html"
    if not src.exists():
        raise FileNotFoundError(src)
    out = PDF_DIR / out_name
    # base_url is the docs/ dir so relative refs to ../assets/ and ../colors_and_type.css resolve
    HTML(filename=str(src), base_url=str(DOCS)).write_pdf(target=str(out))
    return out


def main():
    PDF_DIR.mkdir(exist_ok=True)
    filt = sys.argv[1].lower() if len(sys.argv) > 1 else None
    selected = {k: v for k, v in TARGETS.items() if not filt or filt in k.lower()}
    if not selected:
        print(f"No matching targets for filter: {filt}")
        sys.exit(1)
    for stem, out_name in selected.items():
        print(f">> rendering {stem}.html")
        out = render(stem, out_name)
        size_kb = out.stat().st_size / 1024
        print(f"   OK  pdf/{out_name}  ({size_kb:,.0f} KB)")


if __name__ == "__main__":
    main()
