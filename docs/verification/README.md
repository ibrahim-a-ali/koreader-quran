# Recorded verification

The recorded reports were produced for Quran PDF Helper 0.1.0 using its actual
Lua handlers, KOReader interface doubles, the prepared full PDF, and the
upstream v1.10 plugin/dictionaries. They are not physical-device UI tests.

Separately, the PDF and plugin have been tested in KOReader at different
randomly selected locations. Not every word or every ayah has been tested,
and the functionality has not been completely verified. The recorded automated
reports must not be read as a claim of exhaustive manual verification.

- [Current full-PDF report](verification.json): 604 pages, 6,236 ayah markers,
  114 surah headers, word-region and native MuPDF selection lookups, juz/status
  formats, popup navigation, occurrence filtering and coexistence.
- [Coexistence report](coexistence_verification.json): eight combinations of
  modern/legacy popup hooks, initialization order and readiness order, with
  PDF-to-EPUB-to-PDF switching, separate settings and menus.
- [Earlier PDF build report](previous_pdf_build_verification.json): the prior
  artwork/copied-text comparison, before separating the plugin identity.
- [Earlier dictionary-reference report](word_reference_verification.json):
  dictionary-key/reference checks recorded during PDF preparation.

The report filenames identify separate stages with different selection/counting
methods; their word-region totals are not interchangeable. The plugin rename
did not regenerate the prepared PDF. The current full report includes its hash.

Run the commands in [PDF_SUPPORT.md](../PDF_SUPPORT.md) to generate fresh results.
