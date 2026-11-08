# Contributing

This is an experimental PDF-specific derivative of Quran Helper v1.10.
Practical device testing and reproducible bug reports are useful contributions.

When reporting a problem, include:

- Device model, operating system if relevant, and KOReader version.
- Quran PDF Helper version and whether original Quran Helper is enabled.
- PDF filename/edition, physical page, surah and ayah where relevant.
- Exact actions, expected result, and observed result.
- A screenshot or relevant crash-log excerpt if helpful; remove personal data.

Confirm that the PDF is prepared for this plugin before reporting missing
interactive features. Ordinary Quran PDFs do not contain the lookup geometry.
Send issues for this PDF version here; consult the upstream project for its
unmodified plugin, dictionaries and their content.

For code changes, describe the resulting behavior and relevant validation.
Run the documented PDF/coexistence checks when changing lookup or popup hooks.
Both original-plugin load orders and PDF/EPUB/PDF document switching matter.
Device results should be reported separately from headless handler tests.
