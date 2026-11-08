#!/usr/bin/env python3
"""Build the Quran PDF Helper from checked-in Lua sources.
SPDX-License-Identifier: GPL-3.0-only
"""
from pathlib import Path
import argparse
import zipfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output',nargs='?',type=Path,default=ROOT/'release/quran_pdf_helper_v0.1.0.zip')
    args=parser.parse_args()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(args.output,'w',zipfile.ZIP_DEFLATED) as z:
        for path in sorted((HERE/'quran_pdf.koplugin').iterdir()):
            if path.is_file():z.write(path,Path('quran_pdf.koplugin')/path.name)
    print(args.output)
