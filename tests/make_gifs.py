"""Enregistre des GIF des démons en action, hors écran, avec le vrai code de dessin."""
import os, sys, random, shutil, tempfile, types, datetime as _dt
os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
shutil.rmtree(os.path.join(tempfile.gettempdir(), "h13ris_pets"), ignore_errors=True)
import h13ris_pets as hp
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QImage, QPainter, QColor, QPen
from PyQt6.QtCore import QSettings, QPointF
from PIL import Image

app = QApplication(sys.argv)
QSettings("H13ris", "DesktopPets").clear()
hp.webbrowser = types.SimpleNamespace(open=lambda *a, **k: True)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs")
FPS = 12
DT = 1 / 30.0
BG = QColor("#2f3542")
FLOOR = QColor("#3a4152")
SEG = [hp.Seg(0, 1920, 1040, 0, "A")]


class FakeDT(_dt.datetime):
    NOW = None

    @classmethod
    def now(cls, tz=None):
        return cls.NOW


def set_time(h, day=23):
    FakeDT.NOW = FakeDT(2026, 9, day, int(h), int(round((h % 1) * 60)) % 60)
    hp.datetime = types.SimpleNamespace(datetime=FakeDT, date=_dt.date)


set_time(10.0)


def new_world(seed, decor=True):
    random.seed(seed)
    QSettings("H13ris", "DesktopPets").clear()
    w = hp.World(app, headless=True, fake_terrain=SEG)
    if not decor:
        w.family.toggle_decor(False)
    for p in w.pets:
        p.state = "idle"
        p.y = p.seg.yb - hp.GROUND
        p.timer = 1.0
    return w


def place(p, cx, seg=None):
    seg = seg or SEG[0]
    p.land_msg = None
    p.x = cx - hp.W / 2
    p.y = seg.yb - hp.GROUND
    p.seg = seg
    p.state = "idle"
    p.airborne = False
    p.vx = p.vy = 0.0


