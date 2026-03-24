"""
xml_to_pdf.py — Convert PMC JATS XML full text to a readable PDF.

Usage: python data/xml_to_pdf.py
Output: data/paper.pdf
"""
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from fpdf import FPDF

XML_PATH = Path(__file__).parent / "paper_raw.xml"
PDF_PATH = Path(__file__).parent / "paper.pdf"


def strip_ns(tag: str) -> str:
    """Remove namespace prefix from XML tag."""
    return tag.split("}")[-1] if "}" in tag else tag


def iter_text(elem, depth: int = 0) -> list[tuple[str, str]]:
    """
    Walk JATS XML and yield (style, text) tuples.
    style: 'title' | 'heading' | 'body' | 'caption'
    """
    result = []
    tag = strip_ns(elem.tag)

    # Collect text in this element
    if elem.text and elem.text.strip():
        text = elem.text.strip()
        if tag in ("article-title",):
            result.append(("title", text))
        elif tag in ("title",):
            result.append(("heading", text))
        elif tag in ("label", "caption", "table-wrap-foot"):
            result.append(("caption", text))
        elif tag in ("p", "td", "th", "list-item", "def",):
            result.append(("body", text))
        elif tag not in ("ref", "element-citation", "mixed-citation",
                         "pub-id", "year", "source", "volume", "fpage",
                         "lpage", "issue", "person-group", "name",
                         "surname", "given-names"):
            result.append(("body", text))

    # Recurse children
    for child in elem:
        result.extend(iter_text(child, depth + 1))
        if child.tail and child.tail.strip():
            tail = child.tail.strip()
            if depth == 0:
                result.append(("body", tail))

    return result


def build_pdf(segments: list[tuple[str, str]]) -> FPDF:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_margins(20, 20, 20)

    seen: set[str] = set()

    for style, raw in segments:
        # Deduplicate adjacent identical lines
        key = (style, raw[:80])
        if key in seen:
            continue
        seen.add(key)

        # Sanitize: fpdf latin-1 safe
        text = raw.encode("latin-1", errors="replace").decode("latin-1")

        if style == "title":
            pdf.set_font("Helvetica", "B", 14)
            pdf.multi_cell(0, 7, text)
            pdf.ln(3)
        elif style == "heading":
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 6, text)
            pdf.ln(2)
        elif style == "caption":
            pdf.set_font("Helvetica", "I", 9)
            pdf.multi_cell(0, 5, text)
            pdf.ln(1)
        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 5, text)
            pdf.ln(1)

    return pdf


def main():
    print(f"Parsing {XML_PATH}...")
    tree = ET.parse(str(XML_PATH))
    root = tree.getroot()

    segments = iter_text(root)
    print(f"  Extracted {len(segments)} text segments.")

    pdf = build_pdf(segments)
    pdf.output(str(PDF_PATH))
    size_kb = PDF_PATH.stat().st_size // 1024
    print(f"  Written {PDF_PATH} ({size_kb} KB, {pdf.page} pages)")


if __name__ == "__main__":
    main()
