# Quran PDF Helper

Read a fixed-layout Quran PDF in KOReader with ayah tafsir and grammar lookups,
surah overviews, word dictionaries, and juz/surah status.

**Version 0.1.0 is experimental. Automated handler checks passed; testing on an
actual KOReader device is still pending.**

This is a PDF-only derivative of **Quran Helper v1.10**, developed in
[zeeyado/quran-ebook](https://github.com/zeeyado/quran-ebook). It reuses the
original project's dictionary keys, popup design, navigation, and much of its
plugin code. See [credits](CREDITS.md) and [licensing](LICENSE).

## Downloads

- [Plugin installer](downloads/Quran_PDF_Helper.zip) — extract into your KOReader folder.
- [Short prepared PDF example](examples/Quran_PDF_Example.pdf) — try the lookup format.
- **Full prepared 604-page Quran PDF:** the first public release is being prepared.

Use the matching prepared PDF. An ordinary Quran PDF does not contain the
information this plugin needs for ayah, header, and word lookup.

## What it supports

| Feature | Prepared PDF support |
| --- | --- |
| Ayah lookup | Tafsir/grammar keys for all 6,236 ayahs. |
| Surah overviews | Long-press header regions for all 114 surahs. |
| Word dictionaries | Canonical QPC headwords and verse-occurrence filtering. |
| Popup navigation | Next/previous entries, including across surah boundaries. |
| Juz and surah status | All 30 juz, boundary indicators, and display preferences. |
| Mushaf layout | Existing vector artwork and selectable Arabic text retained. |

Interactive features require KOReader and this plugin. Other PDF viewers can
display the document, but they do not run KOReader plugins.

## Quick start

1. Close KOReader completely.
2. Extract the plugin installer into the KOReader root, merging its `plugins/`
   and `data/` folders.
3. Copy a prepared PDF to the device and restart KOReader.
4. Long-press an ayah number, decorative surah header, or Arabic word.
5. For juz status, enable **Status bar > Status bar items > External content**,
   then **Tools > Quran PDF Helper > Status bar > Show juz in status bar**.

The installer includes the upstream project's English surah-overview and QPC
v1.4 word dictionaries. Obtain other tafsir, grammar, and language dictionaries
from the [original Quran Ebook project](https://github.com/zeeyado/quran-ebook).
Its dictionary documentation explains their contents and installation.

See [full installation and migration instructions](docs/INSTALLATION.txt).

## Using it alongside the original plugin

| | Original Quran Helper | Quran PDF Helper |
| --- | --- | --- |
| Plugin folder | `quran.koplugin` | `quran_pdf.koplugin` |
| Settings | `quran.lua` | `quran_pdf.lua` |
| Role when both are installed | EPUBs | Prepared PDFs |

The supported coexistence baseline is the official original **v1.10**. This
plugin has separate menu/settings and popup-hook state. It does not register
an EPUB language handler. Original plugin files on disk are not changed.

If you installed the earlier experimental `1.10-pdf1` replacement into
`quran.koplugin`, restore the official original before enabling both plugins.
Remove/disable the older `quranpdf.koplugin` trial companion if present.

## Build and development

Build the plugin-only ZIP with Python:

```sh
python tools/koreader_plugin/build_release.py
```

This produces `release/quran_pdf_helper_v0.1.0.zip`, whose top-level folder is
`quran_pdf.koplugin`. Extract that build inside KOReader's **plugins** directory.
The installer linked above includes the `plugins/` parent and belongs in the
KOReader **root** directory.

Development checks use the real Lua handlers with KOReader interface doubles.
Install their dependencies with:

```sh
python -m pip install -r requirements-dev.txt
```

See [the PDF format and verification commands](docs/PDF_SUPPORT.md) and
[recorded verification results](docs/verification/README.md).

The geometry-embedding utility supports the supplied layout. The original
rendering pipeline for recreating the visible mushaf pages is not included.
Do not apply the supplied geometry to a different edition, crop, or layout.

## Contributing

Reports from actual KOReader devices are especially useful. Include the device,
KOReader version, plugin version, page/ayah, and steps to reproduce. See
[contributing](CONTRIBUTING.md). Please report this PDF derivative's problems
in this repository; the original project maintains its own plugin and assets.

## Credits and licence

Based on [zeeyado/quran-ebook](https://github.com/zeeyado/quran-ebook), using the
official Quran Helper v1.10 source at commit
`c9550fdd58b0feec36300dcc42cbb3d5a4ccafc5`. This independent community version
is not an official upstream release.

Plugin code and the supplied development tools are GPL-3.0-only. Keep the
original notices and [licence](LICENSE) with redistributed code. Quran text,
fonts, and dictionary assets retain their respective source notices; the code
licence does not grant additional rights over those assets.
