-- Quran Helper: document adapter for fixed-layout Quran PDFs.
-- SPDX-License-Identifier: GPL-3.0-only
-- Prepared PDFs carry a versioned page manifest in a non-visible page link.
-- The page text and its vector artwork are never modified by this adapter.

local JSON = require("json")
local PDF = {}
PDF.__index = PDF
local PAGE_CACHE_LIMIT = 16

function PDF:remember(pageno,data)
    self.pages[pageno]=data
    self.order[#self.order+1]=pageno
    if #self.order>PAGE_CACHE_LIMIT then
        self.pages[table.remove(self.order,1)]=nil
    end
    return data or nil
end

local alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
local alphabet_values = {}
for i=1,#alphabet do alphabet_values[alphabet:sub(i,i)] = i-1 end

local function decode64(text)
    if #text > 2097152 then return nil end
    local output, accumulator, bits = {}, 0, 0
    for i=1,#text do
        local value = alphabet_values[text:sub(i,i)]
        if value == nil then return nil end
        accumulator, bits = accumulator*64+value, bits+6
        if bits >= 8 then
            bits = bits-8
            local divisor = 2^bits
            output[#output+1] = string.char(math.floor(accumulator/divisor))
            accumulator = accumulator%divisor
        end
    end
    if accumulator ~= 0 then return nil end
    return table.concat(output)
end

local function integer(value, maximum)
    return type(value)=="number" and value>=1 and value<=maximum and value%1==0
end

local function boxValid(row, offset)
    for i=offset,offset+3 do
        if type(row[i])~="number" or row[i]~=row[i] or math.abs(row[i])>100000 then return false end
    end
    return row[offset+2]>row[offset] and row[offset+3]>row[offset+1]
end

local function validate(data, bookpage)
    if type(data)~="table" or data.v~=2 or data.n~=bookpage
        or not integer(data.n,604) or not integer(data.j,30) or not integer(data.s,114)
        or type(data.b)~="boolean" or type(data.z)~="table" or type(data.z[1])~="number"
        or type(data.z[2])~="number" or type(data.h)~="table"
        or type(data.a)~="table" or type(data.w)~="table"
        or #data.h>114 or #data.a>286 or #data.w>2000 then return false end
    for _,row in ipairs(data.h) do
        if type(row)~="table" or not integer(row[1],114) or not boxValid(row,2) then return false end
    end
    for _,row in ipairs(data.a) do
        if type(row)~="table" or not integer(row[1],114) or not integer(row[2],286) or not boxValid(row,3) then return false end
    end
    for _,row in ipairs(data.w) do
        if type(row)~="table" or not integer(row[1],114) or (row[2]~=0 and not integer(row[2],286)) or not integer(row[3],1000)
            or type(row[4])~="string" or #row[4]>1024 or not boxValid(row,5) then return false end
    end
    return true
end

function PDF:page(pageno)
    if self.pages[pageno]~=nil then return self.pages[pageno] or nil end
    local ok, links = pcall(self.document.getPageLinks,self.document,pageno)
    if ok then
        for _,link in ipairs(links or {}) do
            local number,encoded
            if type(link.uri)=="string" then
                number,encoded=link.uri:match("^quran%-ebook://page(%d+)%?format=2&data=([%w_-]+)$")
            end
            if number then
                local raw=decode64(encoded)
                local parsed,data=pcall(JSON.decode,raw or "")
                if parsed and validate(data,tonumber(number)) then
                    local valid_size=true
                    if self.document.getNativePageDimensions then
                        local sized,size=pcall(self.document.getNativePageDimensions,self.document,pageno)
                        valid_size=sized and size and math.abs(size.w-data.z[1])<0.1
                            and math.abs(size.h-data.z[2])<0.1
                    end
                    if valid_size then
                        return self:remember(pageno,data)
                    end
                end
            end
        end
    end
    self:remember(pageno,false)
end

function PDF.new(document)
    if not document or not document.is_pdf or not document.getPageLinks then return nil end
    local self=setmetatable({document=document,pages={},order={}},PDF)
    if self:page(1) then return self end
end

function PDF:current(ui)
    local pageno=ui.paging and ui.paging.current_page
    if not pageno and ui.getCurrentPage then
        local ok,value=pcall(ui.getCurrentPage,ui)
        if ok then pageno=value end
    end
    if pageno then return self:page(pageno) end
end

local function points(selection)
    local output={}
    local pos=selection.pos0
    if pos and type(pos.x)=="number" and type(pos.y)=="number" then output[#output+1]=pos end
    for _,box in ipairs(selection.pboxes or {}) do
        if type(box.x)=="number" and type(box.y)=="number"
            and type(box.w)=="number" and type(box.h)=="number" then
            output[#output+1]={x=box.x+box.w/2,y=box.y+box.h/2}
        end
    end
    return output
end

local function find(rows, offset, locations)
    for _,point in ipairs(locations) do
        local best,area
        for _,row in ipairs(rows) do
            if point.x>=row[offset]-1 and point.x<=row[offset+2]+1
                and point.y>=row[offset+1]-1 and point.y<=row[offset+3]+1 then
                local size=(row[offset+2]-row[offset])*(row[offset+3]-row[offset+1])
                if not area or size<area then best,area=row,size end
            end
        end
        if best then return best end
    end
end

local digits={ ["٠"]="0",["١"]="1",["٢"]="2",["٣"]="3",["٤"]="4",
    ["٥"]="5",["٦"]="6",["٧"]="7",["٨"]="8",["٩"]="9" }
local function number(text)
    if type(text)~="string" then return nil end
    for a,b in pairs(digits) do text=text:gsub(a,b) end
    text=text:gsub("\226\128\142",""):gsub("\226\128\143",""):match("^%s*(.-)%s*$")
    if text:match("^%d+$") then return tonumber(text) end
end

function PDF:selection(selection)
    local pos=selection and selection.pos0
    if type(pos)~="table" or not pos.page then return nil end
    if type(selection.pos1)=="table" and selection.pos1.page~=pos.page then return nil end
    local data=self:page(pos.page)
    if not data then return nil end
    local locations=points(selection)
    local header=find(data.h,2,locations)
    if header then return {kind="surah",surah=header[1]} end
    local ayah=find(data.a,3,locations)
    if ayah and (not selection.text or number(selection.text)==ayah[2]) then
        return {kind="ayah",surah=ayah[1],ayah=ayah[2]}
    end
    local word=find(data.w,5,locations)
    if word then
        return {kind="word",surah=word[1],ayah=word[2]>0 and word[2] or nil,position=word[3],text=word[4]}
    end
end

return PDF
