"""Narration ElevenLabs + mix final.

Usage : ELEVENLABS_API_KEY=... [ELEVENLABS_VOICE_ID=...] python3 voice.py
Lit narration.json, génère un segment par scène (eleven_multilingual_v2), le cale sur le
début de sa scène (accéléré jusqu'à x1.18 s'il déborde), baisse la musique sous la voix,
puis produit voice.wav, mix.wav et pets_tiktok.mp4 (à partir de video_raw.mp4).
"""
import json, os, subprocess, sys, wave, urllib.request
import numpy as np

KEY = os.environ.get("ELEVENLABS_API_KEY")
VOICE = os.environ.get("ELEVENLABS_VOICE_ID", "h5FvD7dtq6DnVBPv8li")
FF = os.environ.get("FFMPEG", "ffmpeg")
SR = 44100
if not KEY:
    sys.exit("ELEVENLABS_API_KEY manquante")

def tts(text, path):
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}?output_format=mp3_44100_128",
        data=json.dumps({"text": text, "model_id": "eleven_multilingual_v2",
                         "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.35, "use_speaker_boost": True}}).encode(),
        headers={"xi-api-key": KEY, "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r, open(path, "wb") as f:
        f.write(r.read())

def load_wav(path):
    with wave.open(path, "rb") as w:
        assert w.getframerate() == SR and w.getnchannels() == 1
        return np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float64) / 32767

def save_wav(path, x):
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())

segs = json.load(open("narration.json"))
music = load_wav("music.wav")
N = len(music)
voice = np.zeros(N)
os.makedirs("voice", exist_ok=True)
for i, s in enumerate(segs):
    mp3 = f"voice/seg{i:02d}.mp3"; wavp = f"voice/seg{i:02d}.wav"
    if not os.path.exists(mp3):
        tts(s["text"], mp3)
    # trim silence, mono 44.1k
    subprocess.run([FF, "-y", "-v", "error", "-i", mp3, "-af", "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse",
                    "-ac", "1", "-ar", str(SR), wavp], check=True)
    x = load_wav(wavp)
    slot = s["end"] - s["start"]
    dur = len(x) / SR
    if dur > slot:
        rate = min(dur / slot, 1.18)
        subprocess.run([FF, "-y", "-v", "error", "-i", wavp, "-af", f"atempo={rate:.4f}", "-ac", "1", "-ar", str(SR), wavp + ".t.wav"], check=True)
        x = load_wav(wavp + ".t.wav"); dur = len(x) / SR
        if dur > slot + 0.3:
            print(f"  ! segment {i} déborde encore ({dur:.2f}s pour {slot:.2f}s) : {s['text']}")
    st = int(s["start"] * SR); n = min(len(x), N - st)
    voice[st:st + n] += x[:n]
    print(f"seg {i}: {dur:5.2f}s / slot {slot:.2f}s  {s['text'][:50]}")

# normalise la voix, puis ducking de la musique (-9 dB sous la voix, attaque/retour doux)
voice /= max(1e-6, np.max(np.abs(voice))) / 0.9
env = np.abs(voice)
k = int(0.08 * SR); env = np.convolve(env, np.ones(k) / k, mode="same")
gate = (env > 0.02).astype(float)
k2 = int(0.35 * SR); gate = np.convolve(gate, np.ones(k2) / k2, mode="same")
duck = 1.0 - gate * (1 - 10 ** (-9 / 20))
mix = music * duck * 0.55 + voice
mix /= max(1e-6, np.max(np.abs(mix))) / 0.95
save_wav("voice.wav", voice); save_wav("mix.wav", mix)
subprocess.run([FF, "-y", "-v", "error", "-i", "video_raw.mp4", "-i", "mix.wav", "-map", "0:v", "-map", "1:a",
                "-af", "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=44100", "-ar", "44100", "-ac", "2",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", "pets_tiktok.mp4"], check=True)
print("OK -> pets_tiktok.mp4 (avec narration)")
