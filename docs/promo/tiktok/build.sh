#!/usr/bin/env bash
# Régénère docs/promo/tiktok/pets_tiktok.mp4 (motion design 9:16, 38 s, 3D + narration).
# Prérequis : node + playwright (npx playwright install chromium), python3 + numpy + Pillow + PyQt6 + edge-tts,
#             ffmpeg dans le PATH (ou FFMPEG=/chemin). Voix ElevenLabs si ELEVENLABS_API_KEY est définie.
set -euo pipefail
cd "$(dirname "$0")"
FF="${FFMPEG:-ffmpeg}"
python3 render_sprites.py                                      # sprites/ : scènes de tests/make_gifs.py, fond transparent
python3 audio.py                                               # music.wav (synthé + sfx calés sur les coupes)
FFMPEG="$FF" PAGE=pets.html OUT=video_raw.mp4 node render.mjs  # images Chromium (WebGL SwiftShader) -> x264
FFMPEG="$FF" python3 voice.py                                  # narration (edge-tts gratuit, ou ElevenLabs) + ducking + mux
"$FF" -y -v error -ss 2.4 -i pets_tiktok.mp4 -frames:v 1 -q:v 2 cover.jpg
echo "OK -> pets_tiktok.mp4 + cover.jpg"
