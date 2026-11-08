#!/usr/bin/env python3
"""Attach Quran Helper page manifests without changing PDF artwork or text.

Usage: python tools/mushaf_pdf/embed_koreader.py INPUT.pdf LAYOUT.json OUTPUT.pdf
Requires PyMuPDF. See docs/PDF_SUPPORT.md for the page-manifest contract.
SPDX-License-Identifier: GPL-3.0-only
"""
import argparse
import base64
import json
from pathlib import Path
import fitz


def embed(source: Path, layout: Path, output: Path) -> dict:
    manifest = json.loads(layout.read_text(encoding="utf-8"))
    if manifest.get("schema") != "quran-ebook-pdf-2":
        raise ValueError("Unsupported Quran PDF manifest schema")
    pages = manifest["pages"]
    doc = fitz.open(source)
    if len(doc) != len(pages):
        raise ValueError("Layout page count does not match the PDF")
    for i, data in enumerate(pages):
        page = doc[i]
        if abs(page.rect.width-data["z"][0])>0.01 or abs(page.rect.height-data["z"][1])>0.01:
            raise ValueError(f"Native page dimensions differ on PDF page {i+1}")
        for link in page.get_links():
            if link.get("uri", "").startswith("quran-ebook://page") and "?format=2&data=" in link["uri"]:
                page.delete_link(link)
        encoded = base64.urlsafe_b64encode(json.dumps(data, ensure_ascii=False,
            separators=(",", ":")).encode("utf-8")).decode("ascii").rstrip("=")
        page.insert_link({"kind": fitz.LINK_URI, "from": fitz.Rect(-40,-40,-39,-39),
            "uri": f"quran-ebook://page{data['n']}?format=2&data={encoded}"})
    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output, garbage=3, deflate=True)
    return {"pages": len(pages), "ayahs": sum(len(p["a"]) for p in pages),
        "surah_headers": sum(len(p["h"]) for p in pages),
        "word_regions": sum(len(p["w"]) for p in pages), "output": str(output)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("layout", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve():
        parser.error("Use a separate output file")
    print(json.dumps(embed(args.input, args.layout, args.output), ensure_ascii=False))
