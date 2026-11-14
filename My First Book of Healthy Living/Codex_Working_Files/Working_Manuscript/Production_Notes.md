# Production notes - My First Book of Healthy Living

## Structure and decisions

- Professor_Supplied preserves the raw materials and original cover/illustration board.
- Codex_Working_Files/Working_Manuscript contains the clean book master, editorial map/change log, source notes, illustration records and build scripts.
- For_Professor contains only finished book copies.

Selected illustration originals remain in Working_Manuscript/Illustration_References/mine/. Byte-for-byte WebP copies are in Working_Manuscript/Selected_Illustrations/. PNG files in Selected_Illustrations/png_review/ are Chrome-rendered derivatives for PDF, Word and EPUB embedding.

## Rebuild sequence

Run from C:\Users\ASUS\Resyin Books:

1. render_illustrated_preview.py renders the manuscript source HTML.
2. compose_book_html.py creates A5 print and A4 digital layouts, separates front and back matter, adds title pages, uses the chapter cards as full-page openers, and stages the artwork.
3. Run render_prints.py once to establish pagination. Then number_contents.py reads the actual chapter-art opening pages from both PDFs and inserts those page numbers in the Contents; it leaves links active in A4 and removes link wrappers from the A5 print HTML.
4. Run render_prints.py again to produce the final A5 and A4 PDFs. Check that the numbered chapter openers still match the art-page locations.
5. build_2up.py uses the retained PyMuPDF package from Serenity and Tranquillity to place consecutive A5 pages on landscape sheets. The two-up output is print-only and has no link annotations.
6. build_editable_docx.py writes the A5 Word file with 13 pt body text and all ten images embedded.
7. build_epub.py builds the reflowable EPUB with larger default text, cover, chapter navigation, linked vocabulary and topic finder, and all images embedded.
8. Verify page sizes/counts, visible illustration placement, digital link destinations, text extraction and EPUB/DOCX ZIP/XML integrity.
9. After EPUB and Word have embedded the assets, remove only the temporary `For_Professor/Illustrations/`, `For_Professor/Cover_Front.png` and generated `.html` files. Leave the six usable book files and README in `For_Professor`.

No software installation or network download was needed. Source art was not overwritten. The original text and WebP images remain preserved.

## Final production data

- Print interior: A5, 61 pages; 14 pt body text and no page border.
- Two-up printer PDF: landscape A4, 31 sheets, two consecutive A5 pages per sheet; print-only.
- Digital readable PDF: A4, 49 pages; page-numbered clickable contents, topic finder, glossary terms and chapter navigation.
- EPUB: reflowable, 112% default text, linked navigation and glossary, topic finder, cover and ten chapter illustrations embedded.
- Editable manuscript: A5 page size, 13 pt body text and ten illustrations embedded.
- Online-store cover: standalone front-only JPEG from the supplied wrap.

“Find a Topic” is at the end of the book. Entries link to relevant chapters, and every “New words” item links to a glossary definition. The A5 Contents prints chapter-opening page locators without interactive annotations. Contents, vocabulary, chapter-end navigation and topic-finder links are interactive in the A4 PDF and EPUB. No dense scholarly index was added because chapter links and this topic guide are a better fit for a short children's guide.

The supplied ISBN failed its checksum. No ISBN was fabricated or printed in any new file. The publisher must assign ISBNs; a printer-specific physical wrap requires the selected printer's template and final print ISBN because the spine width and barcode cannot be guessed.
