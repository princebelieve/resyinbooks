# Resyin Books: production history and repeatable workflow

This guide records how *Serenity and Tranquillity* and *Givers and Takers in Africa* reached their current deliverables. It separates book-specific decisions from the reusable production sequence and identifies rework that can be avoided on the next title.

## Current project folders

- Both project folders now contain only current deliverables and `CURRENT_FILES.md`. Superseded editions, source copies, scripts, intermediates, audits and previews were deleted from the active folders after being committed to Git.
- The shared production history and reusable workflow remain in this file. Earlier source and support files can be restored from Git history when needed.
- Each project's `CURRENT_FILES.md` is the delivery index. Use it instead of opening files by guessing from a working directory.

## Reusable production sequence for the next book

### 1. Receive, preserve and inventory

1. Save every supplied source file byte-for-byte in a clearly named `Source_Materials` folder. Keep the original cover art with the sources.
2. Record a file inventory and identify which files are the manuscript, author brief, proposal, research/reference material, images and production directions.
3. Commit the received source package before editing so that it can be restored even if the active project is later cleaned to final-only files.
4. Separate authored book text from embedded instructions, planning notes and file metadata before assembly. Keep a source-boundary note so that instructions are not accidentally printed as book prose.
5. Do not edit the source originals. Make repairs in a separate working copy and log each one.

### 2. Agree the editorial boundary before layout

1. Establish the intended title, subtitle, author, publisher, language, edition and book structure from the supplied materials.
2. Assemble the manuscript in the author's supplied order. Preserve chapters, headings, numbering and wording unless a specific correction is justified and recorded.
3. Identify corrupted text, citations, duplicate references, unresolved factual claims and editorial notes. Repair only clear mechanical damage; place uncertain material in an author-review list.
4. Compare the assembled manuscript against the source passages before typesetting. Confirm chapter and section counts, text line/paragraph coverage, tables and back matter.
5. Obtain author review of substantive corrections and open reference or biography questions before pagination is treated as final.

### 3. Freeze book metadata and front matter

1. Create the title page and a copyright page using approved rights wording, publisher imprint and edition/date details. Do this before producing the first final interior.
2. Confirm ISBN assignment separately for each format being issued. Print ISBN belongs as plain text on the print copyright page and can appear as a barcode on the printed back cover. A separately published EPUB or PDF may require its own format-specific ISBN. Never invent, reuse or copy an ISBN from another edition.
3. Build the table of contents from the actual final chapter structure. It belongs in the front matter; the subject index does not.
4. Keep title, subtitle, author, publisher, ISBN and edition metadata consistent across copyright page, cover, PDF metadata, EPUB package metadata and retailer submission fields.

### 4. Produce one editable master, then derive the editions

1. Retain one editable Word master with semantic heading styles, refreshable contents and stable source text. Keep an indexed Word copy separate if native Word index fields are needed.
2. Render the print interior page-by-page at the selected trim size (A5 for these two projects). The interior PDF does not include the print wrap cover.
3. Render a separate screen-reading PDF at the chosen digital size (A4 for these projects). Do not describe a reflowable EPUB as A4 or A5; it adjusts to the reading device.
4. Build the EPUB from the editable/source text, not from PDF text extraction. Include semantic navigation, copyright/rights text, a digital cover image, accessible headings and an index whose links point to sections rather than fixed PDF pages.
5. Add the subject index only after all chapters and back matter are stable. Place it after the conclusion, references, appendices, glossary, author note and other supplied end matter. Regenerate its page locators separately for each fixed-page PDF. The Word INDEX field must be refreshed in Word after its own layout is settled.
6. Create a two-up A5 file from the final one-page A5 print PDF only when useful to the printer. Two-up is not booklet imposition; do not create it as an assumed universal requirement.

### 5. Make the digital front cover and print wrap as separate assets

1. Produce a standalone front-only JPEG or PNG for ebook/retailer upload. It must show only the front panel, with no spine, barcode or back-cover panel. Store it as its own file, separate from the cover image embedded in a PDF or EPUB.
2. Produce the print wrap only after the print interior page count, trim, paper, binding and bleed are known. Use the selected printer's current template whenever possible.
3. Derive the spine from the actual final page count and the printer's stock. A KDP paper coefficient is only appropriate for a KDP-bound proof; it is not a universal printer specification.
4. Compare the wrap's front, spine and back panels against the template. Check barcode clearance, title/author spelling, crop/bleed and the ISBN before export.

