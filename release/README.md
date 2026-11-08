# Build outputs and upstream verification inputs

`python tools/koreader_plugin/build_release.py` writes the plugin-only ZIP here.
The verification commands expect original upstream dictionary/plugin archives
here when their default paths are used. Those external inputs are not included
in the source tree; obtain them from zeeyado/quran-ebook.

The two project release assets are `quran_pdf_helper_v0.1.0.zip` (the PDF-only
plugin) and `Quran_Tafsir.pdf` (the full prepared Quran PDF). Dictionaries and
sample PDFs are not bundled. Obtain dictionaries from zeeyado/quran-ebook.

Distribute the full PDF as a release asset rather than committing it to this
source directory. The plugin ZIP contains only its folder, code and licence.
