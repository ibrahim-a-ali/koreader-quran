local _ = require("gettext")
return {
    name = "quran_pdf",
    version = "0.1.0",
    fullname = _("Quran PDF Helper"),
    description = _([[Interactive companion for prepared Quran PDFs in KOReader.
Ayah tafsir/grammar lookup, surah overviews, popup navigation, juz/surah status,
and occurrence-specific word lookup. Uses the original project's dictionaries.

Based on Quran Helper v1.10 by zeeyado/quran-ebook, GPL-3.0-only.
Independent PDF-only plugin with its own settings; the original Quran Helper
continues to handle EPUBs. Experimental: target-device UI testing is pending.]]),
}