### 6. Run one final quality-control pass

- Compare all retained manuscript text with the agreed source assembly; review every logged edit.
- Check title page, copyright page, contents, chapter order, page size, page count, running heads and folios.
- Check that the bibliography/back matter precedes the subject index, and that the index is the final section.
- Verify ISBN number and format assignment; check its appearance on print copyright page and back-cover barcode where applicable.
- Check PDF links after saving, index locators against each edition, and two-up links if that file is requested.
- Run EPUBCheck on the final EPUB, verify package resources and link targets, and inspect representative phone/tablet sizes with enlarged text.
- Inspect the first, middle and final pages, copyright page, contents, index, back matter, cover JPEG and full-wrap proof visually.
- Update the file guide. For a final-only handoff, keep only deliverables and the file guide in the project folder. First confirm the source, tools and production history are committed; then delete working copies when the user requests it. Compare file hashes before removing duplicate deliverables.
- Commit the finished project locally. Treat a GitHub push as a separate network operation and confirm that it succeeded before saying the remote is updated.

## How *Serenity and Tranquillity* was produced

### Source and editorial choices

The retained editable manuscript was used for EPUB text, while corrected print and digital PDFs were used for the fixed-layout indexed editions. The manuscript contains 25 chapters and 250 numbered sections. Its earlier contents listed 18 chapters, so the contents was rebuilt to match the manuscript; unsupported lists of figures and tables were removed when their referenced material was absent.

During the earlier interior work, many small numbered sections were consolidated and renumbered while their body text was retained. That was a substantial editorial intervention. It was specific to that book's earlier structure and is not a default production step. The newer *Givers and Takers* book therefore kept Prof's 158 numbered sections in order rather than repeating that restructuring.

The latest EPUB was built from the editable DOCX and checked against 5,440 retained paragraphs. It contains 25 chapters, 250 sections, navigation, a subject index and selective related-topic links. The supplied print ISBN `978-978-965-123-4` fails the ISBN-13 checksum, so no ISBN was included in the EPUB and no replacement was invented. Confirm the correct identifier with the publisher before future publication.

### Current editions and cover

The current editions are a 345-page A5 print PDF, 229-page A4 screen PDF, 173-spread two-up file, indexed Word manuscript, reflowable EPUB and standalone front JPEG. EPUBCheck reported zero errors and warnings; mobile reflow, link targets and index locators were checked.

The current standalone retailer cover is [Cover_Front_OnlineStore_From_Original.jpg](Serenity%20and%20Tranquillity/Cover_Front_OnlineStore_From_Original.jpg). It is a separate image file, not just the cover page inside a PDF. The current folder has no final full-wrap print cover because the retained wrap was prepared for an older page count; a print provider's template is needed for a new wrap.

### Index-placement note

The original *Serenity and Tranquillity* index was near the end, not at the beginning: it occupied print pages 334–340 and digital pages 221–225, before the remaining list of tables/frameworks, author's note and final reflection. That was a Codex placement error, not a standard to copy. I have now rebuilt its current PDFs and editable Word copy so the index follows all end matter. It occupies print pages 339–345 and digital pages 225–229; total page counts remain 345 and 229.

### Rework that could have been avoided

- The early 299-page print layout and its related cover calculations became obsolete when the later 339-page head-corrected interior was produced and indexed to 345 pages.
- Cover work based on an earlier page count had to be reconsidered. The final 345-page edition still needs its printer-specific full wrap.
- The 18-chapter contents and unsupported figure/table lists required rebuilding once the actual 25-chapter manuscript was compared with the front matter.
- Consolidating and renumbering sections added editorial scope. It should be done only when the author approves a documented restructuring, not as routine formatting.
- The index was initially inserted before some end matter. Rebuilding was necessary to move it; future editions should paginate and index only after the full end matter is assembled.

## How *Givers and Takers in Africa* was produced

### Source boundaries and preservation

