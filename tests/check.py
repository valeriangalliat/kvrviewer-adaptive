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
checks = r'''
local function near(a, b) assert(math.abs(a - b) < 1e-8, a .. " != " .. b) end
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
assert(controls.ImageProjection.attrs.INP_Default == 1)
assert(controls.TinyPlanet.attrs.INP_Default == 1)
assert(controls.Zoom.attrs.INP_Default == 0.5)

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
