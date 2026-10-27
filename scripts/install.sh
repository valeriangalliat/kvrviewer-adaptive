#!/bin/sh
set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
fusion_dir="$HOME/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion"
mkdir -p "$fusion_dir/Fuses/Kartaverse/KartaVP/Warp" "$fusion_dir/Templates/Edit/Effects/KartaVP/Warp"
cp "$repo_dir/Fuses/Kartaverse/KartaVP/Warp/kvrViewer.fuse" "$fusion_dir/Fuses/Kartaverse/KartaVP/Warp/kvrViewerAdaptive.fuse"
cp "$repo_dir/Templates/Edit/Effects/KartaVP/Warp/kvrViewer.setting" "$fusion_dir/Templates/Edit/Effects/KartaVP/Warp/kvrViewer Adaptive.setting"
cp "$repo_dir/Templates/Edit/Effects/KartaVP/Warp/kvrViewer.png" "$fusion_dir/Templates/Edit/Effects/KartaVP/Warp/kvrViewer Adaptive.png"
printf '%s\n' 'Installed kvrViewer Adaptive. Restart DaVinci Resolve to load it.'
