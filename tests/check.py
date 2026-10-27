"""Compile the real Fuse and exercise its helpers using Resolve's bundled LuaJIT."""
import ctypes
import ctypes.util
import os
from pathlib import Path

root = Path(__file__).resolve().parents[1]
library = os.environ.get("LUA_LIBRARY") or ctypes.util.find_library("luajit-5.1")
if not library:
    library = "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/libluajit-5.1.2.dylib"
lua = ctypes.CDLL(library)
lua.luaL_newstate.restype = ctypes.c_void_p
lua.luaL_openlibs.argtypes = [ctypes.c_void_p]
lua.luaL_loadstring.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
lua.lua_pcall.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int]
lua.lua_tolstring.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p]
lua.lua_tolstring.restype = ctypes.c_char_p
lua.lua_close.argtypes = [ctypes.c_void_p]

source = (root / "Fuses/Kartaverse/KartaVP/Warp/kvrViewer.fuse").read_text()
template = (root / "Templates/Edit/Effects/KartaVP/Warp/kvrViewer.setting").read_text()
assert 'ImageProjection = Input { Value = 1, }' in template
assert 'Default = 1,' in template.split('ImageProjection = InstanceInput {', 1)[1].split('},', 1)[0]
assert 'QualityNotice = Input' in template
assert 'ICS_ControlPage = "Controls"' in template
assert 'base64,' not in template
checks = r'''
local function near(a, b) assert(math.abs(a - b) < 1e-8, a .. " != " .. b) end
local function input(value) return {GetValue = function() return {Value = value} end} end
InWidth, InHeight = input("640"), input("480")
InOutputFormat = input(0)
InInputStereo, InAnaglyph, InImageProjection = input(0), input(0), input(1)
self = {Comp = {GetPrefs = function() error("Must not depend on composition size") end}}
local w, h = outputSize({})
assert(w == 1920 and h == 1080)
InOutputFormat = input(1)
w, h = outputSize({})
assert(w == 1080 and h == 1920)
InOutputFormat = input(0)
InOutputFormat = input(2)
InInputStereo = input(0)
InWidth, InHeight = input("640"), input("480")
w, h = outputSize({})
assert(w == 640 and h == 480)
for _, bad in ipairs({"", "abc", "0", "-1", "1920.5", "16385", "inf"}) do
    InWidth = input(bad)
    assert(not pcall(outputSize, {}))
end
InWidth, InHeight = input("1080"), input("1080")
w, h = outputSize({})
assert(w == 1080 and h == 1080)

local function noop() end
-- Verify the actual UI definitions and Custom field visibility.
local controls = {}
self = {
    AddInput = function(_, label, id, attrs)
        local control = {attrs = attrs}
        function control:SetAttrs(changes)
            for key, value in pairs(changes) do self.attrs[key] = value end
        end
        controls[id] = control
        return control
    end,
    AddOutput = function() return {} end,
    BeginControlNest = noop, EndControlNest = noop,
}
Create()
assert(controls.QualityNotice == nil) -- warning belongs only to the Edit-page wrapper
assert(controls.OutputFormat.attrs.INP_Default == 0)
assert(controls.ImageProjection.attrs.INP_Default == 1)
assert(controls.TinyPlanet.attrs.INP_Default == 1)
assert(controls.Zoom.attrs.INP_Default == 0.5)
assert(controls.Width.attrs.INPID_InputControl == "TextEditControl")
assert(controls.Height.attrs.INPID_InputControl == "TextEditControl")
NotifyChanged(controls.OutputFormat, {Value = 2}, 0)
assert(controls.Width.attrs.IC_Visible and controls.Height.attrs.IC_Visible)
NotifyChanged(controls.OutputFormat, {Value = 0}, 0)
assert(not controls.Width.attrs.IC_Visible and not controls.Height.attrs.IC_Visible)
'''
state = lua.luaL_newstate()
try:
    lua.luaL_openlibs(state)
    program = "FuRegisterClass = function() end\n" + source + "\n" + checks
    program += "\nassert(loadstring(" + "[====[return " + template + "]====]" + "))"
    result = lua.luaL_loadstring(state, program.encode())
    if not result:
        result = lua.lua_pcall(state, 0, 0, 0)
    if result:
        raise RuntimeError(lua.lua_tolstring(state, -1, None).decode())
finally:
    lua.lua_close(state)
print("PASS: Fuse/template syntax and feature checks")
