#!/usr/bin/env python3
"""Run Quran Helper's real Lua handlers against a prepared PDF and metadata.

Dependencies: pymupdf, lupa (LuaJIT 2.1 binding).
The UI doubles verify handler behavior; a device smoke test is still required.
SPDX-License-Identifier: GPL-3.0-only
"""
from pathlib import Path
from collections import defaultdict
import argparse,base64,gzip,json,re,struct,zipfile,time,unicodedata
import fitz
from lupa.luajit21 import LuaRuntime

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
PLUGIN=HERE/'quran_pdf.koplugin'

def lua_table(runtime,value):
    if isinstance(value,dict):return runtime.table_from({k:lua_table(runtime,v) for k,v in value.items()})
    if isinstance(value,list):return runtime.table_from([lua_table(runtime,v) for v in value])
    return value

def runtime(source):
    lua=LuaRuntime(unpack_returned_tuples=True)
    lua.globals().decode_json=lambda text:lua_table(lua,json.loads(text))
    lua.execute((HERE/'mock_koreader.lua').read_text())
    lua.execute('package.path=... .. "/?.lua;" .. package.path',str(PLUGIN))
    lua.globals().Quran=lua.execute(source)
    return lua

def ko_words(page):
    out=[]
    for block in page.get_text('rawdict',flags=0)['blocks']:
        for line in block.get('lines',[]):
            chars=[c for span in line['spans'] for c in span['chars']];group=[]
            for c in chars+[{'c':' '}]:
                code=ord(c['c'])
                if c['c'].isspace() or 0x2000<=code<=0x206f:
                    if group:
                        box=fitz.Rect(group[0]['bbox'])
                        for ch in group[1:]:box|=fitz.Rect(ch['bbox'])
                        if box.width>0 and box.height>0:out.append((''.join(ch['c'] for ch in group),box))
                        group=[]
                else:group.append(c)
    return out

def dictionary_keys(path):
    z=zipfile.ZipFile(path);raw=z.read(next(n for n in z.namelist() if n.endswith('.idx')))
    entries=defaultdict(list);i=0
    while i<len(raw):
        end=raw.index(b'\0',i);key=raw[i:end].decode();off,size=struct.unpack('>II',raw[end+1:end+9])
        entries[key].append((off,size));i=end+9
    return entries,z

