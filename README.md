# kvrViewer Adaptive

A standalone derivative of KartaVR's KVRViewer for DaVinci Resolve/Fusion.

## Upstream source

The first commit imports the complete KVRViewer package, byte-for-byte, from
[We Suck Less / Reactor](https://gitlab.com/WeSuckLess/Reactor), directory
`Atoms/com.AndrewHazelden.KartaVP.Tools.kvrViewer`, at commit
`aeaaae678d010655a7c9ed8b866a96811f8db8bc` (package version 5.85).

Reactor is the package manager and also hosts this package's source. This
repository contains only KVRViewer's package, without the rest of Reactor.

KVRViewer is by David Kohen and Andrew Hazelden, with contributions and shader
origins credited in the Fuse header. The upstream source and package manifest
declare LGPL-3.0. Their notices and attribution are retained. Changes in this
repository are distributed under the same license.

The root import commit is the permanent, unmodified upstream baseline. Later
commits contain this README and our changes, so the derivative can be reviewed
with an ordinary Git diff.

## Install on macOS

```sh
git clone https://github.com/valeriangalliat/kvrviewer-adaptive.git
cd kvrviewer-adaptive
./scripts/install.sh
```

Restart Resolve after the first install. Add kvrViewer Adaptive between MediaIn
and MediaOut in the clip's Fusion graph. The installer copies the renamed Fuse
and Edit-page wrapper into your user Fusion folders, keeping stock KVRViewer
intact. Reactor is not required.

To update, pull changes and rerun the installer. Existing Fusion nodes can load
Fuse changes via Settings → Edit Code → Reload Fuse; wrapper layout changes
require a new effect instance.

## Development

Run `python3 tests/check.py` with Resolve installed on macOS, or set `LUA_LIBRARY`
to a Lua 5.1/LuaJIT shared library. The runner compiles the Fuse and template and
uses a mock host to check their controls. Rendering changes also need testing in
Resolve.

## Projection default

The Edit-page wrapper defaults to 360VR, matching direct Fusion use. Other
projection and stereo defaults are unchanged.
