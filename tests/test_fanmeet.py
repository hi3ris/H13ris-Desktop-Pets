"""Fan meeting : déroulé complet pour chaque groupe, groupe perso, interruptions."""
import os, sys, random, collections, types, shutil, tempfile
os.environ["QT_QPA_PLATFORM"] = "offscreen"
shutil.rmtree(os.path.join(tempfile.gettempdir(), "h13ris_pets"), ignore_errors=True)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import h13ris_pets as hp
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings

app = QApplication(sys.argv)
QSettings("H13ris", "DesktopPets").clear()
random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 3)
FAKE = [hp.Seg(0, 1920, 1040, 0, "A"), hp.Seg(1920, 4480, 1400, 0, "B")]
DT = 1 / 30
hp.webbrowser = types.SimpleNamespace(open=lambda *a, **k: True)
w = hp.World(app, headless=True, fake_terrain=FAKE)
f, fm = w.family, w.fanmeet


def run(sec):
    for _ in range(int(sec / DT)):
        w.now += DT
        w.advance(DT)


run(3)
for _ in range(3):                                   # quelques habitants comme fans
    f.force_birth()
    t = 0
    while (w.duo is not None or f.egg is not None) and t < 90:
        run(0.5)
        t += 0.5
for p in f.people:
    p.age = 5.0
run(20)
print("fans potentiels :", len(w.pets) + len(f.alive()))


def meet(key):
    t = 0
    while not fm.can_start() and t < 120:
        run(0.5)
        t += 0.5
    w.cancel_duo()
    assert fm.start(key), "start refusé"
    g = fm.group
    phases, poses, says = collections.Counter(), set(), collections.Counter()
    t = 0
    while fm.active and t < 180:
        run(0.5)
        t += 0.5
        phases[fm.phase] += 1
        for i in fm.idols:
            if i.cur_pose():
                poses.add(i.cur_pose())
        for q in w.everyone():
            if q.bubble:
                says[q.bubble[:14]] += 1
    print("%-8s %4.0fs phases=%s poses=%s stats=%s" % (g["name"], t, dict(phases), sorted(poses), fm.stats))
    assert not fm.active and t < 180, "rencontre bloquée"
    assert not fm.idols and fm.banner is None
    assert all(not p.busy for p in w.pets) or w.duo or f.scene, [p.busy for p in w.pets]
    assert all(p.fan_prop is None and p.state != "ko" for p in w.pets + f.alive())
    assert sum(fm.stats.values()) >= 3, fm.stats
    assert {"bow", "big_heart"} <= poses
    return fm.stats


for key in ("nova7", "lumi"):
    meet(key)
    run(10)
print("chronique :", [e["s"] for e in f.events if e["k"] == "fanmeet"])
assert len([e for e in f.events if e["k"] == "fanmeet"]) == 2

# groupe perso via l'éditeur
dlg = hp.GroupEditor(fm)
dlg.name.setText("STARLIGHT")
dlg.randomize()
key, g = dlg.result_group()
fm.save_custom(key, g)
print("groupe perso :", g["name"], len(g["members"]), "membres, chant", g["chant"])
fm2 = hp.FanMeet(w)
assert key in fm2.groups(), "groupe perso non sauvegardé"
meet(key)

# interruption par la chasse et par le dodo
w.cancel_duo()
while not fm.can_start():
    run(0.5)
assert fm.start("nova7")
run(8)
w.set_role("hunter")
run(1)
assert not fm.active and not fm.idols
w.set_role(None)
run(5)
while not fm.can_start():
    run(0.5)
assert fm.start("lumi")
run(6)
w.all_sleep()
assert not fm.active
# visite surprise
run(5)
for p in w.pets:
    p.wake("!")
fm.visit_cd = 0.5
run(3)
print("visite surprise :", fm.active, fm.group and fm.group["name"])
assert fm.active
fm.end()
w.shutdown()
print("OK")
