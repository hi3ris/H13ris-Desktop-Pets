import os, sys, random, time, collections
os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import h13ris_pets as hp
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings

app = QApplication(sys.argv)
QSettings("H13ris", "DesktopPets").clear()
random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 7)

# terrain simulé : A (gauche), B (droite, plus bas = écran plus grand), C (sous A, inaccessible à pied)
FAKE = [hp.Seg(0, 1920, 1040, 0, "A"), hp.Seg(1920, 4480, 1400, 0, "B"), hp.Seg(0, 1920, 2160, 1080, "C")]
DT = 1 / 30


def run(w, sec, worlds=None):
    worlds = worlds or [w]
    for _ in range(int(sec / DT)):
        for ww in worlds:
            ww.now += DT
            ww.advance(DT)


def check_bounds(w, tag):
    T = w.terrain
    for p in w.pets:
        if p.state in ("gone", "ghost", "tunnel", "ride"):
            continue
        assert T.x0 - 20 <= p.cx() <= T.x1 + 20, (tag, p.name, p.cx())
        assert p.feet() <= T.max_yb + 5, (tag, p.name, p.feet(), p.state)


# ---------------- 1. vie normale multi-écrans ----------------
w = hp.World(app, headless=True, fake_terrain=FAKE)
w.mode = "chaos"
a, b = w.pets
segs_seen = collections.Counter()
states = collections.Counter()
duos = collections.Counter()
tunnels = 0
for i in range(int(400 / DT)):
    w.now += DT
    w.advance(DT)
    for p in w.pets:
        if p.seg is not None:
            segs_seen[(p.name, p.seg.name)] += 1
        states[p.state] += 1
        if p.state == "tunnel" and p.tunnel and p.tunnel["ph"] == "dig" and p.tunnel["t"] < DT * 1.5:
            tunnels += 1
    if w.duo:
        duos[w.duo["kind"]] += 1
    if i % 30 == 0:
        check_bounds(w, "life")
print("segs:", dict(segs_seen))
print("states:", dict(states))
print("duos vus:", dict(duos), "tunnels:", tunnels, "bond:", round(w.bond), "coffres ouverts:", w.opened)

# ---------------- 2. chaque duo forcé ----------------
for kind in ["chat", "debate", "highfive", "bump", "chase", "photo", "dance", "race", "hide_seek", "piggy", "war"]:
    w.cancel_duo()
    for p in w.pets:
        p.dizzy = 0
        if p.state == "sleep":
            p.wake()
    ok = w.start_duo(kind)
    t = 0
    while w.duo and t < 90:
        run(w, 0.5)
        t += 0.5
        check_bounds(w, kind)
    print("%-10s start=%s dur=%5.1fs left=%s states=%s" % (kind, ok, t, w.duo is not None, [p.state for p in w.pets]))

# ---------------- 3. coffres + objets ----------------
w.cancel_duo()
for p in w.pets:
    p.item = None
w.spawn_chest(a.cx() + 200, a.feet())
w.spawn_chest(b.cx() - 200, b.feet())
run(w, 25)
print("après coffres:", [(p.name, p.item, p.shield, round(p.veh_t)) for p in w.pets],
      "coffres restants:", len([c for c in w.chests.values() if not c["taken"]]))

# ---------------- 4. chasse : deux instances ----------------
hunterW = hp.World(app, headless=True, fake_terrain=FAKE)
time.sleep(0.05)
preyW = hp.World(app, headless=True, fake_terrain=FAKE)
worlds = [w, hunterW, preyW]
w.hunt_enabled = True
run(w, 1.0, worlds)
print("rôles:", w.role, hunterW.role, preyW.role, "arbitre:", w.is_arbiter(), hunterW.is_arbiter(), preyW.is_arbiter())
assert w.role == "hunter" and hunterW.role == "prey" and preyW.role == "prey", "rôles"
mind = 9999
hits = 0
prey_hp = []
t = 0
while t < 240 and not preyW.dead and not hunterW.dead:
    run(w, 0.5, worlds)
    t += 0.5
    for p in w.pets:
        for r in w.remote:
            if r.active():
                mind = min(mind, hp.dist2(p.cx(), p.feet(), r.cx(), r.feet()))
    prey_hp.append(tuple(round(p.hp) for p in preyW.pets))
    if int(t) % 30 == 0 and abs(t - int(t)) < 0.01:
        print("  t=%3d garde=%s intrus=%s hp=%s camo=%s items=%s coffres=%d" % (
            t, [(p.name, p.state, int(p.cx())) for p in w.pets],
            [(p.name, p.state, int(p.cx())) for p in preyW.pets],
            [round(p.hp) for p in preyW.pets], [p.camo for p in preyW.pets],
            [p.item for p in preyW.pets], len(w.chest_list())))
print("distance min garde/intrus:", round(mind), "hp intrus final:", prey_hp[-1],
      "morts:", [p.gone for p in preyW.pets], "processus intrus mort:", preyW.dead,
      "kills garde:", w.hunt.get("kills"), "score hunterW(prey2):", [p.hp for p in hunterW.pets])
print("liaison ok:", w.link.ok, "peers:", len(w.link.peers))
for ww in worlds:
    ww.link.close()
print("OK")
