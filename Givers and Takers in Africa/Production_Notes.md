# Production notes

## Reference workflow

This production follows the workflow and retained tools in `Serenity and Tranquillity`: a 6 × 9 editable master; separate print and screen PDF layouts; a linked, edition-specific index; EPUB built from the source text; two-up output; generated cover derivative; and retained validation/audit reports. The old book's editorial decisions were not copied. Its consolidation and renumbering of small sections are intentionally not repeated.

## Current outputs

- A5 indexed print interior: 166 pages.
- A4 indexed reading PDF: 114 pages, including the front-only cover, 183 index locator links, 41 selective related-topic links and 77 return-to-index controls.
- A5 two-up print file: 83 spreads, preserving PDF navigation.
- Reflowable EPUB 3: all 15 chapters, all 158 numbered sections, the cropped cover, linked contents, 49 subject entries and related-topic links.
- Indexed DOCX copy: 170 section-level XE markers and a native INDEX field; the underlying 6 × 9 source master remains as a separate file.
- The indexed PDFs contain the same 49-entry section-based index. `Production/Subject_Index_Audit.json` maps its entries to the manuscript sections and source-edition locators.

The subject index is an editorial first pass that should be reviewed for preferred terminology and scope. Its PDF page references are generated separately for each trim/layout; the Word index field must be refreshed in Word to compute its own references.

## Source and cover handling

`Source_Materials` contains the original supplied files unchanged. The source parser assembles the fifteen manuscript chapters and marked back matter, excludes proposal/brief directions and production notes, applies only documented working-copy repairs, and retains all numbered headings. The original wrap is preserved. `Cover_Front_OnlineStore.jpg` is a digital front-panel crop from the provided wrap, following the same crop workflow documented in the previous book. It is not a new print wrap.

The existing cover ISBN passes its checksum, but its assignment to this edition is unconfirmed. It has not been added to EPUB metadata. The print-wrap spine remains uncalculated until the final page count and printer paper specification are known.

## Rebuild sequence

1. `python build_manuscript.py` rebuilds the editable source master.
2. `python build_pdf_interiors.py` renders A5 and A4 base interiors through local Edge.
3. `python build_pdf_indexes.py` uses the PyMuPDF package already retained under `Serenity and Tranquillity/.python_libs` to add each PDF's section-based index and navigation, then creates the link-preserving two-up file, previews and audit.
4. `python build_indexed_docx.py` creates a separate editable copy with native Word index markers.
5. `python build_epub.py` creates the reflowable EPUB from source text and the same index configuration.
6. `python validate_epub.py` extracts a review tree and checks EPUB resource/fragment targets. `node check_epub_mobile.mjs` records the responsive preview checks. EPUBCheck 5.4.0 reports are in `Production/EPUB_Validation`.

Base PDFs and intermediate HTML are retained in `Production` to make each stage reproducible. Use the `*_Indexed.pdf` editions listed in `CURRENT_FILES.md` for review.
