"""Impose an A5 PDF as consecutive left/right pages on A4 landscape sheets.

Uses the repository's retained PyMuPDF installation under the Serenity project.
The final sheet receives a blank right-hand half if the source page count is odd.
"""
from pathlib import Path
import sys

PROJECT = Path(__file__).resolve().parents[2]
REPOSITORY = PROJECT.parent
sys.path.insert(0, str(REPOSITORY / "Serenity and Tranquillity" / "Codex_Working_Files" / ".python_libs"))
import fitz  # noqa: E402

SOURCE = PROJECT / "For_Professor" / "WAEC_NECO_English_Language_Revision_Handbook_Review_Draft_A5.pdf"
OUTPUT = PROJECT / "For_Professor" / "WAEC_NECO_English_Language_Revision_Handbook_Two_Up_Review.pdf"

source = fitz.open(SOURCE)
imposed = fitz.open()
sheet_width, sheet_height = 841.89, 595.28  # A4 landscape, points
half_width = sheet_width / 2

for index in range(0, len(source), 2):
    sheet = imposed.new_page(width=sheet_width, height=sheet_height)
    sheet.show_pdf_page(fitz.Rect(0, 0, half_width, sheet_height), source, index)
    if index + 1 < len(source):
        sheet.show_pdf_page(fitz.Rect(half_width, 0, sheet_width, sheet_height), source, index + 1)
    else:
        sheet.draw_rect(
            fitz.Rect(half_width, 0, sheet_width, sheet_height),
            color=(1, 1, 1),
            fill=(1, 1, 1),
        )

imposed.save(OUTPUT)
print(f"Created {OUTPUT} with {len(imposed)} sheets from {len(source)} A5 pages.")
