# kvrViewer Adaptive

KVRViewer with long-edge zoom and faster 360° playback in DaVinci Resolve/Fusion.

## What's different

- **Consistent zoom across aspect ratios.** Long-Edge Zoom keeps the same view
  along the longest edge when switching between portrait, landscape, and square.
  It uses the original zoom control and on-screen handle, in both perspective
  and Tiny Planet modes. Higher values zoom in; lower values widen the view.
- **Faster playback.** Mono 360VR avoids forced GPU-to-CPU transfers, and the
  shader skips unused projection calculations. This made playback much faster
  in our testing; gains will depend on your setup.
- **Simple output sizes.** Choose 1920×1080, 1080×1920, or Custom. Custom accepts
  whole-pixel dimensions from 1 to 16384, without sliders. No Auto setting that
  confuses source, composition, and timeline dimensions.
- **360VR by default**, including in the Edit-page wrapper. Zoom defaults to 0.5;
  the original stereo and Tiny Planet defaults are unchanged.

## Install and use

On macOS:

```sh
git clone https://github.com/valeriangalliat/kvrviewer-adaptive.git
cd kvrviewer-adaptive
./scripts/install.sh
```

Restart Resolve after the first install. In the clip's Fusion graph, add
**kvrViewer Adaptive** between MediaIn and MediaOut. For stitched 360 footage,
choose 360VR and Mono, then select your output resolution.

**Use it directly in Fusion for full source quality.** In our tests, the
Edit-page effect received a 5760×2880 panorama already resized to 1080×1920.
Direct Fusion received the full source. The Edit-page wrapper is still available
under Effects → Custom 360, with a warning about this limitation. Stretch fixes
its input layout, but cannot recover lost detail.

The installer keeps stock KVRViewer intact. To update, pull changes and rerun it.
Existing Fusion nodes can reload via **Settings → Edit Code → Reload Fuse**;
wrapper layout changes require a new effect instance.

## Zoom compatibility

Zoom is normalized to the output's longest edge, rather than always its width.
For square pixels:

```text
internal KVR zoom = long-edge zoom / min(1, width / height)
```

For example, Long-Edge Zoom 0.5625 matches stock Zoom 1 in 9:16 and stock Zoom
0.5625 in 16:9. Existing zoom animations are not converted automatically.
180VR retains its original extra zoom multiplier; fisheye keeps its original
field-of-view control. Adaptive refers to zoom, not automatic timeline sizing.

## Source and license

Based on KVRViewer by David Kohen and Andrew Hazelden, distributed through
[Reactor](https://gitlab.com/WeSuckLess/Reactor/-/tree/master/Atoms/com.AndrewHazelden.KartaVP.Tools.kvrViewer).
The first commit is an unmodified import of package 5.85 at upstream commit
`aeaaae678d010655a7c9ed8b866a96811f8db8bc`. Later commits separate our changes
by feature. The original package manifest and example remain for reference.

LGPL-3.0, as declared upstream. Attribution remains in the source; license texts
are in [COPYING](COPYING) and [COPYING.LESSER](COPYING.LESSER).

## Development

Run `python3 tests/check.py` with Resolve installed on macOS, or set `LUA_LIBRARY`
to a Lua 5.1/LuaJIT shared library. The checks cover Lua compilation, controls,
output sizing, zoom math, and shader parameter dispatch using a mock GPU host.
Check actual playback and a full-quality export in Resolve when changing rendering.
