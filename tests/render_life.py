import os, sys, random, shutil, tempfile
os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
shutil.rmtree(os.path.join(tempfile.gettempdir(), "h13ris_pets"), ignore_errors=True)
import h13ris_pets as hp
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
from PyQt6.QtCore import QRectF, Qt, QSettings
app = QApplication(sys.argv)
random.seed(11)
QSettings("H13ris", "DesktopPets").clear()
w = hp.World(app, headless=True)
f = w.family
a, b = w.pets
for p in w.pets:
    p.state = "idle"
    p.y = p.seg.yb - hp.GROUND
    p.blink = 0
    p.tilt = 0


def person(age, acc=None, hue=280, **kw):
    tr = hp.Person.make_traits(w, parents=w.pets, gen=1)
    tr.update(age=age, acc=acc, hue=hue)
    k = hp.Person(w, tr)
    k.seg = a.seg
    k.x = 0
    k.y = k.seg.yb - hp.GROUND
    k.state = "idle"
    k.t = 1.0
    k.blink = 0
    k.tilt = 0
    for key, v in kw.items():
        setattr(k, key, v)
    f.people.append(k)
    return k


cast = [
    ("bébé", person(0.5, "noeud", 265)),
    ("enfant à l'école", person(3, "helice", 290, duty="school")),
    ("ado (devoirs)", person(10, "lunettes", 310, duty="study")),
    ("adulte au travail", person(20, None, 330, duty="work")),
    ("visiteur", person(18, None, 40, visitor=True)),
    ("aîné (canne)", person(45, None, 300)),
    ("deuil (ruban)", person(22, None, 200, ribbon_t=100)),
]
cast[5][1].set_expr("happy", 2)
a.duty, a.helping = "help", cast[2][1].name          # Hybris aide aux devoirs (ordinateur)
b.show_item, b.show_item_t = "anneau", 0.8           # Iblis montre une bague

CW, Y = 130, 40
sheet = QPixmap(1560, 510)
sheet.fill(QColor("#39404f"))
p = QPainter(sheet)
p.setRenderHint(QPainter.RenderHint.Antialiasing)
p.save(); p.translate(-30, Y); a.paint_all(p); p.restore()
for i, (lab, k) in enumerate(cast):
    p.save(); p.translate(110 + i * CW, Y); k.paint_all(p); p.restore()
p.save(); p.translate(110 + len(cast) * CW, Y); b.paint_all(p); p.restore()
labels = [("Hybris (aide)", 80)] + [(lab, 220 + i * CW) for i, (lab, _) in enumerate(cast)] + [("Iblis (bague)", 220 + len(cast) * CW)]
p.setPen(QColor("#e8e8f0")); p.setFont(QFont("Sans", 9))
for lab, x in labels:
    p.drawText(QRectF(x - 70, Y + 200, 140, 16), Qt.AlignmentFlag.AlignCenter, lab)

# décor du village et accessoires de cérémonie
props = [("maison", dict()), ("ecole", dict()), ("bureau", dict()), ("arche", dict(opened=True, t=1.0)),
         ("gateau", dict(opened=True, t=0.6)), ("tombe", dict(label="Kira", flowers=3)), ("gribouillis", dict(hue=120)),
         ("cadeau", dict()), ("egg", dict(hue=290, crack=0.8))]
x = 100
for kind, attrs in props:
    pr = hp.Prop(kind, 0, 0, hue=attrs.pop("hue", 300.0), label=attrs.pop("label", ""))
    for key, v in attrs.items():
        setattr(pr, key, v)
    pr.age = 1.5
    wide = kind in hp.WIDE_PROPS
    S = pr.width()
    p.save(); p.translate(x - S / 2, 462 - S + 8); pr.paint(p); p.restore()
    p.drawText(QRectF(x - 80, 480, 160, 16), Qt.AlignmentFlag.AlignCenter, kind)
    x += 200 if wide else 130
    pr.hide()
p.end()
sheet.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "apercu_vie.png"))
print("ok")
