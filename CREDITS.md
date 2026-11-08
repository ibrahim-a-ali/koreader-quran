# Credits and provenance

## Original plugin and dictionaries

[Quran Ebook by zeeyado](https://github.com/zeeyado/quran-ebook) provides the
original Quran Helper plugin, dictionary keys and dictionary resources.
Quran PDF Helper derives substantial code from its official v1.10 plugin,
based on repository commit `c9550fdd58b0feec36300dcc42cbb3d5a4ccafc5`.

The original popup design, grammar/tafsir and overview lookup conventions,
navigation, word-result filtering, status formatting and QPC normalization
are reused. This project adds the prepared-PDF adapter and separate PDF-only
plugin identity, settings and coexistence handling. Modifications are recorded
in [CHANGELOG.md](CHANGELOG.md). Retain GPL-3.0 notices and COPYING.

## Reading software and content sources

The source vector-format Quran PDF was obtained from the **King Fahd Glorious
Quran Printing Complex**. Its original page layout and vector artwork have
been preserved. AI-assisted processing was used to enable Arabic word
selection and copying and to add the information required for ayah lookups.

[KOReader](https://github.com/koreader/koreader) provides the reader and the
interfaces used by the plugin. The Quran Ebook project documents its text,
dictionary and font sources, including Quran.com and King Fahd Complex
resources. Consult those source notices when redistributing assets.

Dictionaries are not bundled with the release. Users should obtain them from
the [original Quran Ebook project](https://github.com/zeeyado/quran-ebook).

This project does not claim authorship of Quran text, translations, tafsir,
fonts, dictionaries, or the original Quran Helper plugin. It is an independent
community derivative; upstream endorsement is not implied.
