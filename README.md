# Quran PDF Helper for KOreader

This project aims to preserve the Quran's original page layout while enabling the **tafseer and word
lookup features** of the original
[Quran Ebook project](https://github.com/zeeyado/quran-ebook) in **KOReader**.

The Quran PDF was obtained from the **King Fahd Glorious Quran Printing
Complex**. Its original page layout and vector artwork have been preserved.
AI-assisted processing was used to enable Arabic word selection and copying
and to add the information needed for ayah lookups.

The PDF plugin adapts this prepared PDF to the original project's dictionary
keys and lookup features.

<p align="center">
  <a href="screenshots/koreader-page-151.png">
    <img src="screenshots/koreader-page-151.png" alt="KOReader Quran reading view on page 151" width="47%">
  </a>
  <a href="screenshots/koreader-page-604.png">
    <img src="screenshots/koreader-page-604.png" alt="KOReader Quran reading view on page 604" width="47%">
  </a>
</p>

*Click either screenshot to view it at full size.*

## Downloads

The two downloads are prepared in a draft release and await publication.

| File | Description |
| --- | --- |
| `quran_pdf_helper_v0.1.3.zip` | PDF plugin for KOReader. |
| `Quran_Original_Layout_KOReader_Interactive.pdf` | Original vector layout with interactive lookups in KOReader. |

## Setup

1. Install **KOReader** on your device.
2. Extract the plugin ZIP into KOReader's **plugins** folder, so the folder is
   `plugins/quran_pdf.koplugin/`.
3. Copy `Quran_Original_Layout_KOReader_Interactive.pdf` to your device and open it in KOReader.
4. Visit the **[original Quran Ebook project](https://github.com/zeeyado/quran-ebook)**
   to download dictionaries, tafseers, and related resources. Follow its
   dictionary installation instructions.

Dictionaries are not bundled here. Long-press an ayah number or word to use
the corresponding lookup once the relevant dictionaries are installed.

## Recommended KOReader settings

For comfortable reading while preserving the original mushaf layout:

- **Fit:** Width.
- **View mode:** Continuous.
- **Page gap:** 0~1, for continuous Quran viewing without gaps between pages.
- **Status bar:** Always visible.
- Under **Status bar → Status bar items**, enable **Current page** and **External content** to display the **page number, juz and surah name**.
- Under **Settings → Taps and gestures → Page turns**, enable **Invert page turns and dialogs**.
- **Reflow:** Keep it off.

## Testing

The PDF and lookup features have been tested in KOReader at different, randomly selected
locations. **Not every word or every ayah has been tested, and the functionality
has not been completely verified.** This remains an experimental release.
Please report any issues with the page, surah/ayah, selected word, and KOReader
version.

## Credits

The plugin is adapted from **Quran Helper v1.10** by
[zeeyado/quran-ebook](https://github.com/zeeyado/quran-ebook). Original credits
and GPL-3.0 licence notices are retained. See the [licence](LICENSE).
