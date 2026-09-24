"""Simulation accélérée de la vie de famille et de communauté (v5)."""
import os, sys, random, collections, datetime as _dt, types, shutil, tempfile
os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
shutil.rmtree(os.path.join(tempfile.gettempdir(), "h13ris_pets"), ignore_errors=True)
import h13ris_pets as hp
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings

app = QApplication(sys.argv)
QSettings("H13ris", "DesktopPets").clear()
random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 7)
FAKE = [hp.Seg(0, 1920, 1040, 0, "A"), hp.Seg(1920, 4480, 1400, 0, "B")]
DT = 1 / 30
hp.webbrowser = types.SimpleNamespace(open=lambda *a, **k: True)


# ---- horloge contrôlable ----
class FakeDT(_dt.datetime):
    NOW = None

    @classmethod
    def now(cls, tz=None):
        return cls.NOW


def set_time(h, day=23):
    FakeDT.NOW = FakeDT(2026, 9, day, int(h), int(round((h % 1) * 60)) % 60)
    hp.datetime = types.SimpleNamespace(datetime=FakeDT, date=_dt.date)


set_time(10.0)                       # mercredi 10h


def run(w, sec, hook=None):
    for _ in range(int(sec / DT)):
        w.now += DT
        w.advance(DT)
        if hook:
            hook()


def logs(f, kind):
    return [e["s"] for e in f.events if e["k"] == kind]


w = hp.World(app, headless=True, fake_terrain=FAKE)
f = w.family
a, b = w.pets
assert f.active, "famille inactive"
print("fondateurs:", a.name, a.persona, "|", b.name, b.persona, "| décor:", sorted(f.decor))
run(w, 5)

# ---------- 1. naissance ----------
f.force_birth()
t = 0
while (w.duo is not None or f.egg is not None) and t < 90:
    run(w, 0.5)
    t += 0.5
assert f.people, "pas d'enfant"
k = f.people[0]
print("naissance: %s gen %d parents %s persona %s stage %s (%.0fs)" % (k.name, k.gen, k.parents, k.persona, k.stage, t))
assert k.gen == 1 and set(k.parents) == {"Hybris", "Iblis"} and logs(f, "naissance")

# ---------- 2. anniversaire : bébé -> enfant ----------
k.age = 1.52
run(w, 3)
assert f.scene is not None and f.scene["kind"] == "birthday", f.scene
t = 0
while f.scene is not None and t < 60:
    run(w, 0.5)
    t += 0.5
print("anniversaire: stage=%s taille=%.2f scène %.0fs | %s" % (k.stage, k.size, t, logs(f, "anniversaire")))
assert k.stage == "enfant" and logs(f, "anniversaire") and f.scene is None

# ---------- 3. école ----------
set_time(10.0)
f.assign_duties(force=True)
assert k.duty == "school", k.duty
run(w, 45)
d_school = abs(k.cx() - f.school_x())
print("école: duty=%s distance école %d px état %s" % (k.duty, d_school, k.state))
assert d_school < 140, d_school

# ---------- 4. devoirs (accélérés) + aide d'un parent ----------
hp.HOMEWORK_MIN = (0.35, 0.2)
set_time(15.6)
f.assign_duties(force=True)
assert k.duty == "study", k.duty
g0 = k.grade
helped = False
t = 0
while k.hw_day is None and t < 120:
    run(w, 0.5)
    t += 0.5
    helped = helped or any(p.duty == "help" and p.helping == k.name for p in w.pets)
print("devoirs: fini en %.0fs, note %.2f -> %.2f, aide parent=%s | %s" % (t, g0, k.grade, helped, logs(f, "ecole")))
assert k.hw_day is not None and k.grade > g0
run(w, 5)
assert k.duty is None and all(p.duty != "help" for p in w.pets)

# ---------- 5. bêtises et punitions ----------
set_time(17.2)
f.assign_duties(force=True)
k.persona = ["espiègle", "sportif"]
k.fun = 30.0
n0 = len(logs(f, "betise"))
a.item, a.ammo = "banane", 1                        # de quoi chiper
b.sleep(200)                                        # de quoi réveiller


def cheeky():
    k.mischief_cd = 0.0


run(w, 240, cheeky)
mis = logs(f, "betise")
print("bêtises: %d | %s" % (len(mis) - n0, mis[-4:]))
assert len(mis) > n0, "aucune bêtise"
# vérif directe de chaque type
k.punished_t = 0.0
kinds = collections.Counter()
for kind in ("gribouillis", "chipe", "chahut", "boule"):
    k.state = "idle"
    k.punished_t = 0.0
    a.item, a.ammo = "marteau", 1
    a.state, b.state = "idle", "sleep"
    a.x = k.x + 100
    b.x = k.x - 100
    a.seg = b.seg = k.seg
    random.seed(kind)
    before = len(f.events)
    orig = hp.random.choice
    hp.random.choice = lambda seq, _k=kind, _o=orig: _k if (isinstance(seq, list) and _k in seq) else _o(seq)
    f.do_mischief(k)
    hp.random.choice = orig
    kinds[kind] = len(f.events) - before
    run(w, 2)
print("types de bêtises testés:", dict(kinds), "| puni:", k.punished_t > 0, "obéissance", k.obedience)
assert all(v >= 1 for v in kinds.values()), kinds
print("boules de neige en vol:", len(w.shots))
run(w, 3)
assert all(p.hp >= 99 for p in w.pets), "une boule de neige a fait des dégâts"

# ---------- 6. ado -> adulte, visiteur, cour, mariage ----------
k.punished_t = 0.0
k.age = 14.2
run(w, 3)
t = 0
while (f.scene is not None or f.queue) and t < 120:
    run(w, 0.5)
    t += 0.5
