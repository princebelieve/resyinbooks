# Production notes

## Reference workflow

This production follows the workflow and retained tools in `Serenity and Tranquillity`: a 6 × 9 editable master; separate print and screen PDF layouts; a linked, edition-specific index; EPUB built from the source text; two-up output; generated cover derivative; and retained validation/audit reports. The old book's editorial decisions were not copied. Its consolidation and renumbering of small sections are intentionally not repeated.

## Current outputs

- A5 indexed print interior: 167 pages, including a copyright page with the print ISBN.
- A4 indexed reading PDF: 115 pages, including the front-only cover and copyright page, 183 index locator links, 41 selective related-topic links and 77 return-to-index controls.
- A5 two-up print file: 84 spreads, preserving PDF navigation and the print copyright page.
- Reflowable EPUB 3: all 15 chapters, all 158 numbered sections, the cropped cover, linked contents, 49 subject entries and related-topic links.
- Indexed DOCX copy: 170 section-level XE markers and a native INDEX field; the underlying 6 × 9 source master remains as a separate file.
- The indexed PDFs contain the same 49-entry section-based index. `Production/Subject_Index_Audit.json` maps its entries to the manuscript sections and source-edition locators.

The subject index is an editorial first pass that should be reviewed for preferred terminology and scope. Its PDF page references are generated separately for each trim/layout; the Word index field must be refreshed in Word to compute its own references.

## Source and cover handling

`Source_Materials` contains the original supplied files unchanged. The source parser assembles the fifteen manuscript chapters and marked back matter, excludes proposal/brief directions and production notes, applies only documented working-copy repairs, and retains all numbered headings. `Cover_Front_OnlineStore.jpg` is the digital front-panel crop from the supplied wrap, produced with the same crop workflow used by the previous book.

The original full wrap was not suitable for this interior. Its spine occupied about 140 pixels against a 600-pixel front panel; at A5 that represents about 1.36 inches. The updated 167-page print interior uses an A5 cover proof with a 0.4175-inch spine under the cream-paper assumption retained from the prior workflow. I rebuilt the existing back/front artwork as equal A5 panels, placed the supplied ISBN/barcode on the back and typeset a narrow green/gold spine. The output is a [cover proof](Production/Cover_Spread_A5_167p_Cream_Assumption.pdf), with [dimensions and assumptions recorded](Production/Print_Cover_Audit.json).

The proof follows the prior book's cream-paper coefficient, 0.0025 inches per page. KDP's published cover guidance uses that coefficient for cream paper and requires 0.125-inch bleed; other paper and binding specifications can produce a different spine/template. The proof therefore needs the actual printer's template and paper confirmation before submission. [KDP paperback cover specifications](https://kdp.amazon.com/en_US/help/topic/G201857950) and [cover calculator](https://kdp.amazon.com/cover-templates).

Following the copyright-page pattern in *Serenity and Tranquillity*, I added the supplied print ISBN `978-978-59760-5-2` in plain text on the print copyright page in the A5 print PDF and both Word manuscripts, and retained its barcode on the back cover. The screen PDF and EPUB have the copyright notice but omit the print ISBN because no separate digital-edition ISBN was supplied. Confirm the print ISBN's publisher/distributor assignment before publication.

## Rebuild sequence

1. `python build_manuscript.py` rebuilds the editable source master.
2. `python build_pdf_interiors.py` renders A5 and A4 base interiors through local Edge.
3. `python build_pdf_indexes.py` uses the PyMuPDF package already retained under `Serenity and Tranquillity/.python_libs` to add each PDF's section-based index and navigation, then creates the link-preserving two-up file, previews and audit.
4. `python build_indexed_docx.py` creates a separate editable copy with native Word index markers.
5. `python build_epub.py` creates the reflowable EPUB from source text and the same index configuration.
6. `python validate_epub.py` extracts a review tree and checks EPUB resource/fragment targets. `node check_epub_mobile.mjs` records the responsive preview checks. EPUBCheck 5.4.0 reports are in `Production/EPUB_Validation`.
7. `prepare_print_cover.ps1` rebuilds the A5 wrap proof; `python build_print_cover_pdf.py` wraps it in a dimensioned PDF and refreshes the cover audit.

Base PDFs and intermediate HTML are retained in `Production` to make each stage reproducible. Use the `*_Indexed.pdf` editions listed in `CURRENT_FILES.md` for review.
