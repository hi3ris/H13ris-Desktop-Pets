# Vidéo TikTok · H13ris Desktop Pets

Motion design vertical (1080×1920, 30 fps, 31 s) qui présente les deux démons, dans le
design system Hi3ris « Intercept » (fond `#0c0c0a`, or `#f4d03f`, orange `#ff6b3d`,
Space Grotesk / JetBrains Mono).

| Fichier | Rôle |
| --- | --- |
| `pets_tiktok.mp4` | vidéo finale (H.264 + AAC, −14 LUFS) |
| `cover.jpg` | miniature |
| `caption.md` | légende + hashtags TikTok / Snapchat |
| `pets.html` | la scène : timeline déterministe, `window.seek(t)` positionne tout à l'instant `t` |
| `render.mjs` | capture chaque image dans Chromium (Playwright) et l'envoie à ffmpeg |
| `audio.py` | musique lo-fi synthétisée + whoosh / impact calés sur les coupes (aucun sample externe) |
| `narration.json` | texte de la voix off, un segment par scène avec sa fenêtre de temps |
| `voice.py` | génère la voix avec ElevenLabs (`ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID`), la cale sur les scènes, baisse la musique sous la voix et remuxe |
| `build.sh` | enchaîne tout : extraction des GIF de `docs/`, audio, rendu, mux |

Les extraits animés sont les GIF de `docs/` (duo, polochons, vol, chasse, mariage, fan meeting).

## Storyboard

| Temps | Scène |
| --- | --- |
| 0–2.6 s | Accroche : « Ton bureau est vide. » → « Plus maintenant. » + Hybris qui tombe |
| 2.6–7 s | Titre + duo en direct, fiche Hybris / Iblis |
| 7–10.5 s | Course, chamailleries, bataille de polochons · tous tes écrans |
| 10.5–14 s | Coffres : jetpack, potions, fusée · ils volent |
| 14–17.5 s | Mode chasse : la Garde contre les intrus · 0 réseau |
| 17.5–21 s | Famille : école, mariage, petits-enfants · vraie horloge |
| 21–24 s | Fan meeting K-pop · crée ton groupe |
| 24–27.5 s | Fiche : 1 fichier Python · 0 port · MIT · commande d'install |
| 27.5–31 s | CTA : icône, titre, « Lien en bio », URL GitHub |

Le bas de l'image (20 %) et la bande droite restent libres pour l'interface TikTok.

## Regénérer

```bash
npm i -g playwright && npx playwright install chromium
pip install numpy
ELEVENLABS_API_KEY=... ./build.sh   # avec voix off
./build.sh          # FFMPEG=/chemin/ffmpeg ./build.sh si ffmpeg n'est pas dans le PATH
```
