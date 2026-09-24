"""Mode démo : une vie entière en ~8 minutes, puis retour de la vraie famille."""
import os, sys, random, collections, types, shutil, tempfile
os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
shutil.rmtree(os.path.join(tempfile.gettempdir(), "h13ris_pets"), ignore_errors=True)
import h13ris_pets as hp
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings

app = QApplication(sys.argv)
QSettings("H13ris", "DesktopPets").clear()
random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 5)
FAKE = [hp.Seg(0, 1920, 1040, 0, "A"), hp.Seg(1920, 4480, 1400, 0, "B")]
DT = 1 / 30
hp.webbrowser = types.SimpleNamespace(open=lambda *a, **k: True)

w = hp.World(app, headless=True, fake_terrain=FAKE)
f = w.family


def run(sec, hook=None):
    for _ in range(int(sec / DT)):
        w.now += DT
        w.advance(DT)
        if hook:
            hook()


# une vraie famille d'abord : un enfant, sauvegardé
run(3)
f.force_birth()
t = 0
while (w.duo is not None or f.egg is not None) and t < 90:
    run(0.5)
    t += 0.5
real = [p.name for p in f.people]
f.save()
print("vraie famille :", real)
assert real

# ---- démo ----
f.start_demo()
assert f.demo and not f.people
seen = collections.Counter()
duties = collections.Counter()
stages = set()
maxpop = 0
t = 0.0
while f.demo and t < hp.DEMO_MAX + 60:
    run(1)
    t += 1
    for p in f.people:
        stages.add(p.stage)
        if p.duty:
            duties[p.duty] += 1
    if f.scene:
        seen[f.scene["kind"]] += 1
    maxpop = max(maxpop, f.population())
    if int(t) % 60 == 0:
        print("  t=%3.0fs habitants=%s œuf=%s scène=%s" % (
            t, [(p.name, p.stage, round(p.age)) for p in f.people], bool(f.egg), f.scene and f.scene["kind"]))
print("démo terminée en %.0fs ; scènes %s ; devoirs %s ; étapes %s ; pop max %d" % (
    t, dict(seen), dict(duties), sorted(stages), maxpop))
kinds = collections.Counter(e["k"] for e in f.events)
print("événements de la démo (chronique) :", dict(kinds))
assert not f.demo, "la démo ne s'est pas arrêtée"
assert t < hp.DEMO_MAX, "arrêt seulement par sécurité (%.0fs)" % t
assert {"birthday", "wedding", "depart"} <= set(seen), seen
assert {"bébé", "enfant", "ado", "adulte", "aîné"} <= stages, stages
assert duties["school"] and duties["study"], duties
assert maxpop >= 5, maxpop

# ---- retour de la vraie famille ----
print("après démo :", [p.name for p in f.people], "| mémorial", len(f.memorial), "| événements", len(f.events))
assert [p.name for p in f.people] == real
assert not f.memorial and not f.graves
run(10)
w.shutdown()
print("OK")
