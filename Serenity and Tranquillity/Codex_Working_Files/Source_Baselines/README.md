# Retained layout baselines

These three retained layout baselines are required inputs to `../build_subject_index.py` and must remain available for rebuilding the indexed editions:

- `Serenity_and_Tranquillity_Print_Interior_A5_11pt_HeadCorrected.pdf`
- `Serenity_and_Tranquillity_Digital_Readable_CoverCorrected.pdf`
- `Serenity_and_Tranquillity_Interior_Edit.docx`

They are source/layout baselines, not current deliverables. The current indexed PDFs, EPUB, Word file and standalone cover are in the parent project folder. Exact duplicate final editions and unrelated superseded copies were removed during cleanup.

`TOC_Expanded/` contains reproducible working copies of the two PDFs above. They replace the generic chapter labels with the actual chapter titles, add a second single-column Contents page, and update page numbers and bookmarks. `expand_chapter_contents.py` rebuilds these copies without modifying the retained originals; `build_subject_index.py` reads them preferentially and recalculates the final edition indexes.
