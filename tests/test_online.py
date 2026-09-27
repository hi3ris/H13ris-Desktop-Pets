"""Flux en ligne simulé : mise à jour annoncée par Hybris, messages sponsorisés, à propos."""
import os, sys, json, types, shutil, tempfile, random
os.environ["QT_QPA_PLATFORM"] = "offscreen"
shutil.rmtree(os.path.join(tempfile.gettempdir(), "h13ris_pets"), ignore_errors=True)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import h13ris_pets as hp
from PyQt6.QtWidgets import QApplication, QMenu
from PyQt6.QtCore import QSettings
app = QApplication(sys.argv)
QSettings("H13ris", "DesktopPets").clear()
random.seed(2)
opened = []
hp.webbrowser = types.SimpleNamespace(open=lambda u, *a, **k: opened.append(u))
FEED = dict(version="9.9.0", notes="Test", ads=[dict(text="Qui m'a créé ? ramses.dagban.tg", url="https://ramses.dagban.tg"),
                                             dict(text="lien pas sûr", url="http://evil")], ad_every_min=10)
hp.http_get = lambda url, **k: json.dumps(FEED).encode()
w = hp.World(app, headless=True, fake_terrain=[hp.Seg(0, 1920, 1040, 0, "A")])
o = w.online
DT = 1 / 30
said = []
def run(sec):
    for _ in range(int(sec / DT)):
        w.now += DT; w.advance(DT)
        for p in w.pets:
            if p.bubble and (not said or said[-1] != p.bubble):
                said.append(p.bubble)
run(40)
assert o.update and o.update["version"] == "9.9.0", o.update
w.refresh_menu()
assert w.update_act.isVisible() and "9.9.0" in w.update_act.text()
for p in w.pets: p.wake("!"); p.busy = False
w.cancel_duo()
o.nag_t = 0.1
run(3)
assert any("Mise à jour" in s for s in said), said[-6:]
w.update_act.trigger()
assert opened and opened[-1].endswith("/releases/latest"), opened
for _ in range(40):
    w.cancel_duo()
    for p in w.pets:
        p.wake("!"); p.busy = False
    o.ad_t = 0.05
    run(0.2)
    if any(x.startswith(hp.AD_PREFIX) for x in said):
        break
print("états", [(p.state, p.busy) for p in w.pets], o.calm(), w.family.scene, w.fanmeet.active)
ads = [s for s in said if s.startswith(hp.AD_PREFIX)]
print("pub :", ads)
assert ads
sp = [p for p in w.pets if p.ad_url][0] if any(p.ad_url for p in w.pets) else None
if sp:
    sp.bubble = sp.bubble or "x"
    sp.pet()
    assert opened[-1].startswith("https://"), opened
am = QMenu(); o.fill_about(am)
print([a.text() for a in am.actions() if a.text()])
assert any("ramses.dagban.tg" in a.text() for a in am.actions())
FEED["version"] = "1.0.0"; o.check_now(manual=True)
import time; time.sleep(0.3); run(1)
assert o.update is None
w.shutdown(); print("OK")
