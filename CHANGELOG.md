# Independent plugin identity: 0.1.0

- Limited release downloads to the PDF-only plugin ZIP and full Quran PDF.
  Dictionaries are obtained separately from the original Quran Ebook project.
- Documented the King Fahd Glorious Quran Printing Complex PDF source,
  preserved original vector layout, and AI-assisted word-copy/lookup preparation.
- Recorded KOReader testing at randomly selected locations, while making clear
  that every word and ayah has not been tested and verification is incomplete.
- Renamed the plugin and menu to Quran PDF Helper.
- Changed directory/internal identity to quran_pdf.koplugin / quran_pdf.
- Isolated preferences in quran_pdf.lua; quran.lua stays with the original.
- Renamed the PDF adapter module and separated shared popup-hook state.
- Made this plugin PDF-only; original Quran Helper continues to own EPUBs.
- Added per-document coexistence guards for the original v1.10 popup parser.
- Added close/reset handling so pending PDF navigation cannot affect the next book.
- Added automated tests for both plugin orders, both readiness orders, both
  popup APIs, separate menus/settings and PDF/EPUB/PDF document switching.
- Kept the prepared PDF format, dictionary keys and dictionary files unchanged.
- Updated installation, migration and build instructions. Removed the old
  integration patch that would overwrite the original quran.koplugin folder.

Based on Quran Helper v1.10 by zeeyado/quran-ebook, GPL-3.0-only.
Modified 2026-11-08. KOReader spot checks completed; exhaustive verification
of every word and ayah remains incomplete.
