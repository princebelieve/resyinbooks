# Current book files

Use the files in this folder. Superseded editions and old cover wraps are in [Archive_Obsolete](Archive_Obsolete/README.md); no files were deleted. Preview images are in `Previews`. The subject index follows all end matter at the back of the book.

For the documented production history, avoidable rework and reusable checklist for both Resyin books, see [Book_Production_Workflow.md](../Book_Production_Workflow.md).

| File | Use |
| --- | --- |
| [Reflowable EPUB](Serenity_and_Tranquillity.epub) | Recommended for phones, tablets, e-readers and ebook-store submission. Adjustable text, linked contents, section-based index and related-topic links. Validated with EPUBCheck: zero errors or warnings. |
| [Digital PDF](Serenity_and_Tranquillity_Digital_Readable_Indexed.pdf) | Reading on screen: 229 pages, clickable index, related-topic links and return-to-index controls. |
| [A5 print interior](Serenity_and_Tranquillity_Print_Interior_A5_Indexed.pdf) | 345 individual pages for printing; index links also work on screen. |
| [Two-up hardcopy](Serenity_and_Tranquillity_Hardcopy_A5_2up_Indexed.pdf) | 173 landscape spreads with working index links. Use only when the printer requests two-up pages. |
| [Editable Word manuscript](Serenity_and_Tranquillity_Interior_Edit_Indexed.docx) | Editable text and native Word index fields. Select all and press F9 in Word to populate page references. PDF interactive links are added during PDF production. |
| `Cover_Front_OnlineStore_From_Original.jpg` | Current front cover image for online stores. |

## Reading the digital PDF

- Click an underlined index number to open that page. Each end of a range is separately clickable.
- Click a subject after **See** to open its index entry.
- Selected underlined key terms in the chapters open a substantive related section. There is at most one link for a given term per chapter.
- Click **Subject index** at the bottom of a chapter page to return to the index.
- Use the PDF reader's Back or Previous View command to return to where you were reading. Viewer support and shortcuts vary.

These are internal PDF links; they do not need an internet connection. A PDF reader that supports internal links is required. The digital PDF has 177 related-topic links and 203 return-to-index links, in addition to 497 index-number links and 22 index cross-reference links.

## Reading and submitting the EPUB

Open `Serenity_and_Tranquillity.epub` in an EPUB reader and adjust the font size to suit your screen. The text reflows; no zooming or fixed page size is required. Contents and the subject index link to chapters and sections. Selective related-topic links and chapter-end links back to Contents and Subject index are included.

Use the `.epub` file as the ebook manuscript for stores that accept EPUB, and use the existing front-cover JPEG if the store requests a separate cover image. This file has not been uploaded or published. Store approval also depends on their metadata, rights and content requirements.

The supplied ISBN fails its checksum and was omitted from this EPUB's copyright page and metadata. The EPUB has a valid UUID identifier. Confirm a suitable ebook ISBN if a chosen distributor requires one; no ISBN has been invented or reassigned.

See [EPUB_Production_Notes.md](EPUB_Production_Notes.md) for validation reports and rebuilding instructions. EPUB source text came from the editable manuscript rather than extracted PDF pages.

## Production

There is no current full print cover wrap: the archived wraps fit older page counts. Resize the spine for the 345-page interior using the printer's paper specification before printing.

`build_subject_index.py` rebuilds the current editions from the retained source editions in `Archive_Obsolete`, using PyMuPDF in `.python_libs`. `Subject_Index_Audit.json` records locator evidence and every added one-page PDF link, including destination and rectangle. See [Production_Notes.md](Production_Notes.md) and [Subject_Index_Notes.md](Subject_Index_Notes.md) for details.