class Recorder:
    def __init__(self, worlds, width=640, height=270, floor=SEG[0].yb, zoom=1.0):
        self.worlds = worlds if isinstance(worlds, list) else [worlds]
        self.wd, self.ht = width, height
        self.floor = floor
        self.zoom = zoom
        self.frames = []
        self.cam = None

    def actors(self):
        out = []
        for w in self.worlds:
            out += [p for p in w.everyone() if p.active() and p.isVisible() or p.state in ("ghost",)]
        return out

    def frame(self, focus=None, fixed=None):
        acts = self.actors()
        if fixed is not None:
            target = fixed
        elif focus:
            target = sum(p.cx() for p in focus) / len(focus)
        else:
            target = sum(p.cx() for p in acts) / max(1, len(acts))
        vw, vh = self.wd / self.zoom, self.ht / self.zoom            # vue en unités écran
        target = max(vw / 2, min(SEG[0].x1 - vw / 2, target))
        self.cam = target if self.cam is None else self.cam + (target - self.cam) * 0.15
        x0, y0 = self.cam - vw / 2, self.floor + 14 - vh
        img = QImage(self.wd, self.ht, QImage.Format.Format_RGBA8888)
        img.fill(BG)
        p = QPainter(img)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        p.scale(self.zoom, self.zoom)
        p.setPen(QPen(FLOOR, 2))
        p.drawLine(QPointF(0, self.floor - y0 + 1), QPointF(vw, self.floor - y0 + 1))
        for w in self.worlds:
            f = w.family
            props = list(f.decor.values()) + list(f.dyn.values()) + list(w.props.values())
            if f.egg and f.egg.get("prop") is not None:
                props.append(f.egg["prop"])
            if getattr(w, "fanmeet", None) is not None and w.fanmeet.banner is not None:
                props.append(w.fanmeet.banner)
            for pr in props:
                s = pr.width()
                p.save()
                p.translate(pr.x - s / 2 - x0, pr.y - s + 8 - y0)
                pr.paint(p)
                p.restore()
        for w in self.worlds:
            for s in w.shots:
                p.save()
                p.translate(s.x - hp.SHOT / 2 - x0, s.y - hp.SHOT / 2 - y0)
                s.paint(p)
                p.restore()
        for w in self.worlds:
            for pet in sorted(w.everyone(), key=lambda q: (q.state == "ride", q.is_kid)):
                if pet.state == "gone" or (pet.state == "tunnel"):
                    continue
                p.save()
                p.translate(pet.x - x0, pet.y - y0)
                pet.paint_all(p, bubble=True)
                p.restore()
        p.end()
        buf = img.bits().asstring(img.sizeInBytes())
        im = Image.frombuffer("RGBA", (self.wd, self.ht), buf, "raw", "RGBA", img.bytesPerLine(), 1).convert("RGB")
        self.frames.append(im)

    def run(self, sec, focus=None, fixed=None, hook=None):
        acc, per = 0.0, 1.0 / FPS
        for _ in range(int(sec / DT)):
            for w in self.worlds:
                w.now += DT
                w.advance(DT)
            if hook:
                hook()
            acc += DT
            if acc >= per - 1e-9:
                acc -= per
                self.frame(focus, fixed)

    def save(self, name, colors=160):
        frames = self.frames
        step = max(1, len(frames) // 8)
        sample = frames[::step]
        mosaic = Image.new("RGB", (sample[0].width, sample[0].height * len(sample)))
        for i, fr in enumerate(sample):
            mosaic.paste(fr, (0, i * fr.height))
        pal = mosaic.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
        q = [fr.quantize(palette=pal, dither=Image.Dither.NONE) for fr in frames]
        path = os.path.join(OUT, name)
        q[0].save(path, save_all=True, append_images=q[1:], duration=int(1000 / FPS), loop=0, optimize=True)
        print("%-22s %3d images  %6.0f Ko" % (name, len(frames), os.path.getsize(path) / 1024))
        self.frames = []


def settle(w, sec=1.0):
    for _ in range(int(sec / DT)):
        w.now += DT
        w.advance(DT)


# ---------------------------------------------------------------- duo (check, danse)
def gif_duo():
    w = new_world(1, decor=False)
    a, b = w.pets
    place(a, 560)
    place(b, 700)
    b.facing = -1
    settle(w, 0.5)
    r = Recorder(w)
    w.force_duo("highfive")
    r.run(4.2)
    w.cancel_duo()
    w.force_duo("dance")
    r.run(5.0)
    r.save("gif_duo.gif")
    w.shutdown()


# ---------------------------------------------------------------- bataille de polochons
def gif_war():
    w = new_world(3, decor=False)
    a, b = w.pets
    place(a, 480)
    place(b, 760)
    b.facing = -1
    w.cursor_still = 999
    settle(w, 0.5)
    r = Recorder(w, width=720)
    w.force_duo("war")
    r.run(9.0, focus=w.pets)
    r.save("gif_polochons.gif")
    w.shutdown()


# ---------------------------------------------------------------- vol
def gif_flight():
    w = new_world(5, decor=False)
    a, b = w.pets
    place(a, 520)
    place(b, 700)
    settle(w, 0.5)
    r = Recorder(w, height=470)
    a.give_item("jetpack")
    b.give_item("potion_vol")
    settle(w, 0.8)
    a.use_item()
    b.use_item()
    a.walk_to(1150, a.fly_speed)
    b.walk_to(1050, b.fly_speed)
    r.run(7.5)
    r.save("gif_vol.gif")
    w.shutdown()


# ---------------------------------------------------------------- chasse (deux instances)
def gif_hunt():
    random.seed(7)
    QSettings("H13ris", "DesktopPets").clear()
    wa = hp.World(app, headless=True, fake_terrain=SEG)          # la Garde (première instance)
    wa.family.toggle_decor(False)
    settle(wa, 0.3)
    wb = hp.World(app, headless=True, fake_terrain=SEG)          # les intrus
    for w in (wa, wb):
        for p in w.pets:
            place(p, 0)
    place(wa.pets[0], 1180)
    place(wa.pets[1], 1290)
    place(wb.pets[0], 1640)
    place(wb.pets[1], 1740)
    for w in (wa, wb):
        for p in w.pets:
            p.land_msg = None
    for _ in range(40):                                          # la liaison découvre les deux instances
        for w in (wa, wb):
            w.now += DT
            w.advance(DT)
    print("rôles :", wa.role, wb.role)
    for p in wa.pets:
        p.give_item("blaster")
    for p in wb.pets:
        p.give_item("bouclier")
    r = Recorder([wa, wb], width=760)
    r.run(9.0, focus=wa.pets + wb.pets)
    r.save("gif_chasse.gif")
    wa.shutdown()
    wb.shutdown()


# ---------------------------------------------------------------- famille : école, devoirs
def person(w, age, hue, acc=None, **kw):
    f = w.family
    tr = hp.Person.make_traits(w, parents=w.pets, gen=1)
    tr.update(age=age, acc=acc, hue=hue)
    k = hp.Person(w, tr)
    place(k, f.home_x())
    k.timer = 0.5
    for key, v in kw.items():
        setattr(k, key, v)
    f.people.append(k)
    return k


def gif_school():
    set_time(10.0)
    w = new_world(11)
    f = w.family
    a, b = w.pets
    k1 = person(w, 3.0, 290, "helice")
    k2 = person(w, 10.0, 320, "lunettes")
    place(k1, f.school_x() - 260)
    place(k2, f.school_x() - 340)
    place(a, f.school_x() - 120)
    place(b, f.desk_x() + 40)
    f.assign_duties(force=True)
    r = Recorder(w)
    r.run(4.5, fixed=f.school_x() - 120)
    # devoirs : les enfants au bureau, un parent vient aider
    set_time(15.6)
    place(k1, f.desk_x() - 160)
    place(k2, f.desk_x() + 150)
    place(a, f.desk_x() - 40)
    place(b, f.desk_x() + 260)
    f.assign_duties(force=True)
    a.duty, a.helping = "help", k1.name
    a.go_idle(1)
    r.run(5.0, fixed=f.desk_x() + 30)
    r.save("gif_ecole.gif")
    w.shutdown()


# ---------------------------------------------------------------- famille : anniversaire
def gif_birthday():
    set_time(17.5)
    w = new_world(13)
    f = w.family
    a, b = w.pets
    k1 = person(w, 1.49, 300, "noeud")
    k2 = person(w, 5.0, 40, None)
    cx = f.home_x() + 260
    place(a, cx - 150)
    place(b, cx + 150)
    place(k1, cx + 30)
    place(k2, cx - 60)
    f.assign_duties(force=True)
    settle(w, 0.3)
    k1.age = 1.51
    r = Recorder(w)
    r.run(9.5, fixed=cx + 30)
    r.save("gif_anniversaire.gif")
    w.shutdown()


# ---------------------------------------------------------------- famille : mariage
def gif_wedding():
    set_time(17.5)
    w = new_world(17)
    f = w.family
    a, b = w.pets
    k = person(w, 20.0, 300, None)
    tr = hp.Person.make_traits(w, village=True, gen=0)
    tr.update(age=20.0, hue=45)
    v = hp.Person(w, tr)
    f.people.append(v)
    kid = person(w, 4.0, 200, "helice")
    cx = f.home_x() + 260
    place(a, cx - 160)
    place(b, cx + 170)
    place(k, cx - 40)
    place(v, cx + 40)
    place(kid, cx - 90)
    v.facing = -1
    f.assign_duties(force=True)
    settle(w, 0.3)
    k.romance[v.name] = v.romance[k.name] = 80
    k.rel[v.name] = v.rel[k.name] = 50
    f.propose(k, v)
    f.scene_cd = 0.0
    r = Recorder(w, width=700)
    r.run(3.0, fixed=cx)
    r.run(11.0, fixed=cx)
    r.save("gif_mariage.gif")
    w.shutdown()


# ---------------------------------------------------------------- bêtise : boule de neige + gronderie
def gif_mischief():
    set_time(17.5)
    w = new_world(19)
    f = w.family
    a, b = w.pets
    k = person(w, 5.0, 290, "helice")
    k.persona = ["espiègle", "sportif"]
    place(a, f.home_x() + 420)
    place(b, f.home_x() + 560)
    place(k, f.home_x() + 200)
    k.facing = 1
    f.assign_duties(force=True)
    settle(w, 0.3)
    r = Recorder(w)
    r.run(0.8, fixed=f.home_x() + 380)
    orig = hp.random.choice
    hp.random.choice = lambda seq, _o=orig: "boule" if (isinstance(seq, list) and "boule" in seq) else _o(seq)
    old = hp.random.random
    hp.random.random = lambda: 0.1                          # gronderie garantie
    f.do_mischief(k)
    hp.random.choice, hp.random.random = orig, old
    r.run(5.5, focus=[k, b])
    r.save("gif_betise.gif")
    w.shutdown()




# ---------------------------------------------------------------- fan meeting
def gif_fanmeet(key="nova7", name="gif_fanmeeting.gif", seed=4):
    set_time(17.5)
    w = new_world(seed, decor=False)
    f = w.family
    a, b = w.pets
    cx = 900
    place(a, cx - 330)
    place(b, cx + 330)
    kids = [person(w, 5.0, 290, "helice"), person(w, 11.0, 30, "lunettes"), person(w, 20.0, 180, None)]
    for k, x in zip(kids, (cx - 420, cx + 420, cx + 500)):
        place(k, x)
    f.assign_duties(force=True)
    for q in w.everyone():
        q.duty = None
    settle(w, 0.5)
    fm = w.fanmeet
    assert fm.start(key)
    global FPS
    old, FPS = FPS, 10
    r = Recorder(w, width=820, height=300, zoom=0.9)
    settle(w, 1.2)
    r.run(8.0, fixed=fm.stage)                  # arrivée + cris
    r.run(5.0, fixed=fm.stage)                  # salut du groupe
    while fm.phase == "fanservice" and fm.pt < 9:
        settle(w, 0.5)
    r.run(8.0, fixed=fm.stage)                  # photos, selfies, évanouissements
    while fm.phase != "dance" or fm.step < 2:
        settle(w, 0.5)
    r.run(5.0, fixed=fm.stage)                  # chorégraphie
    r.save(name, colors=160)
    FPS = old
    fm.end(quiet=True)
    w.shutdown()


def gif_fanmeet_lumi():
    gif_fanmeet("lumi", "gif_fanmeeting_lumi.gif", seed=9)


if __name__ == "__main__":
    which = sys.argv[1:] or ["duo", "war", "flight", "hunt", "school", "birthday", "wedding", "mischief", "fanmeet", "fanmeet_lumi"]
    for name in which:
        globals()["gif_" + name]()
