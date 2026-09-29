# Vidéo TikTok · H13ris Desktop Pets

Motion design vertical (1080×1920, 30 fps, 38 s) qui présente les deux démons, dans le
design system Hi3ris « Intercept » (fond `#0c0c0a`, or `#f4d03f`, orange `#ff6b3d`,
Space Grotesk / JetBrains Mono). Aucun asset externe : les démons 2D sont rendus par le
vrai code de dessin de `h13ris_pets.py` sur fond transparent, les démons 3D sont
modélisés en three.js, la musique est synthétisée, la voix est une voix neuronale.

| Fichier | Rôle |
| --- | --- |
| `pets_tiktok.mp4` | vidéo finale (H.264 + AAC stéréo, −14 LUFS) |
| `cover.jpg` | miniature |
| `caption.md` | légende + hashtags TikTok / Snapchat |
| `pets.html` | la scène : timeline déterministe, `window.seek(t)` positionne tout (DOM + WebGL) à l'instant `t` |
| `demons3d.js` | démons 3D procéduraux (corps, ventre, cornes, queue cœur/goutte, yeux, joues, accessoires : nœud, hélice, lunettes, lunettes de soleil, canne, couronne, jetpack) |
| `render_sprites.py` | rejoue les scènes de `tests/make_gifs.py` et exporte des séquences WebP à fond transparent dans `sprites/` |
| `render.mjs` | capture chaque image dans Chromium (Playwright, WebGL SwiftShader) et l'envoie à ffmpeg |
| `audio.py` | musique lo-fi synthétisée + whoosh / impact calés sur les coupes |
| `narration.json` | texte de la voix off, un segment par scène avec sa fenêtre de temps |
| `voice.py` | génère la voix (edge-tts gratuit par défaut, ElevenLabs si `ELEVENLABS_API_KEY`), la cale sur les scènes, baisse la musique sous la voix et remuxe |
| `build.sh` | enchaîne tout |
| `three.min.js`, `fonts/` | three.js r128 et polices (OFL) pour un rendu hors ligne |

## Storyboard

| Temps | Scène |
| --- | --- |
| 0–2.6 s | Accroche : « Ton bureau est vide. » → « Plus maintenant. » + Hybris 3D qui tombe |
| 2.6–7.2 s | Titre + duo (check, danse), fiche Hybris / Iblis |
| 7.2–11 s | Course, chamailleries, bataille de polochons · tous tes écrans |
| 11–14.8 s | Coffres : jetpack, potion de vol · ils volent |
| 14.8–18.6 s | Mode chasse : la Garde contre les intrus · 0 réseau |
| 18.6–22.4 s | Famille : mariage sous l'arche · vraie horloge |
| 22.4–25.6 s | Fan meeting NOVA 7 · crée ton groupe |
| 25.6–30.4 s | 3D « Sous toutes leurs formes » : ronde de huit démons (Hybris, bébé, enfant, ado, Iblis, aîné, idole, jetpack) |
| 30.4–34 s | Fiche : 1 fichier Python · 0 port · MIT · commande d'install |
| 34–38 s | CTA : Hybris et Iblis 3D, « Lien en bio », URL GitHub |

Le bas de l'image (20 %) reste libre pour l'interface TikTok.

## Regénérer

```bash
npm i -g playwright && npx playwright install chromium
pip install numpy Pillow PyQt6 edge-tts
./build.sh                          # voix gratuite (edge-tts, fr-FR-RemyMultilingualNeural)
ELEVENLABS_API_KEY=... ./build.sh   # voix ElevenLabs (ELEVENLABS_VOICE_ID pour changer de voix)
FFMPEG=/chemin/ffmpeg ./build.sh    # si ffmpeg n'est pas dans le PATH
```

Pour ne refaire que la voix : `python3 voice.py --engine edge --voice fr-FR-DeniseNeural` (relit `video_raw.mp4`).