Five supplied text files and the supplied full-wrap JPEG were copied unchanged into `Production_Working_Files/Source_Materials` during production. The first text file combines Prof's brief and planning notes with Chapters 1–3; only the passage beginning at `CHAPTER ONE` and ending before `3. DIRECTION FOR THE REMAINING CHAPTERS` was treated as manuscript. The other source files supplied Chapters 4–15 and back matter. At the user's request, the source copies and production files were later deleted from the active tree; their committed versions remain in Git history.

All 15 chapters and 158 numbered headings were assembled in source order. The preservation audit found all 1,892 chapter lines matched after the documented damaged-citation repair. It records 375 back-matter lines/cells and explains the specific changes. No chapter was rewritten, merged or renumbered.

Working-copy changes were limited and logged: repair the damaged Afrobarometer citation and add its full reference; keep one copy each of duplicate Sen (1999) and North (1990) citations; exclude one embedded editorial instruction; and format the 15 policy recommendations in a table without changing their order or wording. The supplied originals were not edited; their committed copies remain in Git history.

### Editions and ISBN/cover handling

The deliverables are a 167-page A5 print PDF, 115-page A4 reading PDF, 84-spread A5 two-up file, editable indexed Word manuscript, reflowable EPUB, standalone front-cover JPEG and print-wrap proof. EPUBCheck reported zero errors and warnings; EPUB links, mobile reflow and PDF link destinations were checked.

The supplied cover displays print ISBN `978-978-59760-5-2`. A copyright page matching the rights wording and page pattern of the prior book was added to the print master, and the print ISBN now appears there as plain text. The existing barcode remains on the printed back-cover art. The number's checksum is valid, but its assignment to this edition must still be confirmed. No digital ISBN was supplied, so none was invented or added to the EPUB or screen PDF.

The standalone retailer image is [Givers_and_Takers_in_Africa_Cover_Front.jpg](Givers%20and%20Takers%20in%20Africa/Givers_and_Takers_in_Africa_Cover_Front.jpg), a 1800 × 2559 JPEG cropped from the supplied full wrap. It is a separate front-only image and can be uploaded as a JPEG where a retailer accepts that size and ratio. The PDF cover is a different full-wrap asset.

The original full wrap's spine was far too wide for the new interior. A 167-page A5 working proof was rebuilt using a cream-paper width assumption carried over from the reference workflow. Its printer template, paper and binding still need confirmation; regenerate it from the printer's template before printing if their specifications differ.

### Rework that could have been avoided

- The print ISBN and copyright page should have been compared with *Serenity and Tranquillity* before the first interior was rendered. Adding it later required rebuilding the print outputs and cover page count.
- The original full-wrap spine should have been measured against the planned page count at intake. This would have revealed the 1.36-inch source spine mismatch before print-cover work.
- Printer paper, binding, trim and bleed should have been established before calling a cover spread final. The cream-paper proof is a useful draft, not printer approval.
- The first PDF index build placed the index before the supplied back matter. It was moved to the very end in the corrected PDFs. Build the index after end matter is frozen and validate its last-page position before publishing.
- Source/brief boundaries should be recorded before assembly. This avoided importing the proposal and drafting directions, but should be the standard first step for every mixed source package.
- Edition changes made after pagination (copyright page, bibliography edits or chapter revisions) force PDF, index, two-up and cover refreshes. Complete those decisions before the final page-count and cover calculations.

## The shortest reliable path for the next title

1. Preserve and inventory all received sources; mark book text, guidance and production instructions.
2. Assemble the editable manuscript and log corrections; obtain author decisions on substantive issues.
3. Complete front matter, copyright page, publisher metadata and format-specific ISBN assignment.
4. Freeze and compare the text; refresh the contents; render print and screen PDFs plus the EPUB.
5. Place the generated subject index after all end matter; create a two-up file only if requested.
6. Make the standalone front cover; build the print wrap from final page count and the selected printer template.
7. Perform one final text, page, index, link, cover and EPUB validation pass; update the file guide.
8. Keep final files and the file guide in the project folder. Commit sources and production history before deleting support copies when a final-only workspace is requested. Confirm separately whether and where the commit was pushed.

