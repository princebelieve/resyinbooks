# EPUB production notes

Created 11 November 2026. Current deliverable: [Serenity_and_Tranquillity.epub](Serenity_and_Tranquillity.epub), approximately 2.2 MB.

## Reading and navigation

This is a reflowable EPUB 3, with relative font sizes, one text column, semantic headings and lists, and no fixed body font size or page dimensions. The cover image scales to the reader. It includes 25 chapters, 250 numbered sections, front and back matter, EPUB 3 navigation, an older-reader NCX, and reading-order landmarks.

The alphabetical subject index contains 267 topic/subtopic entries and 11 See cross-references. Its references link to section headings or specific passages, rather than PDF page numbers. The chapters contain 178 selective related-topic links, with at most one occurrence of a given related term linked per chapter. Chapter-end controls link to Contents and Subject index.

## Source preservation

The source is `Serenity_and_Tranquillity_Interior_Edit_Indexed.docx`. Visible Unicode text was read directly from its XML, avoiding PDF font substitutions and line-break extraction artifacts. Every retained source paragraph was compared with the saved EPUB text: 5,440 paragraphs passed. A leading text bullet is replaced by a semantic list marker, with the remaining wording preserved.

Generated Word contents and index placeholders were replaced with EPUB navigation and a linked subject index. Original PDF files were not changed. The supplied ISBN, 978-978-965-123-4, fails the ISBN-13 checksum; it was omitted from the EPUB copyright page and metadata. No replacement ISBN was invented. The EPUB uses UUID `6ed94faf-cf70-55a1-b5a5-9a8bd915efbb` as its package identifier. Confirm an ebook ISBN if required by the selected distributor.

Title: Serenity and Tranquillity. Subtitle: In Personal Life, Community Life, National Development and the Future of Humanity. Author: Prof. Johnson Agharese Egonmwan. Publisher: Resyin (NG) Consults. Language: British English. The subtitle is retained on the title page and in the description. No publication date or new edition number was invented.

## Validation

- Official EPUBCheck 5.4.0: **0 fatal errors, 0 errors, 0 warnings**. Reports: [epubcheck.txt](EPUB_Validation/epubcheck.txt) and [epubcheck.json](EPUB_Validation/epubcheck.json).
- ZIP packaging, uncompressed first mimetype entry, XML parsing, manifest and spine, unique IDs, cover alternative text, internal resources and fragment targets all passed. Details: [Structure_Report.json](EPUB_Validation/Structure_Report.json).
- 1,013 internal link/resource references were checked, including 813 fragment references.
- Representative chapter, index and contents pages passed twelve browser reflow checks: 320, 390 and 768 CSS-pixel widths, plus 390 pixels with doubled text. No horizontal overflow was detected. Details: [Mobile_Reflow_Report.json](EPUB_Validation/Mobile_Reflow_Report.json).
- Screenshots: [phone chapter](Previews/EPUB/Mobile_Chapter_Preview.png) and [enlarged text](Previews/EPUB/Mobile_LargeText_Preview.png).

Browser checks show XHTML/CSS reflow; they do not certify every device or retailer's conversion. Formal accessibility conformance has not been certified. No store upload or publication was performed.

## Store submission

Upload the `.epub` as the manuscript where EPUB is accepted. If a separate cover is required, use `Cover_Front_OnlineStore_From_Original.jpg`. Complete the store's author, title/subtitle, description, rights, categories, pricing and identifier fields, and inspect its own preview before publishing. Validation demonstrates format conformance, not guaranteed retailer approval.

Official references checked during production:

- [Amazon KDP supported manuscript formats](https://kdp.amazon.com/en_US/help/topic/G200634390) includes EPUB subject to Kindle publishing specifications.
- [Apple Books web publishing](https://authors.apple.com/support/4574-publish-book-from-web) accepts an EPUB file alongside cover and submission metadata.
- [Apple Books metadata guidance](https://itunespartner.apple.com/books/support/12-metadata) describes ISBNs as optional.
- [W3C EPUBCheck](https://www.w3.org/publishing/epubcheck/) is the format-conformance validator used here.

## Rebuilding

Run `python Book_Production/build_epub.py`. This uses the Python standard library and reads the current manuscript, front-cover JPEG and index configuration from `build_subject_index.py`. It writes the EPUB and structural report.

Then rerun EPUBCheck; structural checks alone do not replace it:

```powershell
java -jar Book_Production/.tools/epubcheck-5.4.0/epubcheck.jar Book_Production/Serenity_and_Tranquillity.epub --json Book_Production/EPUB_Validation/epubcheck.json
```

The local `.tools/epub-preview` resources used by `check_epub_mobile.mjs` must also be refreshed from the new EPUB before rerunning the mobile check. `Previews/EPUB` contains representative browser preview resources and screenshots, not a separate edition for distribution.
