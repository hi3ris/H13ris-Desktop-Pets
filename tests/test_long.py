import os, sys, random, time, collections
os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import h13ris_pets as hp
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings
app = QApplication(sys.argv); QSettings("H13ris", "DesktopPets").clear()
seed = int(sys.argv[1]) if len(sys.argv) > 1 else 5
FAKE = [hp.Seg(0, 1920, 1040, 0, "A"), hp.Seg(1920, 4480, 1400, 0, "B"), hp.Seg(0, 1920, 2160, 1080, "C")]
FAKE2 = [hp.Seg(0, 1920, 1040, 0, "A"), hp.Seg(1920, 3840, 1040, 0, "B")]
DT = 1/30
def run(worlds, sec):
    for _ in range(int(sec / DT)):
        for ww in worlds:
            ww.now += DT; ww.advance(DT)
for label, terr in (("3 écrans", FAKE), ("2 écrans côte à côte", FAKE2)):
    random.seed(seed)
    hW = hp.World(app, headless=True, fake_terrain=terr); time.sleep(0.02)
    pW = hp.World(app, headless=True, fake_terrain=terr)
    run([hW, pW], 1)
    t = 0; deaths = []
    while t < 600 and not pW.dead:
        run([hW, pW], 1); t += 1
        d = sum(1 for p in pW.pets if not p.active())
        if d > len(deaths): deaths.append(t)
    print("%-22s durée %4ds  morts aux t=%s  kills garde=%d  coffres ouverts=%d" % (label, t, deaths, hW.hunt.get("kills", 0), hW.opened + pW.opened))
    hW.link.close(); pW.link.close()
