-- Headless test doubles for the public KOReader interfaces used by Quran Helper.
-- These exercise plugin handlers, not graphical rendering on a device.
-- SPDX-License-Identifier: GPL-3.0-only
local Class={}
function Class:extend(o) return setmetatable(o or {},{__index=self}) end
function Class:new(o) o=self:extend(o);if o.init then o:init() end;return o end
package.preload["ui/widget/container/widgetcontainer"]=function() return Class end
package.preload["gettext"]=function() return function(s) return s end end
package.preload["logger"]=function() return {dbg=function() end,info=function() end,warn=function() end} end
package.preload["json"]=function() return {decode=function(text) return decode_json(text) end} end
package.preload["ui/bidi"]=function() return {wrap=function(s) return s end,auto=function(s) return s end} end
package.preload["device"]=function() return {screen={getWidth=function() return 600 end,getHeight=function() return 800 end}} end
package.preload["datastorage"]=function() return {getSettingsDir=function() return "/unused" end} end
package.preload["optmath"]=function() return {round=function(n) return math.floor(n+0.5) end} end
package.preload["ffi/blitbuffer"]=function() return {colorFromString=function(s) return s end} end
package.preload["ui/size"]=function() return {margin={default=8}} end
package.preload["ui/font"]=function() return {getFace=function() return {} end} end
package.preload["ui/event"]=function() return {new=function(self,name,...) return {name=name,...} end} end
Manager={events={},broadcastEvent=function(self,event) self.events[#self.events+1]=event end}
package.preload["ui/uimanager"]=function() return Manager end
local widget=Class:extend{PTF_HEADER="",PTF_BOLD_START="<b>",PTF_BOLD_END="</b>"}
function widget:getSize() return {w=100,h=16} end
function widget:free() end
function widget:paintTo() end
for _,name in ipairs({"ui/geometry","ui/widget/horizontalgroup","ui/widget/horizontalspan",
    "ui/widget/textboxwidget","ui/widget/spinwidget","ui/widget/textwidget"}) do
    package.preload[name]=function() return widget end
end
Settings={}
function Settings:readSetting(k,default) local v=self.values[k];if v==nil then return default end;return v end
function Settings:nilOrTrue(k) return self.values[k]~=false end
function Settings:isTrue(k) return self.values[k]==true end
function Settings:saveSetting(k,v) self.values[k]=v end
function Settings:flush() end
SettingsFiles={}
package.preload["luasettings"]=function() return {open=function(self,path)
    if not SettingsFiles[path] then SettingsFiles[path]=setmetatable({values={},path=path},{__index=Settings}) end
    return SettingsFiles[path]
end} end
Languages={plugins={}}
function Languages:registerPlugin(plugin) self.plugins[plugin.name]=plugin end
package.preload["languagesupport"]=function() return Languages end
Dictionary={}
function Dictionary:onLookupWord(word,sane,boxes,highlight,link,close)
    self.last_lookup={word=word,sane=sane,boxes=boxes,highlight=highlight,link=link,close=close}
    return word
end
function Dictionary:showDict(word,results) self.last_results=results;return results end
function Dictionary:dismissLookupInfo() self.dismissed=true end
package.preload["apps/reader/modules/readerdictionary"]=function() return Dictionary end
Popup={init=function() end,update=function() end,buildButtonLayout=function() return {{ {id="stock"} }} end}
package.preload["ui/widget/dictquicklookup"]=function() return Popup end

function make_ui(document)
    local footer={contents={}}
    function footer:addAdditionalFooterContent(callback) self.contents[callback]=true;self.content=callback end
    function footer:removeAdditionalFooterContent(callback) self.contents[callback]=nil;if self.content==callback then self.content=next(self.contents) end end
    function footer:count() local n=0;for _ in pairs(self.contents) do n=n+1 end;return n end
    function footer:getHeight() return 10 end
    local ui={document=document,doc_props={keywords="Quran",language="ar"},
        menu={registerToMainMenu=function() end},view={footer=footer,paintTo=function() end},
        toc={toc={},fillToc=function() end,cleanUpTocTitle=function(self,s) return s end}}
    if document.is_pdf then ui.paging={current_page=1} end
    function ui:getCurrentPage() return self.paging and self.paging.current_page or self.document:getCurrentPage() end
    ui.dictionary=setmetatable({ui=ui},{__index=Dictionary})
    return ui
end

function make_popup(word)
    local popup={word=word,dictionary="test dictionary",results={{definition=""}}}
    popup.button_table={getButtonById=function(self,id)
        return {enableDisable=function(self,value) self.enabled=value end}
    end}
    function popup:changeDictionary(index) self.changed_index=index end
    function popup:onClose() self.closed=true end
    return popup
end
