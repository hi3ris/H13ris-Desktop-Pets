"""Rend les scènes de tests/make_gifs.py en séquences WebP à fond transparent (vrai code de dessin)."""
import os, sys
os.environ["QT_QPA_PLATFORM"] = "offscreen"
REPO = os.environ.get("PETS_REPO", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
OUT = os.environ.get("SPRITES_OUT", os.path.join(os.getcwd(), "sprites"))
sys.path.insert(0, os.path.join(REPO, "tests")); sys.path.insert(0, REPO)
import make_gifs as mg
from PyQt6.QtGui import QImage, QPainter
from PyQt6.QtCore import Qt, QPointF
from PIL import Image
import h13ris_pets as hp

CFG = {"zoom": 1.7, "w": 1080, "h": 560}
_Base = mg.Recorder

class Rec(_Base):
    def __init__(self, worlds, width=640, height=270, floor=mg.SEG[0].yb, zoom=1.0):
        super().__init__(worlds, CFG["w"], CFG["h"], floor, CFG["zoom"])
    def frame(self, focus=None, fixed=None):
        acts = self.actors()
        if fixed is not None: target = fixed
        elif focus: target = sum(p.cx() for p in focus) / len(focus)
        else: target = sum(p.cx() for p in acts) / max(1, len(acts))
        vw, vh = self.wd / self.zoom, self.ht / self.zoom
        target = max(vw / 2, min(mg.SEG[0].x1 - vw / 2, target))
        self.cam = target if self.cam is None else self.cam + (target - self.cam) * 0.15
        x0, y0 = self.cam - vw / 2, self.floor + 14 - vh
        img = QImage(self.wd, self.ht, QImage.Format.Format_RGBA8888)
        img.fill(Qt.GlobalColor.transparent)
        p = QPainter(img)
        p.setRenderHint(QPainter.RenderHint.Antialiasing); p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        p.scale(self.zoom, self.zoom)
        for w in self.worlds:
            f = w.family
            props = list(f.decor.values()) + list(f.dyn.values()) + list(w.props.values())
            if f.egg and f.egg.get("prop") is not None: props.append(f.egg["prop"])
            if getattr(w, "fanmeet", None) is not None and w.fanmeet.banner is not None: props.append(w.fanmeet.banner)
            for pr in props:
                s = pr.width(); p.save(); p.translate(pr.x - s / 2 - x0, pr.y - s + 8 - y0); pr.paint(p); p.restore()
        for w in self.worlds:
            for s in w.shots:
                p.save(); p.translate(s.x - hp.SHOT / 2 - x0, s.y - hp.SHOT / 2 - y0); s.paint(p); p.restore()
        for w in self.worlds:
            for pet in sorted(w.everyone(), key=lambda q: (q.state == "ride", q.is_kid)):
                if pet.state == "gone" or pet.state == "tunnel": continue
                p.save(); p.translate(pet.x - x0, pet.y - y0); pet.paint_all(p, bubble=True); p.restore()
        p.end()
        buf = img.bits().asstring(img.sizeInBytes())
        self.frames.append(Image.frombuffer("RGBA", (self.wd, self.ht), buf, "raw", "RGBA", img.bytesPerLine(), 1).copy())
    def save(self, name, colors=160):
        d = os.path.join(OUT, name.replace("gif_", "").replace(".gif", "")); os.makedirs(d, exist_ok=True)
        for i, fr in enumerate(self.frames):
            fr.save(os.path.join(d, "f%04d.webp" % (i + 1)), "WEBP", quality=88, method=4)
        print(name, len(self.frames), "frames ->", d, flush=True); self.frames = []

mg.Recorder = Rec
SCENES = {
    "duo":     dict(zoom=1.9, w=1080, h=520),
    "war":     dict(zoom=1.6, w=1080, h=520),
    "flight":  dict(zoom=1.5, w=1080, h=720),
    "hunt":    dict(zoom=1.5, w=1080, h=520),
    "wedding": dict(zoom=1.55, w=1080, h=560),
    "school":  dict(zoom=1.55, w=1080, h=560),
    "fanmeet": dict(zoom=1.15, w=1080, h=440),
}
for name in (sys.argv[1:] or list(SCENES)):
    CFG.update(SCENES[name]); getattr(mg, "gif_" + name)()
