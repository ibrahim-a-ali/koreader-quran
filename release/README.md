# Build outputs and upstream verification inputs

`python tools/koreader_plugin/build_release.py` writes the plugin-only ZIP here.
The verification commands expect original upstream dictionary/plugin archives
here when their default paths are used. Those external inputs are not included
in the source tree; obtain them from zeeyado/quran-ebook.

The full prepared Quran PDF should be distributed as a release asset, not
committed into this source directory. The included installer is linked from
the root README under downloads/.