print("adulte: stage=%s (%.0fs)" % (k.stage, t))
assert k.stage == "adulte"
f.arrive_visitor()
v = [p for p in f.people if p.visitor][0]
print("visiteur: %s stage %s persona %s | %s" % (v.name, v.stage, v.persona, logs(f, "visite")[-1]))
assert v.stage == "adulte" and not k.related(v)
set_time(17.5)
f.assign_duties(force=True)


def eager():
    for p in (k, v):
        p.court_cd = min(p.court_cd, 2.0)
        p.hunger = max(p.hunger, 60)
        p.energy = max(p.energy, 60)
    f.scene_cd = 0.0


t = 0
while not (k.spouse and v.spouse) and t < 600:
    run(w, 1, eager)
    t += 1
print("mariage: %s <-> %s en %.0fs | romance %.0f/%.0f | %s" % (k.spouse, v.spouse, t, k.romance.get(v.name, 0),
                                                              v.romance.get(k.name, 0), logs(f, "mariage")))
assert k.spouse == v.name and v.spouse == k.name and not v.visitor
assert any("arche" in s for s in logs(f, "mariage"))

# ---------- 7. œuf du couple, génération 2 ----------
def fertile():
    f.egg_cd = 0.0
    for p in (k, v):
        p.hunger = max(p.hunger, 60)


t = 0
while not any(p.gen == 2 for p in f.people) and t < 400:
    run(w, 1, fertile)
    t += 1
g2 = [p for p in f.people if p.gen == 2]
print("génération 2: %s en %.0fs" % ([(p.name, p.parents) for p in g2], t))
assert g2 and set(g2[0].parents) == {k.name, v.name}

# ---------- 8. vieillesse, adieux, départ vers la lune, deuil ----------
k.age = k.lifespan * f.scale - hp.FAREWELL_H * f.scale + 0.01
run(w, 2)
print("adieux: farewell=%s stage=%s | %s" % (k.farewell, k.stage, logs(f, "famille")[-1:]))
assert k.stage == "aîné"
t = 0
while (f.scene is not None or f.queue) and t < 120:            # anniversaire « aîné »
    run(w, 0.5)
    t += 0.5
assert k.farewell
k.age = k.lifespan * f.scale + 0.01
t = 0
while k in f.people and t < 200:
    run(w, 0.5, lambda: setattr(f, "scene_cd", min(f.scene_cd, 5.0)))
    t += 0.5
print("départ: %.0fs | mémorial %s | tombes %s | %s" % (t, [m["name"] for m in f.memorial], f.graves, logs(f, "depart")))
assert k not in f.people and f.memorial and f.memorial[-1]["name"] == k.name and f.graves
assert v.spouse is None and v.ribbon_t > 0, (v.spouse, v.ribbon_t)
assert any(key.startswith("tombe") for key in f.decor), f.decor.keys()
assert not k.isVisible()

# ---------- 9. fête et livre ----------
f.force_festival(" (test)")
t = 0
while (f.scene is None or f.scene["kind"] != "festival") and t < 30:
    run(w, 0.5)
    t += 0.5
while f.scene is not None and t < 90:
    run(w, 0.5)
    t += 0.5
print("fête:", logs(f, "fete"))
assert logs(f, "fete")
path = f.write_book()
html = open(path, encoding="utf-8").read()
print("livre: %s (%d octets)" % (path, len(html)))
assert k.name in html and v.name in html and "Mémorial" in html

# ---------- 10. routine des fondateurs : nuit, repas, travail ----------
set_time(23.5)
f.assign_duties(force=True)
run(w, 40)
print("nuit: états fondateurs", [(p.name, p.duty, p.state, int(abs(p.cx() - f.home_x()))) for p in w.pets])
assert all(p.state == "sleep" for p in w.pets)
set_time(12.6)
f.assign_duties(force=True)
run(w, 40)
print("déjeuner:", [(p.name, p.duty, p.state, int(p.hunger)) for p in w.pets])
assert all(p.hunger > 90 for p in w.pets)
set_time(10.0)
worked = set()
for i in range(120):
    f.hours += 0.05
    f.assign_duties(force=True)
    run(w, 1)
    worked |= {p.name for p in w.pets if p.duty == "work" and p.state == "idle"}
print("travail au bureau:", worked)
assert worked

# ---------- 11. sauvegarde / rechargement ----------
f.save()
w.shutdown()
w2 = hp.World(app, headless=True, fake_terrain=FAKE)
f2 = w2.family
print("rechargé: %s | mémorial %d | tombes %d | heures %.1f" % (
    [(p.name, p.stage, round(p.age, 1), p.spouse) for p in f2.people], len(f2.memorial), len(f2.graves), f2.hours))
assert {p.name for p in f2.people} == {p.name for p in f.people if not p.dead}
assert len(f2.memorial) == len(f.memorial) and f2.hours > 0
run(w2, 30)

# ---------- 12. endurance : 15 min de vie sans exception, positions valides ----------
set_time(16.0)
bad = 0
for i in range(int(900 / DT)):
    w2.now += DT
    w2.advance(DT)
    if i % 30 == 0:
        for p in w2.everyone():
            if p.active() and p.state not in ("tunnel",) and not (FAKE[0].x0 - 200 <= p.cx() <= FAKE[1].x1 + 200):
                bad += 1
print("endurance: habitants %d, hors-écran %d, événements %d" % (len(f2.people), bad, len(f2.events)))
assert bad == 0
w2.shutdown()
print("OK")
