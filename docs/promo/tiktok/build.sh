#!/usr/bin/env bash
# Régénère docs/promo/tiktok/pets_tiktok.mp4 (motion design 9:16, 31 s).
# Prérequis : node + playwright (npx playwright install chromium), python3 + numpy, ffmpeg dans le PATH (ou FFMPEG=/chemin).
set -euo pipefail
cd "$(dirname "$0")"
FF="${FFMPEG:-ffmpeg}"
cp ../../icon.png icon.png
for g in duo polochons vol chasse mariage ecole fanmeeting betise anniversaire; do
  mkdir -p "gif/$g"; "$FF" -y -v error -i "../../gif_$g.gif" "gif/$g/f%04d.png"
done
python3 audio.py                                   # music.wav (synthé + sfx calés sur les coupes)
FFMPEG="$FF" node render.mjs                       # video_raw.mp4 (frames Chromium -> x264)
"$FF" -y -v error -i video_raw.mp4 -i music.wav -map 0:v -map 1:a \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=44100" -ar 44100 -ac 2 \
  -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k \
  -shortest -movflags +faststart pets_tiktok.mp4
"$FF" -y -v error -ss 2.3 -i pets_tiktok.mp4 -frames:v 1 -q:v 2 cover.jpg
echo "OK -> pets_tiktok.mp4 + cover.jpg"
