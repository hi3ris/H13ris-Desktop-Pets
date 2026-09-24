import os, sys, random, time, collections
os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import h13ris_pets as hp
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings

app = QApplication(sys.argv)
QSettings("H13ris", "DesktopPets").clear()
seed = int(sys.argv[1]) if len(sys.argv) > 1 else 5
random.seed(seed)
FAKE = [hp.Seg(0, 1920, 1040, 0, "A"), hp.Seg(1920, 4480, 1400, 0, "B"), hp.Seg(0, 1920, 2160, 1080, "C")]
DT = 1 / 30


def run(worlds, sec):
    for _ in range(int(sec / DT)):
        for ww in worlds:
            ww.now += DT
            ww.advance(DT)


def near_edge(p):
    s = p.seg
    return s is not None and (p.cx() - s.x0 < 90 or s.x1 - p.cx() < 90)


# ---- 1. vol en temps de paix : jetpack, ballon, fusée, potion ----
w = hp.World(app, headless=True, fake_terrain=FAKE)
a, b = w.pets
run([w], 4)
for kind in ("jetpack", "ballon", "fusee", "potion_vol"):
    a.give_item(kind)
    top = 0
    landed = False
    if a.state == "sleep":
        a.wake()
    for i in range(int(40 / DT)):
        w.now += DT; w.advance(DT)
        if a.fly_t > 0:
            top = max(top, a.seg.yb - a.feet() if a.seg else 0)
        elif i > 30 and a.grounded():
            landed = True
            break
    print("%-10s altitude max %4d px, retombé au sol: %s, état: %s" % (kind, top, landed, a.state))
w.link.close()


def hunt_scenario(label, prey_items, seconds=240):
    random.seed(seed)
    hunterW = hp.World(app, headless=True, fake_terrain=FAKE)
    time.sleep(0.02)
    preyW = hp.World(app, headless=True, fake_terrain=FAKE)
    worlds = [hunterW, preyW]
    run(worlds, 1.0)
    assert hunterW.role == "hunter" and preyW.role == "prey", (hunterW.role, preyW.role)
    for p, it in zip(preyW.pets, prey_items):
        for k in it:
            p.give_item(k)
    stats = collections.Counter()
    frames = 0
    t = 0.0
    hunter_min_hp = 100
    while t < seconds and not preyW.dead:
        run(worlds, 0.5)
        t += 0.5
        for p in preyW.pets:
            if not p.active():
                continue
            frames += 1
            if p.camo:
                stats["camo"] += 1
            if p.fly_t > 0:
                stats["vol"] += 1
            if p.mood == "war":
                stats["combat"] += 1
            if p.state == "tunnel":
                stats["tunnel"] += 1
            if near_edge(p) and p.state == "idle":
                stats["coin_immobile"] += 1
        hunter_min_hp = min(hunter_min_hp, min(p.hp for p in hunterW.pets))
    alive = sum(1 for p in preyW.pets if p.active())
    pct = {k: "%d%%" % (100 * v / max(1, frames)) for k, v in stats.items()}
    print("%-28s survie %5.1fs  vivants %d  garde hp min %3d  %s" % (label, t, alive, hunter_min_hp, pct))
    for ww in worlds:
        ww.link.close()


hunt_scenario("intrus sans rien", ([], []))
hunt_scenario("intrus blaster+bouclier", (["blaster", "bouclier"], ["blaster"]))
hunt_scenario("intrus marteau", (["marteau"], ["marteau", "bouclier"]))
hunt_scenario("intrus jetpack/ballon", (["jetpack"], ["ballon"]))
hunt_scenario("intrus trottinette", (["trottinette"], ["trottinette"]))
hunt_scenario("intrus potion de vol", (["potion_vol"], ["fusee"]))
print("OK")
