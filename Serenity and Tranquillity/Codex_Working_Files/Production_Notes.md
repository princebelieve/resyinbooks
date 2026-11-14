# Production notes

## Reflowable EPUB (11 November 2026)

[Serenity_and_Tranquillity.epub](../For_Professor/Serenity_and_Tranquillity.epub) is the current ebook edition for phones and ebook-store submission. It contains all 25 chapters and 250 retained numbered sections, the original front cover, a linked contents page and navigation, a section-based subject index, and 178 selective related-topic links. Reader font size and page width remain adjustable.

The EPUB was built directly from the editable DOCX, with 5,440 retained source paragraphs verified against the saved XHTML. Word-generated contents/index placeholders and the invalid supplied ISBN were omitted. Its metadata uses a stable UUID rather than an unconfirmed ebook ISBN. The subtitle remains on the title page and in the description; the main metadata title is Serenity and Tranquillity.

EPUBCheck 5.4.0 passed with zero errors and zero warnings. Internal resources and fragment targets were checked. Twelve representative mobile/tablet reflow checks passed at 320, 390 and 768 CSS pixels, including doubled text at 390 pixels. See [EPUB_Production_Notes.md](EPUB_Production_Notes.md) for details and limitations.

## Indexed editions (11 November 2026)

For current deliverables and reading instructions, see [CURRENT_FILES.md](../CURRENT_FILES.md). `Source_Baselines` contains three retained layout baselines (the prior print PDF, screen PDF and editable DOCX) required by `build_subject_index.py`; they are build inputs, not current editions. Other superseded duplicate editions were removed. Preview images are in `Previews`.

The later TOC correction (14 November 2026) replaces generic chapter labels with all 25 complete chapter titles across two one-column pages. The opening page numbers match each chapter's printed folio. The EPUB keeps its original single-column, reflowable TOC for phones. The digital PDF keeps clickable navigation; the A5 and two-up print files have no link annotations.

The actual extracted body type is 11 pt in the A5 print PDF and 11.5 pt in the A4 digital PDF. After review, the Contents entries in both PDFs were raised from their smaller sizes to 11 pt for readability. Eleven-point body type is within the conventional range for adult print interiors; it is smaller than the 14 pt used for the children's guide.

The existing subject index listed topics without page references and combined multiple entries into paragraphs. The new editions replace it with an alphabetical, two-column index containing 266 topic/subtopic entries, 11 cross-references, letter headings, and page ranges. References were generated separately for each PDF from substantive manuscript sections.

- [Indexed A5 print interior](../For_Professor/Serenity_and_Tranquillity_Print_Interior_A5_Indexed.pdf): 346 pages, based on a 340-page, 11 pt, head-corrected edition with the expanded Contents. Index: pages 340-346, after all remaining end matter.
- [Indexed two-up hardcopy](../For_Professor/Serenity_and_Tranquillity_Hardcopy_A5_2up_Indexed.pdf): 173 landscape spreads; last right-hand page is blank; print-only.
- [Indexed digital PDF](../For_Professor/Serenity_and_Tranquillity_Digital_Readable_Indexed.pdf): 230 pages, with its corrected cover. Index: pages 226-230, after all remaining end matter.
- [Editable indexed manuscript](../For_Professor/Serenity_and_Tranquillity_Interior_Edit_Indexed.docx): native Word index markers and INDEX field. Select all in Word and press F9 to populate its page references after layout.

Chapter text is retained. The added Contents page shifts subsequent page numbers by one; the chapter locators, PDF bookmarks and subject-index references were regenerated from the revised edition. The A5 Contents uses 11 pt and wraps long titles within each row. The retained original and TOC-expanded build baselines remain available in `Source_Baselines`. A current full-wrap print cover is not present; use the selected printer's template to create one for the 346-page interior.

See [index review notes](Subject_Index_Notes.md) and `Subject_Index_Audit.json` for the locator method and entry evidence. Rebuild with `expand_chapter_contents.py` followed by `build_subject_index.py`; PyMuPDF is retained in `.python_libs`. Print files have no interactive links; digital PDF links remain enabled.

## Earlier editions (archived; historical notes below)

## Interior editions

- Print interior: 6 x 9 in, 299 pages, black text, no bleed.
- Screen PDF: A4, 224 pages, with a vector cover page, clickable table of contents, and PDF chapter bookmarks.
- Editable source: 6 x 9 in DOCX. Its table of contents is a Word field and can be refreshed after edits.

The supplied front matter had a contents page for an earlier 18-chapter version, while the manuscript contains 25 chapters. The rebuilt contents follows the supplied chapters. The unsupported lists of figures and tables were removed because no corresponding figures or tables were present. The source chapters had very many small numbered sections; headings were consolidated and renumbered while their body text was retained.

## Cover assumptions

The one-page wrap PDF is sized for a 6 x 9 in KDP paperback on cream paper, using the final 299-page interior. The calculated spine is 0.7475 in; the wrap is 12.9975 x 9.25 in including bleed. Other printers may use different paper calipers or templates; use their cover template before upload.

The ISBN text is retained exactly as supplied: 978-978-965-123-4. The barcode panel is intentionally blank; KDP can add a barcode when a cover is uploaded without one. The ISBN's final digit does not pass the ISBN-13 checksum, so this number may need publisher or retailer verification before listing.
