#!/bin/sh
set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
fusion_dir="$HOME/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion"
mkdir -p "$fusion_dir/Fuses/kvrViewerAdaptive" "$fusion_dir/Templates/Edit/Effects/Custom 360"
cp "$repo_dir/Fuses/Kartaverse/KartaVP/Warp/kvrViewer.fuse" "$fusion_dir/Fuses/kvrViewerAdaptive/kvrViewerAdaptive.fuse"
cp "$repo_dir/Templates/Edit/Effects/KartaVP/Warp/kvrViewer.setting" "$fusion_dir/Templates/Edit/Effects/Custom 360/kvrViewer Adaptive.setting"
cp "$repo_dir/Templates/Edit/Effects/KartaVP/Warp/kvrViewer.png" "$fusion_dir/Templates/Edit/Effects/Custom 360/kvrViewer Adaptive.png"
printf '%s\n' 'Installed kvrViewer Adaptive. Restart DaVinci Resolve to load it.'
