# Quran PDF Helper 0.1.0

Quran PDF Helper is an independent, PDF-only derivative of Quran Helper v1.10
from [zeeyado/quran-ebook](https://github.com/zeeyado/quran-ebook), based on commit
`c9550fdd58b0feec36300dcc42cbb3d5a4ccafc5`. Code is GPL-3.0-only. This is an
experimental community version, not an official upstream release.

## Install and migrate

Extract `quran_pdf_helper_v0.1.0.zip` inside KOReader's **plugins** directory,
so it installs at `plugins/quran_pdf.koplugin/`. Copy `Quran_Tafsir.pdf` to the
device. These are the two project downloads; dictionaries are not bundled.
Visit [zeeyado/quran-ebook](https://github.com/zeeyado/quran-ebook) to download
the required dictionaries and follow its installation instructions.
Restart KOReader and use
**Tools > Quran PDF Helper** for PDF preferences.

The official Quran Helper v1.10 can remain installed in
`plugins/quran.koplugin/`. EPUBs continue to use it. If the previous 1.10-pdf1
package replaced that directory, restore the official plugin there first.
Disable/remove the older separate `quranpdf.koplugin` trial companion.
Settings are independent: `quran_pdf.lua` for this PDF plugin and `quran.lua`
for the original. The plugin archive does not overwrite the original plugin folder
or copy its settings. Other upstream dictionaries work without conversion.

Enable **Status bar > Status bar items > External content**, then enable
**Tools > Quran PDF Helper > Status bar > Show juz in status bar**. Long-press
an ayah number for tafsir/grammar, a surah header for its overview, or a word
for the word dictionary. Popup buttons and volume keys navigate entries.

## Features and scope

| Feature | Prepared PDF behavior |
| --- | --- |
| Surah overview | All 114 header regions map to upstream headwords. |
| Ayah tafsir and grammar | All 6,236 ayah markers use the original keys. |
| Popup navigation | Next/previous buttons and volume keys, including surah boundaries. |
| Juz and surah status | All 30 juz, boundary flags and original format preferences. |
| Word lookup | Canonical QPC headwords and verse-occurrence filtering. |
| PDF appearance and copy | Existing vector artwork and selectable Arabic retained. |
| EPUBs and ordinary PDFs | This plugin stays inactive; the original helper handles EPUBs. |

Only PDFs prepared with the supported manifest format gain these features.
Ordinary PDF viewers do not execute KOReader plugins. Other mushaf layouts
need geometry generated from their own renderer.

## Independent identity and coexistence

The directory and internal name are `quran_pdf.koplugin` and `quran_pdf`.
The display/menu name is **Quran PDF Helper**, settings are `quran_pdf.lua`,
and adapter module is `quran_pdf_document.lua`. Shared popup fields use
`_quran_pdf_` instead of the original `_quran_` namespace.

The plugin does not register with CRE LanguageSupport. Native PDF selections
enter the reused lookup state machine through the ReaderDictionary hook.
For a prepared PDF, the original v1.10 instance's unconditional popup-key
parser and document detection are guarded in memory for that document only.
This prevents it from claiming PDF popups or registering duplicate status
content. Those per-instance methods are restored on document close. Original
source and settings on disk remain untouched. EPUB instances are unaffected.
Both hook initialization orders and both ReaderReady orders are tested.
Future upstream versions need their own compatibility check.

## PDF data contract

The existing PDF uses one non-displaying descriptor annotation outside each
page's CropBox, read locally through `document:getPageLinks()`:

    quran-ebook://page<MUSHAF_NUMBER>?format=2&data=<BASE64URL_UTF8_JSON>

The adapter validates JSON, never executes it, and caches up to 16 manifests.
The scheme is retained for compatibility with the existing prepared PDF.
Coordinates use native cropped PDF points: origin at top left, x right,
y down, before screen zoom, rotation or reflow. Original page numbers are
independent of physical page indices, so extracted example pages also work.

| Field | Meaning |
| --- | --- |
| v | Schema version 2. |
| n | Original mushaf page, 1-604. |
| j | Juz, 1-30. |
| s | Current surah, following the last starting surah on multi-surah pages. |
| b | New-juz boundary, excluding juz 1. |
| z | Native cropped page width and height. |
| h | Surah regions: [surah,x0,y0,x1,y1]. |
| a | Ayah regions: [surah,ayah,x0,y0,x1,y1]. |
| w | Word regions: [surah,ayah,position,headword,x0,y0,x1,y1]. |

Ayah zero represents an unnumbered standalone basmala. Canonical headwords
retain the exact spelling used by the upstream QPC v1.4 dictionary. The PDF
also retains named destinations, Arabic bookmarks, and older ayah descriptors.

## Build and verify

Build the plugin-only ZIP (extract it inside KOReader's plugins directory):

    python tools/koreader_plugin/build_release.py

Re-embed the supplied geometry only into its matching 604-page source layout:

    python -m pip install pymupdf
    python tools/mushaf_pdf/embed_koreader.py INPUT.pdf data/pdf_hafs_604_layout.json OUTPUT.pdf

The embedding utility does not infer glyph positions by OCR and does not
rebuild the visible artwork or selectable text layer. Do not apply this layout
to another edition, crop or page geometry.

Run full native-selection and lookup verification with the original dictionary
and official v1.10 archives:

    python -m pip install pymupdf lupa
    python tools/koreader_plugin/verify_pdf_support.py --pdf Quran_Tafsir.pdf --overview release/quran_surah_overview_en_v1.1.zip --word-dictionary release/quran_qpc_en_stardict_v1.4.zip --upstream release/quran_koplugin_v1.10.zip

For the independent plugin coexistence checks alone:

    python tools/koreader_plugin/verify_coexistence.py --upstream release/quran_koplugin_v1.10.zip

The full verifier includes coexistence checks. It covers all ayah and surah
keys, word regions, native MuPDF selections, juz status, popup navigation,
occurrence filtering and unrelated PDFs. Coexistence covers both modern and
legacy popup APIs, both initialization orders and both readiness orders,
separate settings and menus, and PDF-to-EPUB-to-PDF switching. The earlier
PDF build's artwork/text checks are retained in [previous_pdf_build_verification.json](verification/previous_pdf_build_verification.json);
the current plugin-only change does not alter the PDF. Verification reports
are headless results, not an exhaustive check of reading or selection accuracy.

The PDF and plugin have also been tested in KOReader at different randomly
selected locations. Not every word or every ayah has been tested, and the
functionality has not been completely verified. Keep this distinction when
reporting test results or assessing the experimental release.
