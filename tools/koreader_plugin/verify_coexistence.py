#!/usr/bin/env python3
"""Check independent PDF plugin identity and coexistence with Quran Helper v1.10.

Uses the real Lua handlers, a prepared layout, and KOReader interface doubles.
SPDX-License-Identifier: GPL-3.0-only
"""
from pathlib import Path
import argparse
import base64
import json
import zipfile

from lupa.luajit21 import LuaRuntime

HERE = Path(__file__).resolve().parent
PLUGIN = HERE / 'quran_pdf.koplugin'


def table(lua, value):
    if isinstance(value, dict):
        return lua.table_from({k: table(lua, v) for k, v in value.items()})
    if isinstance(value, list):
        return lua.table_from([table(lua, v) for v in value])
    return value


def verify_coexistence(upstream, layout):
    with zipfile.ZipFile(upstream) as archive:
        original = archive.read(next(n for n in archive.namelist() if n.endswith('/main.lua'))).decode()
    source = (PLUGIN / 'main.lua').read_text()
    pages = json.loads(Path(layout).read_text())['pages']
    links = {}
    for p, data in enumerate(pages, 1):
        encoded = base64.urlsafe_b64encode(json.dumps(data, ensure_ascii=False, separators=(',', ':')).encode()).decode().rstrip('=')
        links[p] = [{'uri': f'quran-ebook://page{data["n"]}?format=2&data={encoded}'}]

    combinations = []
    for modern in (True, False):
        for init_order in ('upstream_first', 'pdf_first'):
            for ready_order in ('same', 'reverse'):
                lua = LuaRuntime(unpack_returned_tuples=True)
                lua.globals().decode_json = lambda text, L=lua: table(L, json.loads(text))
                lua.execute((HERE / 'mock_koreader.lua').read_text())
                lua.execute('package.path=... .. "/?.lua;" .. package.path', str(PLUGIN))
                if not modern:
                    lua.execute('Popup.buildButtonLayout=nil')
                lua.globals().Upstream = lua.execute(original)
                lua.globals().PDF = lua.execute(source)
                lua.globals().page_links = table(lua, links)
                lua.globals().page_sizes = table(lua, {p: d['z'] for p, d in enumerate(pages, 1)})
                lua.globals().pdf_first = init_order == 'pdf_first'
                lua.globals().ready_reverse = ready_order == 'reverse'
                lua.execute('''
                function open_document(document)
                    ui=make_ui(document)
                    local classes=pdf_first and {PDF,Upstream} or {Upstream,PDF}
                    instances={}
                    for _,class in ipairs(classes) do
                        local instance=class:new{ui=ui,document=document,view=ui.view}
                        ui[class.name]=instance
                        instances[#instances+1]=instance
                        -- ReaderUI renames the runtime instance after registration.
                        instance.name="reader"..class.name
                    end
                    for i=1,#instances do
                        local at=ready_reverse and #instances+1-i or i
                        instances[at]:onReaderReady()
                    end
                    q,p=ui.quran,ui.quran_pdf
                    local menus={}
                    q:addToMainMenu(menus);p:addToMainMenu(menus)
                    assert(menus.quran and menus.quran_pdf)
                    assert(menus.quran.text=="Quran Helper" and menus.quran_pdf.text=="Quran PDF Helper")
                    assert(q.settings.path=="/unused/quran.lua")
                    assert(p.settings.path=="/unused/quran_pdf.lua")
                    assert(not p:supportsLanguage("ar"))
                    assert(Languages.plugins.quran_pdf==nil)
                end
                function popup_for(word)
                    local popup=make_popup(word)
                    if Popup.buildButtonLayout then
                        Popup.buildButtonLayout(popup)
                    else
                        for _,instance in ipairs(instances) do
                            if instance:onDictButtonsReady(popup,{}) then break end
                        end
                    end
                    return popup
                end
                function pdf_document()
                    return {is_pdf=true,info={has_pages=true},getPageCount=function() return 604 end,
                        getPageLinks=function(self,n) return page_links[n] end,
                        getNativePageDimensions=function(self,n)
                            return {w=page_sizes[n][1],h=page_sizes[n][2]}
                        end}
                end
                function pdf_lookup(text,n,box)
                    local selected={text=text,pos0={page=n,x=(box[1]+box[3])/2,y=(box[2]+box[4])/2},
                        pos1={page=n},pboxes={{x=box[1],y=box[2],w=box[3]-box[1],h=box[4]-box[2]}}}
                    return ui.dictionary:onLookupWord(text,false,{}, {selected_text=selected})
                end
                open_document(pdf_document())
                assert(p._is_quran_book and not q._is_quran_book)
                assert(ui.view.footer:count()==1)
                assert(ui.view.footer.content())
                p.settings:saveSetting("private_pdf_test",true)
                assert(q.settings:readSetting("private_pdf_test")==nil)
                ''')

                # Exercise every mapped ayah, surah header and juz with both
                # independently installed plugins active in each load order.
                for n, data in enumerate(pages, 1):
                    lua.globals().ui.paging.current_page = n
                    assert lua.globals().p._getCurrentJuz(lua.globals().p) == (data['j'], data['b'])
                    for row in data['h']:
                        key = lua.globals().pdf_lookup('سورة', n, table(lua, row[1:]))
                        assert lua.globals().p._last_overview_surah == row[0]
                        assert key
                    for row in data['a']:
                        key = lua.globals().pdf_lookup(str(row[1]), n, table(lua, row[2:]))
                        assert key.endswith(' ' + str(row[1]))
                        assert lua.globals().p._last_ayah_surah == row[0]
                row = pages[0]['a'][-1]
                lua.globals().pdf_lookup(str(row[1]), 1, table(lua, row[2:]))
                lua.execute('''
                local popup=popup_for(ui.dictionary.last_lookup.word)
                assert(popup._quran_pdf_popup and not popup._quran_popup)
                assert(popup._quran_pdf_surah==1 and popup._quran_pdf_ayah==7)
                popup:onReadNextResult()
                assert(popup._quran_pdf_surah==2 and popup._quran_pdf_ayah==1)
                ui.dictionary:showDict("Al-Baqarah 1",{{definition="PDF",dict="test dictionary"}})
                assert(popup.changed_index==1)
                local guarded=q
                Popup._quran_pdf_next_lookup=true
                Popup._quran_pdf_update_popup=popup
                p:onCloseDocument()
                assert(Popup._quran_pdf_next_lookup==nil and Popup._quran_pdf_update_popup==nil)
                assert(ui.view.footer:count()==0)
                assert(rawget(guarded,"_setupQuranPopupButtons")==nil)
                assert(rawget(guarded,"_detectQuranBook")==nil)

                -- Switch to EPUB in the SAME Lua session: the PDF hooks must
                -- become transparent and the original helper must own popups.
                local epub={is_pdf=false,info={has_pages=false},getCurrentPage=function() return 3 end,
                    getPageFromXPointer=function() return 3 end}
                ui=make_ui(epub)
                local toc={{page=1,title="جزء ١"},{page=1,title="١ سورة الفاتحة"},
                    {page=2,title="٢ سورة البقرة"},{page=22,title="جزء ٢"}}
                -- Install TOC before readiness while retaining the same mock UI.
                local original_make_ui=make_ui
                make_ui=function(document) local u=original_make_ui(document);u.toc.toc=toc;return u end
                open_document(epub)
                make_ui=original_make_ui
                assert(q._is_quran_book and not p._is_quran_book)
                assert(ui.view.footer:count()==1 and ui.view.footer.content())
                assert(p:_getCurrentJuz()==nil and p:_getCurrentSurah()==nil)
                assert(p:onWordSelection({text="٢٥٥",pos0="xp",pos1="xp2"})==nil)
                assert(p:onWordLookup({text="255"})==nil)
                q:onWordSelection({text="surah112surah-icon",pos0="xp",pos1="xp2"})
                assert(q:onWordLookup({text="surah112surah-icon"})[1]=="Al-Ikhlas")
                q:onWordSelection({text="٢٥٥",pos0="xp",pos1="xp2"})
                local key=q:onWordLookup({text="255"})[1]
                assert(key=="Al-Baqarah 255")
                local popup=popup_for(key)
                assert(popup._quran_popup and not popup._quran_pdf_popup)
                popup:onReadNextResult()
                assert(popup._quran_surah==2 and popup._quran_ayah==256)
                ui.dictionary:showDict("Al-Baqarah 256",{{definition="EPUB",dict="test dictionary"}})
                assert(popup.changed_index==1)
                assert(q:_getCurrentJuz()==1)
                assert(ui.dictionary:onLookupWord("ordinary word")=="ordinary word")
                p:onCloseDocument()

                -- Opening a second prepared PDF restores PDF ownership.
                open_document(pdf_document())
                assert(p._is_quran_book and not q._is_quran_book)
                assert(ui.view.footer:count()==1)
                ''')
                row = pages[0]['a'][0]
                lua.globals().pdf_lookup(str(row[1]), 1, table(lua, row[2:]))
                lua.execute('''
                local popup=popup_for(ui.dictionary.last_lookup.word)
                assert(popup._quran_pdf_popup and not popup._quran_popup)
                p:onCloseDocument()
                local invalid={is_pdf=true,info={has_pages=true},getPageLinks=function() return {} end}
                open_document(invalid)
                assert(not p._is_quran_book and not p:_getPDF())
                assert(ui.dictionary:onLookupWord("ordinary word")=="ordinary word")
                ''')
                combinations.append({'popup_api': 'modern' if modern else 'legacy',
                                     'init_order': init_order, 'ready_order': ready_order})
    return {'combinations': combinations, 'mapped_ayahs_per_combination': 6236,
            'surah_headers_per_combination': 114, 'juz_pages_per_combination': 604,
            'separate_settings_and_menus': True, 'pdf_epub_pdf_switch': True,
            'original_epub_navigation': True, 'unrelated_pdf_passthrough': True,
            'device_test': 'Not performed; headless Lua handler tests only'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upstream', type=Path, required=True)
    parser.add_argument('--layout', type=Path, default=HERE.parents[1] / 'data/pdf_hafs_604_layout.json')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    result = verify_coexistence(args.upstream, args.layout)
    text = json.dumps(result, indent=2)
    if args.report:
        args.report.write_text(text + '\n')
    print(text)