def verify(pdf,layout,overview,word_dictionary,upstream,original_pdf=None):
    started=time.time();doc=fitz.open(pdf);manifest=json.loads(layout.read_text())['pages']
    assert len(doc)==len(manifest)==604
    wordkeys,wordzip=dictionary_keys(word_dictionary)
    overviewkeys,_=dictionary_keys(overview)
    links={};dimensions={};persisted=[]
    for i,page in enumerate(doc):
        links[i+1]=[{'uri':l['uri']} for l in page.get_links() if l.get('uri')]
        dimensions[i+1]={'w':page.rect.width,'h':page.rect.height}
        encoded=next(l['uri'].split('&data=')[1] for l in links[i+1] if '?format=2&data=' in l['uri'])
        data=json.loads(base64.urlsafe_b64decode(encoded+'='*(-len(encoded)%4)))
        assert data==manifest[i]
        persisted.append(data)
    source=(PLUGIN/'main.lua').read_text();lua=runtime(source)
    lua.globals().page_links=lua_table(lua,links);lua.globals().dimensions=lua_table(lua,dimensions)
    lua.execute('''
    document={is_pdf=true,info={has_pages=true},getPageCount=function() return 604 end,
        getPageLinks=function(self,p) return page_links[p] end,
        getNativePageDimensions=function(self,p) return dimensions[p] end}
    ui=make_ui(document)
    q=Quran:new{ui=ui,document=document,view=ui.view}
    q:onReaderReady()
    assert(q._is_quran_book and ui.view.footer.content)
    function lookup(text,p,x0,y0,x1,y1)
        local selection={text=text,pos0={page=p,x=(x0+x1)/2,y=(y0+y1)/2},pos1={page=p},
            pboxes={{x=x0,y=y0,w=x1-x0,h=y1-y0}}}
        return ui.dictionary:onLookupWord(text,false,{}, {selected_text=selection})
    end
    function context(p)
        ui.paging.current_page=p;q:onPageUpdate()
        local juz,boundary=q:_getCurrentJuz()
        return juz,boundary,q:_getCurrentSurah(),ui.view.footer.content()
    end
    ''')
    lookup=lua.globals().lookup;context=lua.globals().context
    ayahs=headers=word_regions=0;boundaries=[]
    for p,data in enumerate(persisted,1):
        j,b,s,footer=context(p)
        assert (j,b,s)==(data['j'],data['b'],data['s']) and footer
        assert ('*' in footer)==b
        if b:boundaries.append(p)
        for row in data['h']:
            key=lookup('سورة',p,*row[1:])
            assert key in overviewkeys,(p,row,key)
            assert lua.globals().q._last_overview_surah==row[0]
            headers+=1
        for row in data['a']:
            key=lookup(str(row[1]),p,*row[2:])
            assert key.endswith(' '+str(row[1]))
            assert lua.globals().q._last_ayah_surah==row[0] and lua.globals().q._last_ayah_num==row[1]
            ayahs+=1
        for row in data['w']:
            key=lookup('native Arabic text',p,*row[4:])
            assert key==row[3] and key in wordkeys,(p,row[:4],key)
            word_regions+=1
    assert ayahs==6236 and headers==114 and len(boundaries)==29

    native_words=native_numbers=0;native_headers=set()
    for p,page in enumerate(doc,1):
        for text,rect in ko_words(page):
            if not any(unicodedata.category(c).startswith('L') for c in text) and not text.isdigit():continue
            key=lookup(text,p,*rect)
            if text.isdigit():
                assert lua.globals().q._last_ayah_num==int(text),(p,text,key)
                native_numbers+=1
            elif lua.globals().q._last_overview_surah:
                assert key in overviewkeys,(p,text,key)
                native_headers.add(lua.globals().q._last_overview_surah)
            else:
                assert key in wordkeys,('native word failed',p,text,key,list(rect))
                native_words+=1
    assert native_numbers==6236 and len(native_headers)==114
    lua.execute('local count=0;for _ in pairs(q._pdf.pages) do count=count+1 end;assert(count<=16)')

    # All upstream footer/header format settings use the same status functions.
    lua.execute('''
    for _,format in ipairs({"number_arabic","number_latin","name_arabic",
        "name_arabic_with_juz","name_latin","name_latin_with_juz","ordinal_arabic"}) do
        q.settings:saveSetting("juz_display",format)
        q.settings:saveSetting("header_juz_display",format)
        for _,page in ipairs({1,22,42,62,82,102,121,142,162,182,201,222,242,262,282,
            302,322,342,362,382,402,422,442,462,482,502,522,542,562,582}) do
            ui.paging.current_page=page
            assert(q:_getJuzFooterString() and q:_getJuzHeaderString())
        end
    end
    ui.paging.current_page=604
    q.settings:saveSetting("show_surah_in_footer",true)
    for _,format in ipairs({"auto","arabic","arabic_with_surat","latin","latin_with_surat"}) do
        q.settings:saveSetting("surah_display",format)
        assert(q:_getJuzFooterString())
    end
    q.settings:saveSetting("show_surah_in_footer",false)
    q.settings:saveSetting("juz_display","number_arabic")
    ''')

    # The modern layout hook and the older DictButtonsReady handler use the
    # actual upstream popup construction, including next/prev and volume keys.
    lua.execute('''
    lookup("سورة",604,135.5,9.5,229.5,38.5)
    popup=make_popup(ui.dictionary.last_lookup.word)
    buttons=Popup.buildButtonLayout(popup)
    assert(popup._quran_pdf_overview_surah==112 and popup._quran_pdf_popup)
    local next_button,prev_button
    for _,row in ipairs(buttons) do for _,button in ipairs(row) do
        if button.id=="next_surah" then next_button=button end
        if button.id=="prev_surah" then prev_button=button end
    end end
    assert(next_button and prev_button)
    next_button.callback()
    assert(popup._quran_pdf_overview_surah==113 and ui.dictionary.last_lookup.word=="Al-Falaq")
    popup:onReadNextResult()
    assert(popup._quran_pdf_overview_surah==114 and ui.dictionary.last_lookup.word=="An-Nas")
    local before=ui.dictionary.last_lookup.word
    popup:onReadNextResult()
    assert(ui.dictionary.last_lookup.word==before)
    popup:onReadPrevResult()
    assert(popup._quran_pdf_overview_surah==113)
    ui.dictionary:showDict("Al-Falaq",{{definition="overview",dict="test dictionary"}},nil,nil,nil)
    assert(popup.changed_index==1 and ui.dictionary.dismissed)
    lookup("سورة",1,150,103.5,217,123)
    local old=make_popup(ui.dictionary.last_lookup.word)
    assert(q:onDictButtonsReady(old,{}))
    assert(old._quran_pdf_overview_surah==1)
    old:onReadPrevResult();assert(old._quran_pdf_overview_surah==1)
    lookup("7",1,132.96,379.92,148.08,399.96)
    local ayahpopup=make_popup(ui.dictionary.last_lookup.word)
    assert(q:_setupQuranPopupButtons(ayahpopup,{}))
    ayahpopup:onReadNextResult()
    assert(ayahpopup._quran_pdf_surah==2 and ayahpopup._quran_pdf_ayah==1)
    ayahpopup:onReadPrevResult()
    assert(ayahpopup._quran_pdf_surah==1 and ayahpopup._quran_pdf_ayah==7)
    ''')

    # Ordinary word results must be filtered to the pressed verse, using the
    # original helper's result filter rather than an adapter-specific filter.
    sample=next(w for w in persisted[1]['w'] if w[1]>0)
    key=lookup('Arabic text',2,*sample[4:])
    s,a=sample[:2]
    lua.globals().test_s=s;lua.globals().test_a=a
    lua.execute('''
    local right="<!-- ref:"..test_s..":"..test_a..":1 -->"
    local filtered=q:_filterWordResultsByPosition({{definition="<!-- ref:114:6:1 -->"},{definition=right}})
    assert(#filtered==1 and filtered[1].definition==right)
    ''')
    lua.globals().sample_box=lua_table(lua,sample[4:])
    lua.execute('''
    -- KOReader can select a nearby word even when the actual hold point is
    -- outside its box. Preserve the reference resolved from its native pbox.
    local r=sample_box
    local selected={text="Arabic word",pos0={page=2,x=-100,y=-100},pos1={page=2},
        pboxes={{x=r[1],y=r[2],w=r[3]-r[1],h=r[4]-r[2]}}}
    ui.dictionary:onLookupWord(selected.text,false,{}, {selected_text=selected})
    local right="<!-- ref:"..test_s..":"..test_a..":1 -->"
    local filtered=q:_filterWordResultsByPosition({{definition="<!-- ref:114:6:1 -->"},{definition=right}})
    assert(#filtered==1 and filtered[1].definition==right)
    -- Unprepared or malformed PDFs must not activate Quran status content.
    local invalid={is_pdf=true,info={has_pages=true},getPageLinks=function() return {} end}
    local other_ui=make_ui(invalid)
    local other=Quran:new{ui=other_ui,document=invalid,view=other_ui.view}
    other:onReaderReady()
    assert(not other._is_quran_book and other:_getCurrentJuz()==nil)
    assert(other:_getCurrentSurah()==nil and not other_ui.view.footer.content)
    ''')

    # All unchanged copied text and drawing streams remain in place.
    if original_pdf:
        original=fitz.open(original_pdf)
        assert len(original)==len(doc)
        for i,page in enumerate(doc):
            assert page.get_text('rawdict',flags=0)==original[i].get_text('rawdict',flags=0)
            assert b''.join(doc.xref_stream(x) for x in page.get_contents())==b''.join(original.xref_stream(x) for x in original[i].get_contents())
            assert page.cropbox==original[i].cropbox

    from verify_coexistence import verify_coexistence
    coexistence=verify_coexistence(upstream, layout)
    return {'pages':604,'surah_overview_lookups':headers,'ayah_lookups':ayahs,'word_region_lookups':word_regions,
        'native_word_lookups':native_words,'native_ayah_number_lookups':native_numbers,
        'native_surah_headers_identified':len(native_headers),
        'juz_pages_verified':604,'juz_boundaries_verified':29,'juz_formats_verified':7,
        'surah_status_formats_verified':5,'surah_button_and_volume_navigation':True,
        'ayah_navigation_across_surahs':True,'modern_and_legacy_popup_hooks':True,
        'occurrence_filter':True,'imprecise_hold_occurrence_filter':True,
        'unprepared_pdf_passthrough':True,'bounded_page_cache':True,'coexistence':coexistence,
        'pdf_artwork_comparison_performed':bool(original_pdf),'seconds':round(time.time()-started,2),
        'device_test':'Not performed by this headless verifier'}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf',type=Path,required=True)
    parser.add_argument('--layout',type=Path,default=ROOT/'data/pdf_hafs_604_layout.json')
    parser.add_argument('--overview',type=Path,required=True)
    parser.add_argument('--word-dictionary',type=Path,required=True)
    parser.add_argument('--upstream',type=Path,default=ROOT/'release/quran_koplugin_v1.10.zip')
    parser.add_argument('--original-pdf',type=Path)
    parser.add_argument('--report',type=Path)
    args=parser.parse_args()
    report=verify(args.pdf,args.layout,args.overview,args.word_dictionary,args.upstream,args.original_pdf)
    if args.report:args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(report,ensure_ascii=False,indent=2))
