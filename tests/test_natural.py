"""Journée « naturelle » (sans forcer) : rythme des bulles, aide aux devoirs, bêtises, visiteurs."""
import os, sys, random, collections, datetime as _dt, types, shutil, tempfile
os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
shutil.rmtree(os.path.join(tempfile.gettempdir(), "h13ris_pets"), ignore_errors=True)
import h13ris_pets as hp
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings

app = QApplication(sys.argv)
QSettings("H13ris", "DesktopPets").clear()
random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 3)
FAKE = [hp.Seg(0, 1920, 1040, 0, "A"), hp.Seg(1920, 4480, 1400, 0, "B")]
DT = 1 / 30
hp.webbrowser = types.SimpleNamespace(open=lambda *a, **k: True)


class FakeDT(_dt.datetime):
    NOW = None

    @classmethod
    def now(cls, tz=None):
        return cls.NOW


def set_time(h, day=23):
    FakeDT.NOW = FakeDT(2026, 9, day, int(h), int(round((h % 1) * 60)) % 60)
    hp.datetime = types.SimpleNamespace(datetime=FakeDT, date=_dt.date)


SAY = collections.Counter()
_say = hp.Pet.say


TEXTS = collections.Counter()


def counting_say(self, text, dur=2.6):
    SAY[self.name] += 1
    TEXTS[text[:18]] += 1
    return _say(self, text, dur)


hp.Pet.say = counting_say
set_time(15.0)
w = hp.World(app, headless=True, fake_terrain=FAKE)
f = w.family


def run(sec, hook=None):
    for _ in range(int(sec / DT)):
        w.now += DT
        w.advance(DT)
        if hook:
            hook()


def kinds():
    return collections.Counter(e["k"] for e in f.events)


run(5)
# deux enfants rapidement (via la scène de naissance forcée)
for i in range(2):
    f.force_birth()
    t = 0
    while (w.duo is not None or f.egg is not None) and t < 90:
        run(0.5)
        t += 0.5
    for p in f.people:
        p.age = max(p.age, 1.6)          # enfants (pas bébés)
    while (f.scene is not None or f.queue) and t < 200:
        run(0.5)
        t += 0.5
print("habitants:", [(p.name, p.stage, p.persona) for p in f.people])
assert len(f.people) == 2

# ---- 15h30 → 17h00 : devoirs avec la vraie durée, aide des parents ----
SAY.clear()
set_time(15.55)
f.assign_duties(force=True)
helps = collections.Counter()
mins = 0


def watch():
    for p in w.pets:
        if p.duty == "help":
            helps[p.name] += 1


for m in range(90):
    set_time(15.55 + m / 60.0)
    run(60, watch)
print("devoirs 15h30-17h : notes %s, aidés (ticks) %s, devoirs faits %s | bulles/min %.1f" % (
    [(p.name, round(p.grade, 2), p.hw_day is not None) for p in f.people], dict(helps),
    [e["s"] for e in f.events if e["k"] == "ecole"], sum(SAY.values()) / 90.0))
assert all(p.hw_day is not None for p in f.people), "devoirs non finis"
assert helps, "aucun parent n'a aidé"

# ---- 17h → 20h30 : jeu libre, bêtises, dîner ----
SAY.clear()
n0 = kinds()
for m in range(210):
    set_time(17.0 + m / 60.0)
    run(60)
n1 = kinds()
print("bulles fréquentes :", TEXTS.most_common(12))
print("soirée 17h-20h30 : événements %s | bulles/min %.1f | faim %s" % (
    {k: n1[k] - n0.get(k, 0) for k in n1 if n1[k] - n0.get(k, 0)}, sum(SAY.values()) / 210.0,
    [(p.name, int(p.hunger)) for p in w.everyone()]))
assert all(p.hunger > 40 for p in w.everyone()), "quelqu'un a faim"

# ---- 20h30 → 23h30 : dodo des enfants puis des parents ----
for m in range(0, 180, 10):
    set_time(20.5 + m / 60.0)
    run(600)
    if m == 90:
        print("22h :", [(p.name, p.stage, p.duty, p.state) for p in w.everyone()])
        assert all(p.state == "sleep" for p in f.people), "enfants debout à 22h"
print("23h30 :", [(p.name, p.duty, p.state) for p in w.everyone()])
assert all(p.state == "sleep" for p in w.everyone()), "quelqu'un ne dort pas à 23h30"

# ---- nuit → 7h → 8h30 école (jeudi) ----
set_time(7.1, day=24)
run(120)
print("7h : ", [(p.name, p.duty, p.state, int(p.energy)) for p in w.everyone()])
assert all(p.state != "sleep" for p in f.people), "enfants encore au lit à 7h"
set_time(8.5, day=24)
run(90)
print("8h30 :", [(p.name, p.duty, p.state, int(abs(p.cx() - f.school_x()))) for p in f.people])
assert all(p.duty == "school" and abs(p.cx() - f.school_x()) < 160 for p in f.people)

# ---- visiteur naturel : on avance jusqu'à ce qu'un adulte célibataire attire quelqu'un ----
for p in f.people:
    p.age = 15.0
set_time(17.0, day=24)
f.assign_duties(force=True)
t = 0
while (f.scene is not None or f.queue) and t < 300:
    run(0.5)
    t += 0.5
f.visitor_cd = 5.0
run(30)
vis = [p for p in f.people if p.visitor]
print("visiteur naturel :", [(p.name, p.stage) for p in vis], "| population", f.population())
assert vis
print("bulles totales par pet :", dict(SAY))
w.shutdown()
print("OK")
