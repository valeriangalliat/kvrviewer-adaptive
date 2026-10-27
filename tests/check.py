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
for _, size in ipairs({{1080,1920}, {1920,1080}, {1080,1080}, {1080,1440}, {1440,1080}}) do
    local w, h = unpack(size)
    for _, zoom in ipairs({0.01, 0.25, 0.5, 1, 2, 5}) do
        local z = longEdgeZoom(zoom, w, h)
        -- Measure the angle between the center and longest-edge boundary ray.
        local edge = math.max(1, h / w)
        near(2 * math.atan(edge / z), 2 * math.atan(1 / zoom))
    end
end
near(longEdgeZoom(0.5, 1080, 1920), 8/9)
near(longEdgeZoom(0.5, 1920, 1080), 0.5)
near(longEdgeZoom(0.5, 1080, 1080), 0.5)
near(longEdgeZoom(1, 1080, 1920), 16/9)
near(longEdgeZoom(1, 1920, 1080), 1)

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

-- Exercise the real processEye dispatch, not just the normalization helper.
-- Mock image allocation/GPU execution; inspect what would reach the shader.
local function noop() end
local readbacks = 0
function Image(attrs)
    return {
        Width = attrs.IMG_Width, Height = attrs.IMG_Height,
        OriginalWidth = attrs.IMAT_OriginalWidth, OriginalHeight = attrs.IMAT_OriginalHeight,
        DownloadGPUMem = function() readbacks = readbacks + 1 end,
        Fill = noop, OMerge = noop,
        IsMask = function() return false end,
    }
end
ImgRectI, Pixel = noop, noop
local captured
function DVIPComputeNode()
    captured = {srcSize = {}}
    return {
        GetParamBlock = function() return captured end,
        SetParamBlock = noop, AddSampler = noop, AddInput = noop, AddOutput = noop,
        RunSession = function() return true end,
    }
end
InInputStereo, InAnaglyph = input(0), input(0)
InOutputFormat = input(0)
InConvergence, InDomeTiltAngle, InAngle = input(0), input(0), input(0)
InCenter = {GetValue = function() return {X = 0.5, Y = 0.5} end}
InSolidAlpha, InReset, InEdges, InOutputSTMap = input(0), input(0), input(0), input(0)
local src = Image{IMG_Width = 5760, IMG_Height = 2880,
    IMAT_OriginalWidth = 5760, IMAT_OriginalHeight = 2880}
local req = {Time = 0, IsPreCalc = function() return false end}
for _, planet in ipairs({0, 1}) do
    InTinyPlanet = input(planet)
    for _, projection in ipairs({1, 2}) do
        InImageProjection = input(projection)
        local multiplier = projection == 2 and 2 or 1
        for _, zoom in ipairs({0.5, 1, 2}) do
            InZoom = input(zoom)
            InOutputFormat = input(1)
            processEye(req, src, 1)
            near(captured.fov, zoom * 16/9 * multiplier)
            assert(captured.isTinyplanet == planet)
            assert(captured.srcSize[0] == 1080 and captured.srcSize[1] == 1920)
            InOutputFormat = input(0)
            processEye(req, src, 1)
            near(captured.fov, zoom * multiplier)
        end
    end
end
InImage1 = {GetValue = function() return src end}
InImage2 = {GetValue = function() return nil end}
InSwapEyes = input(0)
OutImage1 = {Set = function(_, _, img) assert(img.Width == 1920 and img.Height == 1080) end}
for _, planet in ipairs({0, 1}) do
    InTinyPlanet = input(planet)
    for _, projection in ipairs({1, 2}) do
        InImageProjection = input(projection)
        readbacks = 0
        Process(req)
        assert(readbacks == (projection == 1 and 0 or 2))
    end
end

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
