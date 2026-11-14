# EPUB production notes

`../../../For_Professor/Givers_and_Takers_in_Africa.epub` is the current reflowable EPUB 3, built directly from the preserved text. It contains 15 chapters, 158 numbered sections, the front-only cover image, a linked contents document, a 49-entry section-based index, four See references, and selective cross-topic links. Text reflows to reader font and screen width.

## Validation

- EPUBCheck 5.4.0: zero fatal errors, zero errors, zero warnings.
- `Structure_Report.json`: 20 XHTML documents, 19 spine documents, 236 internal links checked, and no missing file or fragment targets; the first `mimetype` member is uncompressed.
- `Mobile_Reflow_Report.json`: 12 checks at 320, 390 and 768 CSS-pixel widths, including enlarged text at 390 pixels; no horizontal overflow.
- `../Previews/EPUB` contains representative chapter and large-text screenshots.

These checks cover the saved package and representative responsive viewports; they do not certify every reader, accessibility conformance or a retailer's own conversion. No store upload or publication was performed.
