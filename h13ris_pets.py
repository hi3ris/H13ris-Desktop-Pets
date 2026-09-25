#!/usr/bin/env python3
"""
H13ris Desktop Pets — Hybris & Iblis  (v5.1)
Deux petits démons tout ronds qui vivent sur ton bureau, sur TOUS tes écrans.

Installation :  pip install PyQt6
Lancement    :  pythonw h13ris_pets.py        (pythonw = pas de console)
Démarrage auto (Windows) : activé au premier lancement, décochable dans le menu.
                           En ligne de commande : --autostart on | off

MULTI-ÉCRANS
  Chaque écran est un sol. Ils marchent d'un écran à l'autre, tombent sur un
  écran plus bas, sautent sur un écran plus haut, et creusent un tunnel pour
  rejoindre un écran qui n'est pas accessible à pied.

INTERACTIONS DU DUO
  Discussion, check, course-poursuite, bousculade, bataille de polochons,
  cache-cache, portage (l'un grimpe sur l'autre), course, photo, danse,
  partage de potion... Choisies selon leur énergie, leur ennui et leur
  complicité (visibles dans le menu « État »).

COFFRES ET OBJETS (semés sur les écrans, ou via le menu « Semer » / « Donner »)
  Blaster Nerf, marteau-jouet, BlueShield, potion de sang, potion de vitesse,
  potion d'invisibilité, trottinette, peau de banane, fumigène, et pour voler :
  potion de vol (ailes), jetpack, ballon, fusée.

VIE DE FAMILLE ET DE COMMUNAUTÉ (menu « Famille & village »)
  Le village vit sur l'écran principal : une maison, un bureau, une école.
  Hybris et Iblis sont les fondateurs, immortels ; quand leur complicité est
  haute, un œuf apparaît, couve, éclot. Chaque habitant a une couleur héritée,
  deux traits de caractère (espiègle, sage, gourmand, timide, sportif, rêveur,
  grognon, sociable, curieux, artiste), des besoins (énergie, faim, fun, lien)
  et des relations. Les âges se comptent en heures d'activité (application
  ouverte) : bébé → enfant → ado → adulte → aîné, une vie ≈ une semaine de
  bureau (réglable : rythme court / normal / long).
  La journée suit ta vraie horloge : école en semaine (8h-15h), devoirs à
  15h30 (les parents viennent aider, la note progresse F → A), goûter, repas,
  travail des adultes au bureau (ordinateur), coucher des petits à 20h30, des
  ados à 21h30, des adultes à 23h. Les enfants jouent, se chamaillent, font
  des bêtises (gribouillis, chapardage, réveil des dormeurs, boules de neige,
  école buissonnière) et se font gronder : coin, obéissance qui monte.
  Les adultes célibataires se font la cour (compliments, fleur, danse, balade),
  demandent en mariage (refus possible), et tout le village se rassemble pour
  la noce sous l'arche fleurie ; des visiteurs du village arrivent avec leur
  valise pour se marier ici. Les couples ont des œufs (génération 2, 3...).
  Anniversaires avec gâteau à chaque étape, fêtes du village (calendrier ou
  menu), histoires des aînés aux petits. Les aînés font leurs adieux entourés
  des leurs puis « partent vers la lune » ; une tombe fleurie reste, la famille
  porte le deuil. Tout est sauvegardé ; le « livre de famille » (HTML) raconte
  la chronique, l'arbre et le mémorial. Jusqu'à 8 habitants.
  Mode démo (menu) : une vie entière en huit minutes, sans toucher à la vraie
  famille, pour tout voir d'un coup.

FAN MEETING (menu « 🎤 Fan meeting », ou visite surprise de temps en temps)
  Un groupe d'idoles FICTIF débarque avec sa banderole : NOVA 7 (7 garçons) ou
  LUMI (5 filles), chaque membre reconnaissable à sa coiffure, sa couleur de
  cheveux, son accessoire, sa tenue, son rôle et sa pose signature. Les démons
  et tout le village deviennent des fans surexcités : cris, lightsticks aux
  couleurs du groupe, photos, selfies, autographes, cadeaux, cœurs avec les
  doigts, évanouissements (un autre fan vient les réveiller), larmes de joie,
  fanchant avec le nom des membres, chorégraphie synchronisée, adieux déchirants.
  « Créer un groupe… » : ton propre groupe (nom, fandom, couleur, membres).

MODE CHASSE (lance le script plusieurs fois !)
  La première instance devient la Garde : ses deux démons s'allient pour
  traquer et éliminer les intrus. Chaque instance suivante est un duo d'intrus
  qui sait qu'il est pris en chasse : il file vers le point le plus sûr, saute
  par-dessus les gardes, creuse un tunnel, se camoufle, change de planque,
  cherche des coffres... et armé, il tient tête (embuscade, blaster, marteau),
  ou s'envole et bombarde depuis le ciel. Un intrus éliminé
  devient un fantôme ; quand les deux sont éliminés, leur processus se ferme.
  Si la Garde quitte, les plus anciens intrus survivants deviennent la Garde.
  (« Mode chasse » se désactive dans le menu.)

INTERACTIONS
  - Clic gauche      : caresse (cœurs). Trop de clics d'affilée : il boude.
  - Glisser-lâcher   : tu les attrapes et tu peux les lancer (gare au tournis)
  - Clic droit       : menu complet
  - Icône système    : même menu ; double-clic pour masquer / afficher
Politesse : jamais de vol de focus ni du curseur ; ils se cachent tout seuls
quand une application passe en plein écran (Windows).
"""
import json
import math
import os
import random
import signal
import sys
import tempfile
import time
import datetime
import webbrowser

from PyQt6.QtCore import QElapsedTimer, QPointF, QRectF, QSettings, Qt, QTimer
from PyQt6.QtGui import (QActionGroup, QColor, QCursor, QFont, QFontMetrics,
                         QGuiApplication, QIcon, QLinearGradient, QPainter,
                         QPainterPath, QPen, QPixmap, QPolygonF, QRadialGradient)
from PyQt6.QtWidgets import (QApplication, QComboBox, QDialog, QDialogButtonBox, QFormLayout,
                             QHBoxLayout, QHeaderView, QLineEdit, QMenu, QPushButton, QSlider,
                             QSystemTrayIcon, QTableWidget, QVBoxLayout, QWidget)

# --------------------------------------------------------------------------- #
# Réglages
# --------------------------------------------------------------------------- #
W, H = 220, 200          # taille de la fenêtre de chaque pet
GROUND = H - 14          # position des pieds dans la fenêtre
GRAVITY = 1800.0
WALK_SPEED = 62.0
RUN_SPEED = 170.0        # chasseurs
PREY_SPEED = 200.0       # fuyards (un peu plus rapides, mais ils fatiguent)
FPS_ACTIVE = 30
FPS_SLEEP = 10           # quand les deux dorment : quasi zéro CPU
SHOT = 60                # taille des fenêtres projectiles
PROP = 80                # taille des fenêtres coffres / objets
LINK_HZ = 12             # fréquence d'échange entre instances
MAX_HOP = 520            # hauteur max d'un saut vers un écran plus haut

# ---- Famille et communauté (âges en heures d'activité, application ouverte) ----
LIFE_SCALES = {"court": 0.5, "normal": 1.0, "long": 4.0}
STAGES = [("bébé", 1.5, 0.55), ("enfant", 8.0, 0.70), ("ado", 14.0, 0.85),
          ("adulte", 40.0, 1.0), ("aîné", 999.0, 0.95)]        # (nom, fin d'étape en h, taille)
LIFESPAN = (48.0, 56.0)   # heures d'activité avant le départ vers la lune (≈ une semaine de bureau)
# mode démo : une vie entière en ~8 minutes (journée en tranches, vieillissement ×400)
DEMO_DAY = [(7.2, 10), (8.6, 40), (12.6, 14), (14.0, 22), (15.6, 34), (17.5, 50), (19.6, 14), (22.0, 20), (23.6, 14)]
DEMO_AGE = 400.0
DEMO_MAX = 720.0
FAREWELL_H = 1.0          # dernière heure : les adieux
POP_MAX = 8               # habitants (fondateurs compris)
KID_MAX = 6               # compatibilité
BIRTH_BOND = 85           # complicité minimale pour un œuf des fondateurs
BIRTH_COOLDOWN = 1200     # s entre deux naissances spontanées (fondateurs)
EGG_HATCH = (35.0, 60.0)  # s d'incubation
KID_NAMES = ["Pixel", "Bit", "Nano", "Byte", "Chip", "Kilo", "Octet", "Bug", "Ping",
             "Pong", "Cookie", "Token", "Nova", "Mimi", "Hylis", "Ibri", "Hybi", "Lili",
             "Zéro", "Sudo", "Root", "Kern", "Nyx", "Lux", "Echo", "Vega", "Juno", "Rune"]
VILLAGE_NAMES = ["Ada", "Grace", "Hedy", "Linus", "Tux", "Alan", "Kali", "Zed", "Pixie",
                 "Sol", "Mika", "Neo", "Kira", "Orion", "Rune", "Vega", "Juno", "Echo",
                 "Nyx", "Lux", "Ravi", "Koffi", "Ama", "Yao", "Sena", "Efua"]
PERSONAS = ["espiègle", "sage", "gourmand", "timide", "sportif", "rêveur", "grognon",
            "sociable", "curieux", "artiste"]
# journée type (heure locale) ; le week-end : pas d'école ni de travail
ROUTINE = dict(wake=7.0, school=(8.0, 15.0), work=(9.0, 12.0, 13.5, 17.0),
               lunch=12.5, snack=16.5, dinner=19.5, homework=15.5,
               bed_kid=20.5, bed_teen=21.5, bed_adult=23.0)
HOMEWORK_MIN = (25.0, 12.0)   # minutes seul / avec un parent
KID_LINES = dict(
    hello=["Coucou !", "Areuh ?", "Papa ! Papa !", "Bonjour le monde !"],
    play=["Hihi !", "Encore !", "Attrape-moi !", "Regarde !", "Youpi !"],
    cry=["Ouiiin !", "Bouhou...", "Où vous êtes ?!", "Snif..."],
    sleep=["*bâille*", "Dodo...", "Zzz"],
    teen=["Pff.", "Trop nul.", "Je fais ce que je veux.", "Laisse-moi.", "Ok boomer."],
    parent_fetch=["Là, là...", "Je suis là.", "Viens par ici."],
    parent_play=["Guili guili !", "Qui c'est le plus mignon ?", "Attention, je t'attrape !"],
    birth=["Devine quoi ?", "Un bébé !!", "On va être parents !", "Chut, il dort."],
    welcome=["Bienvenue, %s !", "Coucou, %s !", "Il te ressemble, %s !"],
    school=["À l'école !", "Bonjour maîtresse.", "2 + 2 = ... 4 !", "Je lève la main !",
            "C'est quoi un pare-feu ?", "Récré !"],
    homework=["Devoirs...", "Je comprends rien.", "Papa, aide-moi !", "Presque fini.",
              "Les fractions, beurk."],
    homework_done=["Devoirs finis !", "J'ai tout bon !", "Fini, je peux jouer ?"],
    help=["Je t'aide.", "Regarde, c'est facile.", "Bravo, continue !"],
    mischief=["Hihi... personne ne regarde ?", "Oups.", "C'est pas moi !", "Bêtise en cours..."],
    scold=["Au coin !", "Hé ! Ça suffit.", "On ne fait pas ça.", "Va réfléchir dans le coin."],
    corner=["...", "C'est pas juste.", "Pardon...", "Je m'ennuie."],
    caught=["Zut, grillé.", "Pardon !", "C'était pour rire..."],
    grade=["J'ai eu un A !", "Un B, pas mal.", "Bof, un C.", "...un D.", "Un F. Chut."],
    work=["Je surveille le SIEM.", "Ticket fermé.", "Réunion... zzz.", "Faux positif.",
          "Pause café !", "Je patche."],
    meal=["Miam !", "À table !", "C'est bon !", "Encore des biscuits ?", "J'ai faim."],
    story=["Il était une fois un ping...", "Avant, les modems chantaient.",
           "J'ai connu Windows 95, moi.", "Écoutez bien, les petits."],
    elder=["Mes cornes me font mal.", "Doucement...", "Quelle belle journée.", "Où sont mes lunettes ?"],
    farewell=["Bientôt l'heure pour moi.", "Prenez soin de vous.", "Je veillerai depuis la lune.",
              "Ma plus belle aventure."],
    depart=["Adieu, mes chéris.", "À bientôt, là-haut.", "Je pars vers la lune."],
    mourn=["Tu nous manques.", "Snif...", "Regarde, c'est son étoile.", "Il aurait aimé ça."],
    visitor=["Bonjour, je viens du village.", "Il paraît que c'est joli ici.", "Je peux rester un peu ?"],
    court=["Tu as de belles cornes.", "On se balade ?", "Tiens, une fleur.", "Tu danses ?",
           "J'aime bien ton rire."],
    propose=["Veux-tu... m'épouser ?", "Toi et moi, pour toujours ?"],
    accept=["Oui !!", "Mille fois oui !"],
    refuse=["Pas encore...", "Laisse-moi réfléchir."],
    wedding=["Vive les mariés !", "Youpi !", "Bravo !", "Trop beau !"],
    vows=["Je patcherai tes bugs.", "Le dernier biscuit sera à toi.",
          "Je te trouverai à cache-cache.", "Je veillerai sur nos ports."],
    birthday=["Joyeux anniversaire !", "Souffle !", "Hip hip hip hourra !", "Un gâteau !"],
    sibling=["C'est à moi !", "Non, à moi !", "T'es nul.", "Maman !"],
    festival=["C'est la fête !", "On danse !", "Regarde le ciel !", "Des lanternes !"],
    hungry=["J'ai faim.", "Mon ventre gargouille."],
    lonely=["Quelqu'un veut jouer ?", "Je m'ennuie."],
)
BOOK_KINDS = dict(naissance="🥚", anniversaire="🎂", ecole="📚", betise="😈", mariage="💍",
                  visite="🎒", depart="🌙", fete="🎉", exploit="⭐", famille="💞", fanmeet="🎤")

# ---- Fan meeting : groupes d'idoles FICTIFS (aucun groupe réel) ----
HAIR_STYLES = {            # style -> (masse arrière, frange)
    "rideau": (None, "rideau"), "meche": (None, "meche"), "frange": (None, "frange"),
    "pointes": (None, "pointes"), "rase": (None, "rase"), "mulet": ("mulet", "pointes"),
    "boucles": ("boucles", "boucles"), "long": ("long", "rideau"), "carre": ("carre", "frange"),
    "couettes": ("couettes", "frange"), "queue": ("queue", "meche"), "chignon": ("chignon", "rideau"),
}
HAIR_COLORS = {"noir": "#1E1B24", "brun": "#5A3825", "chatain": "#8A5A3B", "blond": "#F2D27A",
               "platine": "#EFEDE6", "argent": "#B9C0CC", "rose": "#FF8FC2", "rouge": "#D8323C",
               "orange": "#FF8A3D", "menthe": "#7FE0C4", "bleu": "#3D6BFF", "violet": "#8E5BD9",
               "lavande": "#B9A6F2", "vert": "#3FA86B"}
IDOL_ACCS = ["aucun", "lunettes", "piercing", "casquette", "bandana", "bonnet", "oreillette",
             "noeud", "serre_tete", "grain", "pansement", "etoile"]
IDOL_OUTFITS = ["costume", "veste", "sweat", "crop", "robe"]
IDOL_ROLES = ["leader", "chant", "rap", "danse", "visual", "maknae"]
IDOL_POSES = ["point", "heart", "peace", "arms_up", "wink", "wave", "big_heart"]
SKIN_TONES = ["#FFE3CF", "#F6D2B6", "#E9BC96", "#C98E66"]
IDOL_GROUPS = {
    "nova7": dict(name="NOVA 7", fandom="Novas", hue=228, stick="etoile",
                  greet="Say the name... NOVA 7 !", chant="NO-VA SE-VEN !",
                  members=[
                      dict(name="Doha", hair="rideau", hc="noir", acc="lunettes", role="leader",
                           outfit="costume", oc="#26306B", skin=1, sig="point"),
                      dict(name="Rion", hair="meche", hc="platine", acc="oreillette", role="chant",
                           outfit="veste", oc="#F4F4F8", skin=0, sig="heart"),
                      dict(name="Seyun", hair="mulet", hc="rouge", acc="piercing", role="rap",
                           outfit="sweat", oc="#22222A", skin=2, sig="peace"),
                      dict(name="Kaen", hair="boucles", hc="brun", acc="casquette", role="danse",
                           outfit="sweat", oc="#FFC93D", skin=3, sig="arms_up"),
                      dict(name="Iseul", hair="long", hc="argent", acc="grain", role="visual",
                           outfit="costume", oc="#ECE9F7", skin=0, sig="wink"),
                      dict(name="Taeo", hair="rase", hc="bleu", acc="pansement", role="chant",
                           outfit="veste", oc="#3FA86B", skin=2, sig="wave"),
                      dict(name="Minu", hair="frange", hc="rose", acc="bonnet", role="maknae",
                           outfit="sweat", oc="#B9A6F2", skin=1, sig="big_heart"),
                  ]),
    "lumi": dict(name="LUMI", fandom="Lumies", hue=330, stick="coeur",
                 greet="Un, deux, trois... on est LUMI !", chant="LU-MI ! LU-MI !",
                 members=[
                     dict(name="Aerin", hair="carre", hc="noir", acc="serre_tete", role="leader",
                          outfit="crop", oc="#FF7FB2", skin=1, sig="point"),
                     dict(name="Nari", hair="long", hc="lavande", acc="etoile", role="chant",
                          outfit="robe", oc="#FFFFFF", skin=0, sig="heart"),
                     dict(name="Dain", hair="couettes", hc="rouge", acc="piercing", role="rap",
                          outfit="veste", oc="#22222A", skin=2, sig="peace"),
                     dict(name="Chaeon", hair="queue", hc="blond", acc="casquette", role="danse",
                          outfit="crop", oc="#7FE0C4", skin=3, sig="arms_up"),
                     dict(name="Yul", hair="chignon", hc="menthe", acc="noeud", role="maknae",
                          outfit="robe", oc="#FFB38A", skin=0, sig="big_heart"),
                 ]),
}
FAN_LINES = dict(
    notice=["C'est... C'est %s ?!", "NON. C'EST %s !!", "Je rêve ou c'est %s ?!"],
    scream=["KYAAAA !!", "AAAAAH !!", "OMG !!", "OPPAAA !!", "JE MEURS !!"],
    rush=["Attendez-moi !!", "Poussez-vous !", "Mon lightstick !!"],
    photo=["Regarde par ici !!", "Juste une photo !!", "Souriiis !"],
    photo_after=["TROP BEAU !!", "Elle est floue... ENCORE !", "Fond d'écran à vie."],
    selfie=["Un selfie ?? S'il te plaît !!", "On fait un selfie ?!"],
    selfie_after=["J'ai un selfie avec %s !!!", "Personne va me croire !!", "Je l'encadre."],
    autograph=["Tu peux signer ici ?!", "Un autographe !! S'il te plaît !"],
    autograph_after=["Je me lave plus jamais les mains.", "Il a signé !!! IL A SIGNÉ !!", "Trésor national."],
    heart=["IL M'A FAIT UN CŒUR !!", "C'était pour moi ?!", "Mon cœur..."],
    faint=["Il m'a... regardé...", "*s'évanouit*", "Trop... de... charisme..."],
    wake=["Hein ? J'ai rêvé ?", "Où je suis ?", "C'était pas un rêve ?!"],
    fan_help=["Réveille-toi !!", "Respire !!", "Tiens bon !"],
    cry=["Je vais pleurer...", "*sanglote de joie*", "C'est le plus beau jour de ma vie."],
    shy=["...b-bonjour...", "*se cache*", "J'ose pas..."],
    gift=["C'est pour toi !!", "Je l'ai fait moi-même !"],
    bye=["NOOOON restez !!", "Revenez vite !!", "On vous aime !!"],
)
IDOL_LINES = dict(
    hello=["Bonjour !", "Coucou !", "Merci d'être là !"],
    photo=["Cheese !", "Comme ça ?", "Encore une ?"],
    selfie=["Oh, bien sûr !", "Viens !", "Tu es où sur la photo ?"],
    sign=["Voilà !", "Avec un petit cœur.", "Pour toi !"],
    heart=["Saranghae !", "Pour toi !", "♥"],
    comfort=["Ne pleure pas !", "Merci, vraiment.", "Hé, ça va aller !"],
    shy=["Salut toi !", "N'aie pas peur !"],
    gift=["Merci !! Je le garde !", "Trop mignon !!"],
    bye=["Merci ! On vous aime !", "À bientôt !", "Prenez soin de vous !"],
)

# Humeurs : fréquence des duos, délai mini entre deux bulles spontanées (s),
# délai mini entre deux batailles automatiques (s, None = jamais)
MODES = {
    "calme":  dict(duo=0.12, bubble=240, war=None, label="Calme"),
    "normal": dict(duo=0.30, bubble=90, war=900, label="Normal"),
    "chaos":  dict(duo=0.55, bubble=25, war=120, label="Chaotique"),
}
DEFAULT_MODE = "normal"

SKINS = {
    "Hybris": dict(body=(235, 0.46, 0.44), belly=(235, 0.50, 0.58),
                   horn="#F6DB8C", horn_line="#C99F45", tail_tip="heart",
                   horn_shape="crescent", blush="#FF9ECF",
                   iris_top="#141338", iris_bot="#58E1FF", mark="H"),
    "Iblis":  dict(body=(354, 0.74, 0.63), belly=(354, 0.85, 0.75),
                   horn="#FFE6D8", horn_line="#D99585", tail_tip="drop",
                   horn_shape="bump", blush="#E0305F",
                   iris_top="#3D0B1C", iris_bot="#FFB547", mark="13"),
}
INK = QColor("#241733")      # traits du visage (jamais du noir pur)

ITEMS = {
    "blaster":          dict(label="Blaster Nerf", kind="weapon", uses=6, w=3),
    "marteau":          dict(label="Marteau-jouet", kind="weapon", uses=8, w=3),
    "bouclier":         dict(label="BlueShield", kind="shield", w=2),
    "potion_sang":      dict(label="Potion de sang", kind="potion", w=3),
    "potion_vitesse":   dict(label="Potion de vitesse", kind="potion", w=2),
    "potion_invisible": dict(label="Potion d'invisibilité", kind="potion", w=2),
    "trottinette":      dict(label="Trottinette", kind="vehicle", w=2),
    "banane":           dict(label="Peau de banane", kind="trap", w=2),
    "fumigene":         dict(label="Fumigène", kind="smoke", w=2),
    "potion_vol":       dict(label="Potion de vol", kind="potion", w=2),
    "jetpack":          dict(label="Jetpack", kind="flight", w=1.5),
    "ballon":           dict(label="Ballon", kind="flight", w=1.5),
    "fusee":            dict(label="Fusée", kind="flight", w=1.5),
}
WEAPONS = ("blaster", "marteau")
FLIGHT_ITEMS = ("jetpack", "ballon", "fusee", "potion_vol")
# vol : durée (s), vitesse horizontale, vitesse verticale, altitude (min, max) au-dessus du sol
FLIGHT = {
    "potion_vol": (14.0, 250.0, 170.0, (170, 300)),
    "jetpack":    (12.0, 330.0, 220.0, (140, 260)),
    "ballon":     (22.0, 70.0, 55.0, (330, 430)),
    "fusee":      (2.4, 640.0, 200.0, (90, 140)),
}
FLY_LINES = {"potion_vol": "Je vole !", "jetpack": "Jetpack !", "ballon": "Wiii !", "fusee": "3, 2, 1... !"}

SOLO_LINES = {
    "Hybris": ["whoami → H13ris", "Tout est vert sur le SIEM.", "Pause café ?",
               "T'as bu de l'eau ?", "Encore un faux positif...",
               "Je veille sur tes ports <3", "Cet écran est à moi."],
    "Iblis": ["sudo make me a sandwich", "Qui a ouvert le port 445 ?",
              "Ce ticket peut attendre.", "Windows Update... encore ?",
              "ping... pong !", "On fait un CTF ?", "J'ai vu un coffre par là."],
}
PET_LINES = ["Hihi !", "Ça chatouille !", "Encore !", "Coucou !",
             "Accès autorisé <3", "Ronron..."]
DUO_CHATS = [("T'as vu cette alerte ?", "Faux positif. Encore."),
             ("On pentest quoi ?", "Le frigo."),
             ("CTF ce soir ?", "Toujours !"),
             ("git push --force ?", "Jamais un vendredi."),
             ("Qui a le plus de flags ?", "Moi. Évidemment."),
             ("Tu dors ?", "Je veille. Nuance.")]
DEBATES = [
    ["Tabs ou espaces ?", "Espaces. Évidemment.", "Hérétique.", "Dit celui qui code sur Notepad."],
    ["Le meilleur port ?", "22.", "443, voyons.", "...445 ?", "NON."],
    ["On patch quand ?", "Vendredi 17h.", "T'es un monstre.", "Un démon, nuance."],
    ["Nmap ou masscan ?", "Les deux.", "Réponse de politicien.", "Réponse de SOC."],
]
ATTACKS = {  # tir direct, salve en cloche, charge (-> nuage de bagarre)
    "Hybris": ("Ping de neige !", "DDoS de flocons !", "Brute-câlin !"),
    "Iblis": ("Oreiller-ball !", "Botnet d'oreillers !", "Ransom-bonk !"),
}
WAR_TAUNTS = {
    "Hybris": ["Ton firewall est en carton !", "Scan terminé. Cible molle.",
               "Patch-toi d'abord !", "Je t'ai dans mes logs !"],
    "Iblis": ["Même pas mal !", "Ton SOC dort ?", "Je vais te chiffrer !",
              "Viens, si t'es root !"],
}
WIN_LINES = {"Hybris": "Menace neutralisée !", "Iblis": "Root obtenu. GG !"}
HIT_WORDS = ["POF !", "BONK !", "PAF !", "BIM !"]
HUNT = dict(
    alert=["Intrusion détectée !", "Processus inconnu !", "Alerte rouge !"],
    ally=["Alliance !", "On les traque.", "Chasse ouverte."],
    search=["Où sont-ils ?", "Scan en cours...", "Ils se cachent.", "Je sens un intrus..."],
    found=["Là-bas !", "Cible acquise !", "Je les vois !", "Par ici !"],
    caught=["Neutralisé.", "kill -9 !", "Fin de processus.", "Un de moins."],
    win=["Mission accomplie !", "Bureau sécurisé !", "Menace éradiquée !"],
    respawn=["Respawn !", "Je reviens !", "Rollback réussi."],
    prey_alert=["On est repérés !", "Cours !!", "La Garde !", "Sépare-toi !"],
    prey_flee=["Pas par là !", "Plus vite !", "Ils arrivent !", "Trouve un coffre !"],
    prey_hide=["Chut...", "Ils me voient pas.", "Planqué.", "..."],
    prey_dead=["Argh... SIGKILL", "Process terminé...", "Nooon !", "x_x"],
    prey_panic=["NOOON !", "Je te vengerai !", "Pas lui !"],
    prey_fight=["Prends ça !", "Reculez !", "J'ai un blaster !"],
    loot=["Un coffre !", "Jackpot !", "Oh, un cadeau !", "À moi !"],
    fly_taunt=["Descends de là !", "Tricheur !", "Reviens au sol !"],
    brave=["Surprise !", "Approche, pour voir.", "J'ai plus peur !", "C'est mon tour !"],
    bomb=["Bombardement !", "Cadeau du ciel !", "Oups, ma main a glissé."],
    dash=["Poussez-vous !", "Vroooum !", "Trop lent !"],
    empty=["Zut, vide !", "Trop tard...", "Raté."],
    tunnel=["Je creuse !", "Tunnel !", "À plus !"],
)


# --------------------------------------------------------------------------- #
# Petits outils
# --------------------------------------------------------------------------- #
def rnd(a, b):
    return random.uniform(a, b)


def hsl(h, s, l):
    return QColor.fromHslF((h % 360) / 360, s, l)


def mkpen(color, width):
    pen = QPen(QColor(color))
    pen.setWidthF(width)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    return pen


NO_PEN = Qt.PenStyle.NoPen
NO_BRUSH = Qt.BrushStyle.NoBrush


def dist2(ax, ay, bx, by):
    """Distance « de bureau » : la hauteur compte moins que la largeur."""
    return math.hypot(ax - bx, (ay - by) * 0.6)


def heart_path(x, y, s):
    p = QPainterPath(QPointF(x, y + s * 0.95))
    p.cubicTo(QPointF(x - s * 1.5, y - s * 0.05), QPointF(x - s * 0.7, y - s * 1.25),
              QPointF(x, y - s * 0.4))
    p.cubicTo(QPointF(x + s * 0.7, y - s * 1.25), QPointF(x + s * 1.5, y - s * 0.05),
              QPointF(x, y + s * 0.95))
    return p


def star_poly(x, y, r1, r2, n=5, rot=0.0):
    pts = []
    for k in range(n * 2):
        r = r1 if k % 2 == 0 else r2
        a = k * math.pi / n - math.pi / 2 + rot
        pts.append(QPointF(x + r * math.cos(a), y + r * math.sin(a)))
    return QPolygonF(pts)


def outlined_text(p, rect, text, fill, outline=QColor(40, 20, 50), w=1):
    p.setPen(outline)
    for dx, dy in ((-w, 0), (w, 0), (0, -w), (0, w), (-w, -w), (w, w)):
        p.drawText(rect.translated(dx, dy), Qt.AlignmentFlag.AlignCenter, text)
    p.setPen(fill)
    p.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)


def roll_item():
    keys = list(ITEMS)
    return random.choices(keys, weights=[ITEMS[k]["w"] for k in keys])[0]


def draw_item_icon(p, kind, x, y, s=1.0, rot=0.0):
    """Icône d'objet (≈ 26 px), utilisée sur les pets, les coffres, les loots."""
    p.save()
    p.translate(x, y)
    p.rotate(rot)
    p.scale(s, s)
    if kind == "blaster":
        p.setPen(mkpen(QColor("#B85A1C"), 1.3))
        p.setBrush(QColor("#FF8A3D"))
        p.drawRoundedRect(QRectF(-12, -6, 22, 9), 3, 3)       # corps
        p.drawRoundedRect(QRectF(-9, 2, 6, 9), 2, 2)          # poignée
        p.setBrush(QColor("#3B6CFF"))
        p.drawRoundedRect(QRectF(8, -5, 7, 7), 2, 2)          # canon bleu
        p.setBrush(QColor("#FFD23F"))
        p.drawEllipse(QPointF(-3, -1.5), 2.2, 2.2)
    elif kind == "marteau":
        p.setPen(mkpen(QColor("#8A5A2B"), 1.3))
        p.setBrush(QColor("#C98A4B"))
        p.drawRoundedRect(QRectF(-2.5, -6, 5, 22), 2, 2)      # manche
        p.setPen(mkpen(QColor("#C9971F"), 1.3))
        p.setBrush(QColor("#FFD23F"))
        p.drawRoundedRect(QRectF(-12, -14, 24, 11), 4, 4)     # tête
        p.setPen(NO_PEN)
        p.setBrush(QColor(255, 255, 255, 120))
        p.drawEllipse(QPointF(-6, -11), 3, 1.6)
    elif kind == "bouclier":
        sh = QPainterPath(QPointF(0, -14))
        sh.cubicTo(QPointF(13, -14), QPointF(13, -8), QPointF(12, 0))
        sh.cubicTo(QPointF(11, 8), QPointF(5, 13), QPointF(0, 15))
        sh.cubicTo(QPointF(-5, 13), QPointF(-11, 8), QPointF(-12, 0))
        sh.cubicTo(QPointF(-13, -8), QPointF(-13, -14), QPointF(0, -14))
        p.setPen(mkpen(QColor("#1F3FA8"), 1.4))
        p.setBrush(QColor("#4A90FF"))
        p.drawPath(sh)
        f = QFont("Segoe UI", 8)
        f.setBold(True)
        p.setFont(f)
        p.setPen(QColor("#FFFFFF"))
        p.drawText(QRectF(-10, -9, 20, 16), Qt.AlignmentFlag.AlignCenter, "H")
    elif kind.startswith("potion"):
        liq = {"potion_sang": "#E0304A", "potion_vitesse": "#3DDC84",
               "potion_invisible": "#B39DFF", "potion_vol": "#7FD3FF"}[kind]
        fl = QPainterPath(QPointF(-3, -13))
        fl.lineTo(QPointF(3, -13))
        fl.lineTo(QPointF(3, -6))
        fl.cubicTo(QPointF(11, -2), QPointF(11, 12), QPointF(0, 13))
        fl.cubicTo(QPointF(-11, 12), QPointF(-11, -2), QPointF(-3, -6))
        fl.closeSubpath()
        p.setPen(mkpen(QColor("#6A5A80"), 1.3))
        p.setBrush(QColor(235, 240, 255, 200))
        p.drawPath(fl)
        p.save()
        p.setClipPath(fl)
        p.setPen(NO_PEN)
        p.setBrush(QColor(liq))
        p.drawRect(QRectF(-12, 1, 24, 14))
        p.setBrush(QColor(255, 255, 255, 110))
        p.drawEllipse(QPointF(-4, 6), 2, 3)
        p.restore()
        p.setPen(NO_PEN)
        p.setBrush(QColor("#C98A4B"))
        p.drawRoundedRect(QRectF(-4, -16, 8, 4), 1.5, 1.5)   # bouchon
    elif kind == "trottinette":
        p.setPen(mkpen(QColor("#1F7A99"), 1.4))
        p.setBrush(QColor("#5EE6FF"))
        p.drawRoundedRect(QRectF(-14, 2, 22, 4), 2, 2)        # plateau
        p.drawLine(QPointF(8, 4), QPointF(14, -12))            # guidon
        p.drawLine(QPointF(10, -12), QPointF(18, -12))
        p.setBrush(QColor("#2B2B3A"))
        p.drawEllipse(QPointF(-11, 8), 4, 4)
        p.drawEllipse(QPointF(9, 8), 4, 4)
    elif kind == "banane":
        b = QPainterPath(QPointF(-12, -2))
        b.cubicTo(QPointF(-8, 10), QPointF(8, 10), QPointF(13, -4))
        b.cubicTo(QPointF(8, 4), QPointF(-6, 5), QPointF(-12, -2))
        p.setPen(mkpen(QColor("#B39A1F"), 1.3))
        p.setBrush(QColor("#FFE24A"))
        p.drawPath(b)
        p.setPen(NO_PEN)
        p.setBrush(QColor("#6B4A1F"))
        p.drawEllipse(QPointF(12, -4), 1.6, 1.6)
    elif kind == "fumigene":
        p.setPen(mkpen(QColor("#4E5468"), 1.3))
        p.setBrush(QColor("#9AA0B4"))
        p.drawRoundedRect(QRectF(-8, -8, 16, 18), 5, 5)
        p.setPen(mkpen(QColor("#6B4A1F"), 1.5))
        p.drawLine(QPointF(0, -8), QPointF(4, -14))
        p.setPen(NO_PEN)
        p.setBrush(QColor("#FF8A3D"))
        p.drawEllipse(QPointF(4.5, -14.5), 2.2, 2.2)
    elif kind == "anneau":
        p.setPen(mkpen(QColor("#C9971F"), 2.6))
        p.setBrush(NO_BRUSH)
        p.drawEllipse(QPointF(0, 2), 8, 8)
        p.setPen(NO_PEN)
        p.setBrush(QColor("#FF7FA0"))
        p.drawPolygon(QPolygonF([QPointF(0, -12), QPointF(6, -6), QPointF(0, -2), QPointF(-6, -6)]))
        p.setBrush(QColor(255, 255, 255, 170))
        p.drawEllipse(QPointF(-2, -8), 1.6, 1.6)
    elif kind == "fleur":
        p.setPen(mkpen(QColor("#2F8F5B"), 2))
        p.drawLine(QPointF(0, 14), QPointF(0, -2))
        p.setPen(NO_PEN)
        p.setBrush(QColor("#3DDC84"))
        p.drawEllipse(QPointF(4, 6), 4, 2)
        for i in range(5):
            a = i * 2 * math.pi / 5
            p.setBrush(QColor("#FF7FA0"))
            p.drawEllipse(QPointF(math.cos(a) * 6, -4 + math.sin(a) * 6), 4, 4)
        p.setBrush(QColor("#FFD23F"))
        p.drawEllipse(QPointF(0, -4), 3, 3)
    elif kind == "biscuit":
        p.setPen(mkpen(QColor("#8A5A2B"), 1.2))
        p.setBrush(QColor("#E0B070"))
        p.drawEllipse(QPointF(0, 0), 10, 10)
        p.setPen(NO_PEN)
        p.setBrush(QColor("#5A3A1F"))
        for dx, dy in ((-4, -3), (3, -4), (1, 3), (-3, 4), (5, 1)):
            p.drawEllipse(QPointF(dx, dy), 1.6, 1.6)
    elif kind == "jetpack":
        p.setPen(mkpen(QColor("#4E5468"), 1.3))
        p.setBrush(QColor("#B9BFD2"))
        p.drawRoundedRect(QRectF(-9, -12, 18, 22), 5, 5)
        p.setBrush(QColor("#6F7590"))
        p.drawRoundedRect(QRectF(-8, 8, 6, 5), 1.5, 1.5)
        p.drawRoundedRect(QRectF(2, 8, 6, 5), 1.5, 1.5)
        p.setPen(NO_PEN)
        p.setBrush(QColor("#FF8A3D"))
        p.drawPolygon(QPolygonF([QPointF(-7, 13), QPointF(-3, 13), QPointF(-5, 19)]))
        p.drawPolygon(QPolygonF([QPointF(3, 13), QPointF(7, 13), QPointF(5, 19)]))
        p.setBrush(QColor("#FF5C8A"))
        p.drawEllipse(QPointF(0, -4), 3, 3)
    elif kind == "ballon":
        p.setPen(mkpen(QColor("#B0202F"), 1.2))
        p.setBrush(QColor("#FF5C6C"))
        p.drawEllipse(QPointF(0, -6), 10, 12)
        p.setPen(NO_PEN)
        p.setBrush(QColor(255, 255, 255, 150))
        p.drawEllipse(QPointF(-4, -10), 2.5, 3.5)
        p.setPen(mkpen(QColor("#B0202F"), 1.2))
        p.drawPolygon(QPolygonF([QPointF(-2, 6), QPointF(2, 6), QPointF(0, 8)]))
        p.setPen(mkpen(QColor("#6B4A1F"), 1.0))
        p.drawLine(QPointF(0, 8), QPointF(2, 16))
    elif kind == "fusee":
        p.setPen(mkpen(QColor("#5A5F75"), 1.2))
        p.setBrush(QColor("#F4F4F8"))
        p.drawRoundedRect(QRectF(-5, -10, 10, 20), 5, 5)
        p.setBrush(QColor("#E0304A"))
        p.drawPolygon(QPolygonF([QPointF(-5, -8), QPointF(0, -16), QPointF(5, -8)]))
        p.drawPolygon(QPolygonF([QPointF(-5, 6), QPointF(-10, 12), QPointF(-5, 10)]))
        p.drawPolygon(QPolygonF([QPointF(5, 6), QPointF(10, 12), QPointF(5, 10)]))
        p.setPen(NO_PEN)
        p.setBrush(QColor("#5EE6FF"))
        p.drawEllipse(QPointF(0, -3), 2.5, 2.5)
        p.setBrush(QColor("#FF8A3D"))
        p.drawPolygon(QPolygonF([QPointF(-3, 10), QPointF(3, 10), QPointF(0, 17)]))
    elif kind == "telephone":
        p.setPen(mkpen(QColor("#2A2D3A"), 1.4))
        p.setBrush(QColor("#3A3F52"))
        p.drawRoundedRect(QRectF(-6, -11, 12, 22), 3, 3)
        p.setPen(NO_PEN)
        p.setBrush(QColor("#9FD8FF"))
        p.drawRoundedRect(QRectF(-4.5, -8.5, 9, 15), 1.5, 1.5)
    elif kind == "carnet":
        p.setPen(mkpen(QColor("#8A3B5E"), 1.3))
        p.setBrush(QColor("#FF9ECF"))
        p.drawRoundedRect(QRectF(-9, -11, 18, 22), 2, 2)
        p.setPen(mkpen(QColor("#FFFFFF"), 1.2))
        p.drawLine(QPointF(-5, -3), QPointF(5, -3))
        p.drawLine(QPointF(-5, 2), QPointF(3, 2))
        p.setPen(NO_PEN)
        p.setBrush(QColor("#FFFFFF"))
        p.drawPath(heart_path(0, -7, 4))
    elif kind == "peluche":
        p.setPen(mkpen(QColor("#7A4E24"), 1.2))
        p.setBrush(QColor("#C98A4B"))
        for ex in (-7, 7):
            p.drawEllipse(QPointF(ex, -9), 4, 4)
        p.drawEllipse(QPointF(0, 0), 10, 10)
        p.setPen(NO_PEN)
        p.setBrush(QColor("#2A1A10"))
        for ex in (-3.5, 3.5):
            p.drawEllipse(QPointF(ex, -1), 1.3, 1.3)
        p.setBrush(QColor("#FF7FA0"))
        p.drawEllipse(QPointF(0, 3), 2.2, 1.5)
    p.restore()


# --------------------------------------------------------------------------- #
# Démarrage automatique (Windows : clé Run de l'utilisateur, pas besoin d'admin)
# --------------------------------------------------------------------------- #
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN_NAME = "H13risPets"


def autostart_command():
    if getattr(sys, "frozen", False):                 # exe PyInstaller
        return '"%s"' % sys.executable
    exe = sys.executable
    pyw = os.path.join(os.path.dirname(exe), "pythonw.exe")
    if os.path.exists(pyw):                            # pas de console au démarrage
        exe = pyw
    return '"%s" "%s"' % (exe, os.path.abspath(__file__))


def autostart_get():
    if sys.platform != "win32":
        return False
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as k:
            winreg.QueryValueEx(k, RUN_NAME)
            return True
    except OSError:
        return False


def autostart_set(on):
    if sys.platform != "win32":
        return False
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as k:
            if on:
                winreg.SetValueEx(k, RUN_NAME, 0, winreg.REG_SZ, autostart_command())
            else:
                try:
                    winreg.DeleteValue(k, RUN_NAME)
                except FileNotFoundError:
                    pass
        return True
    except OSError:
        return False


def foreground_is_fullscreen():
    """Windows : vrai si l'application au premier plan occupe tout l'écran."""
    if sys.platform != "win32":
        return False
    try:
        import ctypes
        from ctypes import wintypes as wt
        u = ctypes.windll.user32
        hwnd = u.GetForegroundWindow()
        if not hwnd:
            return False
        pid = wt.DWORD()
        u.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value == os.getpid():
            return False
        buf = ctypes.create_unicode_buffer(64)
        u.GetClassNameW(hwnd, buf, 64)
        if buf.value in ("WorkerW", "Progman", "Shell_TrayWnd"):
            return False
        r = wt.RECT()
        u.GetWindowRect(hwnd, ctypes.byref(r))

        class MONITORINFO(ctypes.Structure):
            _fields_ = [("cbSize", wt.DWORD), ("rcMonitor", wt.RECT),
                        ("rcWork", wt.RECT), ("dwFlags", wt.DWORD)]
        mi = MONITORINFO()
        mi.cbSize = ctypes.sizeof(mi)
        u.GetMonitorInfoW(u.MonitorFromWindow(hwnd, 2), ctypes.byref(mi))
        m = mi.rcMonitor
        return r.left <= m.left and r.top <= m.top and r.right >= m.right and r.bottom >= m.bottom
    except Exception:
        return False


# --------------------------------------------------------------------------- #
# Terrain : chaque écran est un segment de sol (son bord bas, sans la barre
# des tâches). Les pets marchent d'un segment à l'autre, tombent sur un sol
# plus bas, sautent sur un sol plus haut (≤ MAX_HOP), et creusent un tunnel
# pour rejoindre un segment inaccessible à pied.
# --------------------------------------------------------------------------- #
class Seg:
    __slots__ = ("x0", "x1", "yb", "top", "name", "idx")

    def __init__(self, x0, x1, yb, top, name="", idx=0):
        self.x0, self.x1, self.yb, self.top, self.name, self.idx = x0, x1, yb, top, name, idx

    @property
    def width(self):
        return self.x1 - self.x0

    def contains(self, cx, m=0):
        return self.x0 + m <= cx <= self.x1 - m

    def __repr__(self):
        return "Seg(%d..%d, sol %d)" % (self.x0, self.x1, self.yb)


class Terrain:
    MARGIN = 36              # le corps (±34 px) reste sur l'écran

    def __init__(self, fake=None):
        self.segs = []
        self.reach = {}
        self.refresh(fake)

    def refresh(self, fake=None):
        segs = []
        if fake:
            segs = list(fake)
        else:
            prim = QGuiApplication.primaryScreen()
            screens = [prim] + [s for s in QGuiApplication.screens() if s is not prim] if prim else []
            for s in screens:
                g = s.availableGeometry()
                segs.append(Seg(g.x(), g.x() + g.width(), g.y() + g.height(), g.y(), s.name()))
        if not segs:
            segs = [Seg(0, 1920, 1040, 0, "?")]
        for i, s in enumerate(segs):
            s.idx = i
        self.segs = segs
        self.x0 = min(s.x0 for s in segs)
        self.x1 = max(s.x1 for s in segs)
        self.max_yb = max(s.yb for s in segs)
        self.min_top = min(s.top for s in segs)
        # accessibilité à pied (chute ou saut vers un voisin horizontal)
        adj = {s.idx: set() for s in segs}
        for a in segs:
            for b in segs:
                if a is b:
                    continue
                touching = abs(a.x1 - b.x0) < 12 or abs(b.x1 - a.x0) < 12
                if touching and (b.yb >= a.yb or a.yb - b.yb <= MAX_HOP):
                    adj[a.idx].add(b.idx)
        self.reach = {}
        for a in segs:
            seen, stack = {a.idx}, [a.idx]
            while stack:
                cur = stack.pop()
                for nb in adj[cur]:
                    if nb not in seen:
                        seen.add(nb)
                        stack.append(nb)
            self.reach[a.idx] = seen

    def signature(self):
        return tuple((s.x0, s.x1, s.yb) for s in self.segs)

    # ---- requêtes ----
    def ground_at(self, cx, fy, tol=3):
        """Sol le plus proche sous (ou au niveau de) des pieds en (cx, fy)."""
        best = None
        for s in self.segs:
            if s.x0 <= cx <= s.x1 and s.yb >= fy - tol and (best is None or s.yb < best.yb):
                best = s
        return best

    def ledge_at(self, cx, fy, tol=3):
        """Sol plus haut, atteignable d'un saut, contenant cx."""
        best = None
        for s in self.segs:
            if s.x0 <= cx <= s.x1 and fy - MAX_HOP <= s.yb < fy - tol and (best is None or s.yb > best.yb):
                best = s
        return best

    def seg_near(self, cx, fy):
        """Segment contenant cx dont le sol est le plus proche de fy (sinon le plus proche)."""
        best, bd = None, None
        for s in self.segs:
            dx = 0 if s.x0 <= cx <= s.x1 else min(abs(cx - s.x0), abs(cx - s.x1))
            d = dx * 2 + abs(s.yb - fy)
            if bd is None or d < bd:
                best, bd = s, d
        return best

    def sky(self, cx, fy):
        """(plafond, sol) de l'écran qui contient le point (cx, fy), pour voler."""
        cands = [s for s in self.segs if s.x0 <= cx <= s.x1]
        inside = [s for s in cands if s.top <= fy <= s.yb]
        if inside:
            s = min(inside, key=lambda s: s.yb)
            return s.top, s.yb
        if cands:
            s = min(cands, key=lambda s: min(abs(s.top - fy), abs(s.yb - fy)))
            return s.top, s.yb
        return self.min_top, self.max_yb

    def hunter_free_seg(self, threats, exclude=None):
        """Un écran sans menace (pondéré par l'éloignement), ou None."""
        pool = []
        for s in self.segs:
            if s is exclude:
                continue
            dmin = min((dist2((s.x0 + s.x1) / 2, s.yb, tx, ty) for tx, ty in threats), default=9999)
            if all(not (s.x0 <= tx <= s.x1 and abs(ty - s.yb) < 60) for tx, ty in threats):
                pool.append((s, 200 + dmin))
        if not pool:
            return None
        return random.choices([s for s, _ in pool], weights=[wt for _, wt in pool])[0]

    def reachable(self, a, b):
        if a is None or b is None:
            return True
        return b.idx in self.reach.get(a.idx, {a.idx})

    def clamp_x(self, cx, seg=None):
        if seg is not None:
            return max(seg.x0 + self.MARGIN, min(seg.x1 - self.MARGIN, cx))
        return max(self.x0 + self.MARGIN, min(self.x1 - self.MARGIN, cx))

    def random_seg(self, exclude=None):
        pool = [s for s in self.segs if s is not exclude] or self.segs
        return random.choices(pool, weights=[max(200, s.width) for s in pool])[0]

    def random_x(self, seg=None, margin=90):
        seg = seg or self.random_seg()
        m = min(margin, seg.width / 3)
        return rnd(seg.x0 + m, seg.x1 - m)

    def room(self, seg, cx, direction):
        """Espace disponible à pied dans une direction avant un mur."""
        if seg is None:
            return 0
        edge = seg.x1 - self.MARGIN if direction > 0 else seg.x0 + self.MARGIN
        room = abs(edge - cx)
        nb = self.ground_at(edge + direction * 20, seg.yb) or self.ledge_at(edge + direction * 20, seg.yb)
        if nb is not None and nb is not seg:
            room += nb.width * 0.8
        return room

    def farthest_point(self, threats, prefer=None):
        """Point du terrain le plus éloigné des menaces [(x, y), ...]."""
        best, bs = None, -1
        for s in self.segs:
            n = max(2, int(s.width / 160))
            m = min(150, s.width / 4)
            for i in range(n + 1):
                x = s.x0 + m + (s.width - 2 * m) * i / n
                score = min((dist2(x, s.yb, tx, ty) for tx, ty in threats), default=9999)
                if prefer is not None and s is prefer:
                    score += 120                      # léger bonus : rester à pied
                if score > bs:
                    best, bs = (x, s), score
        return best


# --------------------------------------------------------------------------- #
# Un pet
# --------------------------------------------------------------------------- #
class Pet(QWidget):
    def __init__(self, name, world, skin=None, size=1.0):
        super().__init__(None, Qt.WindowType.FramelessWindowHint
                         | Qt.WindowType.WindowStaysOnTopHint
                         | Qt.WindowType.Tool
                         | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFixedSize(W, H)
        self.setWindowTitle(name)

        self.name, self.world = name, world
        sk = skin or SKINS[name]
        self.sk = sk
        self.size = size
        self.is_kid = False
        self.eye_k = 1.0
        self.cry_t = 0.0
        self.accessory = None
        self.stage = "adulte"                   # les fondateurs sont des adultes (immortels)
        # vie de famille (fondateurs compris)
        self.hunger, self.social = 80.0, 80.0
        self.persona = []
        self.duty = None
        self.work_t = self.study_t = 0.0
        self.helping = None
        self.hw_day = None
        self.fam_cd = 0.0
        # fan meeting : objet de fan tenu en main (lightstick, téléphone, selfie)
        self.fan_prop, self.fan_hue, self.fan_stick = None, 300.0, "rond"
        self.is_idol = False
        self.c_body = hsl(*sk["body"])
        self.c_light = self.c_body.lighter(128)
        self.c_shade = self.c_body.darker(118)
        self.c_line = self.c_body.darker(165)
        self.c_belly = hsl(*sk["belly"])
        self.c_horn, self.c_horn_line = QColor(sk["horn"]), QColor(sk["horn_line"])
        self.c_blush = QColor(sk["blush"])
        self.c_iris_top, self.c_iris_bot = QColor(sk["iris_top"]), QColor(sk["iris_bot"])
        self.partner = None

        # physique / états : fall, drag, idle, walk, sleep, ko, tunnel, ride, ghost, gone
        self.x = self.y = self.vx = self.vy = 0.0
        self.facing = 1
        self.state, self.timer = "fall", 0.0
        self.target_x, self.speed = 0.0, WALK_SPEED
        self.airborne = False
        self.busy = False
        self.seg = None
        self.blocked = False
        self.vel = 0.0
        self._last_cx = None
        # anim
        self.t = rnd(0, 10)
        self.breath_T = rnd(3.0, 4.2)
        self.walk_phase = 0.0
        self.blink, self.next_blink, self.double_blink = 0.0, rnd(2, 5), False
        self.squash = 1.0
        self.look = QPointF(0, 0)
        self.tilt = self.tilt_target = self.tilt_hold = 0.0
        self.tail_a = self.tail_v = 0.0
        self.arm_up = self.hugging = False
        self.spark = 0.0
        self.expr, self.expr_t = None, 0.0     # happy / wink / pout / surprised
        self.dizzy = 0.0
        self.bubble, self.bubble_t, self.talk_t = None, 0.0, 0.0
        self.land_msg = None
        self.particles = []
        # bataille / chasse
        self.hp, self.hp_show = 100.0, 0.0
        self.hurt = self.attack_t = 0.0
        self.mood = None                        # war / hunt / scared
        self.role = None                        # hunter / prey / None
        self.pending_ko = False
        self.floaters = []
        self.cloud_t = 0.0
        self.shake = 0.0
        # humeur
        self.stamina = 100.0
        self.energy = rnd(70, 100)
        self.fun = rnd(50, 90)
        # objets
        self.item, self.ammo = None, 0
        self.shield = 0
        self.veh_t = self.speed_t = self.invis_t = self.smoke_t = 0.0
        self.show_item_t = 0.0
        self.show_item = None
        self.camo = False
        self.still_t = 0.0
        self.opening, self.open_phase = None, None
        self.open_t = self.loot_wait = 0.0
        # tunnel / fantôme / portage
        self.tunnel = None
        self.tunnel_cd = 0.0
        self.fly_t, self.fly_kind = 0.0, None
        self.fly_speed = self.fly_vspeed = self.fly_alt = 0.0
        self.was_flying = False
        self.ghost_t = 0.0
        self.gone = False
        self.ride_on = None
        self.rider = None
        self.ai = {}
        # souris
        self.drag_off = None
        self.press_pos = None
        self.moved = False
        self.drag_hist = []
        self.clicks = []

    # ---------- helpers ----------
    def cx(self):
        return self.x + W / 2

    def feet(self):
        return self.y + GROUND

    def grounded(self):
        return (not self.airborne and self.fly_t <= 0
                and self.state not in ("fall", "drag", "tunnel", "ghost", "gone", "ride"))

    def flying(self):
        return self.fly_t > 0 and self.state in ("idle", "walk")

    def active(self):
        return self.state not in ("ghost", "gone")

    def moving(self):
        return self.state in ("walk", "fall", "drag") or self.airborne or abs(self.vel) > 20

    def hidden(self):
        return (self.camo or self.invis_t > 0 or self.smoke_t > 0
                or self.state in ("tunnel", "ghost", "gone"))

    def alpha(self):
        if self.state == "ghost":
            return 0.55 * min(1.0, self.ghost_t / 1.0)
        if self.invis_t > 0:
            return 0.22
        if self.camo:
            return 0.42
        if self.smoke_t > 0:
            return 0.6
        return 1.0

    def say(self, text, dur=2.6):
        self.bubble, self.bubble_t = text, dur
        self.talk_t = min(1.2, dur * 0.45)

    def set_expr(self, e, dur):
        self.expr, self.expr_t = e, dur

    def go_idle(self, dur=None):
        self.state = "idle"
        self.timer = dur if dur is not None else rnd(1.5, 4)

    def walk_to(self, target_cx, speed=WALK_SPEED):
        if self.state not in ("idle", "walk"):
            return False
        self.target_x = self.world.terrain.clamp_x(target_cx)
        self.speed = speed
        self.state = "walk"
        self.blocked = False
        return True

    def go_to(self, x, seg=None, speed=WALK_SPEED):
        """Marche jusqu'à x (sur seg) ; creuse un tunnel si c'est inaccessible à pied."""
        T = self.world.terrain
        if self.state not in ("idle", "walk"):
            return False
        if self.fly_t > 0:                                   # en vol : tout droit
            return self.walk_to(x, speed)
        if seg is None:
            seg = T.seg_near(x, self.feet())
        cur = self.seg or T.ground_at(self.cx(), self.feet()) or T.seg_near(self.cx(), self.feet())
        if seg is not None and not T.reachable(cur, seg):
            if self.tunnel_cd <= 0 and not self.airborne:
                self.tunnel_to(T.clamp_x(x, seg), seg)
                return True
            return False
        return self.walk_to(T.clamp_x(x, seg) if seg else x, speed)

    def speed_now(self):
        m = 1.0
        if self.veh_t > 0:
            m *= 2.3
        if self.speed_t > 0:
            m *= 1.7
        if self.speed > 120 and self.stamina <= 0.5:
            m *= 0.55
        if self.rider is not None:
            m *= 0.8
        return self.speed * m

    def sleep(self, dur=None):
        if self.state not in ("idle", "walk") or self.fly_t > 0:
            return
        self.state, self.timer = "sleep", dur if dur else rnd(12, 30)

    def wake(self, msg="Hein ? Quoi ?"):
        if self.state == "sleep":
            self.go_idle(2)
            if msg:
                self.say(msg, 1.8)
            self.set_expr("surprised", 0.6)
            self.hop(260)

    def hop(self, v=380):
        if self.grounded():
            self.airborne, self.vy, self.squash = True, -v, 1.16
            self.tail_v -= 4

    def launch(self, vx, vy):
        if self.state in ("ghost", "gone", "tunnel"):
            return
        if self.ride_on is not None:
            self.dismount(False)
        self.state, self.vx, self.vy, self.airborne = "fall", vx, vy, False
        self.camo = False

    def face(self, other):
        self.facing = 1 if other.cx() > self.cx() else -1

    def emit(self, kind, n, x=None, y=None, spread=12):
        x = W / 2 if x is None else x
        y = GROUND - 50 if y is None else y
        for _ in range(n):
            pt = dict(k=kind, x=x + rnd(-spread, spread), y=y + rnd(-spread / 2, spread / 2),
                      age=0.0, s=rnd(0.8, 1.2), ph=rnd(0, 6))
            if kind == "heart":
                pt.update(vx=rnd(-25, 25), vy=rnd(-70, -45), life=rnd(1.0, 1.5))
            elif kind == "dust":
                pt.update(vx=rnd(-55, 55), vy=rnd(-18, -4), life=rnd(0.35, 0.55))
            elif kind == "smoke":
                pt.update(vx=rnd(-30, 30), vy=rnd(-40, -15), life=rnd(1.0, 1.6))
            elif kind == "sparkle":
                pt.update(vx=rnd(-90, 90), vy=rnd(-140, -40), life=rnd(0.4, 0.7))
            elif kind == "snow":
                pt.update(vx=rnd(-110, 110), vy=rnd(-160, -40), life=rnd(0.5, 0.8))
            elif kind == "feather":
                pt.update(vx=rnd(-60, 60), vy=rnd(-90, -30), life=rnd(0.9, 1.4))
            elif kind == "note":
                pt.update(vx=rnd(-20, 20), vy=rnd(-60, -35), life=rnd(1.0, 1.6))
            elif kind == "flash":
                pt.update(vx=0, vy=0, life=0.25)
            elif kind == "flame":
                pt.update(vx=rnd(-30, 30), vy=rnd(60, 140), life=rnd(0.25, 0.45))
            elif kind == "tear":
                pt.update(vx=rnd(-40, 40), vy=rnd(-60, -20), life=rnd(0.5, 0.8))
            self.particles.append(pt)

    def snapshot(self):
        """État publié aux autres instances."""
        return dict(n=self.name, x=round(self.cx()), y=round(self.feet()), vx=round(self.vel),
                    st=self.state, hp=round(self.hp), hid=self.hidden(), gone=self.gone,
                    f=self.facing, it=self.item, veh=self.veh_t > 0, sh=self.shield,
                    fly=self.fly_kind if self.fly_t > 0 else None)

    # ---------- objets ----------
    def give_item(self, kind):
        info = ITEMS.get(kind)
        if not info:
            return
        self.show_item_t = 1.6
        self.show_item = kind
        self.opening, self.open_phase = None, None
        self.emit("sparkle", 6, y=GROUND - 90)
        k = info["kind"]
        if k == "potion":
            if kind == "potion_sang" and self.hp < 95:
                self.drink(kind)
            elif kind == "potion_vitesse":
                self.drink(kind)
            elif kind in ("potion_invisible", "potion_vol") and self.role != "prey":
                self.drink(kind)
            else:
                self.item, self.ammo = kind, 1
        elif k == "flight":
            self.item, self.ammo = kind, 1
            self.say(info["label"] + " !", 1.4)
            if self.role is None:                            # en paix : pour le plaisir
                if self.state == "sleep":
                    self.wake("Oh ?")
                self.use_item()
        elif k == "shield":
            self.shield = 3
            self.say("BlueShield actif !", 1.8)
        elif k == "vehicle":
            self.veh_t = 28.0
            self.say("Vroum !", 1.5)
            self.set_expr("happy", 1.5)
        else:
            self.item, self.ammo = kind, info.get("uses", 1)
            self.say(info["label"] + " !", 1.6)

    def drink(self, kind):
        if kind == "potion_sang":
            self.hp = 100.0
            self.hp_show = 3
            self.emit("heart", 6, y=GROUND - 85)
            self.say("Miam, plein de vie !", 1.6)
        elif kind == "potion_vitesse":
            self.speed_t = 15.0
            self.emit("sparkle", 6, y=GROUND - 60)
            self.say("Turbo !", 1.4)
        elif kind == "potion_invisible":
            self.invis_t = 9.0
            self.say("Pouf, invisible.", 1.4)
        elif kind == "potion_vol":
            self.start_fly(kind)
        self.set_expr("happy", 1.4)

    def use_item(self):
        """Utilise l'objet en main (potion, banane, fumigène). Renvoie True si utilisé."""
        if not self.item:
            return False
        kind = self.item
        if kind.startswith("potion"):
            self.drink(kind)
        elif kind == "banane":
            self.world.drop_trap("banane", self.cx() - self.facing * 46, self.feet(), self)
            self.say("Glisse là-dessus !", 1.4)
        elif kind == "fumigene":
            self.smoke_t = 6.0
            self.emit("smoke", 14, y=GROUND - 40, spread=30)
            self.say("Fumigène !", 1.2)
        elif kind in FLIGHT_ITEMS:
            if not self.start_fly(kind):
                return False
        else:
            return False
        self.item, self.ammo = None, 0
        return True

    def consume_use(self):
        self.ammo -= 1
        if self.ammo <= 0:
            self.say("Plus de munitions !" if self.item == "blaster" else "Cassé...", 1.4)
            self.item, self.ammo = None, 0

    def slip(self):
        if not self.grounded():
            return
        self.launch(self.facing * 170, -340)
        self.dizzy = 2.2
        self.set_expr("surprised", 1.0)
        self.say("Ouups !", 1.4)

    # ---------- tunnel / fantôme / portage ----------
    def tunnel_to(self, x, seg):
        if self.state in ("ghost", "gone", "drag", "ride") or self.fly_t > 0:
            return
        if self.rider is not None:
            self.rider.dismount(True)
        self.state = "tunnel"
        self.tunnel = dict(ph="dig", t=0.0, x=x, seg=seg)
        self.tunnel_cd = 6.0
        self.camo = False
        self.airborne, self.vy = False, 0.0
        if random.random() < 0.5:
            self.say(random.choice(HUNT["tunnel"]), 1.1)

    def tunnel_tick(self, dt):
        tn = self.tunnel
        if tn is None:
            self.go_idle(0.3)
            return
        tn["t"] += dt
        if tn["ph"] == "dig":
            self.squash = 0.62
            if random.random() < dt * 12:
                self.emit("dust", 1, y=GROUND - 2, spread=22)
            if tn["t"] > 0.7:
                tn["ph"], tn["t"] = "under", 0.0
                self.hide()
        elif tn["ph"] == "under":
            if tn["t"] > 0.9:
                seg = tn["seg"]
                self.x = self.world.terrain.clamp_x(tn["x"], seg) - W / 2
                self.y = seg.yb - GROUND
                self.seg = seg
                self.tunnel = None
                self.go_idle(0.4)
                self.setVisible(self.world.visible and not self.world.paused)
                self.emit("dust", 5, y=GROUND - 2, spread=20)
                self.hop(320)

    def die(self, line=None):
        if self.state in ("ghost", "gone"):
            return
        if self.rider is not None:
            self.rider.dismount(True)
        if self.ride_on is not None:
            self.dismount(False)
        self.state, self.ghost_t = "ghost", 3.2
        self.hp, self.item, self.ammo, self.shield = 0.0, None, 0, 0
        self.veh_t = self.invis_t = self.smoke_t = 0.0
        self.fly_t, self.fly_kind, self.was_flying = 0.0, None, False
        self.camo, self.airborne, self.cloud_t = False, False, 0.0
        self.say(line or random.choice(HUNT["prey_dead"]), 2.2)
        self.emit("sparkle", 6, y=GROUND - 60)

    def ghost_tick(self, dt):
        self.ghost_t -= dt
        self.y -= 26 * dt
        self.x += math.sin(self.t * 3) * 10 * dt
        if self.ghost_t <= 0:
            self.state, self.gone = "gone", True
            self.hide()

    def respawn(self, x, seg):
        self.gone = False
        self.state = "idle"
        self.timer = 1.0
        self.hp, self.hp_show = 100.0, 2.0
        self.x, self.y, self.seg = x - W / 2, seg.yb - GROUND, seg
        self.vx = self.vy = 0.0
        self.airborne, self.camo = False, False
        self.setVisible(self.world.visible and not self.world.paused)
        self.emit("sparkle", 8, y=GROUND - 60)
        self.say(random.choice(HUNT["respawn"]), 1.8)
        self.hop(320)

    # ---------- vol ----------
    def start_fly(self, kind):
        if self.state not in ("idle", "walk") or self.airborne or kind not in FLIGHT:
            return False
        if self.rider is not None:
            self.rider.dismount(True)
        dur, sp, vs, alt = FLIGHT[kind]
        self.fly_kind, self.fly_t = kind, dur
        self.fly_speed, self.fly_vspeed = sp, vs
        floor = self.seg.yb if self.seg else self.feet()
        self.fly_alt = floor - rnd(*alt)
        self.was_flying = True
        self.camo, self.airborne, self.vy = False, False, 0.0
        self.tail_v -= 3
        self.emit("sparkle", 5, y=GROUND - 60)
        self.say(FLY_LINES.get(kind, "Je vole !"), 1.4)
        if kind == "fusee":
            self.walk_to(self.cx() + self.facing * 4000, sp)
        return True

    def end_flight(self, popped=False):
        kind = self.fly_kind
        self.fly_t, self.fly_kind, self.was_flying = 0.0, None, False
        if self.state in ("idle", "walk"):
            self.airborne, self.vy = True, 0.0
        if popped or kind == "ballon":
            self.say("Pop !", 1.2)
            self.emit("sparkle", 6, y=GROUND - 120)
            self.set_expr("surprised", 1.2)
        elif kind == "fusee":
            self.emit("smoke", 4, y=GROUND - 40)
        else:
            self.say(random.choice(["Plus de jus !", "Atterrissage...", "Oups."]), 1.3)

    def fly_tick(self, dt):
        T = self.world.terrain
        fy = self.feet()
        top, floor = T.sky(self.cx(), fy)
        alt = max(top + 120, min(floor - 40, self.fly_alt))
        dy = alt - fy
        vs = self.fly_vspeed * dt
        self.y += max(-vs, min(vs, dy))
        if self.state == "walk":
            dx = self.target_x - self.cx()
            step = self.fly_speed * (1.4 if self.speed_t > 0 else 1.0) * dt
            if abs(dx) <= step:
                self.x += dx
                self.go_idle()
            else:
                self.facing = 1 if dx > 0 else -1
                self.x += self.facing * step
                self.walk_phase += dt * 5
        if self.fly_kind == "ballon":
            self.x += math.sin(self.t * 0.7) * 25 * dt
        self.x = T.clamp_x(self.cx()) - W / 2
        self.seg = T.seg_near(self.cx(), floor)
        self.airborne, self.vy = False, 0.0
        if self.fly_kind in ("jetpack", "fusee") and random.random() < dt * 45:
            self.emit("flame", 1, x=W / 2 - self.facing * (30 if self.fly_kind == "jetpack" else 38),
                      y=GROUND - 30, spread=4)

    def mount(self, carrier):
        if not (self.grounded() and carrier.grounded()) or carrier.rider or self.rider:
            return False
        self.ride_on, carrier.rider = carrier, self
        self.state, self.airborne, self.camo = "ride", False, False
        self.set_expr("happy", 3)
        return True

    def dismount(self, gentle=True):
        c = self.ride_on
        if c is None:
            return
        c.rider, self.ride_on = None, None
        if gentle:
            self.launch(c.facing * -120, -300)
        else:
            self.state, self.airborne = "fall", False

    def ride_tick(self, dt):
        c = self.ride_on
        if c is None or c.state in ("fall", "drag", "ko", "ghost", "gone", "tunnel"):
            self.dismount(True)
            return
        bob = abs(math.sin(c.walk_phase)) * 3 if c.state == "walk" else 0
        self.x = c.x + c.facing * 3
        self.y = c.y - 57 - bob - (13 if c.veh_t > 0 else 0)
        self.facing = c.facing
        self.seg = c.seg

    # ---------- simulation ----------
    def tick_timers(self, dt):
        self.next_blink -= dt
        if self.next_blink <= 0:
            self.blink = 0.15
            if not self.double_blink and random.random() < 0.18:
                self.next_blink, self.double_blink = 0.28, True
            else:
                self.next_blink, self.double_blink = rnd(2.0, 6.0), False
        self.blink = max(0.0, self.blink - dt)
        for attr in ("spark", "talk_t", "hurt", "attack_t", "hp_show", "dizzy", "veh_t",
                     "speed_t", "invis_t", "smoke_t", "tunnel_cd", "open_t", "loot_wait",
                     "show_item_t", "fly_t", "cry_t"):
            setattr(self, attr, max(0.0, getattr(self, attr) - dt))
        if self.expr:
            self.expr_t -= dt
            if self.expr_t <= 0:
                self.expr = None
        for f in self.floaters:
            f[1] += dt
        self.floaters = [f for f in self.floaters if f[1] < 1.0]
        if self.smoke_t > 0 and random.random() < dt * 6:
            self.emit("smoke", 1, y=GROUND - 40, spread=26)
        self.tick_particles(dt)
        if self.bubble:
            self.bubble_t -= dt
            if self.bubble_t <= 0:
                self.bubble = None
        # humeur / endurance
        running = self.state == "walk" and self.speed > 120 and not self.airborne
        drain = -6 if self.role == "prey" else -11                 # l'adrénaline des fuyards
        self.stamina = max(0.0, min(100.0, self.stamina + (drain if running else 7) * dt))
        self.energy = max(0.0, min(100.0, self.energy + (1.2 if self.state == "sleep" else -0.05) * dt))
        self.fun = max(0.0, min(100.0, self.fun - 0.05 * dt))

    def tick(self, dt):
        self.t += dt
        self.tick_timers(dt)
        st = self.state
        if st == "gone":
            return
        if st == "ghost":
            self.ghost_tick(dt)
            self.move(int(self.x), int(self.y))
            self.update()
            return
        T = self.world.terrain
        if st == "ride":
            self.ride_tick(dt)
        elif st == "tunnel":
            self.tunnel_tick(dt)
        elif st == "drag":
            pass
        elif self.fly_t > 0 and st in ("idle", "walk"):
            self.fly_tick(dt)
            if st == "idle":
                self.timer -= dt
                if self.timer <= 0 and not self.busy and self.dizzy <= 0:
                    self.world.decide(self)
        else:
            if self.was_flying:
                self.end_flight()
            if st == "fall" or self.airborne:
                self.fly(dt)
            else:
                seg = self.seg
                if seg is None or not seg.contains(self.cx()) or abs(seg.yb - self.feet()) > 4:
                    seg = T.ground_at(self.cx(), self.feet()) or T.seg_near(self.cx(), self.feet())
                self.seg = seg
                self.y = seg.yb - GROUND
            st = self.state
            if st == "walk":
                self.walk_step(dt)
            elif st == "idle":
                self.timer -= dt
                if self.timer <= 0 and not self.busy and self.dizzy <= 0 and not self.airborne:
                    self.world.decide(self)
            elif st == "sleep":
                self.timer -= dt
                if self.timer <= 0:
                    self.wake("Bien dormi !" if random.random() < 0.3 else None)

        # immobilité (camouflage) et vitesse estimée
        if self.moving() or self.state not in ("idle", "sleep"):
            self.still_t = 0.0
            if self.state in ("walk", "fall", "drag") and self.camo:
                self.camo = False
        else:
            self.still_t += dt
        if dt > 0:
            v = (self.cx() - self._last_cx) / dt if self._last_cx is not None else 0.0
            self.vel += (max(-600.0, min(600.0, v)) - self.vel) * min(1.0, dt * 6)
        self._last_cx = self.cx()

        # inclinaison de tête curieuse au repos
        if self.state == "idle" and not self.busy:
            self.tilt_hold -= dt
            if self.tilt_hold <= 0:
                if self.tilt_target == 0 and random.random() < 0.35:
                    self.tilt_target = random.choice((-1, 1)) * rnd(8, 13)
                    self.tilt_hold = rnd(0.9, 2.2)
                else:
                    self.tilt_target, self.tilt_hold = 0.0, rnd(2, 5)
        else:
            self.tilt_target = 0.0
        self.tilt += (self.tilt_target - self.tilt) * min(1.0, dt * 7)

        # queue sur ressort amorti
        moving = self.state in ("walk", "fall") or self.airborne
        target = 0.35 if (self.state == "walk" and self.speed > 120) else 0.15 if moving else 0.0
        if self.state == "drag":
            target = -0.5 + math.sin(self.t * 5) * 0.4
        self.tail_v += (140 * (target - self.tail_a) - 9 * self.tail_v) * dt
        self.tail_a += self.tail_v * dt
        self.squash += (1.0 - self.squash) * min(1.0, dt * 9)

        # regard : curseur s'il est proche, sinon le partenaire
        cur = QCursor.pos()
        hx, hy = self.cx(), self.y + GROUND - 40
        dx, dy = cur.x() - hx, cur.y() - hy
        d = math.hypot(dx, dy)
        if d > 260 and self.partner:
            dx, dy = self.partner.cx() - hx, 0
            d = abs(dx) or 1
        d = d or 1
        tx, ty = dx / d * 1.9, dy / d * 1.6
        k = min(1.0, dt * 8)
        self.look = QPointF(self.look.x() + (tx - self.look.x()) * k,
                            self.look.y() + (ty - self.look.y()) * k)

        self.move(int(self.x), int(self.y))
        self.update()

    def fly(self, dt):
        T = self.world.terrain
        M = T.MARGIN
        prev_fy = self.feet()
        self.vy += GRAVITY * dt
        if self.state == "fall":
            old_x = self.x
            self.x += self.vx * dt
            cx = self.cx()
            if cx < T.x0 + M:
                self.x, self.vx = T.x0 + M - W / 2, abs(self.vx) * 0.5
            elif cx > T.x1 - M:
                self.x, self.vx = T.x1 - M - W / 2, -abs(self.vx) * 0.5
            elif T.ground_at(self.cx(), prev_fy) is None and T.ground_at(old_x + W / 2, prev_fy) is not None:
                self.x, self.vx = old_x, -self.vx * 0.5          # mur entre deux écrans
        self.y += self.vy * dt
        fy = self.feet()
        g = T.ground_at(self.cx(), prev_fy)
        if g is not None and self.vy >= 0 and fy >= g.yb:
            self.y = g.yb - GROUND
            self.seg = g
            self.on_land(self.vy)
        elif g is None and fy > T.max_yb + 200:
            self.respawn_nearby()

    def on_land(self, impact):
        self.emit("dust", 4 if impact > 500 else 2, y=GROUND - 2, spread=16)
        self.tail_v += 5
        if self.state == "fall":
            if impact > 650:
                self.vy, self.vx, self.squash = -impact * 0.35, self.vx * 0.7, 0.72
                if impact > 1100 and not self.pending_ko:
                    self.dizzy = 2.4
            else:
                self.vx = self.vy = 0.0
                self.squash = 0.74
                if self.pending_ko:
                    self.pending_ko = False
                    self.state = "ko"
                else:
                    self.go_idle(rnd(1.5, 3) + self.dizzy)
                    if self.land_msg:
                        self.say("Tout tourne..." if self.dizzy > 0 else self.land_msg, 2.2)
                        self.land_msg = None
        else:
            self.vy, self.airborne, self.squash = 0.0, False, 0.8

    def respawn_nearby(self):
        T = self.world.terrain
        seg = self.seg or T.seg_near(self.cx(), self.feet())
        self.x = T.random_x(seg) - W / 2
        self.y = seg.yb - GROUND
        self.seg = seg
        self.vx = self.vy = 0.0
        self.airborne = False
        self.go_idle(1.5)
        self.emit("dust", 5, y=GROUND - 2, spread=20)
        self.say("Oups !", 1.4)

    def walk_step(self, dt):
        T = self.world.terrain
        M = T.MARGIN
        sp = self.speed_now()
        dx = self.target_x - self.cx()
        step = sp * dt
        if abs(dx) <= step:
            self.x += dx
            self.go_idle()
            return
        d = 1 if dx > 0 else -1
        self.facing = d
        new_cx = self.cx() + d * step
        fy = self.feet()
        seg = self.seg
        if seg is not None and seg.contains(new_cx, M):
            self.x += d * step
        elif self.airborne:
            if T.ground_at(new_cx, fy) is not None or T.ledge_at(new_cx, fy) is not None:
                self.x += d * step
        else:
            g = T.ground_at(new_cx, fy)
            if g is not None:
                self.x += d * step
                if g.yb > fy + 3:                          # sol plus bas : on tombe
                    self.airborne, self.vy = True, 0.0
                    if random.random() < 0.3:
                        self.say("Wooo !", 1.0)
                else:
                    self.seg = g
            else:
                led = T.ledge_at(new_cx, fy)
                if led is not None:                        # sol plus haut : grand saut
                    self.vy = -(math.sqrt(2 * GRAVITY * (fy - led.yb)) + 90)
                    self.airborne, self.squash = True, 1.2
                    self.x += d * step
                    if random.random() < 0.5:
                        self.say("Hop !", 1.0)
                else:                                      # mur
                    self.x = T.clamp_x(self.cx(), seg) - W / 2
                    self.blocked = True
                    self.go_idle(rnd(0.4, 1.2))
                    return
        self.walk_phase += dt * sp / 8

    def tick_particles(self, dt):
        keep = []
        for pt in self.particles:
            pt["age"] += dt
            if pt["age"] >= pt["life"]:
                continue
            k = pt["k"]
            if k in ("heart", "note"):
                pt["x"] += (pt["vx"] + math.sin(pt["age"] * 6 + pt["ph"]) * 25) * dt
                pt["y"] += pt["vy"] * dt
            elif k in ("dust", "smoke"):
                pt["vx"] *= (1 - 3 * dt)
                pt["x"] += pt["vx"] * dt
                pt["y"] += pt["vy"] * dt
            elif k == "feather":
                pt["vy"] += 90 * dt
                pt["x"] += (pt["vx"] + math.sin(pt["age"] * 7 + pt["ph"]) * 40) * dt
                pt["y"] += pt["vy"] * dt
            elif k == "flash":
                pass
            elif k == "flame":
                pt["x"] += pt["vx"] * dt
                pt["y"] += pt["vy"] * dt
            else:
                pt["vy"] += 420 * dt
                pt["x"] += pt["vx"] * dt
                pt["y"] += pt["vy"] * dt
            keep.append(pt)
        self.particles = keep[-70:]

    # ---------- souris ----------
    def mousePressEvent(self, e):
        if self.state in ("ghost", "gone", "tunnel"):
            return
        if e.button() == Qt.MouseButton.LeftButton:
            self.world.cancel_duo()
            if self.ride_on is not None:
                self.dismount(True)
            if self.rider is not None:
                self.rider.dismount(True)
            g = e.globalPosition()
            self.press_pos = g
            self.drag_off = g - QPointF(self.x, self.y)
            self.moved = False
            self.drag_hist = [(time.monotonic(), g)]
        elif e.button() == Qt.MouseButton.RightButton:
            self.world.menu.popup(e.globalPosition().toPoint())

    def mouseMoveEvent(self, e):
        if self.drag_off is None:
            return
        g = e.globalPosition()
        if not self.moved and (g - self.press_pos).manhattanLength() > 6:
            self.moved = True
            self.fly_t, self.fly_kind, self.was_flying = 0.0, None, False
            self.state, self.airborne, self.camo = "drag", False, False
            self.set_expr("surprised", 30)
            if random.random() < 0.5:
                self.say(random.choice(["Hééé !", "Pose-moi !", "Wiii !"]), 1.5)
        if self.moved:
            pos = g - self.drag_off
            self.x, self.y = pos.x(), pos.y()
            now = time.monotonic()
            self.drag_hist.append((now, g))
            self.drag_hist = [h for h in self.drag_hist if now - h[0] < 0.1]

    def mouseReleaseEvent(self, e):
        if self.drag_off is None:
            return
        if self.moved:
            vx = vy = 0.0
            if len(self.drag_hist) >= 2:
                (t0, p0), (t1, p1) = self.drag_hist[0], self.drag_hist[-1]
                dt = max(t1 - t0, 1e-3)
                vx, vy = (p1.x() - p0.x()) / dt, (p1.y() - p0.y()) / dt
            v = math.hypot(vx, vy)
            if v > 1600:
                vx, vy = vx / v * 1600, vy / v * 1600
            self.set_expr(None, 0)
            self.state = "idle"
            self.launch(vx, vy)
            self.land_msg = "Wooo !" if v > 700 else "Atterrissage OK."
        else:
            self.pet()
        self.drag_off = None

    def pet(self):
        if self.state == "sleep":
            self.wake()
            return
        now = time.monotonic()
        self.clicks = [c for c in self.clicks if now - c < 3] + [now]
        if len(self.clicks) >= 4:
            self.clicks = []
            self.set_expr("pout", 2.4)
            self.say("Arrête !", 1.8)
            self.hop(200)
            return
        self.set_expr("happy", 1.4)
        self.emit("heart", 3, y=GROUND - 80)
        self.fun = min(100.0, self.fun + 4)
        self.hop(260)
        if random.random() < 0.5:
            self.say(random.choice(PET_LINES), 1.6)

    # ---------- rendu ----------
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.paint_all(p)
        p.end()

    def face_mode(self):
        st = self.state
        if st == "ghost":
            return "ghost"
        if st == "ko" or self.dizzy > 0:
            return "dizzy"
        if st == "sleep":
            return "sleep"
        if self.hurt > 0:
            return "hurt"
        if self.cry_t > 0:
            return "cry"
        if self.expr:
            return self.expr
        if self.hugging or st == "ride":
            return "happy"
        if self.mood in ("war", "hunt"):
            return "war"
        if self.mood == "scared":
            return "scared"
        return "open"

    def paint_all(self, p, bubble=True):
        cx = W / 2
        st = self.state
        walking = st == "walk" and not self.airborne
        shx = shy = 0.0
        if self.shake > 0:
            shx, shy = rnd(-2.5, 2.5), rnd(-1.5, 1.5)
        p.setOpacity(self.alpha())

        if self.cloud_t > 0 and bubble:
            self.draw_cloud(p, cx)
            self.draw_particles(p)
            self.draw_floaters(p, cx)
            return

        # ombre douce
        h = max(0.0, (self.seg.yb if self.seg else self.feet()) - self.feet())
        if st not in ("drag", "ghost", "ride") and h < 80:
            p.setPen(NO_PEN)
            p.setBrush(QColor(0, 0, 0, int(55 * (1 - h / 80))))
            p.drawEllipse(QPointF(cx, GROUND - 1), 30 * (1 - h / 200), 5)

        sleeping = st == "sleep"
        br = math.sin(self.t * 2 * math.pi / self.breath_T) * (0.035 if sleeping else 0.022)
        sy = self.squash * (1 + br)
        rot, bob = self.tilt, 0.0
        if walking:
            if self.veh_t > 0:
                rot += -6 + math.sin(self.t * 25) * 1.5      # vibrations de trottinette
            else:
                rot += math.sin(self.walk_phase) * 7          # dandinement
                bob = abs(math.sin(self.walk_phase)) * 3
        if st == "drag":
            sy *= 1.07
        if st == "ko":
            sy *= 0.88
            rot += math.sin(self.t * 3) * 5
        if self.dizzy > 0:
            rot += math.sin(self.t * 7) * 5
        if st == "ghost":
            rot += math.sin(self.t * 2) * 6
        flying = self.fly_t > 0
        if flying:
            bob = math.sin(self.t * 3) * 4
            if self.fly_kind == "fusee":
                rot += -28
            elif walking:
                rot += -9
        sx = 1 / sy
        sx *= self.size
        sy *= self.size

        p.save()
        p.translate(cx + shx, GROUND - bob + shy)
        if st == "drag":
            p.translate(0, -74)
            p.rotate(math.sin(self.t * 5) * 9)
            p.translate(0, 74)
        else:
            p.rotate(rot * self.facing)
        p.scale(self.facing * sx, sy)
        if st == "ghost":
            self.draw_ghost(p)
        else:
            self.draw_character(p)
        p.restore()

        # symboles manga (hors silhouette)
        fm = self.face_mode()
        top = GROUND - 70 * sy - bob - (13 if self.veh_t > 0 else 0)
        if fm in ("war", "pout"):
            self.draw_vein(p, cx - 26 * self.facing, top + 2)
        if st == "drag":
            f = QFont("Segoe UI", 15)
            f.setBold(True)
            p.setFont(f)
            outlined_text(p, QRectF(cx + 20, top - 38, 24, 26), "!", QColor("#FFD23F"))
        if fm == "dizzy":
            self.draw_stars(p, cx, top - 6)
        if fm in ("hurt", "scared") or (self.mood == "war" and self.hp < 40 and st != "ko") \
                or (self.speed > 120 and self.stamina < 15 and walking):
            self.draw_sweat(p, cx + 30 * self.facing, top + 14)
        if sleeping:
            self.draw_zzz(p, cx)
        if self.show_item_t > 0:
            a = 1 - self.show_item_t / 1.6
            p.setOpacity(min(1.0, (1.6 - self.show_item_t) * 4) * min(1.0, self.show_item_t * 2))
            draw_item_icon(p, self.show_item, cx, top - 26 - a * 22, 0.9)
            p.setOpacity(self.alpha())
        self.draw_particles(p)
        hp_on = bubble and st not in ("ko", "ghost") and (self.mood in ("war", "hunt", "scared")
                                                          or self.hp_show > 0 or self.hp < 100)
        if hp_on:
            self.draw_hearts_hp(p, cx, top)
        if bubble:
            self.draw_floaters(p, cx)
            self.draw_bubble(p, cx, (12 if hp_on else 0) + (13 if self.veh_t > 0 else 0)
                             + (62 if self.fly_kind == "ballon" else 0) - int((1 - self.size) * 75))

    # ---- personnage (coordonnées locales : pieds en (0,0), regard vers +x) ----
    def draw_character(self, p):
        t, st = self.t, self.state
        walking = st == "walk" and not self.airborne
        ph = self.walk_phase
        fm = self.face_mode()
        veh = self.veh_t > 0

        flying = self.fly_t > 0
        if veh and not flying:
            self.draw_scooter(p, walking)
            p.translate(0, -13)
        if flying:
            self.draw_flight_gear(p)
        self.draw_tail(p)

        # petites jambes
        if not veh or flying:
            p.setPen(NO_PEN)
            p.setBrush(self.c_shade)
            for i, lx in enumerate((-13, 13)):
                lift, dx = 0.0, 0.0
                if walking and not flying:
                    lift = max(0.0, math.sin(ph + i * math.pi)) * 4
                elif st in ("drag", "ride") or flying:
                    lift = -5
                    dx = math.sin(t * 6 + i * 2.2) * 2.5
                p.drawEllipse(QPointF(lx + dx, -5 - lift), 8, 6)

        self.draw_horns(p)

        # corps : blob un peu plus large que haut, dégradé doux
        body = QRectF(-34, -69, 68, 63)
        g = QRadialGradient(QPointF(-12, -52), 62)
        g.setColorAt(0.0, self.c_light)
        g.setColorAt(0.55, self.c_body)
        g.setColorAt(1.0, self.c_shade)
        p.setPen(mkpen(self.c_line, 2.0))
        p.setBrush(g)
        p.drawRoundedRect(body, 30, 29)
        if self.hurt > 0:
            p.setPen(NO_PEN)
            p.setBrush(QColor(255, 255, 255, int(110 * min(1, self.hurt / 0.2))))
            p.drawRoundedRect(body, 30, 29)
        p.setPen(NO_PEN)
        p.setBrush(self.c_belly)
        p.drawEllipse(QPointF(2, -15), 16, 7.5)
        p.setBrush(QColor(255, 255, 255, 80))
        p.drawEllipse(QPointF(-17, -58), 6.5, 3.8)
        p.drawEllipse(QPointF(-9, -62), 2.2, 1.6)
        # marque discrète (redressée pour ne jamais être en miroir)
        p.save()
        p.scale(self.facing, 1)
        f = QFont("Segoe UI", 6)
        f.setBold(True)
        p.setFont(f)
        mc = QColor(self.c_body.darker(135))
        mc.setAlpha(170)
        p.setPen(mc)
        p.drawText(QRectF(2 * self.facing - 12, -20, 24, 11), Qt.AlignmentFlag.AlignCenter,
                   self.sk["mark"])
        p.restore()

        self.draw_hat(p)

        # joues roses
        blush = QColor(self.c_blush)
        big = fm in ("happy", "pout", "war", "wink")
        blush.setAlpha(170 if big else 100)
        p.setPen(NO_PEN)
        p.setBrush(blush)
        for bx in (-23, 24):
            p.drawEllipse(QPointF(bx, -27), 7 if big else 5.5, 4 if big else 3.2)

        self.draw_eyes(p, fm)
        self.draw_mouth(p, fm)
        if self.is_kid:
            self.draw_accessory(p)
        elif self.duty in ("work", "help") and self.state == "idle":
            self.draw_laptop(p)

        # bras (petits moignons)
        p.setPen(NO_PEN)
        p.setBrush(self.c_body.darker(108))
        swing = math.sin(ph) * 2.5 if walking else 0
        if st == "drag":
            p.drawEllipse(QPointF(-32, -54), 5, 6.5)
            p.drawEllipse(QPointF(33, -54), 5, 6.5)
        elif self.rider is not None:
            p.drawEllipse(QPointF(-26, -64), 5, 6.5)
            p.drawEllipse(QPointF(27, -64), 5, 6.5)
        elif self.hugging:
            p.drawEllipse(QPointF(39, -30), 6.5, 5)
        elif veh:
            p.drawEllipse(QPointF(-33, -30), 5, 5)
            p.drawEllipse(QPointF(38, -40), 5.5, 5)
        elif self.attack_t > 0 or self.open_t > 0:
            p.drawEllipse(QPointF(-33, -24), 5, 5)
            p.drawEllipse(QPointF(41, -34), 6.5, 5)
        elif self.arm_up:
            p.drawEllipse(QPointF(-33, -24), 5, 5)
            p.drawEllipse(QPointF(31, -60), 5, 6.5)
        else:
            p.drawEllipse(QPointF(-34, -24 + swing), 5, 5)
            p.drawEllipse(QPointF(34, -24 - swing), 5, 5)

        self.draw_held(p)
        if self.fan_prop:
            draw_fan_prop(self, p)

        if self.spark > 0:
            p.setPen(mkpen(QColor("#FFD23F"), 2.2))
            r0, r1 = 5, 5 + 10 * (1 - self.spark / 0.5)
            for k in range(6):
                a = k * math.pi / 3
                p.drawLine(QPointF(34 + r0 * math.cos(a), -70 + r0 * math.sin(a)),
                           QPointF(34 + r1 * math.cos(a), -70 + r1 * math.sin(a)))
            p.setPen(NO_PEN)

    def draw_accessory(self, p):
        acc, t = self.accessory, self.t
        if self.stage == "ado":                                  # lunettes de soleil
            p.setPen(mkpen(INK, 1.6))
            p.setBrush(QColor(30, 20, 40, 215))
            for ex in (-12, 13):
                p.drawRoundedRect(QRectF(ex - 8, -42, 16, 11), 4, 4)
            p.drawLine(QPointF(-4, -37), QPointF(5, -37))
            p.setPen(NO_PEN)
            p.setBrush(QColor(255, 255, 255, 90))
            p.drawEllipse(QPointF(-15, -40), 3, 1.6)
        elif acc == "noeud":                                     # nœud sur la tête
            p.setPen(mkpen(QColor("#C93A63"), 1.2))
            p.setBrush(QColor("#FF7FA0"))
            p.drawPolygon(QPolygonF([QPointF(-18, -72), QPointF(-30, -80), QPointF(-30, -64)]))
            p.drawPolygon(QPolygonF([QPointF(-18, -72), QPointF(-6, -80), QPointF(-6, -64)]))
            p.drawEllipse(QPointF(-18, -72), 3.5, 3.5)
        elif acc == "helice":                                    # casquette à hélice
            p.setPen(mkpen(QColor("#1F7A99"), 1.3))
            p.setBrush(QColor("#5EE6FF"))
            p.drawRoundedRect(QRectF(-14, -78, 28, 11), 6, 6)
            p.drawLine(QPointF(0, -78), QPointF(0, -84))
            p.setBrush(QColor("#FFD23F"))
            w = 12 * math.cos(t * 12)
            p.drawRoundedRect(QRectF(-w, -87, 2 * w if w else 1, 4), 2, 2)
        elif acc == "lunettes":                                  # lunettes rondes
            p.setPen(mkpen(QColor("#6A5A80"), 1.6))
            p.setBrush(NO_BRUSH)
            for ex in (-12, 13):
                p.drawEllipse(QPointF(ex, -36), 10, 10)
            p.drawLine(QPointF(-2, -36), QPointF(3, -36))

    def draw_laptop(self, p):
        t = self.t
        p.setPen(mkpen(QColor("#3A3F52"), 1.3))
        p.setBrush(QColor("#5A6078"))
        p.drawRoundedRect(QRectF(26, -12, 26, 4), 1, 1)
        p.setBrush(QColor("#1E2233"))
        p.drawRoundedRect(QRectF(28, -30, 22, 18), 2, 2)
        p.setPen(NO_PEN)
        p.setBrush(QColor("#3DDC84") if int(t * 3) % 2 else QColor("#5EE6FF"))
        for i in range(3):
            p.drawRect(QRectF(31, -27 + i * 4, 6 + (i * 5 + int(t * 4)) % 12, 2))

    def draw_flight_gear(self, p):
        t, k = self.t, self.fly_kind
        if k == "potion_vol":                                   # petites ailes
            for sg in (-1, 1):
                p.save()
                p.translate(sg * 22, -56)
                p.rotate(sg * (-20 + math.sin(t * 14) * 28))
                p.setPen(mkpen(QColor("#B9C6E8"), 1.3))
                p.setBrush(QColor(240, 245, 255, 220))
                wing = QPainterPath(QPointF(0, 0))
                wing.cubicTo(QPointF(sg * 14, -26), QPointF(sg * 40, -22), QPointF(sg * 34, -4))
                wing.cubicTo(QPointF(sg * 26, -8), QPointF(sg * 14, -2), QPointF(0, 0))
                p.drawPath(wing)
                p.restore()
        elif k == "jetpack":                                    # sac à dos réacteur
            p.setPen(mkpen(QColor("#4E5468"), 1.4))
            p.setBrush(QColor("#B9BFD2"))
            p.drawRoundedRect(QRectF(-44, -58, 14, 28), 5, 5)
            p.setBrush(QColor("#6F7590"))
            p.drawRoundedRect(QRectF(-42, -31, 10, 5), 1.5, 1.5)
            p.setPen(NO_PEN)
            p.setBrush(QColor("#FF8A3D"))
            f = 6 + math.sin(t * 40) * 3
            p.drawPolygon(QPolygonF([QPointF(-41, -26), QPointF(-33, -26), QPointF(-37, -26 + f + 6)]))
        elif k == "ballon":                                     # ballon + ficelle
            col = QColor("#FF5C6C") if self.name == "Hybris" else QColor("#5EE6FF")
            p.setPen(mkpen(QColor("#6B4A1F"), 1.2))
            p.drawLine(QPointF(2, -68), QPointF(1 + math.sin(t * 2) * 3, -96))
            p.setPen(mkpen(col.darker(140), 1.4))
            p.setBrush(col)
            p.drawEllipse(QPointF(1 + math.sin(t * 2) * 3, -122), 22, 26)
            p.setPen(NO_PEN)
            p.setBrush(QColor(255, 255, 255, 140))
            p.drawEllipse(QPointF(-7 + math.sin(t * 2) * 3, -132), 6, 8)
        elif k == "fusee":                                      # traînée de fusée
            p.setPen(NO_PEN)
            for i in range(4):
                c = QColor("#FF8A3D" if i % 2 else "#FFD23F")
                c.setAlpha(200 - i * 40)
                p.setBrush(c)
                p.drawEllipse(QPointF(-40 - i * 12, -34 + math.sin(t * 30 + i) * 3), 9 - i * 1.5, 6 - i)

    def draw_ghost(self, p):
        t = self.t
        col = QColor("#CBD3EE")
        p.setPen(mkpen(QColor("#8F9BC4"), 2))
        p.setBrush(col)
        body = QPainterPath(QPointF(-32, -40))
        body.cubicTo(QPointF(-32, -80), QPointF(32, -80), QPointF(32, -40))
        body.lineTo(QPointF(32, -8))
        for i in range(4):
            x0 = 32 - i * 16
            body.quadTo(QPointF(x0 - 8, -8 + (6 if i % 2 == 0 else -4) + math.sin(t * 6 + i) * 3),
                        QPointF(x0 - 16, -8))
        body.closeSubpath()
        p.drawPath(body)
        p.setPen(mkpen(self.c_horn_line, 1.2))
        p.setBrush(self.c_horn)
        for sg in (-1, 1):
            p.drawEllipse(QPointF(sg * 16, -76), 5, 7)
        p.setPen(mkpen(INK, 2.4))
        for ex in (-11, 12):
            p.drawLine(QPointF(ex - 4, -54), QPointF(ex + 4, -46))
            p.drawLine(QPointF(ex - 4, -46), QPointF(ex + 4, -54))
        p.setBrush(NO_BRUSH)
        m = QPainterPath(QPointF(-4, -34))
        m.quadTo(QPointF(1, -30), QPointF(6, -34))
        p.drawPath(m)

    def draw_scooter(self, p, moving):
        p.setPen(mkpen(QColor("#1F7A99"), 2))
        p.setBrush(QColor("#5EE6FF"))
        p.drawRoundedRect(QRectF(-30, -7, 54, 6), 3, 3)                # plateau
        p.drawLine(QPointF(22, -6), QPointF(36, -46))                    # guidon
        p.setPen(mkpen(QColor("#1F7A99"), 3.5))
        p.drawLine(QPointF(30, -46), QPointF(44, -46))
        for wx in (-24, 20):
            p.setPen(mkpen(QColor("#1B1B28"), 1.5))
            p.setBrush(QColor("#2B2B3A"))
            p.drawEllipse(QPointF(wx, -1), 7, 7)
            p.setPen(mkpen(QColor("#9AA0B4"), 1.5))
            a = self.t * (18 if moving else 0)
            p.drawLine(QPointF(wx + 5 * math.cos(a), -1 + 5 * math.sin(a)),
                       QPointF(wx - 5 * math.cos(a), -1 - 5 * math.sin(a)))
        if moving and random.random() < 0.3:
            self.emit("dust", 1, x=W / 2 - self.facing * 40, y=GROUND - 3, spread=6)

    def draw_hat(self, p):
        if self.role == "hunter":                                    # casquette de la Garde
            p.setPen(mkpen(QColor("#1F3FA8"), 1.4))
            p.setBrush(QColor("#3B6CFF"))
            p.drawRoundedRect(QRectF(-17, -80, 34, 13), 6, 6)
            p.drawRoundedRect(QRectF(10, -71, 17, 4.5), 2, 2)
            p.setPen(NO_PEN)
            p.setBrush(QColor("#FFD23F"))
            p.drawPolygon(star_poly(0, -74, 4, 1.7))
        elif self.role == "prey":                                    # bandana d'intrus
            p.setPen(mkpen(QColor("#9E1E3A"), 1.2))
            p.setBrush(QColor("#E0304A"))
            p.drawRoundedRect(QRectF(-24, -70, 48, 7), 3, 3)
            p.drawPolygon(QPolygonF([QPointF(-24, -66), QPointF(-36, -60), QPointF(-27, -62)]))
            p.drawPolygon(QPolygonF([QPointF(-24, -66), QPointF(-34, -72), QPointF(-27, -68)]))

    def draw_held(self, p):
        if self.shield > 0:
            draw_item_icon(p, "bouclier", 34, -40, 1.05)
        if self.item and self.state not in ("drag",):
            rot = -25 if self.item == "marteau" else 0
            if self.attack_t > 0 and self.item == "marteau":
                rot = -100 + 90 * (1 - self.attack_t / 0.3)
            draw_item_icon(p, self.item, 42, -32, 0.85, rot)

    def draw_tail(self, p):
        wig = math.sin(self.t * (1.3 if self.state == "sleep" else 3.0)) * 0.12
        phi = 0.95 + self.tail_a + wig
        bx, by = -27.0, -15.0
        tip = QPointF(bx - 25 * math.cos(phi), by - 25 * math.sin(phi))
        ctrl = QPointF(bx - 20 * math.cos(phi - 0.9), by - 20 * math.sin(phi - 0.9) + 4)
        path = QPainterPath(QPointF(bx, by))
        path.quadTo(ctrl, tip)
        p.setPen(mkpen(self.c_line, 5.5))
        p.setBrush(NO_BRUSH)
        p.drawPath(path)
        p.setPen(mkpen(self.c_body.darker(112), 3.2))
        p.drawPath(path)
        ang = math.degrees(math.atan2(tip.y() - ctrl.y(), tip.x() - ctrl.x()))
        p.save()
        p.translate(tip)
        p.rotate(ang + 90)
        p.setPen(mkpen(self.c_horn_line, 1.3))
        p.setBrush(self.c_horn)
        if self.sk["tail_tip"] == "heart":
            p.drawPath(heart_path(0, 1, 5.2))
        else:
            drop = QPainterPath(QPointF(0, 3))
            drop.cubicTo(QPointF(-7, -2), QPointF(-4, -10), QPointF(0, -10))
            drop.cubicTo(QPointF(4, -10), QPointF(7, -2), QPointF(0, 3))
            p.drawPath(drop)
        p.restore()

    def draw_horns(self, p):
        p.setPen(mkpen(self.c_horn_line, 1.4))
        p.setBrush(self.c_horn)
        for sg in (-1, 1):
            o = 2
            if self.sk["horn_shape"] == "crescent":
                hp = QPainterPath(QPointF(sg * 9 + o, -62))
                hp.quadTo(QPointF(sg * 12 + o, -79), QPointF(sg * 25 + o, -81))
                hp.quadTo(QPointF(sg * 19 + o, -73), QPointF(sg * 21 + o, -64))
                hp.closeSubpath()
                p.drawPath(hp)
                p.drawEllipse(QPointF(sg * 24.5 + o, -80.5), 1.8, 1.8)
            else:
                hp = QPainterPath(QPointF(sg * 8 + o, -63))
                hp.quadTo(QPointF(sg * 10 + o, -78), QPointF(sg * 15.5 + o, -78))
                hp.quadTo(QPointF(sg * 21 + o, -77), QPointF(sg * 22 + o, -63))
                hp.closeSubpath()
                p.drawPath(hp)

    def draw_eyes(self, p, fm):
        ey = -36 + (2 if self.is_kid else 0)
        k = self.eye_k
        lx, ly = self.look.x() * self.facing, self.look.y()
        if fm == "pout":
            lx, ly = -1.6, 0.4
        closed = self.blink > 0 and fm in ("open", "war", "pout", "scared")
        for i, ex in enumerate((-12, 13)):
            d = 1 if i == 0 else -1
            mode = fm
            if fm == "wink":
                mode = "happy" if i == 1 else "open"
            if closed:
                mode = "closed"
            if mode == "cry":
                p.setPen(mkpen(INK, 2.4))
                p.setBrush(NO_BRUSH)
                c = QPainterPath(QPointF(ex - 6, ey - 2))
                c.quadTo(QPointF(ex, ey + 3), QPointF(ex + 6, ey - 2))
                p.drawPath(c)
                p.setPen(NO_PEN)
                p.setBrush(QColor("#7FD3FF"))
                for j in range(2):
                    ty = ey + 4 + ((self.t * 40 + j * 9 + i * 5) % 18)
                    p.drawEllipse(QPointF(ex + d * 6, ty), 2.2, 3.2)
            elif mode in ("closed", "sleep"):
                p.setPen(mkpen(INK, 2.3))
                p.setBrush(NO_BRUSH)
                c = QPainterPath(QPointF(ex - 6, ey))
                c.quadTo(QPointF(ex, ey + 4.5), QPointF(ex + 6, ey))
                p.drawPath(c)
            elif mode == "happy":
                p.setPen(mkpen(INK, 2.5))
                p.setBrush(NO_BRUSH)
                c = QPainterPath(QPointF(ex - 6, ey + 2))
                c.quadTo(QPointF(ex, ey - 7), QPointF(ex + 6, ey + 2))
                p.drawPath(c)
            elif mode == "hurt":
                p.setPen(mkpen(INK, 2.4))
                p.setBrush(NO_BRUSH)
                p.drawPolyline(QPolygonF([QPointF(ex - d * 5, ey - 4.5), QPointF(ex + d * 4, ey),
                                          QPointF(ex - d * 5, ey + 4.5)]))
            elif mode == "dizzy":
                p.setPen(mkpen(INK, 1.7))
                p.setBrush(NO_BRUSH)
                sp = QPainterPath()
                a0 = self.t * 8 * d
                for k in range(34):
                    a = k * 0.32
                    r = 0.4 + a * 0.62
                    pt = QPointF(ex + r * math.cos(a + a0), ey + r * math.sin(a + a0))
                    if k == 0:
                        sp.moveTo(pt)
                    else:
                        sp.lineTo(pt)
                p.drawPath(sp)
            else:
                small = mode in ("surprised", "scared")
                p.setPen(NO_PEN)
                p.setBrush(QColor("#FBFAFF"))
                p.drawEllipse(QPointF(ex, ey), 7.4 * k, (9.2 if small else 8.8) * k)
                ix, iy = ex + lx, ey + ly + 0.6
                irx, iry = (3.6 * k, 4.6 * k) if small else (5.9 * k, 7.3 * k)
                gr = QLinearGradient(QPointF(0, iy - iry), QPointF(0, iy + iry))
                gr.setColorAt(0.0, self.c_iris_top)
                gr.setColorAt(0.55, self.c_iris_top)
                gr.setColorAt(1.0, self.c_iris_bot)
                p.setBrush(gr)
                p.drawEllipse(QPointF(ix, iy), irx, iry)
                p.setBrush(QColor(8, 6, 20))
                p.drawEllipse(QPointF(ix, iy - 0.5), irx * 0.45, iry * 0.45)
                p.setBrush(QColor(255, 255, 255))
                p.drawEllipse(QPointF(ix - irx * 0.38, iy - iry * 0.42), irx * 0.36, irx * 0.36)
                p.drawEllipse(QPointF(ix + irx * 0.42, iy + iry * 0.38), irx * 0.17, irx * 0.17)
                if mode in ("war", "pout"):
                    p.save()
                    clip = QPainterPath()
                    clip.addEllipse(QPointF(ex, ey), 7.6, 9.0)
                    p.setClipPath(clip)
                    p.setBrush(self.c_body.darker(104))
                    if mode == "war":
                        poly = [QPointF(ex - d * 9, ey - 12), QPointF(ex + d * 9, ey - 12),
                                QPointF(ex + d * 9, ey - 3.5), QPointF(ex - d * 9, ey - 8)]
                    else:
                        poly = [QPointF(ex - 9, ey - 12), QPointF(ex + 9, ey - 12),
                                QPointF(ex + 9, ey - 3), QPointF(ex - 9, ey - 3)]
                    p.drawPolygon(QPolygonF(poly))
                    p.setPen(mkpen(INK, 1.8))
                    p.drawLine(poly[3], poly[2])
                    p.restore()
                    p.setPen(NO_PEN)

    def draw_mouth(self, p, fm):
        my = -24.5
        st = self.state
        pink = QColor("#FF7FA0")
        if fm == "cry":
            p.setPen(mkpen(INK, 1.6))
            p.setBrush(INK)
            m = QPainterPath(QPointF(-5, my - 2))
            m.quadTo(QPointF(1, my + 8), QPointF(7, my - 2))
            m.quadTo(QPointF(1, my + 1), QPointF(-5, my - 2))
            p.drawPath(m)
            return
        if self.stage == "bébé" and self.talk_t <= 0 and fm in ("open", "sleep", "happy"):
            p.setPen(mkpen(QColor("#C96A9E"), 1.4))            # tétine
            p.setBrush(QColor("#FFB3D9"))
            p.drawEllipse(QPointF(1, my + 1), 5.5, 3.6)
            p.setBrush(QColor("#FF8FC8"))
            p.drawEllipse(QPointF(1, my + 1), 2.0, 2.0)
            return
        if st == "drag" or fm == "surprised":
            p.setPen(NO_PEN)
            p.setBrush(INK)
            p.drawEllipse(QPointF(1, my + 0.5), 2.6, 3.2)
        elif self.talk_t > 0 and fm not in ("dizzy", "hurt"):
            o = 1.2 + abs(math.sin(self.t * 15)) * 2.4
            p.setPen(NO_PEN)
            p.setBrush(INK)
            p.drawEllipse(QPointF(1, my), 3.4, o)
            p.setBrush(pink)
            p.drawEllipse(QPointF(1, my + o * 0.45), 2.0, o * 0.45)
        elif fm in ("dizzy", "hurt", "scared"):
            p.setPen(mkpen(INK, 1.8))
            p.setBrush(NO_BRUSH)
            m = QPainterPath(QPointF(-4.5, my))
            for i in range(1, 5):
                m.lineTo(QPointF(-4.5 + i * 2.8, my + (-2 if i % 2 else 0)))
            p.drawPath(m)
        elif fm == "sleep":
            self.draw_w(p, my, 0.7)
        elif fm == "happy":
            m = QPainterPath(QPointF(-5, my - 1.5))
            m.quadTo(QPointF(1, my + 9), QPointF(7, my - 1.5))
            m.closeSubpath()
            p.setPen(mkpen(INK, 1.4))
            p.setBrush(INK)
            p.drawPath(m)
            p.setPen(NO_PEN)
            p.setBrush(pink)
            p.drawEllipse(QPointF(1, my + 3.2), 2.8, 1.6)
        elif fm in ("pout", "war"):
            p.setPen(mkpen(INK, 1.9))
            p.setBrush(NO_BRUSH)
            m = QPainterPath(QPointF(-3.5, my + 1))
            m.quadTo(QPointF(1, my - 2.5), QPointF(5.5, my + 1))
            p.drawPath(m)
        elif fm == "wink":
            self.draw_w(p, my, 1.0)
            p.setPen(NO_PEN)
            p.setBrush(pink)
            p.drawRoundedRect(QRectF(-1.5, my + 0.5, 5, 5.5), 2.5, 2.5)
        else:
            self.draw_w(p, my, 1.0)
            if self.name == "Iblis":
                p.setPen(NO_PEN)
                p.setBrush(QColor("#FFFFFF"))
                p.drawPolygon(QPolygonF([QPointF(2.6, my + 0.2), QPointF(5.2, my - 0.4),
                                         QPointF(4.1, my + 3.0)]))

    @staticmethod
    def draw_w(p, my, s):
        p.setPen(mkpen(INK, 1.8))
        p.setBrush(NO_BRUSH)
        m = QPainterPath(QPointF(-4.5 * s + 1, my - 1))
        m.quadTo(QPointF(-2.2 * s + 1, my + 3 * s), QPointF(1, my - 0.2))
        m.quadTo(QPointF(2.2 * s + 1, my + 3 * s), QPointF(4.5 * s + 1, my - 1))
        p.drawPath(m)

    # ---- symboles et effets ----
    def draw_vein(self, p, x, y):
        s = 1 + math.sin(self.t * 9) * 0.12
        p.setPen(mkpen(QColor("#FF4F6D"), 2.1))
        p.setBrush(NO_BRUSH)
        for q in range(4):
            p.save()
            p.translate(x, y)
            p.rotate(q * 90)
            p.scale(s, s)
            v = QPainterPath(QPointF(1.8, 6))
            v.quadTo(QPointF(1.8, 1.8), QPointF(6, 1.8))
            p.drawPath(v)
            p.restore()

    def draw_sweat(self, p, x, y):
        p.setPen(mkpen(QColor("#4AA8E0"), 1.2))
        p.setBrush(QColor("#BDE8FF"))
        d = QPainterPath(QPointF(x, y - 7))
        d.quadTo(QPointF(x + 5.5, y + 1.5), QPointF(x, y + 4))
        d.quadTo(QPointF(x - 5.5, y + 1.5), QPointF(x, y - 7))
        p.drawPath(d)

    def draw_stars(self, p, x, y):
        p.setPen(mkpen(QColor("#C9971F"), 1))
        p.setBrush(QColor("#FFD23F"))
        for i in range(3):
            a = self.t * 4 + i * 2.09
            p.drawPolygon(star_poly(x + math.cos(a) * 22, y + math.sin(a) * 6, 5.5, 2.4))

    def draw_zzz(self, p, cx):
        f = QFont("Segoe UI")
        f.setBold(True)
        for i in range(3):
            ph = (self.t * 0.45 + i / 3) % 1
            f.setPointSizeF(7 + ph * 6)
            p.setFont(f)
            p.setPen(QColor(235, 235, 250, int(230 * (1 - ph))))
            p.drawText(QPointF(cx + 22 + ph * 16 + math.sin(self.t * 2 + i) * 3,
                               GROUND - 76 - ph * 40), "z")

    def draw_particles(self, p):
        for pt in self.particles:
            a = 1 - pt["age"] / pt["life"]
            k, x, y, s = pt["k"], pt["x"], pt["y"], pt["s"]
            p.setPen(NO_PEN)
            if k == "heart":
                c = QColor("#FF6FA5")
                c.setAlpha(int(255 * min(1, a * 1.6)))
                p.setBrush(c)
                p.drawPath(heart_path(x, y, 4.5 * s))
            elif k == "note":
                f = QFont("Segoe UI", int(11 * s))
                f.setBold(True)
                p.setFont(f)
                p.setPen(QColor(120, 90, 200, int(255 * a)))
                p.drawText(QPointF(x, y), "♪" if int(pt["ph"]) % 2 else "♫")
            elif k == "dust":
                p.setBrush(QColor(245, 242, 250, int(170 * a)))
                r = (3 + (1 - a) * 6) * s
                p.drawEllipse(QPointF(x, y), r, r * 0.8)
            elif k == "smoke":
                p.setBrush(QColor(150, 155, 175, int(150 * a)))
                r = (6 + (1 - a) * 14) * s
                p.drawEllipse(QPointF(x, y), r, r * 0.85)
            elif k == "sparkle":
                c = QColor("#FFE066")
                c.setAlpha(int(255 * a))
                p.setBrush(c)
                p.drawPolygon(star_poly(x, y, 4.5 * s, 1.4 * s, 4, pt["age"] * 5))
            elif k == "snow":
                p.setBrush(QColor(255, 255, 255, int(240 * a)))
                p.drawEllipse(QPointF(x, y), 2.4 * s, 2.4 * s)
            elif k == "feather":
                p.save()
                p.translate(x, y)
                p.rotate(math.sin(pt["age"] * 6 + pt["ph"]) * 40)
                p.setBrush(QColor(255, 225, 238, int(240 * a)))
                p.drawEllipse(QPointF(0, 0), 5 * s, 2 * s)
                p.restore()
            elif k == "flash":
                p.setBrush(QColor(255, 255, 255, int(200 * a)))
                p.drawRect(QRectF(0, 0, W, H))
            elif k == "flame":
                c = QColor("#FFD23F" if a > 0.5 else "#FF8A3D")
                c.setAlpha(int(230 * a))
                p.setBrush(c)
                p.drawEllipse(QPointF(x, y), 4 * s * a + 1, 4 * s * a + 1)
            elif k == "tear":
                c = QColor("#7FD3FF")
                c.setAlpha(int(230 * a))
                p.setBrush(c)
                p.drawEllipse(QPointF(x, y), 2.2 * s, 3 * s)

    def draw_hearts_hp(self, p, cx, top):
        y = top - 22
        n, s, gap = 5, 4.0, 11
        x0 = cx - gap * (n - 1) / 2
        for i in range(n):
            f = max(0.0, min(1.0, self.hp / 20 - i))
            x = x0 + i * gap
            path = heart_path(x, y, s)
            p.setPen(mkpen(QColor(60, 30, 60, 170), 1.2))
            p.setBrush(QColor(40, 30, 50, 110))
            p.drawPath(path)
            if f > 0.25:
                p.save()
                p.setClipRect(QRectF(x - s * 2, y - s * 2, s * 4 * (1 if f >= 0.75 else 0.5), s * 4))
                p.setPen(NO_PEN)
                p.setBrush(QColor("#FF5C8A"))
                p.drawPath(path)
                p.setBrush(QColor(255, 255, 255, 150))
                p.drawEllipse(QPointF(x - s * 0.55, y - s * 0.35), 1.1, 1.1)
                p.restore()
        if self.shield > 0:
            p.setPen(NO_PEN)
            for i in range(self.shield):
                p.setBrush(QColor("#4A90FF"))
                p.drawEllipse(QPointF(cx + 34 + i * 7, y), 2.6, 2.6)

    def draw_floaters(self, p, cx):
        for text, age in self.floaters:
            a = max(0.0, 1 - age)
            pop = 1 + max(0.0, 0.35 - age) * 1.5
            f = QFont("Segoe UI", int(12 * pop))
            f.setWeight(QFont.Weight.Black)
            p.setFont(f)
            y = GROUND - 118 - age * 30
            fill = QColor("#FFD23F")
            fill.setAlpha(int(255 * a))
            outlined_text(p, QRectF(cx - 70, y - 14, 140, 28), text, fill,
                          QColor(60, 20, 60, int(255 * a)), 1)

    def draw_cloud(self, p, cx):
        t = self.t
        cy = GROUND - 40
        blobs = [(0, -8, 27), (-24, 2, 20), (24, 2, 20), (-13, -26, 18), (15, -26, 18),
                 (-30, -16, 14), (31, -16, 14), (0, 14, 18), (-16, 16, 13), (17, 16, 13)]
        for j in range(2):
            idx = int(t * 5) + j * 7
            rng = random.Random(idx)
            ang = rng.uniform(0, 2 * math.pi)
            kind = rng.choice(["horn_h", "horn_i", "tail_h", "tail_i",
                               "arm_h", "arm_i", "pillow", "snow"])
            ox, oy = cx + math.cos(ang) * 36, cy + math.sin(ang) * 26
            self.draw_poke(p, kind, ox, oy, math.degrees(ang) + 90)
        p.setPen(NO_PEN)
        p.setBrush(QColor("#CFCBE0"))
        for i, (dx, dy, r) in enumerate(blobs):
            j = math.sin(t * 30 + i * 1.7) * 3
            p.drawEllipse(QPointF(cx + dx + j, cy + dy - j * 0.6), r + 2, r + 2)
        p.setBrush(QColor("#F6F4FC"))
        for i, (dx, dy, r) in enumerate(blobs):
            j = math.sin(t * 30 + i * 1.7) * 3
            p.drawEllipse(QPointF(cx + dx + j, cy + dy - j * 0.6), r, r)
        self.draw_stars(p, cx, cy - 44)
        f = QFont("Segoe UI", 11)
        f.setWeight(QFont.Weight.Black)
        p.setFont(f)
        k = int(t / 0.45)
        rng = random.Random(k * 13)
        outlined_text(p, QRectF(cx - 60 + rng.uniform(-30, 30), cy - 72 + rng.uniform(-6, 6), 120, 24),
                      HIT_WORDS[k % len(HIT_WORDS)], QColor("#FFD23F"))

    def draw_poke(self, p, kind, x, y, rot):
        pets = {pp.name: pp for pp in self.world.pets}
        hy, ib = pets["Hybris"], pets["Iblis"]
        p.save()
        p.translate(x, y)
        p.rotate(rot)
        if kind.startswith("horn"):
            src = hy if kind == "horn_h" else ib
            p.setPen(mkpen(src.c_horn_line, 1.3))
            p.setBrush(src.c_horn)
            hp = QPainterPath(QPointF(-5, 4))
            hp.quadTo(QPointF(-3, -12), QPointF(2, -13))
            hp.quadTo(QPointF(6, -8), QPointF(5, 4))
            hp.closeSubpath()
            p.drawPath(hp)
        elif kind.startswith("tail"):
            src = hy if kind == "tail_h" else ib
            p.setPen(mkpen(src.c_line, 3.5))
            p.drawLine(QPointF(0, 6), QPointF(0, -8))
            p.setPen(mkpen(src.c_horn_line, 1.2))
            p.setBrush(src.c_horn)
            p.drawPath(heart_path(0, -12, 5))
        elif kind.startswith("arm"):
            src = hy if kind == "arm_h" else ib
            p.setPen(mkpen(src.c_line, 1.4))
            p.setBrush(src.c_body)
            p.drawEllipse(QPointF(0, -5), 6, 8)
        elif kind == "pillow":
            p.setPen(mkpen(QColor("#E58DB0"), 1.3))
            p.setBrush(QColor("#FFD3E6"))
            p.drawRoundedRect(QRectF(-10, -16, 20, 15), 6, 6)
        else:
            p.setPen(mkpen(QColor("#9CC9EA"), 1.2))
            p.setBrush(QColor("#FFFFFF"))
            p.drawEllipse(QPointF(0, -8), 7, 7)
        p.restore()

    def draw_bubble(self, p, cx, lift=0):
        if not self.bubble:
            return
        alpha = min(1.0, self.bubble_t / 0.3)
        f = QFont("Segoe UI", 9)
        f.setWeight(QFont.Weight.DemiBold)
        p.setFont(f)
        fm = QFontMetrics(f)
        bw = min(W - 6, fm.horizontalAdvance(self.bubble) + 24)
        bh = fm.height() + 12
        top = max(2, GROUND - 100 - bh - lift - (16 if self.is_idol else 0))
        rect = QRectF(cx - bw / 2, top, bw, bh)
        path = QPainterPath()
        path.addRoundedRect(rect, bh / 2, bh / 2)
        tail = QPainterPath()
        tail.addPolygon(QPolygonF([QPointF(cx - 6, top + bh - 1), QPointF(cx + 5, top + bh - 1),
                                   QPointF(cx - 1 + 6 * self.facing, top + bh + 7)]))
        path = path.united(tail)
        p.setOpacity(1.0)
        p.setPen(mkpen(QColor(90, 60, 110, int(90 * alpha)), 1.2))
        p.setBrush(QColor(255, 252, 255, int(245 * alpha)))
        p.drawPath(path)
        p.setPen(QColor(50, 30, 60, int(255 * alpha)))
        text = fm.elidedText(self.bubble, Qt.TextElideMode.ElideRight, int(bw - 14))
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)


# --------------------------------------------------------------------------- #
# Un habitant : enfant des fondateurs, conjoint venu du village, ou descendant.
# Il naît, grandit (bébé → enfant → ado → adulte → aîné), a des traits de
# caractère, des besoins, des relations, se marie, a des enfants, vieillit et
# finit par partir vers la lune. Tout est sauvegardé entre les lancements.
# --------------------------------------------------------------------------- #
def stage_of(age_h, scale=1.0):
    for name, end, size in STAGES:
        if age_h < end * scale:
            return name, size
    return STAGES[-1][0], STAGES[-1][2]


class Person(Pet):
    @staticmethod
    def make_traits(world, parents=None, village=False, gen=1):
        family = world.family
        used = {p.name for p in family.people} | {"Hybris", "Iblis"} | {m["name"] for m in family.memorial}
        if village:
            names = [n for n in VILLAGE_NAMES if n not in used] or VILLAGE_NAMES
            h, s, l = rnd(0, 360), rnd(0.45, 0.75), rnd(0.5, 0.68)
            pa, pb = random.choice(("Hybris", "Iblis")), random.choice(("Hybris", "Iblis"))
            persona = random.sample(PERSONAS, 2)
            pnames = []
        else:
            names = [n for n in KID_NAMES if n not in used] or KID_NAMES
            pa_sk, pb_sk = parents[0].sk["body"], parents[1].sk["body"]
            t = rnd(0.25, 0.75)
            dh = ((pb_sk[0] - pa_sk[0] + 180) % 360) - 180
            h = (pa_sk[0] + dh * t) % 360
            s = (pa_sk[1] + pb_sk[1]) / 2 * rnd(0.9, 1.1)
            l = min(0.72, (pa_sk[2] + pb_sk[2]) / 2 + rnd(0.04, 0.12))
            pa = parents[0].sk.get("horn_src", parents[0].name if parents[0].name in SKINS else "Hybris")
            pb = parents[1].sk.get("horn_src", parents[1].name if parents[1].name in SKINS else "Iblis")
            inherited = [tr for par in parents for tr in getattr(par, "persona", [])]
            persona = []
            if inherited and random.random() < 0.6:
                persona.append(random.choice(inherited))
            while len(persona) < 2:
                tr = random.choice(PERSONAS)
                if tr not in persona:
                    persona.append(tr)
            pnames = [par.name for par in parents]
        return dict(name=random.choice(names), hue=round(h, 1), sat=round(min(0.85, s), 3),
                    lig=round(l, 3), horn=random.choice((pa, pb)), tail=random.choice((pa, pb)),
                    iris=random.choice(("Hybris", "Iblis")),
                    acc=random.choice(["noeud", "helice", "lunettes", None]),
                    age=0.0, gen=gen, parents=pnames, persona=persona,
                    lifespan=round(rnd(*LIFESPAN), 1), born=datetime.date.today().isoformat(),
                    spouse=None, visitor=village, grade=2.0, obedience=50.0,
                    rel={}, romance={}, hunger=80.0, social=80.0, stories=0)

    @staticmethod
    def skin_from(tr):
        base = SKINS.get(tr.get("horn"), SKINS["Hybris"])
        other = SKINS["Iblis" if tr.get("iris") == "Hybris" else "Hybris"]
        h, s, l = tr["hue"], tr["sat"], tr["lig"]
        return dict(body=(h, s, l), belly=(h, s * 0.9, min(0.82, l + 0.12)),
                    horn=base["horn"], horn_line=base["horn_line"],
                    tail_tip=SKINS.get(tr.get("tail"), SKINS["Iblis"])["tail_tip"],
                    horn_shape=base["horn_shape"], horn_src=tr.get("horn", "Hybris"),
                    blush="#FF9ECF", iris_top=SKINS.get(tr.get("iris"), SKINS["Hybris"])["iris_top"],
                    iris_bot=other["iris_bot"], mark="")

    def __init__(self, world, traits):
        super().__init__(traits["name"], world, skin=self.skin_from(traits), size=0.55)
        self.is_kid = True                         # « habitant » (pas un fondateur)
        self.traits = traits
        self.age = float(traits.get("age", 0.0))
        self.accessory = traits.get("acc")
        self.persona = list(traits.get("persona", []))
        self.gen = int(traits.get("gen", 1))
        self.parents = list(traits.get("parents", []))
        self.spouse = traits.get("spouse")
        self.visitor = bool(traits.get("visitor", False))
        self.lifespan = float(traits.get("lifespan", 47.0))
        self.grade = float(traits.get("grade", 2.0))
        self.obedience = float(traits.get("obedience", 50.0))
        self.rel = dict(traits.get("rel", {}))
        self.romance = dict(traits.get("romance", {}))
        self.hunger = float(traits.get("hunger", 80.0))
        self.social = float(traits.get("social", 80.0))
        self.stories = int(traits.get("stories", 0))
        self.attach = random.randrange(2)
        self.lonely_t = self.cry_cd = self.ride_t = 0.0
        self.leaving = None
        self.duty = None
        self.study_t = self.work_t = self.punished_t = self.ribbon_t = 0.0
        self.stay_h = 0.0
        self.farewell = False
        self.dead = False
        self.moodlets = []
        self.mischief_cd = rnd(300, 900)
        self.court_cd = 0.0
        self.engaged = False
        self.energy = rnd(50, 90)
        self.stage = None
        self.apply_stage()

    # ---- étapes de vie ----
    def apply_stage(self):
        stage, size = stage_of(self.age, self.world.family.scale)
        changed = stage != self.stage
        self.stage, self.size = stage, size
        self.eye_k = {"bébé": 1.3, "enfant": 1.15, "ado": 1.05, "adulte": 1.0, "aîné": 1.0}[stage]
        base = SKINS.get(self.traits.get("horn"), SKINS["Hybris"])
        if stage == "aîné":                                   # cornes pâlies
            c = QColor(base["horn"])
            self.c_horn = QColor((c.red() + 200) // 2, (c.green() + 200) // 2, (c.blue() + 205) // 2)
        else:
            self.c_horn = QColor(base["horn"])
        return changed

    def is_minor(self):
        return self.stage in ("bébé", "enfant", "ado")

    def is_adult(self):
        return self.stage in ("adulte", "aîné")

    def walk_speed(self):
        return {"bébé": 56, "enfant": 66, "ado": 76, "adulte": 62, "aîné": 42}[self.stage]

    def run_speed(self):
        return {"bébé": 115, "enfant": 135, "ado": 155, "adulte": 170, "aîné": 95}[self.stage]

    def has(self, trait):
        return trait in self.persona

    def lineage(self):
        """Noms des ascendants connus (2 générations) pour éviter les mariages consanguins."""
        fam = self.world.family
        out = set(self.parents)
        for pn in self.parents:
            par = fam.by_name(pn)
            if par is not None and hasattr(par, "parents"):
                out |= set(par.parents)
        return out

    def related(self, other):
        if other.name in self.parents or self.name in getattr(other, "parents", []):
            return True
        la, lb = self.lineage(), getattr(other, "lineage", lambda: set())()
        return bool(la & lb) or other.name in la or self.name in lb

    def mood_score(self):
        base = (self.energy + self.fun + self.social + self.hunger) / 4
        return max(0.0, min(100.0, base + sum(v for v, _ in self.moodlets)))

    def add_moodlet(self, value, hours=4.0):
        self.moodlets.append([value, self.world.family.hours + hours])

    def opinion(self, name):
        return self.rel.get(name, 0.0)

    def like(self, name, delta, cap=100.0):
        self.rel[name] = max(-100.0, min(cap, self.rel.get(name, 0.0) + delta))

    def to_dict(self):
        d = dict(self.traits)
        d.update(age=round(self.age, 3), spouse=self.spouse, visitor=self.visitor,
                 grade=round(self.grade, 2), obedience=round(self.obedience, 1),
                 rel={k: round(v, 1) for k, v in self.rel.items()},
                 romance={k: round(v, 1) for k, v in self.romance.items()},
                 hunger=round(self.hunger, 1), social=round(self.social, 1),
                 persona=self.persona, gen=self.gen, parents=self.parents,
                 lifespan=self.lifespan, stories=self.stories)
        return d

    def snapshot(self):
        d = Pet.snapshot(self)
        d["kid"] = True
        return d

    # ---- dessin : lunettes, canne, ruban, cartable, livre, ordinateur ----
    def draw_accessory(self, p):
        st = self.stage
        t = self.t
        if st == "aîné":
            p.setPen(mkpen(QColor("#6A5A80"), 1.6))
            p.setBrush(QColor(255, 255, 255, 60))
            for ex in (-12, 13):
                p.drawEllipse(QPointF(ex, -36), 9.5, 9.5)
            p.drawLine(QPointF(-2.5, -36), QPointF(3.5, -36))
            p.setPen(mkpen(QColor("#8A5A2B"), 3.2))                  # canne
            p.drawLine(QPointF(40, -30), QPointF(44, -2))
            p.setPen(mkpen(QColor("#8A5A2B"), 3.2))
            p.drawArc(QRectF(34, -38, 12, 10), 0, 180 * 16)
        else:
            Pet.draw_accessory(self, p)
        if self.ribbon_t > 0:                                       # ruban de deuil
            p.setPen(NO_PEN)
            p.setBrush(QColor("#2A2A36"))
            p.drawPolygon(QPolygonF([QPointF(-24, -30), QPointF(-16, -20), QPointF(-20, -12),
                                     QPointF(-28, -22)]))
        if self.visitor and self.state in ("idle", "walk"):         # petite valise
            p.setPen(mkpen(QColor("#7A4E24"), 1.3))
            p.setBrush(QColor("#C98A4B"))
            p.drawRoundedRect(QRectF(-48, -22, 16, 12), 2, 2)
            p.drawLine(QPointF(-43, -22), QPointF(-37, -22))
        if self.duty in ("school", "study") and self.state in ("idle", "sleep"):   # livre
            p.save()
            p.translate(36, -40 + math.sin(t * 2) * 1.5)
            p.rotate(-12)
            p.setPen(mkpen(QColor("#2B5FB3"), 1.3))
            p.setBrush(QColor("#4A90FF"))
            p.drawRoundedRect(QRectF(-9, -7, 18, 14), 2, 2)
            p.setPen(mkpen(QColor("#FFFFFF"), 1.0))
            p.drawLine(QPointF(0, -6), QPointF(0, 6))
            p.drawLine(QPointF(-6, -3), QPointF(-2, -3))
            p.drawLine(QPointF(2, -3), QPointF(6, -3))
            p.restore()
        if self.duty == "work" and self.state == "idle":            # ordinateur portable
            p.setPen(mkpen(QColor("#3A3F52"), 1.3))
            p.setBrush(QColor("#5A6078"))
            p.drawRoundedRect(QRectF(26, -12, 26, 4), 1, 1)
            p.setBrush(QColor("#1E2233"))
            p.drawRoundedRect(QRectF(28, -30, 22, 18), 2, 2)
            p.setPen(NO_PEN)
            p.setBrush(QColor("#3DDC84") if int(t * 3) % 2 else QColor("#5EE6FF"))
            for i in range(3):
                p.drawRect(QRectF(31, -27 + i * 4, 6 + (i * 5 + int(t * 4)) % 12, 2))


# --------------------------------------------------------------------------- #
# Fenêtres « décor » : projectiles, coffres, pièges, loots.
# Toutes transparentes aux clics.
# --------------------------------------------------------------------------- #
class Overlay(QWidget):
    def __init__(self, size):
        super().__init__(None, Qt.WindowType.FramelessWindowHint
                         | Qt.WindowType.WindowStaysOnTopHint
                         | Qt.WindowType.Tool
                         | Qt.WindowType.WindowTransparentForInput
                         | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setFixedSize(size, size)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.paint(p)
        p.end()

    def paint(self, p):
        pass

    def kill(self):
        self.hide()
        self.deleteLater()


class Shot(Overlay):
    """Projectile : boule de neige (Hybris), oreiller (Iblis) ou fléchette Nerf."""

    def __init__(self, owner, target, x, y, vx, vy, g, dmg, kind=None):
        super().__init__(SHOT)
        self.owner, self.target = owner, target
        self.x, self.y, self.vx, self.vy, self.g, self.dmg = x, y, vx, vy, g, dmg
        self.kind = kind or ("pillow" if owner.name == "Iblis" else "snow")
        self.dodge = g == 0 and random.random() < 0.35
        self.t = 0.0
        self.spin = rnd(-400, 400) if self.kind == "pillow" else 0
        self.step(0)
        self.show()

    def step(self, dt):
        self.t += dt
        self.vy += self.g * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.move(int(self.x - SHOT / 2), int(self.y - SHOT / 2))
        self.update()

    def paint(self, p):
        c = SHOT / 2
        v = math.hypot(self.vx, self.vy) or 1
        ux, uy = -self.vx / v, -self.vy / v
        p.setPen(NO_PEN)
        for k in range(3):                                   # petite traînée
            d = 12 + k * 6
            col = (QColor(255, 220, 235, 120 - k * 35) if self.kind == "pillow"
                   else QColor(220, 240, 255, 130 - k * 38))
            p.setBrush(col)
            p.drawEllipse(QPointF(c + ux * d, c + uy * d), 4 - k, 4 - k)
        p.save()
        p.translate(c, c)
        if self.kind == "pillow":
            p.rotate(self.t * self.spin)
            p.setPen(mkpen(QColor("#E58DB0"), 1.5))
            p.setBrush(QColor("#FFD6E8"))
            p.drawRoundedRect(QRectF(-12, -9, 24, 18), 7, 7)
            p.setPen(mkpen(QColor("#F2A9C8"), 1.1))
            p.drawLine(QPointF(-7, 0), QPointF(7, 0))
            p.setPen(NO_PEN)
            p.setBrush(QColor("#E58DB0"))
            for sx, sy in ((-12, -9), (12, -9), (-12, 9), (12, 9)):
                p.drawEllipse(QPointF(sx, sy), 2, 2)
        elif self.kind == "dart":
            p.rotate(math.degrees(math.atan2(self.vy, self.vx)))
            p.setPen(mkpen(QColor("#B85A1C"), 1.3))
            p.setBrush(QColor("#FF8A3D"))
            p.drawRoundedRect(QRectF(-12, -4, 20, 8), 3, 3)
            p.setBrush(QColor("#3B6CFF"))
            p.drawEllipse(QPointF(10, 0), 5, 5)
        else:
            g = QRadialGradient(QPointF(-3, -3), 12)
            g.setColorAt(0, QColor("#FFFFFF"))
            g.setColorAt(0.7, QColor("#EAF6FF"))
            g.setColorAt(1, QColor("#B8DDF7"))
            p.setPen(mkpen(QColor("#9CC9EA"), 1.2))
            p.setBrush(g)
            p.drawEllipse(QPointF(0, 0), 10, 10)
            p.setPen(NO_PEN)
            p.setBrush(QColor("#FFE066"))
            p.drawPolygon(star_poly(6, -7, 3.5, 1.1, 4, self.t * 6))
        p.restore()


class Prop(Overlay):
    """Coffre, peau de banane ou loot qui s'envole. Posé au sol en (x, y)."""

    def __init__(self, kind, x, y, item=None, hue=300.0, label=""):
        super().__init__(PROP if kind not in WIDE_PROPS else PROP * 2)
        self.kind, self.x, self.y, self.item = kind, x, y, item
        self.hue = hue
        self.label = label
        self.flowers = 0
        self.crack = 0.0                       # œuf : avancement de l'éclosion
        self.t = rnd(0, 6)
        self.open_t = 0.0                      # > 0 : animation d'ouverture
        self.opened = False
        self.age = 0.0
        w = self.width()
        self.move(int(x - w / 2), int(y - w + 8))
        self.show()

    def place(self, x, y):
        self.x, self.y = x, y
        w = self.width()
        self.move(int(x - w / 2), int(y - w + 8))

    def step(self, dt):
        self.t += dt
        self.age += dt
        if self.opened:
            self.open_t += dt
        self.update()

    def paint(self, p):
        w = self.width()
        cx, gy = w / 2, w - 8
        if self.kind == "chest":
            self.paint_chest(p, cx, gy)
        elif self.kind == "egg":
            self.paint_egg(p, cx, gy)
        elif self.kind in DECOR_PAINTERS:
            DECOR_PAINTERS[self.kind](self, p, cx, gy)
        elif self.kind == "banane":
            p.setPen(NO_PEN)
            p.setBrush(QColor(0, 0, 0, 45))
            p.drawEllipse(QPointF(cx, gy - 1), 16, 4)
            draw_item_icon(p, "banane", cx, gy - 7, 1.4)
        elif self.kind == "loot":
            a = max(0.0, 1 - self.age / 1.4)
            p.setOpacity(min(1.0, a * 2))
            draw_item_icon(p, self.item, cx, gy - 30 - self.age * 26, 1.3)
            p.setOpacity(1.0)
            p.setPen(NO_PEN)
            for i in range(5):
                ang = self.age * 3 + i * 1.26
                c = QColor("#FFE066")
                c.setAlpha(int(255 * a))
                p.setBrush(c)
                p.drawPolygon(star_poly(cx + math.cos(ang) * (18 + self.age * 20),
                                        gy - 30 - self.age * 10 + math.sin(ang) * 10, 4, 1.4, 4))

    def paint_egg(self, p, cx, gy):
        t = self.t
        p.setPen(NO_PEN)
        p.setBrush(QColor(0, 0, 0, 50))
        p.drawEllipse(QPointF(cx, gy - 1), 18, 4)
        spot = hsl(self.hue, 0.5, 0.72)
        line = QColor("#D9C3A5")
        shell = QColor("#FFF6E8")
        if self.opened:                                          # éclosion : les deux moitiés
            k = min(1.0, self.open_t / 0.5)
            p.save()
            p.translate(cx, gy)
            p.setPen(mkpen(line, 1.5))
            p.setBrush(shell)
            half = QPainterPath(QPointF(-16, -18))
            half.lineTo(QPointF(-12, -10))
            half.lineTo(QPointF(-6, -18))
            half.lineTo(QPointF(0, -10))
            half.lineTo(QPointF(6, -18))
            half.lineTo(QPointF(12, -10))
            half.lineTo(QPointF(16, -18))
            half.quadTo(QPointF(16, 2), QPointF(0, 2))
            half.quadTo(QPointF(-16, 2), QPointF(-16, -18))
            p.drawPath(half)
            p.translate(-10 * k, -46 - 40 * k)
            p.rotate(-35 * k)
            p.drawEllipse(QPointF(0, 0), 15, 13)
            p.restore()
            p.setPen(NO_PEN)
            for i in range(6):
                ang = self.open_t * 4 + i * 1.05
                c = QColor("#FFE066")
                c.setAlpha(int(255 * max(0.0, 1 - self.open_t / 1.2)))
                p.setBrush(c)
                p.drawPolygon(star_poly(cx + math.cos(ang) * (16 + self.open_t * 30),
                                        gy - 24 + math.sin(ang) * 12 - self.open_t * 10, 4, 1.4, 4))
            return
        wob = math.sin(t * 7) * (3 + self.crack * 9) if self.crack > 0.3 else math.sin(t * 2) * 2
        p.save()
        p.translate(cx, gy)
        p.rotate(wob)
        p.setPen(mkpen(line, 1.6))
        p.setBrush(shell)
        egg = QPainterPath(QPointF(0, 0))
        egg.cubicTo(QPointF(-22, 0), QPointF(-18, -40), QPointF(0, -46))
        egg.cubicTo(QPointF(18, -40), QPointF(22, 0), QPointF(0, 0))
        p.drawPath(egg)
        p.setPen(NO_PEN)
        p.setBrush(spot)
        for sx, sy, r in ((-7, -28, 4), (6, -18, 3.5), (2, -36, 2.6), (-4, -10, 2.8)):
            p.drawEllipse(QPointF(sx, sy), r, r * 0.8)
        p.setBrush(QColor(255, 255, 255, 120))
        p.drawEllipse(QPointF(-7, -36), 4, 6)
        if self.crack > 0.5:                                     # fissures
            p.setPen(mkpen(QColor("#8A7A5A"), 1.3))
            n = 1 + int((self.crack - 0.5) * 8)
            for i in range(min(n, 4)):
                x0, y0 = -10 + i * 7, -22 - (i % 2) * 6
                p.drawPolyline(QPolygonF([QPointF(x0, y0), QPointF(x0 + 3, y0 - 5),
                                          QPointF(x0 + 5, y0 + 2), QPointF(x0 + 9, y0 - 3)]))
        p.restore()

    def paint_chest(self, p, cx, gy):
        t = self.t
        # ombre + corps
        p.setPen(NO_PEN)
        p.setBrush(QColor(0, 0, 0, 55))
        p.drawEllipse(QPointF(cx, gy - 1), 24, 5)
        bob = 0 if self.opened else abs(math.sin(t * 2.5)) * 1.5
        p.save()
        p.translate(cx, gy - bob)
        wood, dark, gold = QColor("#C98A4B"), QColor("#7A4E24"), QColor("#FFD23F")
        p.setPen(mkpen(dark, 1.6))
        p.setBrush(wood)
        p.drawRoundedRect(QRectF(-22, -22, 44, 22), 4, 4)                     # coffre
        p.setPen(mkpen(dark, 1.2))
        for x in (-12, 12):
            p.drawLine(QPointF(x, -22), QPointF(x, 0))
        if self.opened:                                                        # lueur
            k = min(1.0, self.open_t / 0.4)
            g = QRadialGradient(QPointF(0, -20), 30)
            g.setColorAt(0, QColor(255, 240, 150, int(230 * k)))
            g.setColorAt(1, QColor(255, 240, 150, 0))
            p.setPen(NO_PEN)
            p.setBrush(g)
            p.drawEllipse(QPointF(0, -20), 34, 26)
        # couvercle (tourne autour de l'arrière)
        p.save()
        p.translate(0, -22)
        if self.opened:
            p.rotate(-min(1.0, self.open_t / 0.35) * 105)
        lid = QPainterPath(QPointF(-22, 0))
        lid.lineTo(QPointF(22, 0))
        lid.lineTo(QPointF(22, -8))
        lid.quadTo(QPointF(0, -22), QPointF(-22, -8))
        lid.closeSubpath()
        p.setPen(mkpen(dark, 1.6))
        p.setBrush(wood.lighter(108))
        p.drawPath(lid)
        p.setPen(mkpen(dark, 1.2))
        for x in (-12, 12):
            p.drawLine(QPointF(x, 0), QPointF(x, -13))
        p.restore()
        p.setPen(mkpen(QColor("#B8901F"), 1.2))                                # serrure
        p.setBrush(gold)
        p.drawRoundedRect(QRectF(-5, -26, 10, 9), 2, 2)
        p.setBrush(dark)
        p.setPen(NO_PEN)
        p.drawEllipse(QPointF(0, -22), 1.6, 1.6)
        p.restore()
        if not self.opened and int(t * 1.3) % 3 == 0:                          # petite étincelle
            ph = (t * 1.3) % 1
            c = QColor("#FFE066")
            c.setAlpha(int(255 * (1 - ph)))
            p.setBrush(c)
            p.drawPolygon(star_poly(cx + 18, gy - 34 - ph * 8, 4 + ph * 2, 1.4, 4, ph * 3))


# --------------------------------------------------------------------------- #
# Décor du village : maison, école, bureau, gâteau, arche de mariage, tombe,
# gribouillis, cadeau. Dessinés au sol en (x, y).
# --------------------------------------------------------------------------- #
WIDE_PROPS = ("maison", "ecole", "arche", "banniere")


def _shadow(p, cx, gy, rx=22):
    p.setPen(NO_PEN)
    p.setBrush(QColor(0, 0, 0, 45))
    p.drawEllipse(QPointF(cx, gy - 1), rx, 4)


def paint_maison(pr, p, cx, gy):
    _shadow(p, cx, gy, 44)
    p.setPen(mkpen(QColor("#7A4E24"), 1.6))
    p.setBrush(QColor("#F3DFC4"))
    p.drawRoundedRect(QRectF(cx - 42, gy - 44, 84, 44), 4, 4)               # murs
    p.setBrush(QColor("#E0304A"))
    p.drawPolygon(QPolygonF([QPointF(cx - 50, gy - 44), QPointF(cx, gy - 82), QPointF(cx + 50, gy - 44)]))
    p.setBrush(QColor("#8A5A2B"))
    p.drawRoundedRect(QRectF(cx - 10, gy - 30, 20, 30), 3, 3)               # porte
    p.setPen(NO_PEN)
    p.setBrush(QColor("#FFD23F"))
    p.drawEllipse(QPointF(cx + 5, gy - 15), 1.8, 1.8)
    p.setPen(mkpen(QColor("#7A4E24"), 1.3))
    p.setBrush(QColor("#BDE8FF"))
    for wx in (cx - 28, cx + 28):                                            # fenêtres
        p.drawRoundedRect(QRectF(wx - 8, gy - 36, 16, 12), 2, 2)
        p.drawLine(QPointF(wx, gy - 36), QPointF(wx, gy - 24))
    p.setPen(mkpen(QColor("#7A4E24"), 1.3))
    p.setBrush(QColor("#9AA0B4"))
    p.drawRect(QRectF(cx + 24, gy - 78, 8, 16))                              # cheminée
    if int(pr.t) % 2 == 0:
        p.setPen(NO_PEN)
        for i in range(3):
            c = QColor(220, 220, 235, 120 - i * 35)
            p.setBrush(c)
            p.drawEllipse(QPointF(cx + 28 + i * 4 + math.sin(pr.t + i) * 2, gy - 84 - i * 8), 4 + i * 1.5, 4 + i * 1.5)
    f = QFont("Segoe UI", 7)
    f.setBold(True)
    p.setFont(f)
    p.setPen(QColor("#7A4E24"))
    p.drawText(QRectF(cx - 40, gy - 10, 80, 10), Qt.AlignmentFlag.AlignCenter, pr.label or "H13ris & Cie")


def paint_ecole(pr, p, cx, gy):
    _shadow(p, cx, gy, 30)
    p.setPen(mkpen(QColor("#7A4E24"), 1.6))
    p.setBrush(QColor("#8A5A2B"))
    p.drawRect(QRectF(cx - 2, gy - 40, 4, 40))                               # poteau
    p.setBrush(QColor("#2B5FB3"))
    p.drawRoundedRect(QRectF(cx - 34, gy - 66, 68, 30), 4, 4)                # panneau
    p.setPen(NO_PEN)
    p.setBrush(QColor("#FFD23F"))
    p.drawPolygon(QPolygonF([QPointF(cx - 30, gy - 66), QPointF(cx, gy - 80), QPointF(cx + 30, gy - 66)]))
    f = QFont("Segoe UI", 8)
    f.setBold(True)
    p.setFont(f)
    p.setPen(QColor("#FFFFFF"))
    p.drawText(QRectF(cx - 34, gy - 66, 68, 30), Qt.AlignmentFlag.AlignCenter, "ÉCOLE")
    p.setPen(mkpen(QColor("#1F7A99"), 1.2))                                  # petit tableau
    p.setBrush(QColor("#2F6B4F"))
    p.drawRoundedRect(QRectF(cx + 24, gy - 30, 30, 22), 2, 2)
    p.setPen(mkpen(QColor("#FFFFFF"), 1.0))
    p.drawText(QRectF(cx + 24, gy - 30, 30, 22), Qt.AlignmentFlag.AlignCenter, "2+2")


def paint_bureau(pr, p, cx, gy):
    _shadow(p, cx, gy, 30)
    p.setPen(mkpen(QColor("#7A4E24"), 1.4))
    p.setBrush(QColor("#C98A4B"))
    p.drawRoundedRect(QRectF(cx - 30, gy - 30, 60, 6), 2, 2)                # plateau
    p.drawRect(QRectF(cx - 26, gy - 24, 4, 24))
    p.drawRect(QRectF(cx + 22, gy - 24, 4, 24))
    p.setPen(mkpen(QColor("#3A3F52"), 1.3))
    p.setBrush(QColor("#1E2233"))
    p.drawRoundedRect(QRectF(cx - 16, gy - 54, 32, 22), 2, 2)                # écran
    p.setBrush(QColor("#5A6078"))
    p.drawRect(QRectF(cx - 3, gy - 32, 6, 3))
    p.setPen(NO_PEN)
    for i in range(4):                                                       # lignes de logs
        p.setBrush(QColor("#3DDC84") if (i + int(pr.t * 2)) % 3 else QColor("#FF5C8A"))
        p.drawRect(QRectF(cx - 12, gy - 50 + i * 4.5, 6 + (i * 7 + int(pr.t * 5)) % 16, 2))
    p.setBrush(QColor("#E0304A"))
    p.drawEllipse(QPointF(cx + 24, gy - 36), 3.5, 3.5)                       # mug
    p.setPen(mkpen(QColor("#E0304A"), 1.2))
    p.setBrush(NO_BRUSH)
    p.drawArc(QRectF(cx + 26, gy - 39, 5, 6), -90 * 16, 180 * 16)


def paint_gateau(pr, p, cx, gy):
    _shadow(p, cx, gy, 20)
    p.setPen(mkpen(QColor("#B0607A"), 1.3))
    p.setBrush(QColor("#FFC1D9"))
    p.drawRoundedRect(QRectF(cx - 20, gy - 18, 40, 18), 4, 4)
    p.setBrush(QColor("#FFF1F6"))
    p.drawRoundedRect(QRectF(cx - 20, gy - 20, 40, 6), 3, 3)
    p.setBrush(QColor("#FFD6E8"))
    p.drawRoundedRect(QRectF(cx - 13, gy - 30, 26, 12), 3, 3)
    p.setPen(NO_PEN)
    for i, bx in enumerate((cx - 8, cx, cx + 8)):                            # bougies
        p.setBrush(QColor("#5EE6FF") if i % 2 else QColor("#FFD23F"))
        p.drawRect(QRectF(bx - 1.5, gy - 40, 3, 10))
        p.setBrush(QColor("#FF8A3D"))
        p.drawEllipse(QPointF(bx, gy - 43 + math.sin(pr.t * 12 + i) * 0.8), 2, 3)
    p.setBrush(QColor("#E0304A"))
    p.drawEllipse(QPointF(cx - 12, gy - 16), 2, 2)
    p.drawEllipse(QPointF(cx + 10, gy - 12), 2, 2)


def paint_arche(pr, p, cx, gy):
    _shadow(p, cx, gy, 40)
    p.setPen(mkpen(QColor("#F6DB8C"), 5))
    p.setBrush(NO_BRUSH)
    p.drawArc(QRectF(cx - 46, gy - 100, 92, 120), 0, 180 * 16)
    p.setPen(NO_PEN)
    for i in range(14):
        a = math.pi * i / 13
        fx, fy = cx + 46 * math.cos(a), gy - 40 - 60 * math.sin(a)
        p.setBrush(QColor(["#FF7FA0", "#FFD23F", "#7FD3FF", "#B39DFF"][i % 4]))
        p.drawEllipse(QPointF(fx, fy), 5, 5)
        p.setBrush(QColor("#FFFFFF"))
        p.drawEllipse(QPointF(fx, fy), 1.6, 1.6)
    if pr.opened:                                                            # confettis
        for i in range(10):
            ph = (pr.open_t * 0.6 + i * 0.1) % 1
            c = QColor(["#FF7FA0", "#FFD23F", "#7FD3FF", "#3DDC84"][i % 4])
            c.setAlpha(int(230 * (1 - ph)))
            p.setBrush(c)
            p.drawRect(QRectF(cx - 40 + i * 8 + math.sin(pr.t * 5 + i) * 6, gy - 100 + ph * 90, 4, 4))


def paint_tombe(pr, p, cx, gy):
    _shadow(p, cx, gy, 16)
    p.setPen(mkpen(QColor("#6A6E86"), 1.4))
    p.setBrush(QColor("#B9BFD2"))
    p.drawRoundedRect(QRectF(cx - 14, gy - 36, 28, 36), 8, 8)
    p.setPen(NO_PEN)
    p.setBrush(QColor("#8F96AE"))
    p.drawRect(QRectF(cx - 18, gy - 4, 36, 4))
    f = QFont("Segoe UI", 6)
    f.setBold(True)
    p.setFont(f)
    p.setPen(QColor("#3A3F52"))
    p.drawText(QRectF(cx - 14, gy - 32, 28, 10), Qt.AlignmentFlag.AlignCenter, (pr.label or "")[:7])
    p.setPen(QColor("#6A6E86"))
    p.drawText(QRectF(cx - 14, gy - 22, 28, 10), Qt.AlignmentFlag.AlignCenter, "☾")
    p.setPen(NO_PEN)
    for i in range(min(4, pr.flowers)):                                     # fleurs
        fx = cx - 12 + i * 8
        p.setBrush(QColor("#3DDC84"))
        p.drawRect(QRectF(fx - 0.7, gy - 8, 1.4, 8))
        p.setBrush(QColor(["#FF7FA0", "#FFD23F", "#7FD3FF", "#B39DFF"][i % 4]))
        p.drawEllipse(QPointF(fx, gy - 9), 3, 3)
    p.setBrush(QColor("#FFD23F"))                                            # petite étoile
    p.drawPolygon(star_poly(cx + 16, gy - 42 + math.sin(pr.t * 2) * 2, 3.5, 1.4))


def paint_gribouillis(pr, p, cx, gy):
    p.setPen(mkpen(QColor("#FF7FA0"), 2.2))
    p.setBrush(NO_BRUSH)
    rng = random.Random(int(pr.hue))
    path = QPainterPath(QPointF(cx - 24, gy - 8))
    for i in range(7):
        path.quadTo(QPointF(cx - 24 + i * 8 + rng.uniform(-6, 6), gy - 22 + rng.uniform(-6, 6)),
                    QPointF(cx - 20 + i * 7, gy - 6 + rng.uniform(-6, 2)))
    p.drawPath(path)
    p.setPen(mkpen(QColor("#5EE6FF"), 2.0))
    p.drawEllipse(QPointF(cx + 12, gy - 16), 7, 7)
    p.drawLine(QPointF(cx + 9, gy - 17), QPointF(cx + 11, gy - 17))
    p.drawLine(QPointF(cx + 13, gy - 17), QPointF(cx + 15, gy - 17))
    p.drawArc(QRectF(cx + 8, gy - 16, 8, 5), 0, -180 * 16)


def paint_cadeau(pr, p, cx, gy):
    _shadow(p, cx, gy, 14)
    bob = abs(math.sin(pr.t * 3)) * 2
    p.setPen(mkpen(QColor("#B0607A"), 1.3))
    p.setBrush(QColor("#FF7FA0"))
    p.drawRoundedRect(QRectF(cx - 12, gy - 20 - bob, 24, 20), 3, 3)
    p.setPen(NO_PEN)
    p.setBrush(QColor("#FFD23F"))
    p.drawRect(QRectF(cx - 2, gy - 20 - bob, 4, 20))
    p.drawRect(QRectF(cx - 12, gy - 12 - bob, 24, 4))
    p.setPen(mkpen(QColor("#C9971F"), 1.2))
    p.setBrush(NO_BRUSH)
    p.drawEllipse(QPointF(cx - 4, gy - 24 - bob), 4, 3)
    p.drawEllipse(QPointF(cx + 4, gy - 24 - bob), 4, 3)


DECOR_PAINTERS = dict(maison=paint_maison, ecole=paint_ecole, bureau=paint_bureau, gateau=paint_gateau,
                      arche=paint_arche, tombe=paint_tombe, gribouillis=paint_gribouillis, cadeau=paint_cadeau)


# --------------------------------------------------------------------------- #
# Liaison entre instances : chaque processus publie son état ~12 fois/s dans
# un petit fichier JSON du dossier temporaire et lit ceux des autres.
# Zéro réseau, zéro port ouvert. L'instance la plus ancienne est l'« arbitre » :
# elle sème les coffres, tranche qui les ouvre, et ses démons forment la Garde.
# --------------------------------------------------------------------------- #
class RemotePet:
    """Vue locale d'un pet d'une autre instance (position extrapolée)."""

    def __init__(self, iid, role, d, t_recv):
        self.iid, self.role = iid, role
        self.name = d.get("n", "?")
        self.x0, self.y0, self.vx = d.get("x", 0), d.get("y", 0), d.get("vx", 0)
        self.state = d.get("st", "idle")
        self.hp = d.get("hp", 100)
        self.hid = bool(d.get("hid", False))
        self.gone = bool(d.get("gone", False))
        self.facing = d.get("f", 1)
        self.item = d.get("it")
        self.veh = bool(d.get("veh", False))
        self.shield = d.get("sh", 0)
        self.fly = d.get("fly")
        self.t_recv = t_recv
        self.cloud_t = 0.0
        self.key = (iid, self.name)

    def cx(self):
        return self.x0 + self.vx * min(0.3, max(0.0, time.monotonic() - self.t_recv))

    def feet(self):
        return self.y0

    def moving(self):
        return abs(self.vx) > 20 or self.state in ("walk", "fall")

    def active(self):
        return not self.gone and self.state not in ("ghost", "gone")


class Link:
    STALE = 4.0          # s sans nouvelles : l'instance est considérée partie

    def __init__(self):
        self.dir = os.path.join(tempfile.gettempdir(), "h13ris_pets")
        self.iid = "%x%04x" % (os.getpid(), random.randrange(65536))
        self.born = time.time()
        self.path = os.path.join(self.dir, "inst_%s.json" % self.iid)
        self.seq = 0
        self.events = []
        self.peers = {}          # iid -> dict(state, seen, last_seq)
        self.inbox = []          # (iid, event)
        self.ok = True
        try:
            os.makedirs(self.dir, exist_ok=True)
            self.cleanup()
        except OSError:
            self.ok = False

    def cleanup(self):
        now = time.time()
        for fn in os.listdir(self.dir):
            fp = os.path.join(self.dir, fn)
            try:
                if now - os.path.getmtime(fp) > 30:
                    os.remove(fp)
            except OSError:
                pass

    def emit(self, **ev):
        self.seq += 1
        ev["seq"] = self.seq
        self.events.append(ev)
        self.events = self.events[-40:]

    def publish(self, state):
        if not self.ok:
            return
        state.update(iid=self.iid, born=self.born, t=time.time(), ev=self.events)
        tmp = self.path + ".tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(state, f, separators=(",", ":"))
            os.replace(tmp, self.path)
        except OSError:
            pass

    def poll(self):
        """Lit les autres instances. Renvoie (arrivées, départs)."""
        if not self.ok:
            return [], []
        now = time.time()
        found = set()
        try:
            names = os.listdir(self.dir)
        except OSError:
            return [], []
        for fn in names:
            if not fn.startswith("inst_") or not fn.endswith(".json"):
                continue
            iid = fn[5:-5]
            if iid == self.iid:
                continue
            fp = os.path.join(self.dir, fn)
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    st = json.load(f)
            except (OSError, ValueError):
                continue
            if now - st.get("t", 0) > self.STALE:
                if now - st.get("t", 0) > 20:
                    try:
                        os.remove(fp)
                    except OSError:
                        pass
                continue
            found.add(iid)
            peer = self.peers.get(iid)
            if peer is None:
                last = max([e.get("seq", 0) for e in st.get("ev", [])] or [0])
                peer = self.peers[iid] = dict(state=st, seen=time.monotonic(), last_seq=last, new=True)
            peer["state"], peer["seen"] = st, time.monotonic()
            top = peer["last_seq"]
            for ev in st.get("ev", []):
                sq = ev.get("seq", 0)
                if sq > peer["last_seq"]:
                    top = max(top, sq)
                    to = ev.get("to")
                    if to in (None, "*", "arb", self.iid):
                        self.inbox.append((iid, ev))
            peer["last_seq"] = top
        arrived = [iid for iid, pr in self.peers.items() if pr.pop("new", False)]
        gone = [iid for iid in list(self.peers) if iid not in found]
        for iid in gone:
            del self.peers[iid]
        return arrived, gone

    def close(self):
        try:
            os.remove(self.path)
        except OSError:
            pass


# --------------------------------------------------------------------------- #
# Vie de famille et de communauté (dans l'instance arbitre uniquement) :
# journée réelle (école, devoirs, travail, repas, dodo), besoins et caractères,
# bêtises et punitions, amours, mariages, œufs, visiteurs du village,
# anniversaires, vieillesse, départs vers la lune, deuil, chronique et livre.
# --------------------------------------------------------------------------- #
GRADE_LETTERS = ["F", "D", "C", "B", "A"]


def grade_letter(g):
    return GRADE_LETTERS[max(0, min(4, int(round(g))))]


class Family:
    def __init__(self, world):
        self.w = world
        self.people = []
        self.memorial = []
        self.events = []
        self.graves = []
        self.egg = None
        self.scene = None
        self.queue = []
        self.decor = {}
        self.dyn = {}
        self.active = False
        st = world.settings
        self.hours = float(st.value("hours", 0.0))
        self.scale = LIFE_SCALES.get(st.value("life_scale", "normal"), 1.0)
        self.decor_on = st.value("decor", True, type=bool)
        self.death_mode = st.value("death_mode", "lune")
        self.toasts_on = st.value("toasts", True, type=bool)
        self.last_birth = float(st.value("last_birth", 0.0))
        self.visitor_cd = float(st.value("visitor_cd", rnd(1200, 2400)))
        self.egg_cd = 0.0
        self.save_t = 30.0
        self.assign_t = 0.0
        self.slot = {}
        self.today = None
        self.toasts = 0
        self.scene_cd = 0.0
        self.festival_done = None
        self.bubble_cd = 0.0
        self.story_cd = 0.0
        self.hw_reminded = None
        self.toast_cap = 3
        # mode démo : une vie entière en quelques minutes, sans toucher à la vraie famille
        self.demo = False
        self.demo_t = 0.0
        self.demo_done = None
        self.demo_fest = False

    # ---------- activation / sauvegarde ----------
    def activate(self):
        if self.active:
            return
        self.active = True
        w, st = self.w, self.w.settings
        for p in w.pets:
            key = "persona_" + p.name
            saved = st.value(key, "")
            p.persona = [x for x in str(saved).split(",") if x in PERSONAS] if saved else random.sample(PERSONAS, 2)
            st.setValue(key, ",".join(p.persona))
        self.load()
        self.assign_duties(force=True)

    def load(self):
        """Recharge habitants, mémorial, chronique et tombes depuis la sauvegarde."""
        w, st = self.w, self.w.settings
        for key, default in (("people", "[]"), ("memorial", "[]"), ("events", "[]"), ("graves", "[]")):
            try:
                data = json.loads(st.value(key, default))
            except (TypeError, ValueError):
                data = []
            setattr(self, key, data)
        loaded = []
        for tr in self.people[:POP_MAX]:
            try:
                loaded.append(Person(w, tr))
            except Exception:
                continue
        self.people = loaded
        home = w.terrain.segs[0]
        for p in self.people:
            p.x = w.terrain.clamp_x(self.home_x() + rnd(-200, 200), home) - W / 2
            p.y = home.yb - GROUND
            p.seg = home
            p.state = "idle"
            p.timer = rnd(1, 3)
            p.setVisible(w.visible and not w.paused)
        self.build_decor()

    def clear_cast(self):
        """Retire tous les habitants et objets de l'écran (sans rien sauvegarder)."""
        self.end_scene()
        for p in self.people:
            p.hide()
        self.people = []
        for pr in list(self.decor.values()) + list(self.dyn.values()):
            pr.kill()
        self.decor, self.dyn = {}, {}
        if self.egg and self.egg.get("prop"):
            self.egg["prop"].kill()
        self.egg, self.queue = None, []
        for p in self.w.pets:
            p.duty, p.helping, p.ribbon_t = None, None, 0.0

    def deactivate(self):
        """Une instance plus ancienne est arbitre : on lui laisse la famille (sans écraser la sauvegarde)."""
        if not self.active:
            return
        self.demo = False
        self.active = False
        self.clear_cast()

    # ---------- mode démo ----------
    def start_demo(self):
        """Une vie entière en ~8 minutes : naissance, école, bêtises, mariage, petits-enfants, vieillesse."""
        w = self.w
        if not self.active or self.demo:
            return
        self.save()                                             # la vraie famille est à l'abri
        w.cancel_duo()
        self.clear_cast()
        self.memorial, self.graves, self.events = [], [], []
        self.build_decor()
        self.demo, self.demo_t, self.demo_done, self.demo_fest = True, 0.0, None, False
        self.toast_cap, self.toasts = 12, 0
        self.visitor_cd, self.egg_cd, self.scene_cd, self.story_cd = 15.0, 0.0, 0.0, 0.0
        for p in w.pets:
            p.hunger = p.energy = 100.0
            if p.state == "sleep":
                p.wake("Action !")
        self.assign_duties(force=True)
        self.log("fete", "Mode démo : une vie entière en huit minutes.", toast=True)
        self.force_birth()
        self.sync_demo_act()

    def stop_demo(self, msg=True):
        if not self.demo:
            return
        self.demo = False
        self.toast_cap = 3
        self.clear_cast()
        self.load()                                             # retour de la vraie famille
        self.assign_duties(force=True)
        self.sync_demo_act()
        if msg and self.w.tray is not None:
            try:
                self.w.tray.showMessage("H13ris — démo", "Fin de la démo : la vraie famille est de retour.",
                                        QSystemTrayIcon.MessageIcon.Information, 5000)
            except Exception:
                pass

    def demo_tick(self, dt):
        self.demo_t += dt
        t = self.demo_t
        if t > 25 and not self.people and self.egg is None:      # sécurité : ponte directe
            a = self.w.pets[0]
            self.lay_egg(a.cx() + 60 * a.facing, self.home_seg(), self.w.pets, hatch=8)
        if not self.demo_fest and t > 330 and self.scene is None and not self.queue:
            self.demo_fest = True
            self.force_festival(" (démo)")
        if self.memorial and self.demo_done is None:
            self.demo_done = t
        if (self.demo_done is not None and t - self.demo_done > 40 and self.scene is None) or t > DEMO_MAX:
            self.stop_demo()

    def demo_clock(self):
        """Journée en tranches de quelques secondes ; chaque « jour » de démo change de date."""
        total = sum(d for _, d in DEMO_DAY)
        day, rem = divmod(self.demo_t, total)
        h = DEMO_DAY[-1][0]
        for hour, dur in DEMO_DAY:
            if rem < dur:
                h = hour
                break
            rem -= dur
        base = datetime.datetime.now().replace(hour=int(h), minute=int((h % 1) * 60), second=0, microsecond=0)
        return base + datetime.timedelta(days=int(day) + 1)

    def cool(self, lo, hi, demo_lo=None, demo_hi=None):
        """Délai aléatoire, raccourci en mode démo."""
        if self.demo:
            return rnd(demo_lo if demo_lo is not None else lo / 10, demo_hi if demo_hi is not None else hi / 10)
        return rnd(lo, hi)

    def save(self):
        if not self.active or self.demo:
            return
        st = self.w.settings
        try:
            st.setValue("people", json.dumps([p.to_dict() for p in self.people if not p.dead]))
            st.setValue("memorial", json.dumps(self.memorial[-40:]))
            st.setValue("events", json.dumps(self.events[-400:]))
            st.setValue("graves", json.dumps(self.graves[-8:]))
            st.setValue("hours", self.hours)
            st.setValue("visitor_cd", self.visitor_cd)
            st.setValue("last_birth", self.last_birth)
        except Exception:
            pass

    def by_name(self, name):
        for p in self.w.pets + self.people:
            if p.name == name:
                return p
        return None

    def alive(self):
        return [p for p in self.people if not p.dead and p.leaving is None]

    def population(self):
        return len(self.w.pets) + len(self.alive())

    def minors(self):
        return [p for p in self.alive() if p.is_minor()]

    def adults(self):
        return [p for p in self.alive() if p.is_adult()]

    def parents_of(self, p):
        out = [self.by_name(n) for n in getattr(p, "parents", [])]
        out = [q for q in out if q is not None and q.active() and not getattr(q, "dead", False)]
        return out or [q for q in self.w.pets if q.active()]

    def children_of(self, p):
        return [k for k in self.alive() if p.name in k.parents]

    def home_seg(self):
        return self.w.terrain.segs[0]

    def home_x(self):
        seg = self.home_seg()
        return seg.x0 + seg.width * 0.22

    def desk_x(self):
        seg = self.home_seg()
        return seg.x0 + seg.width * 0.42

    def school_x(self):
        seg = self.home_seg()
        return seg.x0 + seg.width * 0.80

    def cemetery_x(self, i):
        seg = self.home_seg()
        return seg.x0 + 110 + i * 46

    # ---------- décor ----------
    def build_decor(self):
        for pr in self.decor.values():
            pr.kill()
        self.decor = {}
        if not (self.decor_on and self.w.visible and not self.w.paused):
            return
        seg = self.home_seg()
        self.decor["maison"] = Prop("maison", self.home_x(), seg.yb)
        self.decor["bureau"] = Prop("bureau", self.desk_x(), seg.yb)
        self.decor["ecole"] = Prop("ecole", self.school_x(), seg.yb)
        for i, g in enumerate(self.graves[-6:]):
            pr = Prop("tombe", self.cemetery_x(i), seg.yb, label=g.get("name", ""))
            pr.flowers = int(g.get("flowers", 1))
            self.decor["tombe%d" % i] = pr

    def set_visible(self, on):
        if not self.active:
            return
        for pr in list(self.decor.values()) + list(self.dyn.values()):
            pr.setVisible(on)
        if self.egg and self.egg.get("prop"):
            self.egg["prop"].setVisible(on)
        if on and self.decor_on and not self.decor:
            self.build_decor()

    def toggle_decor(self, on):
        self.decor_on = on
        self.w.settings.setValue("decor", on)
        self.build_decor()

    def set_scale(self, key):
        self.scale = LIFE_SCALES.get(key, 1.0)
        self.w.settings.setValue("life_scale", key)
        for p in self.people:
            p.apply_stage()

    def set_death_mode(self, on):
        self.death_mode = "lune" if on else "jamais"
        self.w.settings.setValue("death_mode", self.death_mode)

    def set_toasts(self, on):
        self.toasts_on = bool(on)
        self.w.settings.setValue("toasts", self.toasts_on)

    def slot_label(self):
        """Moment de la journée du village, pour le menu."""
        c = self.slot
        if not c:
            return "—"
        if c.get("night"):
            return "nuit"
        for key, lab in (("school", "école"), ("homework", "devoirs"), ("lunch", "déjeuner"), ("snack", "goûter"),
                         ("dinner", "dîner"), ("work", "travail"), ("evening", "soirée")):
            if c.get(key):
                return lab
        return "temps libre"

    def person_label(self, p):
        """Une ligne par habitant : nom — étape, âge · caractère · note/mariage · activité."""
        duty = {"school": "à l'école", "study": "fait ses devoirs", "work": "au travail", "meal": "à table",
                "sleep": "au lit", "help": "aide aux devoirs"}
        bits = ["%s/%s" % tuple(p.persona) if len(p.persona) == 2 else "/".join(p.persona)]
        if p.is_minor() and p.stage != "bébé":
            bits.append("note %s" % grade_letter(p.grade))
        if p.spouse:
            bits.append("marié%s à %s" % ("e" if p.name[-1] == "a" else "", p.spouse))
        if p.visitor:
            bits.append("visiteur")
        if p.punished_t > 0:
            bits.append("au coin")
        elif p.state == "sleep":
            bits.append("dort")
        elif p.duty in duty:
            bits.append(duty[p.duty])
        elif p.farewell:
            bits.append("fait ses adieux")
        return "%s — %s, %.1f h · %s" % (p.name, p.stage, p.age, " · ".join(bits))

    def add_dyn(self, kind, x, y, **kw):
        did = "%s-%d" % (kind, self.w.new_id_int())
        if self.w.visible and not self.w.paused:
            self.dyn[did] = Prop(kind, x, y, **kw)
        return did

    def drop_dyn(self, did):
        pr = self.dyn.pop(did, None)
        if pr is not None:
            pr.kill()

    # ---------- chronique ----------
    def log(self, kind, text, toast=False):
        stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.events.append(dict(t=stamp, k=kind, s=text))
        self.events = self.events[-400:]
        today = datetime.date.today().isoformat()
        if self.today != today:
            self.today, self.toasts = today, 0
        if toast and self.toasts_on and self.w.tray is not None and self.toasts < self.toast_cap:
            self.toasts += 1
            try:
                self.w.tray.showMessage("H13ris — %s" % kind, text, QSystemTrayIcon.MessageIcon.Information, 6000)
            except Exception:
                pass

    def famsay(self, p, text, dur=2.0, force=False):
        if force or self.bubble_cd <= 0:
            p.say(text, dur)
            self.bubble_cd = 10.0
            return True
        return False

    # ---------- boucle ----------
    def tick(self, dt):
        if not self.active or dt <= 0:
            return
        self.hours += dt / 3600.0
        self.save_t -= dt
        self.bubble_cd = max(0.0, self.bubble_cd - dt)
        self.story_cd = max(0.0, self.story_cd - dt)
        self.scene_cd = max(0.0, self.scene_cd - dt)
        self.assign_t -= dt
        if self.assign_t <= 0:
            self.assign_t = 1.0 if self.demo else 5.0
            self.assign_duties()
        if self.demo:
            self.demo_tick(dt)
            if not self.active:
                return
        self.needs_tick(dt)
        self.egg_tick(dt)
        self.people_tick(dt)
        self.scene_tick(dt)
        self.social_tick(dt)
        for did, pr in list(self.dyn.items()):
            pr.step(dt)
            if pr.kind in ("gribouillis",) and pr.age > 600:
                self.drop_dyn(did)
            elif pr.kind == "gateau" and pr.age > 90:
                self.drop_dyn(did)
            elif pr.kind == "cadeau" and pr.age > 60:
                self.drop_dyn(did)
        for pr in self.decor.values():
            pr.step(dt)
        if self.egg and self.egg.get("prop") is not None:
            self.egg["prop"].step(dt)
        if self.save_t <= 0:
            self.save_t = 30.0
            self.save()

    # ---------- journée réelle ----------
    def clock(self):
        if self.demo:
            now, wd = self.demo_clock(), True
        else:
            now = datetime.datetime.now()
            wd = now.weekday() < 5
        h = now.hour + now.minute / 60.0
        r = ROUTINE
        return dict(h=h, weekday=wd, today=now.date().isoformat(),
                    night=(h >= r["bed_adult"] or h < r["wake"]),
                    bed_kid=(h >= r["bed_kid"] or h < r["wake"]),
                    bed_teen=(h >= r["bed_teen"] or h < r["wake"]),
                    school=wd and r["school"][0] <= h < r["school"][1],
                    work=wd and (r["work"][0] <= h < r["work"][1] or r["work"][2] <= h < r["work"][3]),
                    homework=wd and r["homework"] <= h < r["homework"] + 1.5,
                    lunch=r["lunch"] <= h < r["lunch"] + 0.5,
                    snack=r["snack"] <= h < r["snack"] + 0.5,
                    dinner=r["dinner"] <= h < r["dinner"] + 0.5,
                    evening=(20.0 <= h < 22.0))

    def assign_duties(self, force=False):
        w = self.w
        self.slot = c = self.clock()
        busy_scene = self.scene is not None or w.role is not None
        for p in w.pets + self.alive():
            if p.duty == "help" and not force:
                continue
            duty = None
            kid = getattr(p, "is_kid", False)
            stage = getattr(p, "stage", "adulte")
            if busy_scene:
                duty = None
            elif stage == "bébé":
                duty = "sleep" if c["bed_kid"] else None
            elif stage in ("enfant", "ado"):
                if (c["bed_kid"] if stage == "enfant" else c["bed_teen"]):
                    duty = "sleep"
                elif c["school"] and not getattr(p, "skip_day", None) == c["today"]:
                    duty = "school"
                elif c["homework"] and p.hw_day != c["today"]:
                    duty = "study"
                elif c["snack"] or c["dinner"]:
                    duty = "meal"
            else:                                             # adultes, aînés, fondateurs
                if c["night"]:
                    duty = "sleep"
                elif c["lunch"] or c["dinner"]:
                    duty = "meal"
                elif c["work"] and stage == "adulte" and not getattr(p, "visitor", False) \
                        and ((not kid and c["h"] < 12) if self.demo
                             else ((self.hours * 60 + hash(p.name) % 40) % 40) < 12):
                    duty = "work"
                elif stage == "aîné" and 14.0 <= c["h"] < 15.0:
                    duty = "sleep"
            if duty != p.duty:
                p.duty = duty
                p.study_t = 0.0
                if duty != "sleep" and p.state == "sleep" and not c["night"] and (duty or p.energy > 40):
                    p.wake("Hm ? Déjà ?" if duty is None else random.choice(
                        ["Debout !", "C'est l'heure !", "*bâille* J'arrive.", "Hm... oui oui."]))
                if duty == "school" and kid and self.bubble_cd <= 0:
                    self.famsay(p, random.choice(KID_LINES["school"]), 1.8)

    def duty_target(self, p):
        """Position à rejoindre pour le devoir en cours (x, seg)."""
        seg = self.home_seg()
        d = p.duty
        if d in ("sleep", "meal"):
            return self.home_x() + ((hash(p.name) % 7) - 3) * 34, seg
        if d in ("study", "work", "help"):
            return self.desk_x() + ((hash(p.name) % 5) - 2) * 26, seg
        if d == "school":
            return self.school_x() + ((hash(p.name) % 5) - 2) * 40, seg
        return None, seg

    def do_duty(self, p):
        """Renvoie True si le devoir occupe le pet."""
        d = p.duty
        if d is None:
            return False
        tx, seg = self.duty_target(p)
        near = tx is not None and abs(p.cx() - tx) < 40 and p.seg is seg
        if not near:
            if p.state in ("idle", "walk") and p.fam_cd <= 0:
                p.fam_cd = 1.5
                sp = getattr(p, "walk_speed", lambda: WALK_SPEED)()
                p.go_to(tx, seg, sp if d != "school" else sp * 1.3)
            return True
        if d == "sleep":
            if p.state != "sleep":
                p.facing = 1 if p.cx() < self.home_x() else -1
                p.sleep(rnd(600, 1200))
                if p.energy < 30 and self.bubble_cd <= 0:
                    self.famsay(p, random.choice(KID_LINES["sleep"]), 1.5)
            return True
        if d == "meal":
            if p.state == "idle" and p.fam_cd <= 0:
                p.fam_cd = rnd(20, 40)
                p.hunger = 100.0
                p.social = min(100.0, p.social + 15)
                p.show_item, p.show_item_t = "biscuit", 1.4
                self.famsay(p, random.choice(KID_LINES["meal"]), 1.6)
                p.set_expr("happy", 2)
                p.go_idle(rnd(20, 40))
            elif p.state == "walk":
                pass
            return True
        if d == "school":
            if p.state == "idle":
                p.facing = 1 if p.cx() < self.school_x() else -1
                if p.timer < 0.5:
                    p.go_idle(rnd(15, 40))
                if self.bubble_cd <= 0 and random.random() < 0.02:
                    self.famsay(p, random.choice(KID_LINES["school"]), 1.8)
                    p.arm_up = True
                    QTimer.singleShot(1200, lambda p=p: setattr(p, "arm_up", False))
            return True
        if d == "study":
            if p.state == "idle":
                p.facing = 1 if p.cx() < self.desk_x() else -1
                if p.timer < 0.5:
                    p.go_idle(rnd(10, 25))
                if self.bubble_cd <= 0 and random.random() < 0.015:
                    self.famsay(p, random.choice(KID_LINES["homework"]), 1.8)
            return True
        if d == "work":
            if p.state == "idle":
                p.facing = 1 if p.cx() < self.desk_x() else -1
                if p.timer < 0.5:
                    p.go_idle(rnd(10, 25))
                if self.bubble_cd <= 0 and random.random() < 0.01:
                    self.famsay(p, random.choice(KID_LINES["work"]), 1.8)
            return True
        if d == "help":
            kid = self.by_name(p.helping) if p.helping else None
            if kid is None or kid.duty != "study":
                p.duty, p.helping = None, None
                return False
            if p.state == "idle":
                p.facing = 1 if kid.cx() > p.cx() else -1
                if p.timer < 0.5:
                    p.go_idle(rnd(8, 15))
                if self.bubble_cd <= 0 and random.random() < 0.02:
                    self.famsay(p, random.choice(KID_LINES["help"]), 1.6)
            return True
        return False

    # ---------- besoins ----------
    def needs_tick(self, dt):
        w = self.w
        for p in w.pets + self.alive():
            p.fam_cd = max(0.0, getattr(p, "fam_cd", 0.0) - dt)
            if p.state == "sleep":
                p.hunger = max(0.0, p.hunger - 0.002 * dt)
                continue
            gour = 1.4 if "gourmand" in p.persona else 1.0
            soc = 1.5 if "sociable" in p.persona else 0.6 if "timide" in p.persona else 1.0
            p.hunger = max(0.0, p.hunger - 0.005 * gour * dt)          # ~5 h entre deux repas
            near = any(q is not p and q.active() and dist2(p.cx(), p.feet(), q.cx(), q.feet()) < 160
                       for q in w.pets + self.alive())
            p.social = max(0.0, min(100.0, p.social + (0.25 if near else -0.04 * soc) * dt))
            if getattr(p, "is_kid", False) and p.is_minor():
                p.fun = max(0.0, p.fun - 0.01 * dt)
            if p.duty == "study" and p.state == "idle":
                helper = any(q.duty == "help" and q.helping == p.name for q in w.pets + self.adults())
                sage = 0.7 if "sage" in p.persona else 1.0
                p.study_t += dt * (2.1 if helper else 1.0) / sage
                if p.study_t >= (12.0 if self.demo else HOMEWORK_MIN[0] * 60):
                    self.finish_homework(p, helper)
            if p.duty == "work" and p.state == "idle":
                p.fun = max(0.0, p.fun - 0.01 * dt)
        for p in self.alive():
            p.moodlets = [m for m in p.moodlets if m[1] > self.hours]

    def finish_homework(self, p, helped):
        p.hw_day = self.slot.get("today")
        p.duty, p.study_t = None, 0.0
        old = grade_letter(p.grade)
        p.grade = min(4.0, p.grade + (0.5 if p.mood_score() >= 50 else 0.34))
        p.fun = min(100.0, p.fun + 15)
        p.add_moodlet(6, 4)
        self.famsay(p, random.choice(KID_LINES["homework_done"]), 2.2, force=True)
        p.set_expr("happy", 2.5)
        p.emit("sparkle", 5, y=GROUND - 60)
        for q in self.w.pets + self.adults():
            if q.duty == "help" and q.helping == p.name:
                q.duty, q.helping = None, None
                q.say("Bravo !", 1.6)
                q.emit("heart", 2, y=GROUND - 80)
                p.like(q.name, 4)
        new = grade_letter(p.grade)
        if new != old:
            self.famsay(p, KID_LINES["grade"][4 - GRADE_LETTERS.index(new)], 2.4, force=True)
            self.log("ecole", "%s est passé%s à %s en classe." % (p.name, "" if p.name[-1] != "a" else "e", new))
        elif random.random() < 0.3:
            self.log("ecole", "%s a fini ses devoirs%s." % (p.name, " avec de l'aide" if helped else " tout seul"))

    # ---------- œufs ----------
    def lay_egg(self, x, seg, parents, hatch=None):
        if self.egg is not None or self.population() >= POP_MAX:
            return False
        gen = 1 + max([getattr(par, "gen", 0) for par in parents] + [0])
        traits = Person.make_traits(self.w, parents=parents, gen=gen)
        x = self.w.terrain.clamp_x(x, seg)
        prop = Prop("egg", x, seg.yb, hue=traits["hue"]) if (self.w.visible and not self.w.paused) else None
        self.egg = dict(x=x, seg=seg, t=0.0, hatch=hatch if hatch else (8.0 if self.demo else rnd(*EGG_HATCH)),
                        traits=traits,
                        prop=prop, done=False, parents=[par.name for par in parents])
        self.last_birth = time.time()
        self.w.settings.setValue("last_birth", self.last_birth)
        return True

    def egg_tick(self, dt):
        e = self.egg
        if e is None:
            return
        e["t"] += dt
        pr = e.get("prop")
        if not e["done"]:
            if pr is not None:
                pr.crack = min(1.0, e["t"] / e["hatch"])
            if e["t"] >= e["hatch"]:
                self.hatch_egg()
        elif e["t"] >= e["hatch"] + 1.5:
            if pr is not None:
                pr.kill()
            self.egg = None

    def hatch_egg(self):
        e = self.egg
        if e is None:
            return
        pr = e.get("prop")
        if pr is not None:
            pr.opened = True
        e["done"] = True
        k = Person(self.w, e["traits"])
        k.x = e["x"] - W / 2
        k.y = e["seg"].yb - GROUND
        k.seg = e["seg"]
        k.state = "idle"
        k.timer = 2.0
        k.setVisible(self.w.visible and not self.w.paused)
        k.emit("sparkle", 8, y=GROUND - 60)
        k.hop(280)
        k.say(random.choice(KID_LINES["hello"]), 2.4)
        k.set_expr("happy", 3)
        self.people.append(k)
        parents = [self.by_name(n) for n in e["parents"]]
        for par in parents:
            if par is not None and par.active():
                par.say(random.choice(KID_LINES["welcome"]) % k.name, 2.8)
                par.set_expr("happy", 3)
                par.emit("heart", 5, y=GROUND - 80)
                k.like(par.name, 30)
                par.rel = getattr(par, "rel", {})
        self.log("naissance", "%s est né%s : %s, %s." % (k.name, "" if k.name[-1] != "a" else "e",
                                                        " et ".join(e["parents"]), "/".join(k.persona)), toast=True)
        self.save()

    def force_birth(self):
        w = self.w
        if self.egg is not None or self.population() >= POP_MAX:
            random.choice(w.pets).say("On a déjà les mains pleines !", 2)
            return
        w.cancel_duo()
        if not w.start_duo("birth", quick=True):
            a = w.pets[0]
            self.lay_egg(a.cx() + 60 * a.facing, a.seg or self.home_seg(), w.pets, hatch=12)

    def couple_eggs(self, dt):
        """Les couples mariés (hors fondateurs) ont aussi des œufs."""
        self.egg_cd -= dt
        if self.egg_cd > 0 or self.egg is not None or self.population() >= POP_MAX or self.scene is not None:
            return
        self.egg_cd = 12.0 if self.demo else 300.0
        for p in self.adults():
            if p.stage != "adulte" or not p.spouse:
                continue
            q = self.by_name(p.spouse)
            if q is None or not q.active() or getattr(q, "dead", False) or getattr(q, "stage", "") != "adulte":
                continue
            kids = [k for k in self.alive() if p.name in k.parents and q.name in k.parents]
            if len(kids) >= 2 or p.hunger < 30 or q.hunger < 30:
                continue
            if random.random() < 0.25:
                self.lay_egg((p.cx() + q.cx()) / 2, self.home_seg(), [p, q])
                p.say(random.choice(KID_LINES["birth"][:2]), 2)
                q.set_expr("happy", 3)
                q.emit("heart", 4, y=GROUND - 80)
                return

    # ---------- habitants : vieillissement, pleurs, punitions, adieux ----------
    def people_tick(self, dt):
        w = self.w
        for p in list(self.people):
            if p.dead:
                continue
            p.age += dt / 3600.0 * (DEMO_AGE if self.demo else 1.0)
            p.cry_cd = max(0.0, p.cry_cd - dt)
            p.mischief_cd = max(0.0, p.mischief_cd - dt)
            p.court_cd = max(0.0, p.court_cd - dt)
            p.ribbon_t = max(0.0, p.ribbon_t - dt)
            if p.punished_t > 0:
                p.punished_t -= dt
                if p.punished_t <= 0:
                    p.set_expr("happy", 2)
                    self.famsay(p, "Je peux sortir du coin ?", 1.8)
            if p.state == "ride":
                p.ride_t += dt
                if p.ride_t > 13:
                    p.ride_t = 0.0
                    p.dismount(True)
            if p.leaving is not None:                          # visiteur qui s'en va
                p.leaving += dt
                if p.leaving > 8:
                    p.hide()
                    self.people.remove(p)
                    self.save()
                continue
            if p.visitor:
                p.stay_h += dt / 3600.0
            if p.apply_stage():
                self.queue.append(("birthday", p))
            # adieux et départ vers la lune
            if not p.visitor and p.stage == "aîné" and self.death_mode == "lune":
                if p.age >= p.lifespan * self.scale - FAREWELL_H * self.scale and not p.farewell:
                    p.farewell = True
                    self.famsay(p, random.choice(KID_LINES["farewell"]), 3, force=True)
                    self.log("famille", "%s sent que l'heure approche et fait ses adieux." % p.name, toast=True)
                if p.age >= p.lifespan * self.scale and not any(q is p for _, q in self.queue) \
                        and not (self.scene and self.scene.get("who") is p):
                    self.queue.insert(0, ("depart", p))
            # bébés seuls
            parents = self.parents_of(p)
            if w.role is None and p.is_minor() and parents and p.state in ("idle", "walk") and p.duty is None:
                dmin = min(dist2(p.cx(), p.feet(), q.cx(), q.feet()) for q in parents)
                if dmin > 380 and p.stage == "bébé":
                    p.lonely_t += dt
                else:
                    p.lonely_t = max(0.0, p.lonely_t - dt * 2)
                if p.lonely_t > 4 and p.cry_t <= 0 and p.cry_cd <= 0:
                    p.cry_t, p.cry_cd = 4.0, 7.0
                    p.say(random.choice(KID_LINES["cry"]), 2.2)
                if p.cry_t > 0 and random.random() < dt * 4:
                    p.emit("tear", 1, x=W / 2 + rnd(-10, 10), y=GROUND - 40 * p.size - 8)
            else:
                p.lonely_t = 0.0

    # ---------- cérémonies ----------
    def scene_tick(self, dt):
        w = self.w
        if self.scene is None:
            if self.queue and self.scene_cd <= 0 and w.role is None and not w.fanmeet.active:
                if w.duo is not None:
                    if self.queue[0][0] != "depart":              # les adieux n'attendent pas
                        return
                    w.cancel_duo()
                kind, who = self.queue.pop(0)
                if isinstance(who, Person) and (who.dead or who.leaving is not None):
                    return
                self.start_scene(kind, who)
            return
        sc = self.scene
        sc["t"] += dt
        fn = getattr(self, "scene_" + sc["kind"], None)
        if fn is None:
            self.end_scene()
        else:
            fn(sc, dt)

    def cast(self):
        return [p for p in self.w.pets + self.alive() if p.active() and p.state not in ("drag", "ghost", "gone")]

    def start_scene(self, kind, who):
        w = self.w
        w.cancel_duo()
        seg = self.home_seg()
        center = self.home_x() + 260
        sc = dict(kind=kind, who=who, t=0.0, step=0, seg=seg, cx=center, props=[])
        self.scene = sc
        cast = self.cast()
        for p in cast:
            p.busy = True
            p.duty = None
            if p.state == "sleep":
                p.wake("Oh ?")
            if p.state == "ride":
                p.dismount(True)
            p.camo = False
        self.gather(sc, cast)

    def gather(self, sc, cast, spacing=64):
        who = sc.get("who")
        i = 0
        for p in cast:
            if p is who or (isinstance(who, tuple) and p in who):
                continue
            side = -1 if i % 2 == 0 else 1
            k = i // 2 + 1
            p.go_to(sc["cx"] + side * (70 + k * spacing), sc["seg"], 110)
            i += 1
        if isinstance(who, tuple):
            who[0].go_to(sc["cx"] - 44, sc["seg"], 90)
            who[1].go_to(sc["cx"] + 44, sc["seg"], 90)
        elif who is not None:
            who.go_to(sc["cx"], sc["seg"], 90)

    def gathered(self, sc):
        cast = self.cast()
        return sc["t"] > 22 or all(p.state != "walk" for p in cast)

    def end_scene(self):
        sc, self.scene = self.scene, None
        if sc is None:
            return
        for did in sc.get("props", []):
            self.drop_dyn(did)
        for p in self.cast():
            p.busy = self.w.role is not None
            p.arm_up = p.hugging = False
            if p.state == "idle":
                p.timer = rnd(1, 3)
        self.scene_cd = 6.0 if self.demo else 120.0
        self.assign_duties(force=True)

    def nxt(self, sc, step):
        sc.update(step=step, t=0.0)

    def scene_birthday(self, sc, dt):
        p, t, s = sc["who"], sc["t"], sc["step"]
        if s == 0:
            if self.gathered(sc):
                sc["props"].append(self.add_dyn("gateau", sc["cx"] + 60, sc["seg"].yb))
                for q in self.cast():
                    q.face(p) if q is not p else None
                    if q is not p and random.random() < 0.5:
                        q.say(random.choice(KID_LINES["birthday"]), 2)
                    q.set_expr("happy", 3)
                self.nxt(sc, 1)
        elif s == 1 and t > 2.5:
            p.say("Souffle !", 1.4)
            p.set_expr("surprised", 0.8)
            self.nxt(sc, 2)
        elif s == 2 and t > 1.5:
            for did in sc["props"]:
                pr = self.dyn.get(did)
                if pr is not None:
                    pr.opened = True
            p.emit("sparkle", 10, y=GROUND - 70)
            p.squash = 1.3
            p.hop(340)
            p.say("J'ai grandi !" if p.stage != "aîné" else "Je suis un aîné, maintenant.", 2.4)
            for q in self.cast():
                q.emit("sparkle" if q is p else "heart", 3, y=GROUND - 80)
                q.hop(240)
                if isinstance(q, Person):
                    q.add_moodlet(4, 4)
            p.fun = min(100.0, p.fun + 30)
            self.log("anniversaire", "%s est maintenant %s (%d h)." % (p.name, p.stage, p.age), toast=True)
            self.nxt(sc, 3)
        elif s == 3 and t > 4:
            self.end_scene()

    def scene_wedding(self, sc, dt):
        a, b = sc["who"]
        t, s = sc["t"], sc["step"]
        if s == 0:
            if self.gathered(sc):
                sc["props"].append(self.add_dyn("arche", sc["cx"], sc["seg"].yb))
                a.face(b)
                b.face(a)
                for q in self.cast():
                    if q not in (a, b):
                        q.face(a)
                        q.set_expr("happy", 6)
                self.nxt(sc, 1)
        elif s == 1 and t > 1.5:
            a.say(random.choice(KID_LINES["vows"]), 2.6)
            self.nxt(sc, 2)
        elif s == 2 and t > 2.8:
            b.say(random.choice(KID_LINES["vows"]), 2.6)
            self.nxt(sc, 3)
        elif s == 3 and t > 2.8:
            for q in (a, b):
                q.show_item, q.show_item_t = "anneau", 1.6
                q.hugging = True
                q.emit("heart", 6, x=W / 2 + 30 * q.facing, y=GROUND - 70)
            self.nxt(sc, 4)
        elif s == 4 and t > 2.0:
            for did in sc["props"]:
                pr = self.dyn.get(did)
                if pr is not None:
                    pr.opened = True
            for q in self.cast():
                if q not in (a, b):
                    q.say(random.choice(KID_LINES["wedding"]), 2)
                    q.hop(300)
                    q.emit("sparkle", 4, y=GROUND - 90)
            a.hugging = b.hugging = False
            a.spouse, b.spouse = b.name, a.name
            a.engaged = b.engaged = False
            for q in (a, b):
                if isinstance(q, Person):
                    q.visitor = False
                    q.add_moodlet(10, 24)
                    q.like(q.spouse, 40)
            if isinstance(b, Person) and isinstance(a, Person):
                if a.gen == 0 and b.gen == 0:
                    a.gen = b.gen = 1
                elif a.gen == 0:
                    a.gen = b.gen
                elif b.gen == 0:
                    b.gen = a.gen
            sc["props"].append(self.add_dyn("gateau", sc["cx"] + 90, sc["seg"].yb))
            self.log("mariage", "%s et %s se sont mariés sous l'arche fleurie." % (a.name, b.name), toast=True)
            self.nxt(sc, 5)
        elif s == 5:
            beat = int(t * 2.2)
            if beat != sc.get("beat"):
                sc["beat"] = beat
                for i, q in enumerate(self.cast()):
                    if (i + beat) % 2 == 0:
                        q.hop(260)
                    if random.random() < 0.4:
                        q.emit("note", 1, y=GROUND - 85)
            if t > 9:
                self.save()
                self.end_scene()

    def scene_depart(self, sc, dt):
        p, t, s = sc["who"], sc["t"], sc["step"]
        if s == 0:
            if self.gathered(sc):
                for q in self.cast():
                    if q is not p:
                        q.face(p)
                p.say(random.choice(KID_LINES["farewell"]), 3, )
                self.nxt(sc, 1)
        elif s == 1 and t > 3.2:
            for q in self.cast():
                if q is not p:
                    q.say(random.choice(KID_LINES["mourn"]), 2.6)
                    q.set_expr("pout", 5)
                    q.emit("tear", 3, y=GROUND - 45)
            p.say(random.choice(KID_LINES["depart"]), 3)
            p.set_expr("happy", 4)
            self.nxt(sc, 2)
        elif s == 2 and t > 3.0:
            p.die(line="☾")
            p.ghost_t = 7.0
            p.dead = True
            p.emit("sparkle", 12, y=GROUND - 60)
            self.memorial.append(dict(name=p.name, gen=p.gen, persona=p.persona, born=p.traits.get("born", ""),
                                      died=datetime.date.today().isoformat(), age=round(p.age, 1),
                                      hue=p.traits.get("hue", 300), parents=p.parents, spouse=p.spouse))
            self.graves.append(dict(name=p.name, flowers=2))
            self.graves = self.graves[-6:]
            for q in self.alive() + self.w.pets:
                if q is p:
                    continue
                rel = (p.name in getattr(q, "parents", [])) or q.name in p.parents or q.spouse == p.name \
                    if isinstance(q, Person) else True
                if rel:
                    q.ribbon_t = 7200.0 if isinstance(q, Person) else 0.0
                    if isinstance(q, Person):
                        q.add_moodlet(-12, 6)
                if isinstance(q, Person) and q.spouse == p.name:
                    q.spouse = None
            self.log("depart", "%s est parti%s vers la lune, entouré%s des siens, à %d h." % (
                p.name, "" if p.name[-1] != "a" else "e", "" if p.name[-1] != "a" else "e", p.age), toast=True)
            self.nxt(sc, 3)
        elif s == 3 and t > 8:
            if p in self.people:
                self.people.remove(p)
            self.build_decor()
            self.save()
            self.end_scene()

    def scene_festival(self, sc, dt):
        t, s = sc["t"], sc["step"]
        if s == 0:
            if self.gathered(sc):
                sc["props"].append(self.add_dyn("gateau", sc["cx"], sc["seg"].yb))
                for q in self.cast():
                    q.say(random.choice(KID_LINES["festival"]), 2)
                    q.set_expr("happy", 8)
                self.nxt(sc, 1)
        elif s == 1:
            beat = int(t * 2.2)
            if beat != sc.get("beat"):
                sc["beat"] = beat
                for i, q in enumerate(self.cast()):
                    if (i + beat) % 2 == 0:
                        q.hop(260)
                    if random.random() < 0.5:
                        q.emit("note" if beat % 3 else "sparkle", 1, y=GROUND - 85)
            if t > 20:
                for q in self.cast():
                    q.fun = min(100.0, q.fun + 25)
                    q.social = min(100.0, q.social + 25)
                self.log("fete", "Tout le village a fait la fête%s." % sc.get("label", ""))
                self.end_scene()

    def force_festival(self, label=""):
        if self.scene is None:
            self.queue.append(("festival", None))
            self.scene_cd = 0.0

    # ---------- vie sociale : bêtises, amours, visiteurs, fêtes ----------
    def social_tick(self, dt):
        w = self.w
        if w.role is not None or self.scene is not None or w.fanmeet.active:
            return
        # fêtes du calendrier (une fois par jour de fête, le soir)
        today = datetime.date.today()
        key = today.isoformat()
        c = self.slot
        if self.festival_done != key and c.get("evening") and (
                (today.month == 12 and today.day >= 20) or (today.month == 10 and today.day == 31)
                or (today.weekday() == 5 and today.day <= 7)):
            self.festival_done = key
            self.w.settings.setValue("festival_done", key)
            self.queue.append(("festival", None))
        # bêtises
        for p in self.minors():
            if p.stage == "bébé" or p.punished_t > 0 or p.state not in ("idle", "walk") or p.mischief_cd > 0:
                continue
            base = 0.0006 * (8 if self.demo else 1)
            base *= 4 if "espiègle" in p.persona else 0.3 if "sage" in p.persona else 1
            base *= 1.5 if p.fun < 40 else 1
            base *= 0.5 if p.obedience > 70 else 1
            if random.random() < base * dt * 60:
                self.do_mischief(p)
        # amours
        singles = [p for p in self.adults() if p.stage == "adulte" and not p.spouse and p.leaving is None
                   and not p.engaged]
        for p in singles:
            if p.court_cd > 0 or p.state not in ("idle", "walk") or p.duty is not None:
                continue
            cands = [q for q in singles if q is not p and not p.related(q)
                     and dist2(p.cx(), p.feet(), q.cx(), q.feet()) < 900 and q.state in ("idle", "walk")]
            if not cands:
                continue
            q = max(cands, key=lambda q: p.romance.get(q.name, 0))
            p.court_cd = self.cool(45, 90, 4, 7)
            self.court(p, q)
        # visiteurs du village
        self.visitor_cd -= dt
        if self.visitor_cd <= 0:
            self.visitor_cd = self.cool(1500, 3000, 20, 30)
            visitors = [p for p in self.alive() if p.visitor]
            if singles and not visitors and self.population() < POP_MAX:
                self.arrive_visitor()
        for p in [p for p in self.alive() if p.visitor and p.leaving is None]:
            if p.stay_h > 2.5 and not p.spouse and p.state in ("idle", "walk") and self.scene is None:
                p.leaving = 0.0
                p.say(random.choice(["Je repasserai !", "Merci pour l'accueil.", "À la prochaine !"]), 2.6)
                p.go_to(self.home_seg().x1 - 60, self.home_seg(), p.run_speed())
                self.log("visite", "%s est reparti%s au village." % (p.name, "" if p.name[-1] != "a" else "e"))
        self.couple_eggs(dt)
        # chamailleries entre frères et sœurs
        kids = [p for p in self.minors() if p.stage != "bébé" and p.state == "idle" and p.duty is None]
        if len(kids) >= 2 and random.random() < dt * 0.004:
            a, b = random.sample(kids, 2)
            if dist2(a.cx(), a.feet(), b.cx(), b.feet()) < 140 and a.fun < 60:
                a.say(random.choice(KID_LINES["sibling"]), 1.6)
                b.say(random.choice(KID_LINES["sibling"]), 1.6)
                b.launch((1 if b.cx() > a.cx() else -1) * 160, -260)
                a.set_expr("pout", 2)
                b.set_expr("pout", 2)
                a.like(b.name, -3)
                b.like(a.name, -3)
                self.scold_near(a, both=b)

    def do_mischief(self, p):
        w = self.w
        kinds = ["gribouillis", "chipe", "chahut", "boule"]
        if p.duty == "school" and p.stage == "ado" and "espiègle" in p.persona:
            kinds.append("seche")
        kind = random.choice(kinds)
        p.mischief_cd = self.cool(1800, 4800, 20, 40)
        others = [q for q in w.pets + self.alive() if q is not p and q.active()]
        done = None
        if kind == "gribouillis":
            self.add_dyn("gribouillis", p.cx() + p.facing * 40, p.feet(), hue=rnd(0, 999))
            p.attack_t = 0.8
            done = "a gribouillé sur le bureau"
        elif kind == "chipe":
            victims = [q for q in others if q.item and dist2(p.cx(), p.feet(), q.cx(), q.feet()) < 300]
            if victims:
                v = random.choice(victims)
                p.item, p.ammo, v.item, v.ammo = v.item, v.ammo, None, 0
                v.say("Hé ! Mon %s !" % ITEMS[p.item]["label"].lower(), 1.8)
                v.set_expr("surprised", 1.5)
                done = "a chipé le %s de %s" % (ITEMS[p.item]["label"].lower(), v.name)
        elif kind == "chahut":
            victims = [q for q in others if q.state == "sleep" and dist2(p.cx(), p.feet(), q.cx(), q.feet()) < 400]
            if victims:
                v = random.choice(victims)
                p.go_to(v.cx() - 40, v.seg, p.run_speed())
                v.wake("Hein ?! Quoi ?!")
                v.set_expr("pout", 2)
                done = "a réveillé %s en sautant à côté" % v.name
        elif kind == "boule":
            victims = [q for q in others if q.state in ("idle", "walk") and dist2(p.cx(), p.feet(), q.cx(), q.feet()) < 500]
            if victims:
                v = random.choice(victims)
                p.facing = 1 if v.cx() > p.cx() else -1
                w.shoot(p, v, arc=True, T=0.8, dmg=0)
                done = "a lancé une boule de neige sur %s" % v.name
        elif kind == "seche":
            p.skip_day = self.slot.get("today")
            p.duty = None
            p.go_to(self.w.terrain.random_x(p.seg), p.seg, p.run_speed())
            done = "a séché l'école"
        if done is None:
            return
        p.set_expr("wink", 2)
        self.famsay(p, random.choice(KID_LINES["mischief"]), 1.8, force=True)
        p.fun = min(100.0, p.fun + 15)
        caught = self.scold_near(p)
        self.log("betise", "%s %s%s." % (p.name, done, " et s'est fait attraper" if caught else " sans se faire voir"))

    def scold_near(self, kid, both=None):
        """Un parent à proximité gronde (60 %). Renvoie True si l'enfant est puni."""
        parents = [q for q in self.parents_of(kid) if q.state in ("idle", "walk")
                   and dist2(kid.cx(), kid.feet(), q.cx(), q.feet()) < 450]
        if not parents or random.random() > 0.6:
            return False
        par = random.choice(parents)
        par.face(kid)
        par.say(random.choice(KID_LINES["scold"]), 2.2)
        par.set_expr("pout", 2.5)
        for k in (kid, both):
            if k is None:
                continue
            k.punished_t = self.cool(40, 60, 10, 15)
            k.obedience = min(100.0, k.obedience + 10)
            k.like(par.name, -3)
            k.set_expr("pout", 3)
            k.say(random.choice(KID_LINES["caught"]), 1.8)
            k.cancel = True
            corner = k.seg.x0 + 70 if kid.cx() < (k.seg.x0 + k.seg.x1) / 2 else k.seg.x1 - 70
            k.go_to(corner, k.seg, k.walk_speed())
        return True

    def court(self, p, q):
        """Un pas de plus vers le mariage : compliment, fleur, danse ou balade."""
        w = self.w
        d = dist2(p.cx(), p.feet(), q.cx(), q.feet())
        if d > 120:
            p.go_to(q.cx() - (1 if q.cx() > p.cx() else -1) * 60, q.seg, p.walk_speed())
            return
        p.face(q)
        q.face(p)
        act = random.choice(["compliment", "fleur", "danse", "balade"])
        gain = 8
        if act == "fleur":
            p.show_item, p.show_item_t = "fleur", 1.6
            gain = 10
        elif act == "danse":
            p.hop(280)
            q.hop(280)
            p.emit("note", 2, y=GROUND - 85)
        elif act == "balade":
            x = w.terrain.random_x(p.seg)
            p.go_to(x - 40, p.seg, p.walk_speed())
            q.go_to(x + 40, p.seg, q.walk_speed())
        p.say(random.choice(KID_LINES["court"]), 2)
        q.set_expr("happy", 2.5)
        q.emit("heart", 2, y=GROUND - 80)
        p.romance[q.name] = min(100.0, p.romance.get(q.name, 0) + gain)
        q.romance[p.name] = min(100.0, q.romance.get(p.name, 0) + gain * rnd(0.6, 1.1))
        p.like(q.name, 3)
        q.like(p.name, 3)
        p.social = min(100.0, p.social + 15)
        q.social = min(100.0, q.social + 15)
        if p.romance[q.name] >= 60 and q.romance.get(p.name, 0) >= 45 and p.opinion(q.name) >= 30:
            self.propose(p, q)

    def propose(self, p, q):
        p.show_item, p.show_item_t = "anneau", 2.0
        p.say(random.choice(KID_LINES["propose"]), 2.6)
        p.set_expr("surprised", 2)
        if self.demo or (q.mood_score() >= 45 and random.random() < 0.85):
            q.say(random.choice(KID_LINES["accept"]), 2.4)
            q.set_expr("happy", 4)
            for r in (p, q):
                r.emit("heart", 6, y=GROUND - 80)
                r.court_cd = 999999
                r.engaged = True
            self.queue.append(("wedding", (p, q)))
            self.log("mariage", "%s a demandé %s en mariage : oui !" % (p.name, q.name), toast=True)
        else:
            q.say(random.choice(KID_LINES["refuse"]), 2.2)
            q.set_expr("pout", 2)
            p.romance[q.name] = max(0.0, p.romance[q.name] - 15)
            p.court_cd = self.cool(600, 600, 20, 20)
            self.log("famille", "%s a demandé %s en mariage... pas encore." % (p.name, q.name))

    def arrive_visitor(self):
        w = self.w
        traits = Person.make_traits(w, village=True, gen=0)
        v = Person(w, traits)
        v.age = 14.5 * self.scale + rnd(0, 8)                   # jeune adulte
        v.apply_stage()
        seg = self.home_seg()
        v.x = seg.x1 - 70 - W / 2
        v.y = seg.yb - GROUND
        v.seg = seg
        v.state = "idle"
        v.timer = 1.0
        v.setVisible(w.visible and not w.paused)
        v.say(random.choice(KID_LINES["visitor"]), 3)
        v.go_to(self.home_x() + 300, seg, v.walk_speed())
        self.people.append(v)
        self.log("visite", "%s, %s, arrive du village avec sa valise." % (v.name, "/".join(v.persona)), toast=True)

    # ---------- décisions des habitants ----------
    def decide_person(self, p):
        w = self.w
        if w.role is not None:                                  # chasse : on se fait tout petit
            p.camo = w.role == "prey"
            p.go_idle(rnd(2, 4))
            return
        p.camo = False
        if p.dead or p.leaving is not None or self.scene is not None:
            p.go_idle(1.5)
            return
        if p.punished_t > 0:
            if self.bubble_cd <= 0 and random.random() < 0.3:
                self.famsay(p, random.choice(KID_LINES["corner"]), 1.6)
            p.go_idle(rnd(2, 4))
            return
        if self.do_duty(p):
            return
        parents = self.parents_of(p)
        if p.energy < 20 and random.random() < 0.7:
            self.famsay(p, random.choice(KID_LINES["sleep"]), 1.5)
            p.sleep(rnd(60, 180))
            return
        if p.hunger < 30 and p.fam_cd <= 0:
            p.fam_cd = 60.0
            if abs(p.cx() - self.home_x()) > 60:
                p.go_to(self.home_x() + rnd(-40, 40), self.home_seg(), p.run_speed())
                self.famsay(p, random.choice(KID_LINES["hungry"]), 1.5)
            else:
                p.hunger = min(100.0, p.hunger + 45)
                p.show_item, p.show_item_t = "biscuit", 1.4
                p.say("Miam.", 1.2)
                p.go_idle(3)
            return
        if p.farewell and random.random() < 0.5:
            self.famsay(p, random.choice(KID_LINES["farewell"]), 2.4)
            p.go_idle(rnd(3, 6))
            return
        if p.is_minor():
            return self.decide_minor(p, parents)
        return self.decide_adult(p)

    def decide_minor(self, p, parents):
        T = self.w.terrain
        # aider ? non. suivre les parents (surtout bébé), jouer, siestes, ados qui râlent
        if not parents:
            p.walk_to(T.random_x(p.seg), p.walk_speed())
            return
        if random.random() < 0.15:
            p.attach += 1
        par = parents[p.attach % len(parents)]
        d = dist2(p.cx(), p.feet(), par.cx(), par.feet())
        if par.state == "sleep" and d < 220 and random.random() < 0.4 and p.stage != "ado":
            p.sleep(rnd(15, 30))
            return
        follow = 140 if p.stage == "bébé" else 320 if p.stage == "enfant" else 700
        if d > follow:
            p.go_to(par.cx() - par.facing * rnd(50, 90), par.seg, p.run_speed() if d > 400 else p.walk_speed())
            return
        r = random.random()
        sibs = [o for o in self.alive() if o is not p and o.is_minor() and o.stage != "bébé"]
        if r < 0.22:
            p.hop(240 if p.stage == "bébé" else 300)
            if random.random() < 0.35:
                self.famsay(p, random.choice(KID_LINES["play"]), 1.4)
            p.set_expr("happy", 1.5)
            p.fun = min(100.0, p.fun + 3)
            p.go_idle(1.5)
        elif r < 0.42 and sibs and p.stage != "bébé":
            o = random.choice(sibs)
            p.go_to(o.cx() + rnd(-60, 60), o.seg, p.run_speed())
            p.set_expr("happy", 2)
            p.fun = min(100.0, p.fun + 4)
            p.social = min(100.0, p.social + 5)
        elif r < 0.6:
            p.walk_to(p.cx() + rnd(-180, 180), p.walk_speed())
        elif r < 0.7 and p.stage == "ado" and self.bubble_cd <= 0:
            self.famsay(p, random.choice(KID_LINES["teen"]), 2.2)
            p.set_expr("pout", 2.5)
            p.go_idle(3)
        elif r < 0.78 and self.bubble_cd <= 0:
            self.famsay(p, random.choice(KID_LINES["hello"] if p.stage == "bébé" else KID_LINES["play"]), 2)
            p.go_idle(2.5)
        else:
            p.go_idle(rnd(2, 4))

    def decide_adult(self, p):
        w, T = self.w, self.w.terrain
        if p.stage == "aîné" and self.story_cd <= 0 and random.random() < 0.25:
            kids = [k for k in self.minors() if dist2(p.cx(), p.feet(), k.cx(), k.feet()) < 350]
            if kids:
                self.story_cd = 30.0 if self.demo else 240.0
                p.say(random.choice(KID_LINES["story"]), 3)
                p.stories += 1
                for k in kids:
                    k.set_expr("happy", 3)
                    k.fun = min(100.0, k.fun + 10)
                    if random.random() < 0.5:
                        k.say("Encore !", 1.5)
                p.go_idle(5)
                return
        if p.stage == "aîné" and random.random() < 0.2 and self.bubble_cd <= 0:
            self.famsay(p, random.choice(KID_LINES["elder"]), 2)
            p.go_idle(4)
            return
        if p.spouse and random.random() < 0.25:
            q = self.by_name(p.spouse)
            if q is not None and q.active():
                if dist2(p.cx(), p.feet(), q.cx(), q.feet()) > 200:
                    p.go_to(q.cx() - (1 if q.cx() > p.cx() else -1) * 50, q.seg, p.walk_speed())
                else:
                    p.face(q)
                    p.emit("heart", 1, y=GROUND - 80)
                    p.go_idle(3)
                return
        kids = self.children_of(p)
        if kids and self.parent_hook(p):
            return
        if p.social < 35 and random.random() < 0.6:
            others = [q for q in w.pets + self.alive() if q is not p and q.active() and q.state in ("idle", "walk")]
            if others:
                q = random.choice(others)
                if dist2(p.cx(), p.feet(), q.cx(), q.feet()) > 150:
                    p.go_to(q.cx() + rnd(-70, 70), q.seg, p.walk_speed())
                else:
                    p.face(q)
                    self.famsay(p, random.choice(DUO_CHATS)[0], 2)
                    p.social = min(100.0, p.social + 20)
                    q.social = min(100.0, q.social + 10)
                    p.like(q.name, 2)
                    p.go_idle(3)
                return
        r = random.random()
        if r < 0.45:
            near_home = self.home_x() + rnd(-350, 350) if p.visitor else T.random_x(p.seg)
            p.walk_to(near_home, p.walk_speed())
        elif r < 0.55 and "curieux" in p.persona and len(T.segs) > 1:
            seg = T.random_seg(exclude=p.seg)
            p.go_to(T.random_x(seg), seg, p.walk_speed())
        elif r < 0.65 and w.chest_list() and w.seek_chest(p, 0.0, radius=700):
            return
        elif r < 0.75 and "sportif" in p.persona:
            p.hop(330)
            p.go_idle(1.5)
        elif r < 0.82 and self.bubble_cd <= 0:
            self.famsay(p, random.choice(SOLO_LINES["Hybris"] + SOLO_LINES["Iblis"]), 2.2)
            p.go_idle(3)
        else:
            p.go_idle(rnd(2, 5))

    def parent_hook(self, p):
        """Un parent (fondateur ou habitant) s'occupe des petits. Renvoie True s'il est occupé."""
        w = self.w
        mine = [k for k in self.alive() if p.name in k.parents] or (self.minors() if p in w.pets else [])
        if not mine:
            return False
        kid = next((k for k in mine if (k.cry_t > 0 or k.lonely_t > 3) and k.leaving is None), None)
        if kid is not None:
            d = dist2(p.cx(), p.feet(), kid.cx(), kid.feet())
            if d > 100:
                p.go_to(kid.cx() - (1 if kid.cx() > p.cx() else -1) * 40, kid.seg, 120)
                if random.random() < 0.4:
                    p.say(random.choice(KID_LINES["parent_fetch"]), 1.6)
            else:
                kid.cry_t, kid.lonely_t = 0.0, 0.0
                kid.set_expr("happy", 2)
                kid.emit("heart", 3, y=GROUND - 60)
                p.emit("heart", 2, y=GROUND - 80)
                p.face(kid)
                kid.like(p.name, 3)
                if random.random() < 0.5 and kid.mount(p):
                    kid.ride_t = 0.0
                    p.say("Allez, hop !", 1.4)
                p.go_idle(2)
            return True
        studying = [k for k in mine if k.duty == "study" and k.state == "idle"
                    and not any(q.duty == "help" and q.helping == k.name for q in w.pets + self.adults())]
        if studying and p.duty is None and random.random() < 0.5:
            k = random.choice(studying)
            p.duty, p.helping = "help", k.name
            self.famsay(p, random.choice(KID_LINES["help"]), 1.8, force=True)
            return True
        if self.egg is not None and not self.egg["done"] and p.name in self.egg["parents"] and random.random() < 0.3:
            e = self.egg
            if abs(p.cx() - e["x"]) > 90:
                p.go_to(e["x"] + random.choice((-70, 70)), e["seg"], 90)
            else:
                p.facing = 1 if e["x"] > p.cx() else -1
                p.say(random.choice(["Ça bouge !", "Chut, il dort.", "Bientôt..."]), 1.8)
                p.set_expr("happy", 2)
                p.go_idle(3)
            return True
        near = [k for k in mine if k.leaving is None and k.state in ("idle", "walk") and k.punished_t <= 0
                and k.duty is None and dist2(p.cx(), p.feet(), k.cx(), k.feet()) < 400]
        if near and random.random() < 0.12:
            kid = random.choice(near)
            d = dist2(p.cx(), p.feet(), kid.cx(), kid.feet())
            if d > 80:
                p.go_to(kid.cx() - (1 if kid.cx() > p.cx() else -1) * 45, kid.seg, 90)
            else:
                p.face(kid)
                p.attack_t = 0.6
                p.say(random.choice(KID_LINES["parent_play"]), 1.8)
                kid.set_expr("happy", 2.5)
                kid.say("Hihihi !", 1.5)
                kid.hop(220)
                kid.emit("heart", 3, y=GROUND - 60)
                kid.like(p.name, 2)
                p.go_idle(2.5)
            return True
        return False

    def founder_hook(self, p):
        """Les fondateurs vivent aussi la journée : dodo, travail, repas, enfants, adieux."""
        if not self.active or self.w.role is not None or self.scene is not None:
            return False
        if self.do_duty(p):
            return True
        if p.hunger < 30 and p.fam_cd <= 0:                     # petit creux : un biscuit à la maison
            p.fam_cd = 60.0
            if abs(p.cx() - self.home_x()) > 60:
                p.go_to(self.home_x() + rnd(-40, 40), self.home_seg(), 90)
                self.famsay(p, random.choice(KID_LINES["hungry"]), 1.5)
            else:
                p.hunger = min(100.0, p.hunger + 45)
                p.show_item, p.show_item_t = "biscuit", 1.4
                p.say("Miam.", 1.2)
                p.go_idle(3)
            return True
        elders = [q for q in self.alive() if q.farewell]
        if elders and random.random() < 0.3:
            q = elders[0]
            if dist2(p.cx(), p.feet(), q.cx(), q.feet()) > 90:
                p.go_to(q.cx() - (1 if q.cx() > p.cx() else -1) * 40, q.seg, 100)
            else:
                p.face(q)
                p.hugging = True
                QTimer.singleShot(2500, lambda p=p: setattr(p, "hugging", False))
                p.say(random.choice(KID_LINES["mourn"][:2]), 2)
                p.emit("heart", 2, y=GROUND - 80)
                p.go_idle(3)
            return True
        if self.graves and random.random() < 0.03 and self.decor_on:
            i = len(self.graves[-6:]) - 1
            gx = self.cemetery_x(i)
            if abs(p.cx() - gx) > 60:
                p.go_to(gx + 40, self.home_seg(), 80)
            else:
                p.facing = -1
                p.say(random.choice(KID_LINES["mourn"]), 2.2)
                p.set_expr("pout", 2.5)
                pr = self.decor.get("tombe%d" % i)
                if pr is not None:
                    pr.flowers = min(4, pr.flowers + 1)
                p.go_idle(4)
            return True
        return self.parent_hook(p) if (self.people or self.egg) else False

    def founders_can_lay(self):
        return (self.egg is None and self.population() < POP_MAX and self.scene is None
                and time.time() - self.last_birth > BIRTH_COOLDOWN)

    # ---------- livre de famille ----------
    def write_book(self):
        w = self.w
        path = os.path.join(tempfile.gettempdir(), "h13ris_livre_de_famille.html")
        def avatar(hue, size=28):
            return ('<span class="av" style="width:%dpx;height:%dpx;background:hsl(%d,55%%,62%%)"></span>'
                    % (size, size, int(hue)))
        rows = []
        for p in w.pets:
            h = SKINS[p.name]["body"][0]
            rows.append("<div class='card'>%s<b>%s</b> — fondateur immortel · %s</div>"
                        % (avatar(h), p.name, "/".join(p.persona) or "—"))
        for p in sorted(self.alive(), key=lambda q: (q.gen, q.age)):
            extra = []
            if p.is_minor():
                extra.append("note %s" % grade_letter(p.grade))
            if p.spouse:
                extra.append("marié%s à %s" % ("e" if p.name[-1] == "a" else "", p.spouse))
            if p.parents:
                extra.append("enfant de %s" % " et ".join(p.parents))
            if p.visitor:
                extra.append("visiteur du village")
            rows.append("<div class='card'>%s<b>%s</b> — %s, %.1f h, génération %d · %s%s</div>"
                        % (avatar(p.traits.get("hue", 300)), p.name, p.stage, p.age, p.gen,
                           "/".join(p.persona), (" · " + ", ".join(extra)) if extra else ""))
        mem = "".join("<div class='card dim'>%s<b>%s</b> — parti%s vers la lune le %s à %s h (génération %s%s)</div>"
                      % (avatar(m.get("hue", 300)), m["name"], "e" if m["name"][-1] == "a" else "",
                         m.get("died", "?"), m.get("age", "?"), m.get("gen", "?"),
                         (", enfant de " + " et ".join(m["parents"])) if m.get("parents") else "")
                      for m in reversed(self.memorial)) or "<p class='dim'>Personne n'est encore parti.</p>"
        evs = "".join("<li><span class='k'>%s</span> <span class='t'>%s</span> %s</li>"
                      % (BOOK_KINDS.get(e["k"], "•"), e["t"], e["s"]) for e in reversed(self.events[-200:])) \
            or "<li class='dim'>Rien encore. Laissez-les vivre.</li>"
        html = """<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>Livre de famille — H13ris</title>
<style>
body{font-family:Segoe UI,system-ui,sans-serif;background:#1d2030;color:#e9e9f2;margin:0;padding:28px;max-width:900px;margin:auto}
h1{font-weight:700;margin:0 0 4px}h2{margin-top:32px;border-bottom:1px solid #3a3f55;padding-bottom:6px}
.sub{color:#9aa0b8;margin-bottom:20px}.card{display:flex;align-items:center;gap:12px;background:#262a3c;border-radius:12px;padding:10px 14px;margin:6px 0}
.av{display:inline-block;border-radius:50%%;flex:none;box-shadow:inset -3px -3px 0 rgba(0,0,0,.15)}
.dim{opacity:.6}ul{list-style:none;padding:0}li{padding:6px 0;border-bottom:1px dashed #33384d}.k{margin-right:6px}.t{color:#9aa0b8;font-size:.85em;margin-right:8px}
</style></head><body>
<h1>📖 Livre de famille d'Hybris &amp; Iblis</h1>
<div class="sub">%s · %d habitant(s) · %.1f h de vie commune · %d parti(s) vers la lune</div>
<h2>Habitants</h2>%s
<h2>Mémorial</h2>%s
<h2>Chronique</h2><ul>%s</ul>
</body></html>""" % (datetime.datetime.now().strftime("%d/%m/%Y %H:%M"), self.population(), self.hours,
                     len(self.memorial), "".join(rows), mem, evs)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            webbrowser.open("file:///" + path.replace("\\", "/"))
        except Exception:
            pass
        return path

    # ---------- menu ----------
    def toggle_demo(self, on):
        if on:
            self.start_demo()
            if not self.demo:
                random.choice(self.w.pets).say("La famille vit dans la première instance !" if not self.active
                                               else "Pas maintenant !", 2.4)
                self.sync_demo_act()
        else:
            self.stop_demo()

    def sync_demo_act(self):
        act = getattr(self.w, "demo_act", None)
        if act is not None:
            act.blockSignals(True)
            act.setChecked(self.demo)
            act.blockSignals(False)

    def fill_menu(self, fm):
        w = self.w
        fm.clear()

        def add(text, fn, enabled=True, tip=None):
            act = fm.addAction(text)
            act.triggered.connect(fn)
            act.setEnabled(enabled)
            if tip:
                act.setToolTip(tip)
            return act

        ok = self.active and w.role is None
        add("📖 Livre de famille", self.write_book, self.active,
            "Ouvre la chronique, l'arbre et le mémorial dans le navigateur.")
        add("🥚 Avoir un bébé maintenant", self.force_birth,
            ok and self.egg is None and self.population() < POP_MAX, "Hybris et Iblis pondent un œuf tout de suite.")
        add("🎒 Inviter un visiteur du village", self.arrive_visitor, ok and self.population() < POP_MAX,
            "Un jeune adulte arrive avec sa valise, prêt à se marier ici.")
        add("🎉 Organiser une fête", lambda: self.force_festival(" (à ta demande)"), ok and self.scene is None)
        add("📸 Photo de famille", lambda: w.force_duo("photo"), ok)
        fm.addSeparator()
        if not self.active:
            fm.addAction("Le village vit dans la première instance lancée.").setEnabled(False)
            return
        if self.demo:
            fm.addAction("🎬 Démo en cours (%d s) — la vraie famille reviendra ensuite." % self.demo_t).setEnabled(False)
        if self.egg is not None and not self.egg["done"]:
            fm.addAction("🥚 Un œuf couve : éclosion dans %d s" % max(0, self.egg["hatch"] - self.egg["t"])).setEnabled(False)
        people = sorted(self.alive(), key=lambda q: (q.gen, q.age))
        if not people:
            fm.addAction("Pas encore d'habitant (complicité %d / %d)" % (w.bond, BIRTH_BOND)).setEnabled(False)
        else:
            fm.addAction("Habitants (%d / %d) :" % (self.population(), POP_MAX)).setEnabled(False)
            for p in people:
                fm.addAction("    " + self.person_label(p)).setEnabled(False)
        if self.memorial:
            names = ", ".join(m["name"] for m in self.memorial[-4:])
            fm.addAction("☾ Partis vers la lune : %s%s" % (names, "…" if len(self.memorial) > 4 else "")).setEnabled(False)



# --------------------------------------------------------------------------- #
# Fan meeting : un groupe d'idoles (fictif) passe sur le bureau. Les démons et
# tout le village deviennent des fans surexcités : cris, photos, selfies,
# autographes, cœurs, évanouissements, larmes de joie, fanchant, chorégraphie.
# Les groupes sont inventés ; l'éditeur permet de créer les siens.
# --------------------------------------------------------------------------- #
import re  # noqa: E402

OUTFIT_COLORS = dict(HAIR_COLORS, blanc="#F4F4F8")


def draw_lightstick(p, x, y, hue, shape, angle=0.0, glow=1.0, s=1.0):
    p.save()
    p.translate(x, y)
    p.rotate(angle)
    p.scale(s, s)
    p.setPen(mkpen(QColor("#2A2D3A"), 1.2))
    p.setBrush(QColor("#F4F4F8"))
    p.drawRoundedRect(QRectF(-2.6, -20, 5.2, 22), 2, 2)
    c = hsl(hue, 0.85, 0.62)
    g = QRadialGradient(QPointF(0, -28), 16)
    halo = QColor(c)
    halo.setAlpha(int(120 * glow))
    g.setColorAt(0.0, halo)
    g.setColorAt(1.0, QColor(c.red(), c.green(), c.blue(), 0))
    p.setPen(NO_PEN)
    p.setBrush(g)
    p.drawEllipse(QPointF(0, -28), 16, 16)
    p.setPen(mkpen(c.darker(150), 1.2))
    p.setBrush(c.lighter(100 + int(40 * glow)))
    if shape == "etoile":
        p.drawPolygon(star_poly(0, -28, 9, 4.2))
    elif shape == "coeur":
        p.drawPath(heart_path(0, -28, 7))
    else:
        p.drawEllipse(QPointF(0, -28), 7.5, 7.5)
    p.setPen(NO_PEN)
    p.setBrush(QColor(255, 255, 255, 190))
    p.drawEllipse(QPointF(-2.5, -31), 2.2, 1.6)
    p.restore()


def draw_fan_prop(pet, p):
    """Objet de fan tenu par un démon ou un habitant (coordonnées locales du pet)."""
    kind = pet.fan_prop
    if kind == "lightstick":
        wave = math.sin(pet.t * 7) * 20
        glow = 0.7 + 0.3 * math.sin(pet.t * 9)
        if pet.arm_up:
            draw_lightstick(p, 31, -58, pet.fan_hue, pet.fan_stick, -10 + wave, glow)
        else:
            draw_lightstick(p, 37, -26, pet.fan_hue, pet.fan_stick, 25 + wave * 0.4, glow)
    elif kind == "telephone":
        draw_item_icon(p, "telephone", 40, -58 if pet.arm_up else -40, 0.8)
    elif kind == "selfie":
        draw_item_icon(p, "telephone", 36, -88, 0.8, -12)


def paint_banniere(pr, p, cx, gy):
    c = hsl(pr.hue, 0.7, 0.55)
    _shadow(p, cx, gy, 70)
    p.setPen(mkpen(QColor("#5A5F75"), 2.4))
    for px in (cx - 70, cx + 70):
        p.drawLine(QPointF(px, gy), QPointF(px, gy - 108))
    p.setPen(NO_PEN)
    p.setBrush(QColor("#FFD23F"))
    for px in (cx - 70, cx + 70):
        p.drawEllipse(QPointF(px, gy - 110), 3.5, 3.5)
    rect = QRectF(cx - 66, gy - 104, 132, 36)
    g = QLinearGradient(rect.topLeft(), rect.bottomLeft())
    g.setColorAt(0, c.lighter(115))
    g.setColorAt(1, c.darker(115))
    p.setPen(mkpen(c.darker(160), 1.4))
    p.setBrush(g)
    path = QPainterPath(rect.topLeft())
    path.lineTo(rect.topRight())
    path.lineTo(rect.bottomRight())
    for k in range(6):                                   # bord festonné
        x1 = rect.right() - (k + 1) * rect.width() / 6
        path.quadTo(QPointF(x1 + rect.width() / 12, rect.bottom() + 6), QPointF(x1, rect.bottom()))
    path.closeSubpath()
    p.drawPath(path)
    f = QFont("Segoe UI", 12)
    f.setWeight(QFont.Weight.Black)
    p.setFont(f)
    outlined_text(p, rect, pr.label, QColor("#FFFFFF"), c.darker(190), 1)
    p.setPen(NO_PEN)
    for k in range(9):                                   # guirlande d'ampoules
        on = (int(pr.t * 4) + k) % 3 == 0
        p.setBrush(QColor("#FFF6B0") if on else QColor(255, 210, 63, 150))
        p.drawEllipse(QPointF(cx - 64 + k * 16, gy - 110 + (k % 2) * 3), 2.6, 2.6)
    for sx in (-1, 1):
        p.setBrush(QColor(255, 255, 255, 200))
        p.drawPolygon(star_poly(cx + sx * 56, gy - 60, 4, 1.8, rot=pr.t))


DECOR_PAINTERS["banniere"] = paint_banniere


# --------------------------------------------------------------------------- #
# Une idole : petit personnage chibi (tête ronde, coiffure et accessoire
# distinctifs, tenue de scène, pose signature, nom sous les pieds).
# --------------------------------------------------------------------------- #
class Idol(Pet):
    DANCE = ["arms_up", "point", "wave", "peace", "heart", "point", "arms_up", "big_heart"]

    def __init__(self, world, group, m):
        skin = dict(body=(20, 0.5, 0.8), belly=(20, 0.5, 0.85), horn="#000000", horn_line="#000000",
                    tail_tip="#000000", horn_shape="", blush="#FF9EB8",
                    iris_top=m.get("eyes", "#8A5A3B"), iris_bot="#2A1A14", mark="")
        super().__init__(m["name"], world, skin=skin)
        self.is_idol = True
        self.busy = True
        self.group, self.m = group, m
        self.c_skin = QColor(SKIN_TONES[int(m.get("skin", 0)) % len(SKIN_TONES)])
        self.c_hair = QColor(HAIR_COLORS.get(m.get("hc"), m.get("hc", "#1E1B24")))
        self.c_outfit = QColor(OUTFIT_COLORS.get(m.get("oc"), m.get("oc", "#26306B")))
        self.c_group = hsl(group.get("hue", 300), 0.75, 0.55)
        self.c_line = self.c_skin.darker(170)
        self.c_body = self.c_skin
        self.eye_k = 0.95
        self.pose, self.pose_t, self.dance_pose = None, 0.0, None
        self.delay, self.entered, self.exited = 0.0, False, False
        self.spot = 0.0
        self.show_name = True

    # ---- poses ----
    def set_pose(self, pose, dur=1.8):
        self.pose, self.pose_t = pose, dur
        if pose == "wink":
            self.set_expr("wink", dur)
        elif pose in ("heart", "big_heart", "peace", "wave", "arms_up"):
            self.set_expr("happy", dur)

    def cur_pose(self):
        if self.dance_pose:
            return self.dance_pose
        if self.pose_t > 0:
            return self.pose
        return None

    def tick(self, dt):
        self.pose_t = max(0.0, self.pose_t - dt)
        Pet.tick(self, dt)

    def snapshot(self):
        d = Pet.snapshot(self)
        d["idol"] = True
        return d

    def paint_all(self, p, bubble=True):
        Pet.paint_all(self, p, bubble)
        if self.show_name and bubble and self.state not in ("ghost", "gone"):
            f = QFont("Segoe UI", 7)
            f.setWeight(QFont.Weight.Bold)
            p.setFont(f)
            p.setOpacity(self.alpha())
            outlined_text(p, QRectF(W / 2 - 40, GROUND + 1, 80, 12), self.name, self.c_group.lighter(135),
                          QColor(30, 20, 40), 1)

    # ---- dessin (pieds en (0,0), regard vers +x) ----
    def draw_character(self, p):
        t, st = self.t, self.state
        walking = st == "walk" and not self.airborne
        ph = self.walk_phase
        fm = self.face_mode()
        pose = self.cur_pose()
        outfit = self.m.get("outfit", "veste")
        if pose == "bow":
            p.translate(0, -16)
            p.rotate(26)
            p.translate(0, 16)
        oc, sk = self.c_outfit, self.c_skin
        pants = QColor("#2A2D3A") if oc.lightness() > 150 else QColor("#F4F4F8") if outfit == "costume" \
            and oc.lightness() < 60 else QColor("#3A3F52")
        if outfit == "costume":
            pants = oc.darker(115)
        # jambes et chaussures
        for i, lx in enumerate((-7, 7)):
            lift = max(0.0, math.sin(ph + i * math.pi)) * 5 if walking else 0.0
            if st in ("drag", "fall") or self.airborne:
                lift = 2 + math.sin(t * 8 + i) * 2
            p.setPen(mkpen(pants.darker(150), 1.1))
            p.setBrush(pants if outfit not in ("robe", "crop") else sk)
            p.drawRoundedRect(QRectF(lx - 4.5, -22 - lift, 9, 17), 4, 4)
            p.setPen(mkpen(QColor("#9AA0B8"), 1.0))
            p.setBrush(QColor("#FFFFFF") if outfit != "costume" else QColor("#1E1B24"))
            p.drawRoundedRect(QRectF(lx - 4.5, -7 - lift, 12, 7), 3, 3)
        # jupe / robe
        if outfit in ("robe", "crop"):
            skirt = oc if outfit == "robe" else oc.darker(125)
            p.setPen(mkpen(skirt.darker(150), 1.2))
            p.setBrush(skirt)
            sw = math.sin(t * 3) * 1.5
            p.drawPolygon(QPolygonF([QPointF(-11, -30), QPointF(11, -30), QPointF(17 + sw, -14),
                                     QPointF(-17 + sw, -14)]))
        # torse
        top_y = -45
        waist = -30 if outfit == "crop" else -20
        g = QLinearGradient(QPointF(0, top_y), QPointF(0, waist))
        g.setColorAt(0, oc.lighter(110))
        g.setColorAt(1, oc.darker(112))
        p.setPen(mkpen(oc.darker(160), 1.4))
        p.setBrush(g)
        torso = QPainterPath(QPointF(-15, top_y + 3))
        torso.quadTo(QPointF(0, top_y - 2), QPointF(15, top_y + 3))
        torso.lineTo(QPointF(13, waist))
        torso.quadTo(QPointF(0, waist + 3), QPointF(-13, waist))
        torso.closeSubpath()
        p.drawPath(torso)
        if outfit == "crop":                                    # ventre
            p.setPen(NO_PEN)
            p.setBrush(sk)
            p.drawRoundedRect(QRectF(-12, -31, 24, 3), 1.5, 1.5)
        p.setPen(NO_PEN)
        if outfit == "costume":                                 # chemise + cravate/nœud
            p.setBrush(QColor("#FFFFFF"))
            p.drawPolygon(QPolygonF([QPointF(-6, top_y + 1), QPointF(6, top_y + 1), QPointF(0, -30)]))
            p.setBrush(self.c_group)
            p.drawPolygon(QPolygonF([QPointF(-1.8, top_y + 3), QPointF(1.8, top_y + 3), QPointF(2.6, -31),
                                     QPointF(0, -28), QPointF(-2.6, -31)]))
        elif outfit == "veste":                                 # veste ouverte, t-shirt
            p.setBrush(QColor("#FFFFFF") if oc.lightness() < 200 else QColor("#2A2D3A"))
            p.drawRect(QRectF(-4, top_y + 1, 8, waist - top_y - 2))
            p.setPen(mkpen(oc.darker(170), 1.0))
            p.drawLine(QPointF(-4, top_y + 2), QPointF(-4, waist - 1))
            p.drawLine(QPointF(4, top_y + 2), QPointF(4, waist - 1))
            p.setPen(NO_PEN)
        elif outfit == "sweat":                                 # capuche + cordons + poche
            p.setBrush(oc.darker(118))
            p.drawEllipse(QPointF(-3, top_y + 1), 11, 4)
            p.setPen(mkpen(QColor("#FFFFFF"), 1.1))
            p.drawLine(QPointF(-3, top_y + 3), QPointF(-3, top_y + 11))
            p.drawLine(QPointF(3, top_y + 3), QPointF(3, top_y + 11))
            p.setPen(mkpen(oc.darker(150), 1.0))
            p.drawLine(QPointF(-8, -26), QPointF(8, -26))
            p.setPen(NO_PEN)
        elif outfit == "robe":
            p.setBrush(self.c_group.lighter(130))
            p.drawEllipse(QPointF(0, -31), 11, 2)
        # cou
        p.setBrush(sk.darker(106))
        p.drawRect(QRectF(-4, -50, 8, 7))
        # cheveux (arrière)
        back, bangs = HAIR_STYLES.get(self.m.get("hair"), (None, "rideau"))
        self.draw_hair_back(p, back)
        # tête
        hg = QRadialGradient(QPointF(-6, -74), 30)
        hg.setColorAt(0, sk.lighter(106))
        hg.setColorAt(1, sk.darker(106))
        p.setPen(mkpen(self.c_line, 1.4))
        p.setBrush(hg)
        p.drawEllipse(QPointF(-23, -63), 3.6, 4.6)
        p.drawEllipse(QPointF(23, -63), 3.6, 4.6)
        p.drawEllipse(QPointF(0, -66), 24, 24)
        if self.hurt > 0:
            p.setPen(NO_PEN)
            p.setBrush(QColor(255, 255, 255, 100))
            p.drawEllipse(QPointF(0, -66), 24, 24)
        # joues
        big = fm in ("happy", "wink")
        bl = QColor(self.c_blush)
        bl.setAlpha(170 if big else 110)
        p.setPen(NO_PEN)
        p.setBrush(bl)
        for bx in (-14, 15):
            p.drawEllipse(QPointF(bx, -56), 4.5 if big else 3.6, 2.6)
        # visage : yeux et bouche des pets, réduits
        p.save()
        p.translate(0, -64)
        p.scale(0.74, 0.74)
        p.translate(0, 36)
        self.draw_eyes(p, fm)
        self.draw_mouth(p, fm)
        p.restore()
        # cheveux (avant) et accessoire
        self.draw_bangs(p, bangs)
        self.draw_idol_acc(p, self.m.get("acc", "aucun"))
        self.draw_arms(p, pose, walking, ph)

    # ---- cheveux ----
    def hair_brush(self, top=-94, bottom=-40):
        g = QLinearGradient(QPointF(0, top), QPointF(0, bottom))
        g.setColorAt(0, self.c_hair.lighter(118))
        g.setColorAt(1, self.c_hair.darker(118))
        return g

    def draw_hair_back(self, p, back):
        if not back:
            return
        hc = self.c_hair
        p.setPen(mkpen(hc.darker(150), 1.3))
        p.setBrush(self.hair_brush())
        if back == "long":
            p.drawRoundedRect(QRectF(-28, -86, 56, 62), 16, 14)
        elif back == "carre":
            p.drawRoundedRect(QRectF(-29, -88, 58, 44), 16, 8)
        elif back == "mulet":
            p.drawRoundedRect(QRectF(-27, -76, 24, 34), 8, 8)
        elif back == "couettes":
            for sx in (-1, 1):
                p.save()
                p.translate(sx * 30, -60)
                p.rotate(sx * -12)
                p.drawEllipse(QPointF(0, 6), 7.5, 17)
                p.restore()
            p.setPen(NO_PEN)
            p.setBrush(self.c_group)
            for sx in (-1, 1):
                p.drawEllipse(QPointF(sx * 27, -73), 3.5, 3.5)
        elif back == "queue":
            p.save()
            p.translate(-24, -74)
            p.rotate(28 + math.sin(self.t * 4) * 6)
            p.drawEllipse(QPointF(0, 14), 7.5, 17)
            p.restore()
            p.setPen(NO_PEN)
            p.setBrush(self.c_group)
            p.drawEllipse(QPointF(-23, -76), 3.5, 3.5)
        elif back == "chignon":
            p.drawEllipse(QPointF(-2, -95), 10, 9)
            p.setPen(NO_PEN)
            p.setBrush(self.c_group)
            p.drawRoundedRect(QRectF(-8, -89, 12, 3), 1.5, 1.5)
        elif back == "boucles":
            for k in range(9):
                a = math.radians(150 + k * 30)
                p.drawEllipse(QPointF(25 * math.cos(a), -64 + 25 * math.sin(a)), 8, 8)

    def draw_bangs(self, p, bangs):
        hc = self.c_hair
        p.setPen(mkpen(hc.darker(150), 1.3))
        p.setBrush(self.hair_brush(-94, -60))
        if bangs == "rase":
            path = QPainterPath(QPointF(23, -74))
            path.arcTo(QRectF(-25, -91, 50, 50), 18, 144)
            path.closeSubpath()
            p.setBrush(hc)
            p.drawPath(path)
            p.setPen(NO_PEN)
            p.setBrush(hc.darker(130))
            for k in range(7):
                p.drawEllipse(QPointF(-15 + k * 5, -82 + (k % 2) * 2), 0.9, 0.9)
            return
        path = QPainterPath(QPointF(26, -60))
        path.arcTo(QRectF(-26, -92, 52, 52), 0, 180)
        if bangs == "rideau":
            path.lineTo(QPointF(-24, -54))
            path.quadTo(QPointF(-16, -72), QPointF(0, -80))
            path.quadTo(QPointF(16, -72), QPointF(24, -54))
        elif bangs == "frange":
            path.lineTo(QPointF(-24, -60))
            path.lineTo(QPointF(-20, -70))
            for k in range(9):
                x = -20 + (k + 1) * 4.4
                path.lineTo(QPointF(x, -69 if k % 2 == 0 else -72))
            path.lineTo(QPointF(24, -60))
        elif bangs == "meche":
            path.lineTo(QPointF(-24, -64))
            path.quadTo(QPointF(-6, -70), QPointF(8, -78))
            path.quadTo(QPointF(14, -64), QPointF(25, -52))
        elif bangs == "pointes":
            path.lineTo(QPointF(-24, -62))
            for k, (x, y) in enumerate(((-16, -73), (-10, -66), (-3, -75), (4, -67), (11, -74), (17, -64),
                                        (22, -70))):
                path.lineTo(QPointF(x, y))
            path.lineTo(QPointF(25, -58))
        elif bangs == "boucles":
            path.lineTo(QPointF(-24, -64))
            path.lineTo(QPointF(24, -64))
        path.closeSubpath()
        p.drawPath(path)
        if bangs == "pointes":                                   # épis sur le dessus
            spikes = QPainterPath()
            for k in range(5):
                a = math.radians(200 + k * 35)
                bx, by = 22 * math.cos(a), -66 + 22 * math.sin(a)
                tx, ty = 33 * math.cos(a + 0.18), -66 + 33 * math.sin(a + 0.18)
                spikes.addPolygon(QPolygonF([QPointF(bx - 5 * math.sin(a), by + 5 * math.cos(a)),
                                             QPointF(tx, ty),
                                             QPointF(bx + 5 * math.sin(a), by - 5 * math.cos(a))]))
            p.drawPath(spikes)
        if bangs == "boucles":
            for k in range(7):
                x = -21 + k * 7
                p.drawEllipse(QPointF(x, -68 - 4 * math.sin(k * math.pi / 6)), 5.5, 5.5)
        # reflet
        p.setPen(mkpen(QColor(255, 255, 255, 110), 1.6))
        p.setBrush(NO_BRUSH)
        p.drawArc(QRectF(-18, -88, 30, 20), 40 * 16, 80 * 16)

    # ---- accessoires ----
    def draw_idol_acc(self, p, acc):
        grp = self.c_group
        if acc == "lunettes":
            p.setPen(mkpen(QColor("#2A2D3A"), 1.5))
            p.setBrush(QColor(255, 255, 255, 50))
            for ex in (-9, 10):
                p.drawEllipse(QPointF(ex, -64), 6.8, 6.8)
            p.drawLine(QPointF(-2.2, -64), QPointF(3.2, -64))
        elif acc == "piercing":
            p.setPen(mkpen(QColor("#FFD23F"), 1.3))
            p.setBrush(NO_BRUSH)
            p.drawEllipse(QPointF(24, -58), 2.4, 2.4)
            p.drawEllipse(QPointF(-24, -58), 2.4, 2.4)
        elif acc == "casquette":
            p.setPen(mkpen(grp.darker(160), 1.3))
            p.setBrush(grp)
            p.drawChord(QRectF(-26, -96, 52, 40), 0, 180 * 16)
            p.drawRoundedRect(QRectF(8, -79, 26, 5), 2.5, 2.5)
            p.setPen(NO_PEN)
            p.setBrush(QColor("#FFFFFF"))
            p.drawEllipse(QPointF(-2, -88), 3, 3)
        elif acc == "bandana":
            p.setPen(mkpen(QColor("#8E1A24"), 1.1))
            p.setBrush(QColor("#D8323C"))
            p.drawRoundedRect(QRectF(-25, -80, 50, 7), 3, 3)
            p.drawPolygon(QPolygonF([QPointF(-24, -78), QPointF(-34, -72), QPointF(-30, -80)]))
            p.setPen(NO_PEN)
            p.setBrush(QColor("#FFFFFF"))
            for k in range(5):
                p.drawEllipse(QPointF(-16 + k * 8, -76.5), 1, 1)
        elif acc == "bonnet":
            p.setPen(mkpen(grp.darker(160), 1.3))
            p.setBrush(grp.lighter(115))
            p.drawChord(QRectF(-26, -100, 52, 50), 0, 180 * 16)
            p.setBrush(grp)
            p.drawRoundedRect(QRectF(-27, -79, 54, 8), 4, 4)
            p.setBrush(QColor("#FFFFFF"))
            p.drawEllipse(QPointF(0, -101), 5, 5)
        elif acc == "oreillette":
            p.setPen(mkpen(QColor("#2A2D3A"), 1.2))
            p.setBrush(QColor("#2A2D3A"))
            p.drawEllipse(QPointF(23, -63), 2.6, 3)
            p.setBrush(NO_BRUSH)
            path = QPainterPath(QPointF(23, -60))
            path.quadTo(QPointF(24, -52), QPointF(15, -50))
            p.drawPath(path)
            p.setBrush(QColor("#2A2D3A"))
            p.drawEllipse(QPointF(14, -50), 1.8, 1.8)
        elif acc == "noeud":
            p.setPen(mkpen(QColor("#B8336A"), 1.1))
            p.setBrush(QColor("#FF7FB2"))
            p.drawPolygon(QPolygonF([QPointF(-14, -88), QPointF(-24, -95), QPointF(-24, -81)]))
            p.drawPolygon(QPolygonF([QPointF(-14, -88), QPointF(-4, -95), QPointF(-4, -81)]))
            p.drawEllipse(QPointF(-14, -88), 3, 3)
        elif acc == "serre_tete":
            p.setPen(mkpen(grp.lighter(130), 3.2))
            p.setBrush(NO_BRUSH)
            p.drawArc(QRectF(-25, -92, 50, 50), 25 * 16, 130 * 16)
        elif acc == "grain":
            p.setPen(NO_PEN)
            p.setBrush(QColor("#3A2418"))
            p.drawEllipse(QPointF(14, -58), 1.1, 1.1)
        elif acc == "pansement":
            p.save()
            p.translate(-14, -57)
            p.rotate(-20)
            p.setPen(mkpen(QColor("#C98A4B"), 0.9))
            p.setBrush(QColor("#F2C99A"))
            p.drawRoundedRect(QRectF(-6, -2.2, 12, 4.4), 2, 2)
            p.setPen(NO_PEN)
            p.setBrush(QColor("#C98A4B"))
            for dx in (-1.5, 1.5):
                p.drawEllipse(QPointF(dx, 0), 0.6, 0.6)
            p.restore()
        elif acc == "etoile":
            p.setPen(mkpen(QColor("#C99A1C"), 1.0))
            p.setBrush(QColor("#FFD23F"))
            p.drawPolygon(star_poly(15, -86, 6, 2.6))

    # ---- bras et gestes ----
    def draw_arms(self, p, pose, walking, ph):
        sw = math.sin(ph) * 5 if walking else 0.0
        t = self.t
        front, back = (19, -22 + sw), (-19, -22 - sw)
        felbow = belbow = None
        extra = None
        if pose == "wave":
            front = (27 + math.sin(t * 12) * 4, -70)
        elif pose == "point":
            front = (38, -60)
        elif pose == "heart":
            front, extra = (13, -52), "finger_heart"
        elif pose in ("peace", "wink"):
            front, extra = (22, -70), "peace"
        elif pose == "arms_up":
            front, back = (22, -86), (-22, -86)
        elif pose == "big_heart":
            front, back = (2, -100), (-2, -100)
            felbow, belbow = (27, -84), (-27, -84)
        elif pose == "sign":
            front, extra = (32, -38), "pen"
        elif pose == "mic":
            front, extra = (12, -54), "mic"
        elif pose == "bow":
            front, back = (8, -24), (-8, -24)
        elif self.state == "drag":
            front, back = (24, -56), (-24, -56)
        oc = self.c_outfit
        pen = mkpen(oc.darker(150), 7.6)
        inner = mkpen(oc, 5.6)
        for (sx, sy), hand, elbow in (((-14, -42), back, belbow), ((14, -42), front, felbow)):
            path = QPainterPath(QPointF(sx, sy))
            if elbow:
                path.quadTo(QPointF(*elbow), QPointF(*hand))
            else:
                path.lineTo(QPointF(*hand))
            p.setBrush(NO_BRUSH)
            p.setPen(pen)
            p.drawPath(path)
            p.setPen(inner)
            p.drawPath(path)
            p.setPen(mkpen(self.c_skin.darker(140), 1.0))
            p.setBrush(self.c_skin)
            p.drawEllipse(QPointF(*hand), 3.8, 3.8)
        p.setPen(NO_PEN)
        if extra == "finger_heart" or pose == "big_heart":
            hx, hy = (19, -62) if extra else (0, -110)
            s = 4 if extra else 7
            p.setBrush(QColor("#FF4F7B"))
            p.drawPath(heart_path(hx, hy - math.sin(t * 6) * 1.5, s))
        elif extra == "peace":
            p.setPen(mkpen(self.c_skin.darker(140), 2.2))
            p.drawLine(QPointF(22, -72), QPointF(19, -79))
            p.drawLine(QPointF(23, -72), QPointF(26, -79))
        elif extra == "pen":
            p.setPen(mkpen(QColor("#2A2D3A"), 2))
            p.drawLine(QPointF(33, -39), QPointF(40, -47 + math.sin(t * 20) * 2))
        elif extra == "mic":
            p.setPen(mkpen(QColor("#2A2D3A"), 3))
            p.drawLine(QPointF(12, -52), QPointF(8, -44))
            p.setPen(NO_PEN)
            p.setBrush(QColor("#5A5F75"))
            p.drawEllipse(QPointF(13, -57), 3.4, 3.4)


def syllabes(name):
    low = re.sub(r"[^a-z]", "", name.lower())
    parts = re.findall(r"[^aeiouy]*[aeiouy]+(?:[^aeiouy](?![aeiouy]))?", low)
    if not parts:
        return name.upper()
    rest = low[len("".join(parts)):]
    parts[-1] += rest
    return "-".join(parts).upper()


# --------------------------------------------------------------------------- #
# Le metteur en scène de la rencontre.
# --------------------------------------------------------------------------- #
class FanMeet:
    GAP = 64

    def __init__(self, world):
        self.w = world
        self.active = False
        self.idols, self.fans = [], []
        self.group = self.key = None
        self.banner = None
        self.phase, self.pt, self.step = None, 0.0, 0
        self.acts = []
        self.engaged = set()
        self.next_act = 0.0
        self.stats = {}
        self.spots = {}
        st = world.settings
        try:
            self.custom = json.loads(st.value("idol_groups", "{}")) or {}
        except (TypeError, ValueError):
            self.custom = {}
        self.surprise = st.value("idol_visits", True, type=bool)
        self.visit_cd = rnd(5400, 10800)

    # ---------- groupes ----------
    def groups(self):
        d = dict(IDOL_GROUPS)
        d.update(self.custom)
        return d

    def save_custom(self, key, g):
        self.custom[key] = g
        self.w.settings.setValue("idol_groups", json.dumps(self.custom))

    def delete_custom(self, key):
        self.custom.pop(key, None)
        self.w.settings.setValue("idol_groups", json.dumps(self.custom))

    def set_surprise(self, on):
        self.surprise = bool(on)
        self.w.settings.setValue("idol_visits", self.surprise)

    def can_start(self):
        w = self.w
        return not self.active and w.role is None and w.family.scene is None and not w.paused

    # ---------- début ----------
    def start(self, key):
        w = self.w
        g = self.groups().get(key)
        if g is None or not self.can_start() or not g.get("members"):
            return False
        fans = [p for p in w.pets + w.family.alive()
                if p.active() and p.state not in ("drag", "tunnel", "ghost", "gone", "ko")]
        if not fans:
            return False
        w.cancel_duo()
        T = w.terrain
        seg = T.segs[0]
        for f in fans:
            if f.state == "ride":
                f.dismount(True)
            if f.rider is not None:
                f.rider.dismount(True)
            if f.state == "sleep":
                f.wake("Hein ?!")
            f.busy, f.duty, f.camo = True, None, False
            f.opening, f.open_phase = None, None
            f.fan_hue, f.fan_stick = g.get("hue", 300), g.get("stick", "rond")
            f.pending_ko = False
        n = len(g["members"])
        width = (n - 1) * self.GAP
        nl = (len(fans) + 1) // 2
        margin = width / 2 + 90 + nl * 60
        xs = sorted(f.cx() for f in fans)
        mid = xs[len(xs) // 2]
        lo, hi = seg.x0 + margin, seg.x1 - margin
        stage = min(max(mid, lo), hi) if lo < hi else (seg.x0 + seg.x1) / 2
        self.stage, self.seg = stage, seg
        # places des fans : de part et d'autre de la formation
        left = sorted(fans, key=lambda q: q.cx())[:nl]
        right = sorted(fans, key=lambda q: q.cx())[nl:]
        self.spots = {}
        for side, grp in ((-1, left), (1, right)):
            order = sorted(grp, key=lambda q: abs(q.cx() - stage))
            for k, f in enumerate(order):
                self.spots[f] = T.clamp_x(stage + side * (width / 2 + 84 + k * 60), seg)
        self.entry = seg.x0 + 30 if stage - seg.x0 > seg.x1 - stage else seg.x1 - 30
        dirn = 1 if self.entry < stage else -1
        vis = w.visible and not w.paused
        self.banner = Prop("banniere", stage, seg.yb, hue=g.get("hue", 300), label=g["name"]) if vis else None
        self.idols = []
        for i, m in enumerate(g["members"]):
            idol = Idol(w, g, m)
            idol.x, idol.y, idol.seg = self.entry - W / 2, seg.yb - GROUND, seg
            idol.state, idol.facing = "idle", dirn
            idol.delay = 0.4 + i * 0.35
            idol.spot = stage - width / 2 + i * self.GAP
            idol.setVisible(False)
            self.idols.append(idol)
        self.fans, self.group, self.key = fans, g, key
        self.acts, self.engaged = [], set()
        self.stats = dict(photo=0, selfie=0, autographe=0, coeur=0, evanoui=0, larmes=0, cadeau=0)
        self.active = True
        self.go("arrive")
        return True

    def go(self, phase):
        self.phase, self.pt, self.step = phase, 0.0, 0

    def leader(self):
        for i in self.idols:
            if i.m.get("role") == "leader":
                return i
        return self.idols[0]

    def free_fans(self):
        return [f for f in self.fans if f not in self.engaged and f.active() and f.state in ("idle", "walk")
                and not f.airborne]

    def free_idols(self):
        return [i for i in self.idols if i not in self.engaged and i.entered and not i.exited
                and i.state in ("idle", "walk")]

    def scream(self, fans, n_bubbles=2, faint=False):
        talkers = random.sample(fans, min(n_bubbles, len(fans))) if fans else []
        for f in fans:
            if f.state == "ko":
                continue
            f.floaters.append([random.choice(FAN_LINES["scream"]), random.uniform(0, 0.3)])
            f.hop(rnd(300, 420))
            f.emit("heart", 3, y=GROUND - 80)
            f.set_expr("happy", 2.5)
            f.arm_up = True
            self.later(1.3, lambda f=f: setattr(f, "arm_up", False))
        for f in talkers:
            f.say(random.choice(FAN_LINES["scream"]), 1.6)
        if faint:
            cands = [f for f in self.free_fans()]
            if len(cands) >= 2 and random.random() < 0.6:
                self.faint(random.choice(cands))

    # ---------- boucle ----------
    def tick(self, dt):
        w = self.w
        if not self.active:
            if self.surprise and dt > 0:
                self.visit_cd -= dt
                if self.visit_cd <= 0:
                    self.visit_cd = rnd(5400, 10800)
                    awake = [p for p in w.pets if p.state != "sleep"]
                    if awake and w.duo is None and w.visible and self.can_start():
                        self.start(random.choice(list(self.groups())))
            return
        if dt <= 0:
            return
        if w.role is not None:
            self.end(quiet=True)
            return
        self.pt += dt
        for idol in self.idols:
            if not idol.entered and self.pt >= idol.delay and self.phase == "arrive":
                idol.entered = True
                idol.setVisible(w.visible and not w.paused)
                idol.emit("sparkle", 6, y=GROUND - 70)
                idol.walk_to(idol.spot, 150)
        for a in list(self.acts):
            a[1] -= dt
            while a[1] <= 0:
                try:
                    a[1] += next(a[0])
                except StopIteration:
                    if a in self.acts:
                        self.acts.remove(a)
                    break
                except Exception:
                    if a in self.acts:
                        self.acts.remove(a)
                    break
        getattr(self, "phase_" + self.phase)(dt)

    def run(self, gen):
        self.acts.append([gen, 0.0])

    def later(self, delay, fn):
        def gen():
            yield delay
            fn()
        self.run(gen())

    def home(self, who, speed=110):
        if isinstance(who, Idol):
            who.walk_to(who.spot, speed)
        elif who in self.spots and who.state in ("idle", "walk"):
            who.go_to(self.spots[who], self.seg, speed)

    # ---------- phases ----------
    def phase_arrive(self, dt):
        g, s = self.group, self.step
        if s == 0 and self.pt > 0.9:
            f = min(self.fans, key=lambda q: abs(q.cx() - self.entry))
            f.face(self.idols[0])
            f.say(random.choice(FAN_LINES["notice"]) % g["name"], 2.2)
            f.set_expr("surprised", 1.5)
            f.hop(300)
            self.step = 1
        elif s == 1 and self.pt > 2.2:
            self.scream(self.fans, 2)
            for f in self.fans:
                f.fan_prop = "lightstick"
                self.later(rnd(0.2, 0.9), lambda f=f: self.home(f, 170))
            self.step = 2
        elif s == 2:
            ready = all(i.entered and i.state == "idle" and abs(i.cx() - i.spot) < 14 for i in self.idols)
            if ready or self.pt > 18:
                for i in self.idols:
                    i.facing = -1 if i.cx() < self.stage else 1
                for f in self.fans:
                    if f.state == "idle":
                        f.facing = 1 if f.cx() < self.stage else -1
                self.go("greet")

    def phase_greet(self, dt):
        s, L = self.step, self.leader()
        if s == 0:
            L.set_pose("mic", 1.6)
            L.say("Deux, trois !", 1.4)
            self.step = 1
        elif s == 1 and self.pt > 1.4:
            for k, i in enumerate(self.idols):
                i.set_pose(i.m.get("sig", "wave"), 2.4)
                self.later(k * 90 / 1000.0, lambda i=i: i.hop(240))
            L.say(self.group.get("greet", "Bonjour !"), 2.8)
            self.scream(self.fans, 1)
            self.step = 2
        elif s == 2 and self.pt > 3.6:
            for i in self.idols:
                i.set_pose("bow", 1.4)
            self.scream(self.fans, 2, faint=True)
            self.step = 3
        elif s == 3 and self.pt > 5.4:
            self.duration = 22 + 3 * min(len(self.fans), 6)
            self.next_act = 0.3
            self.go("fanservice")

    def phase_fanservice(self, dt):
        self.next_act -= dt
        if self.pt < self.duration - 4 and self.next_act <= 0:
            self.next_act = rnd(1.3, 2.3)
            self.pick_act()
        if random.random() < dt * 0.8:                          # ambiance
            f = random.choice(self.fans)
            if f not in self.engaged and f.state == "idle" and not f.airborne:
                if random.random() < 0.5:
                    f.hop(260)
                    f.arm_up = True
                    self.later(0.7, lambda f=f: setattr(f, "arm_up", False))
                else:
                    f.floaters.append([random.choice(FAN_LINES["scream"]), 0.0])
        if random.random() < dt * 0.35:
            i = random.choice(self.free_idols() or [None])
            if i is not None and i.cur_pose() is None:
                i.set_pose(i.m.get("sig", "wave"), 1.6)
        if self.pt > self.duration and not any(i in self.engaged for i in self.idols):
            self.go("dance")

    def pick_act(self):
        fans, idols = self.free_fans(), self.free_idols()
        if not fans or not idols:
            return
        kinds = dict(photo=3, selfie=2, autographe=2, coeur=2, larmes=1, cadeau=1, timide=1, chant=1)
        if len(fans) < 2:
            kinds.pop("chant")
        if not any("timide" in f.persona for f in fans):
            kinds["timide"] = 0.4
        kind = random.choices(list(kinds), weights=list(kinds.values()))[0]
        f = random.choice(fans)
        i = min(idols, key=lambda q: abs(q.cx() - f.cx()) + rnd(0, 150))
        if kind == "chant":
            self.run(self.act_chant())
            return
        if kind == "timide":
            shy = [q for q in fans if "timide" in q.persona]
            f = random.choice(shy or fans)
        self.engaged |= {f, i}
        self.run(self.act_wrap(getattr(self, "act_" + kind)(f, i), f, i))

    def act_wrap(self, gen, f, i):
        try:
            yield from gen
        finally:
            self.engaged.discard(f)
            self.engaged.discard(i)
            if self.active:
                if f.fan_prop in ("telephone", "selfie"):
                    f.fan_prop = "lightstick"
                f.arm_up = False
                if f.state in ("idle", "walk"):
                    self.home(f)
                if i.state in ("idle", "walk") and self.phase == "fanservice":
                    self.home(i, 90)

    def approach(self, f, i, dist):
        side = 1 if f.cx() >= i.cx() else -1
        f.go_to(i.cx() + side * dist, i.seg or self.seg, 170)
        t = 0.0
        while (f.state == "walk" or f.airborne) and t < 5:
            yield 0.1
            t += 0.1
        f.face(i)
        i.face(f)

    # ---------- actions ----------
    def act_photo(self, f, i):
        yield from self.approach(f, i, 92)
        f.fan_prop, f.arm_up = "telephone", True
        f.say(random.choice(FAN_LINES["photo"]), 1.5)
        yield 0.9
        i.set_pose(i.m.get("sig", "peace"), 2.2)
        i.say(random.choice(IDOL_LINES["photo"]), 1.3)
        yield 0.6
        for _ in range(2):
            f.emit("flash", 1)
            i.emit("flash", 1)
            f.floaters.append(["CLIC !", 0.0])
            yield 0.45
        f.say(random.choice(FAN_LINES["photo_after"]), 1.8)
        f.hop(340)
        f.emit("heart", 4, y=GROUND - 80)
        f.set_expr("happy", 2)
        self.stats["photo"] += 1
        yield 1.0

    def act_selfie(self, f, i):
        yield from self.approach(f, i, 40)
        f.say(random.choice(FAN_LINES["selfie"]), 1.6)
        yield 1.0
        i.say(random.choice(IDOL_LINES["selfie"]), 1.3)
        side = 1 if f.cx() > i.cx() else -1
        f.facing = i.facing = side
        f.fan_prop = "selfie"
        i.set_pose("peace", 2.2)
        f.set_expr("wink", 2)
        yield 0.9
        f.emit("flash", 1)
        i.emit("flash", 1)
        f.floaters.append(["CLIC !", 0.0])
        yield 0.7
        f.say(random.choice(FAN_LINES["selfie_after"]).replace("%s", i.name), 2.0)
        f.hop(360)
        f.emit("heart", 5, y=GROUND - 80)
        self.stats["selfie"] += 1
        yield 1.2

    def act_autographe(self, f, i):
        yield from self.approach(f, i, 52)
        f.show_item, f.show_item_t = "carnet", 1.6
        f.say(random.choice(FAN_LINES["autograph"]), 1.6)
        yield 1.2
        i.set_pose("sign", 1.6)
        i.say(random.choice(IDOL_LINES["sign"]), 1.4)
        yield 1.1
        i.emit("sparkle", 5, y=GROUND - 50)
        f.show_item, f.show_item_t = "carnet", 1.6
        yield 0.5
        f.say(random.choice(FAN_LINES["autograph_after"]), 2.0)
        f.cry_t = 2.2
        f.hop(300)
        f.emit("heart", 4, y=GROUND - 80)
        self.stats["autographe"] += 1
        yield 1.2

    def act_coeur(self, f, i):
        i.face(f)
        i.set_pose("heart", 2.0)
        i.say(random.choice(IDOL_LINES["heart"]), 1.4)
        i.emit("heart", 3, y=GROUND - 90)
        yield 0.9
        self.stats["coeur"] += 1
        if random.random() < 0.55:
            self.faint(f)
        else:
            f.say(random.choice(FAN_LINES["heart"]), 1.8)
            f.floaters.append(["KYAAA !!", 0.0])
            f.hop(400)
            f.emit("heart", 6, y=GROUND - 80)
        yield 1.0

    def act_larmes(self, f, i):
        f.cry_t = 5.0
        f.say(random.choice(FAN_LINES["cry"]), 1.8)
        self.stats["larmes"] += 1
        yield 1.0
        side = 1 if i.cx() > f.cx() else -1
        i.walk_to(f.cx() + side * 46, 110)
        t = 0.0
        while i.state == "walk" and t < 5:
            yield 0.1
            t += 0.1
        i.face(f)
        i.set_pose("wave", 1.2)
        i.say(random.choice(IDOL_LINES["comfort"]), 1.6)
        i.emit("heart", 3, y=GROUND - 90)
        yield 1.4
        f.cry_t = 0.0
        f.set_expr("happy", 2)
        f.say("M-merci...", 1.4)
        f.emit("heart", 3, y=GROUND - 80)
        yield 1.0

    def act_cadeau(self, f, i):
        yield from self.approach(f, i, 50)
        f.show_item, f.show_item_t = "peluche", 1.6
        f.say(random.choice(FAN_LINES["gift"]), 1.5)
        yield 1.2
        i.show_item, i.show_item_t = "peluche", 1.6
        i.say(random.choice(IDOL_LINES["gift"]), 1.6)
        i.set_expr("happy", 2)
        i.hop(260)
        f.emit("heart", 4, y=GROUND - 80)
        self.stats["cadeau"] += 1
        yield 1.4

    def act_timide(self, f, i):
        side = 1 if f.cx() > self.stage else -1
        f.go_to(f.cx() + side * 70, self.seg, 90)
        f.say(random.choice(FAN_LINES["shy"][1:]), 1.4)
        yield 1.4
        i.walk_to(f.cx() - side * 50, 100)
        t = 0.0
        while i.state == "walk" and t < 6:
            yield 0.1
            t += 0.1
        i.face(f)
        f.face(i)
        i.set_pose("wave", 1.6)
        i.say(random.choice(IDOL_LINES["shy"]), 1.5)
        yield 1.3
        f.say(FAN_LINES["shy"][0], 1.6)
        f.set_expr("happy", 3)
        f.emit("heart", 2, y=GROUND - 80)
        yield 1.4

    def act_chant(self):
        fans = [f for f in self.free_fans()]
        random.shuffle(fans)
        members = self.group["members"]
        for k, m in enumerate(members):
            if not fans:
                break
            f = fans[k % len(fans)]
            f.say(syllabes(m["name"]) + " !", 0.9)
            f.arm_up = True
            self.later(0.6, lambda f=f: setattr(f, "arm_up", False))
            yield 0.55
        for f in fans:
            f.hop(300)
            f.arm_up = True
            self.later(0.9, lambda f=f: setattr(f, "arm_up", False))
        if fans:
            fans[0].say(self.group.get("chant", "!!!"), 1.8)
        L = self.leader()
        if L not in self.engaged:
            L.say("Merci !!", 1.3)
            L.set_pose("big_heart", 1.6)
        for i in self.idols:
            i.emit("sparkle", 2, y=GROUND - 80)
        yield 1.0

    def faint(self, f):
        if f.state not in ("idle", "walk"):
            return
        self.engaged.add(f)
        f.say(random.choice(FAN_LINES["faint"]), 1.6)
        f.set_expr("happy", 1.0)
        f.emit("heart", 5, y=GROUND - 80)
        f.pending_ko = True
        f.launch(-f.facing * 70, -300)
        self.stats["evanoui"] += 1
        self.run(self.act_wake(f))

    def act_wake(self, f):
        yield rnd(3.5, 5.5)
        helpers = [q for q in self.free_fans() if q is not f]
        h = min(helpers, key=lambda q: abs(q.cx() - f.cx())) if helpers else None
        if h is not None:
            self.engaged.add(h)
            side = 1 if h.cx() > f.cx() else -1
            h.go_to(f.cx() + side * 44, self.seg, 170)
            t = 0.0
            while h.state == "walk" and t < 4:
                yield 0.1
                t += 0.1
            h.face(f)
            h.say(random.choice(FAN_LINES["fan_help"]), 1.4)
            h.attack_t = 0.6
            f.emit("feather", 3, y=GROUND - 40)
            yield 1.2
        t = 0.0
        while f.state == "fall" and t < 3:
            yield 0.1
            t += 0.1
        f.pending_ko = False
        if f.state == "ko":
            f.go_idle(1.0)
        f.dizzy = 1.2
        f.hop(260)
        f.say(random.choice(FAN_LINES["wake"]), 1.8)
        self.engaged.discard(f)
        if h is not None:
            self.engaged.discard(h)
            self.home(h)
        yield 1.0
        if self.active:
            self.home(f)

    def phase_dance(self, dt):
        s = self.step
        if s == 0:
            for i in self.idols:
                i.pose_t = 0.0
                self.home(i, 130)
            for f in self.free_fans():
                self.home(f, 130)
            self.step = 1
        elif s == 1 and (self.pt > 4 or all(i.state == "idle" for i in self.idols)):
            for i in self.idols:
                i.facing = -1 if i.cx() < self.stage else 1
            self.leader().say("Notre nouvelle chanson !", 1.8)
            self.scream(self.fans, 1)
            self.step, self.pt = 2, 0.0
            self.beat = -1
        elif s == 2:
            beat = int(self.pt * 2.2)
            if beat != self.beat:
                self.beat = beat
                pose = Idol.DANCE[beat % len(Idol.DANCE)]
                for i in self.idols:
                    i.dance_pose = pose
                    if beat % 2 == 0:
                        i.hop(210)
                    if beat % 4 == 0:
                        i.facing = -i.facing
                    if random.random() < 0.3:
                        i.emit("note", 1, y=GROUND - 100)
                for f in self.fans:
                    if f.state == "idle" and f not in self.engaged and not f.airborne:
                        f.arm_up = beat % 2 == 0
                        if beat % 2 == 0 and random.random() < 0.6:
                            f.hop(240)
                if beat == 9 and self.fans:
                    random.choice(self.fans).say(self.group.get("chant", "!!!"), 1.8)
            if self.pt > 11:
                for i in self.idols:
                    i.dance_pose = None
                    i.facing = -1 if i.cx() < self.stage else 1
                    i.set_pose("big_heart", 2.2)
                for f in self.fans:
                    f.arm_up = False
                self.scream(self.fans, 2, faint=True)
                self.go("bye")

    def phase_bye(self, dt):
        s = self.step
        if s == 0 and self.pt > 2.4:
            L = self.leader()
            L.say(random.choice(IDOL_LINES["bye"]), 2.2)
            for i in self.idols:
                i.set_pose("wave", 2.4)
            talk = random.sample(self.fans, min(2, len(self.fans)))
            for f in talk:
                if f.state == "idle":
                    f.say(random.choice(FAN_LINES["bye"]), 1.8)
            for f in self.fans:
                if random.random() < 0.35 and f.state == "idle":
                    f.cry_t = 3.0
            self.step = 1
        elif s == 1 and self.pt > 5.0:
            for k, i in enumerate(self.idols):
                i.pose_t = 0.0
                i.walk_to(self.entry, 150 + k * 4)
            dirn = 1 if self.entry > self.stage else -1
            for f in self.free_fans()[:2]:
                f.go_to(self.stage + dirn * rnd(120, 220), self.seg, 170)
                f.say("Attendez !!", 1.2)
            self.step = 2
        elif s == 2:
            for i in self.idols:
                if not i.exited and (abs(i.cx() - self.entry) < 16 or self.pt > 16):
                    i.exited = True
                    i.emit("sparkle", 6, y=GROUND - 70)
                    i.hide()
            if all(i.exited for i in self.idols):
                self.step, self.pt = 3, 0.0
        elif s == 3 and self.pt > 1.2:
            self.end()

    # ---------- fin ----------
    def end(self, quiet=False):
        if not self.active:
            return
        w = self.w
        self.active = False
        self.acts = []
        self.engaged = set()
        for i in self.idols:
            i.hide()
            i.deleteLater()
        self.idols = []
        if self.banner is not None:
            self.banner.kill()
            self.banner = None
        for f in self.fans:
            f.busy = w.role is not None
            f.fan_prop, f.arm_up = None, False
            f.cry_t = 0.0
            f.pending_ko = False
            if f.state == "ko":
                f.go_idle(1.0)
                f.say(random.choice(FAN_LINES["wake"]), 1.8)
            elif f.state == "idle":
                f.timer = rnd(1, 3)
        self.fans = []
        self.visit_cd = rnd(5400, 10800)
        if quiet or not self.group:
            return
        st, g = self.stats, self.group
        bits = []
        for k, one, many in (("selfie", "selfie", "selfies"), ("photo", "photo", "photos"),
                             ("autographe", "autographe", "autographes"), ("cadeau", "cadeau", "cadeaux"),
                             ("evanoui", "évanouissement", "évanouissements"),
                             ("larmes", "fan en larmes", "fans en larmes")):
            if st.get(k):
                bits.append("%d %s" % (st[k], one if st[k] == 1 else many))
        text = "%s est passé au village ! %s." % (g["name"], ", ".join(bits) if bits else "Des cris, beaucoup de cris")
        if w.family.active:
            w.family.log("fanmeet", text, toast=True)
            w.family.save()
        elif w.tray is not None:
            try:
                w.tray.showMessage("H13ris — fan meeting", text, QSystemTrayIcon.MessageIcon.Information, 5000)
            except Exception:
                pass

    def set_visible(self, on):
        if self.banner is not None:
            self.banner.setVisible(on)
        for i in self.idols:
            i.setVisible(on and i.entered and not i.exited)

    # ---------- menu ----------
    def fill_menu(self, fm):
        fm.clear()
        if self.active:
            fm.addAction("🎤 %s est là ! (%s)" % (self.group["name"], self.phase)).setEnabled(False)
            fm.addAction("Terminer la rencontre").triggered.connect(lambda: self.end())
            return
        ok = self.can_start()
        for key, g in self.groups().items():
            a = fm.addAction("🎤 %s — %d membres%s" % (g["name"], len(g.get("members", [])),
                                                     " (%s)" % g["fandom"] if g.get("fandom") else ""))
            a.triggered.connect(lambda _=False, k=key: self.start(k) or random.choice(self.w.pets).say(
                "Pas maintenant !", 1.5))
            a.setEnabled(ok)
        fm.addSeparator()
        fm.addAction("✏ Créer un groupe…").triggered.connect(lambda: self.edit(None))
        if self.custom:
            ed = fm.addMenu("✏ Modifier un groupe")
            dl = fm.addMenu("🗑 Supprimer un groupe")
            for key, g in self.custom.items():
                ed.addAction(g["name"]).triggered.connect(lambda _=False, k=key: self.edit(k))
                dl.addAction(g["name"]).triggered.connect(lambda _=False, k=key: self.delete_custom(k))

    def edit(self, key):
        dlg = GroupEditor(self, key)
        if dlg.exec():
            k, g = dlg.result_group()
            self.save_custom(k, g)
            return k
        return None


# --------------------------------------------------------------------------- #
# Éditeur de groupe (nom, fandom, couleur du lightstick, membres).
# --------------------------------------------------------------------------- #
class GroupEditor(QDialog):
    COLS = ["Nom", "Coiffure", "Cheveux", "Accessoire", "Tenue", "Couleur tenue", "Peau", "Rôle", "Pose"]

    def __init__(self, fanmeet, key=None):
        super().__init__(None, Qt.WindowType.WindowStaysOnTopHint)
        self.fm, self.key = fanmeet, key
        g = fanmeet.custom.get(key) if key else None
        self.setWindowTitle("Groupe d'idoles" + (" — " + g["name"] if g else ""))
        self.resize(860, 420)
        lay = QVBoxLayout(self)
        form = QFormLayout()
        self.name = QLineEdit(g["name"] if g else "MON GROUPE")
        self.fandom = QLineEdit(g.get("fandom", "") if g else "Fans")
        self.greet = QLineEdit(g.get("greet", "") if g else "Bonjour, on est MON GROUPE !")
        self.hue = QSlider(Qt.Orientation.Horizontal)
        self.hue.setRange(0, 359)
        self.hue.setValue(int(g.get("hue", 270)) if g else random.randrange(360))
        self.stick = QComboBox()
        self.stick.addItems(["etoile", "coeur", "rond"])
        if g:
            self.stick.setCurrentText(g.get("stick", "rond"))
        form.addRow("Nom du groupe", self.name)
        form.addRow("Nom du fandom", self.fandom)
        form.addRow("Salut du groupe", self.greet)
        form.addRow("Couleur officielle", self.hue)
        form.addRow("Lightstick", self.stick)
        lay.addLayout(form)
        self.table = QTableWidget(0, len(self.COLS))
        self.table.setHorizontalHeaderLabels(self.COLS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        lay.addWidget(self.table)
        row = QHBoxLayout()
        for label, fn in (("+ Membre", lambda: self.add_row()), ("– Membre", self.del_row),
                          ("🎲 Tout au hasard", self.randomize)):
            b = QPushButton(label)
            b.clicked.connect(fn)
            row.addWidget(b)
        lay.addLayout(row)
        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        lay.addWidget(bb)
        for m in (g["members"] if g else [self.random_member(i) for i in range(5)]):
            self.add_row(m)

    @staticmethod
    def random_member(i=0):
        names = ["Jaeyi", "Soren", "Hwan", "Bora", "Eunji", "Kyo", "Mirae", "Tae", "Ilan", "Yuna", "Rei", "Sol"]
        return dict(name=random.choice(names), hair=random.choice(list(HAIR_STYLES)),
                    hc=random.choice(list(HAIR_COLORS)), acc=random.choice(IDOL_ACCS),
                    outfit=random.choice(IDOL_OUTFITS), oc=random.choice(list(OUTFIT_COLORS)),
                    skin=random.randrange(len(SKIN_TONES)), role="leader" if i == 0 else random.choice(IDOL_ROLES),
                    sig=random.choice(IDOL_POSES))

    def combo(self, items, cur):
        c = QComboBox()
        c.addItems([str(x) for x in items])
        c.setCurrentText(str(cur))
        return c

    def add_row(self, m=None):
        if self.table.rowCount() >= 9:
            return
        m = m or self.random_member(self.table.rowCount())
        r = self.table.rowCount()
        self.table.insertRow(r)
        self.table.setCellWidget(r, 0, QLineEdit(m["name"]))
        opts = [list(HAIR_STYLES), list(HAIR_COLORS), IDOL_ACCS, IDOL_OUTFITS, list(OUTFIT_COLORS),
                [str(k) for k in range(len(SKIN_TONES))], IDOL_ROLES, IDOL_POSES]
        keys = ["hair", "hc", "acc", "outfit", "oc", "skin", "role", "sig"]
        for c, (items, k) in enumerate(zip(opts, keys), start=1):
            self.table.setCellWidget(r, c, self.combo(items, m.get(k, items[0])))

    def del_row(self):
        if self.table.rowCount() > 1:
            self.table.removeRow(self.table.rowCount() - 1)

    def randomize(self):
        n = random.randint(3, 9)
        self.table.setRowCount(0)
        for i in range(n):
            self.add_row(self.random_member(i))
        self.hue.setValue(random.randrange(360))

    def result_group(self):
        keys = ["hair", "hc", "acc", "outfit", "oc", "skin", "role", "sig"]
        members = []
        for r in range(self.table.rowCount()):
            m = dict(name=self.table.cellWidget(r, 0).text().strip()[:12] or "Idole")
            for c, k in enumerate(keys, start=1):
                v = self.table.cellWidget(r, c).currentText()
                m[k] = int(v) if k == "skin" else v
            members.append(m)
        name = self.name.text().strip()[:18] or "MON GROUPE"
        g = dict(name=name, fandom=self.fandom.text().strip()[:18], hue=self.hue.value(),
                 stick=self.stick.currentText(), greet=self.greet.text().strip()[:40] or "Bonjour !",
                 chant="%s !" % "-".join(syllabes(name).split("-")[:4]), members=members)
        key = self.key or "perso_%d" % int(time.time())
        return key, g


# --------------------------------------------------------------------------- #
# Le monde : boucle unique, cerveau du duo, coffres, liaison, chasse.
# --------------------------------------------------------------------------- #
class World:
    def __init__(self, app, headless=False, fake_terrain=None):
        self.app = app
        self.headless = headless
        self.terrain = Terrain(fake_terrain)
        self.fake_terrain = fake_terrain
        self.pets = [Pet("Hybris", self), Pet("Iblis", self)]
        a, b = self.pets
        a.partner, b.partner = b, a
        self.duo = None
        self.visible = True
        self.paused = False
        self.dead = False
        self.shots = []
        self.props = {}
        self.chests = {}
        self.drops = {}
        self.chest_timer = rnd(40, 90)
        self.next_id = 1
        self.opened = 0
        self.score = {"Hybris": 0, "Iblis": 0}
        self.bond = 60.0
        self.settings = QSettings("H13ris", "DesktopPets")
        self.mode = self.settings.value("mode", DEFAULT_MODE)
        if self.mode not in MODES:
            self.mode = DEFAULT_MODE
        self.hunt_enabled = self.settings.value("hunt", True, type=bool)
        self.autostart_msg = None
        if sys.platform == "win32" and not headless:
            if not self.settings.value("autostart_init", False, type=bool):
                if autostart_set(True):
                    self.autostart_msg = "Je reviendrai à chaque démarrage !"
                self.settings.setValue("autostart_init", True)
            elif autostart_get():
                autostart_set(True)
        self.now = 0.0
        self.last_bubble = -999.0
        self.last_war = 0.0
        self.freeze = 0.0
        self.fs_check = 0.0
        self.terrain_check = 5.0
        self.greet_cd = 0.0
        self.last_cursor, self.cursor_still = QCursor.pos(), 0.0
        # liaison / chasse
        self.link = Link()
        self.link_acc = 0.0
        self.remote = []
        self.arbiter = self.link.iid
        self.role = None
        self.peer_roles = {}
        self.hunt = dict(phase=None, t=0.0, last_seen=None, kills=0)
        self.respawn_q = []
        self.quit_t = None
        self.tray = None
        # famille et communauté (vit dans l'instance arbitre, la plus ancienne)
        self.next_int = 0
        self.family = Family(self)
        self.fanmeet = FanMeet(self)

        # point d'apparition : l'écran principal, ou loin des autres instances
        home, base = self.terrain.segs[0], None
        self.link.poll()
        others = [(pd.get("x", 0), pd.get("y", 0)) for pr in self.link.peers.values()
                  for pd in pr["state"].get("pets", [])]
        if others:
            far = self.terrain.farthest_point(others)
            if far:
                base, home = far
        if base is None:
            base = home.x0 + home.width * 0.5
        for pet, off, msg in ((a, -60, "Coucou H13ris !"), (b, 60, "On est où là ?")):
            pet.x = self.terrain.clamp_x(base + off, home) - W / 2
            pet.y = max(home.top + 20, home.yb - GROUND - 260)
            pet.seg = home
            pet.land_msg = msg
            pet.show()
        if self.autostart_msg:
            b.land_msg = self.autostart_msg
        live = [(self.link.born, self.link.iid)] + [(pr["state"].get("born", 0), iid)
                                                    for iid, pr in self.link.peers.items()]
        self.arbiter = min(live)[1]
        if self.is_arbiter():
            self.family.activate()

        self.menu = self.build_menu()
        if not headless and QSystemTrayIcon.isSystemTrayAvailable():
            self.tray = QSystemTrayIcon(self.make_icon(a), app)
            self.tray.setToolTip("H13ris — Hybris & Iblis")
            self.tray.setContextMenu(self.menu)
            self.tray.activated.connect(self.on_tray)
            self.tray.show()

        self.clock = QElapsedTimer()
        self.clock.start()
        self.timer = QTimer()
        self.timer.timeout.connect(self.step)
        self.interval = 1000 // FPS_ACTIVE
        if not headless:
            self.timer.start(self.interval)
            app.aboutToQuit.connect(self.shutdown)

    @property
    def cfg(self):
        return MODES[self.mode]

    def is_arbiter(self):
        return self.arbiter == self.link.iid

    def new_id(self):
        self.next_id += 1
        return "%s-%d" % (self.link.iid, self.next_id)

    def pet_by_name(self, n):
        for p in self.everyone():
            if p.name == n:
                return p
        return None

    def everyone(self):
        return self.pets + self.family.people + self.fanmeet.idols

    @property
    def kids(self):
        return self.family.alive()

    def new_id_int(self):
        self.next_int += 1
        return self.next_int

    def shutdown(self):
        if self.family.active:
            self.family.save()
        for pr in self.props.values():
            pr.hide()
        self.family.set_visible(False)
        self.fanmeet.end(quiet=True)
        self.link.close()

    # ---------- boucle ----------
    def step(self):
        dt = min(self.clock.restart() / 1000.0, 0.1)
        self.now += dt
        self.fs_check -= dt
        if self.fs_check <= 0:
            self.fs_check = 1.5
            fs = foreground_is_fullscreen()
            if fs and not self.paused:
                self.paused = True
                self.cancel_duo()
                for p in self.everyone():
                    p.hide()
                for pr in self.props.values():
                    pr.hide()
                self.family.set_visible(False)
                self.fanmeet.set_visible(False)
            elif not fs and self.paused:
                self.paused = False
                for p in self.everyone():
                    p.setVisible(self.visible and not p.gone)
                self.ensure_props()
        want = 500 if self.paused else 1000 // (
            FPS_SLEEP if all(p.state == "sleep" or not p.active() for p in self.everyone())
            and not self.shots and self.family.scene is None else FPS_ACTIVE)
        if want != self.interval:
            self.interval = want
            self.timer.setInterval(want)
        if self.paused:
            self.link_tick(dt)                      # rester visible pour les autres
            return
        self.terrain_check -= dt
        if self.terrain_check <= 0:
            self.terrain_check = 5.0
            self.update_tray_tip()
            if self.fake_terrain is None:
                sig = self.terrain.signature()
                self.terrain.refresh()
                if self.terrain.signature() != sig:
                    for p in self.pets:
                        p.seg = None
        cur = QCursor.pos()
        if cur != self.last_cursor:
            self.last_cursor, self.cursor_still = cur, 0.0
        else:
            self.cursor_still += dt
        self.advance(dt)

    def advance(self, dt):
        pdt = dt
        if self.freeze > 0:                                  # hit-stop
            self.freeze -= dt
            pdt = 0.0
        for p in self.pets:
            p.shake = self.freeze if (p.hurt > 0 and self.freeze > 0) else 0.0
            p.tick(pdt)
        for k in self.family.people:
            k.tick(pdt)
        for k in list(self.fanmeet.idols):
            k.tick(pdt)
        self.family.tick(pdt)
        self.fanmeet.tick(pdt)
        self.link_tick(dt)
        self.props_tick(pdt)
        self.hunt_tick(pdt)
        self.run_shots(pdt)
        self.run_duo(pdt)
        self.misc_tick(pdt)

    def bubble_ok(self):
        return self.now - self.last_bubble > self.cfg["bubble"]

    def misc_tick(self, dt):
        self.greet_cd = max(0.0, self.greet_cd - dt)
        for p in self.everyone():
            # ouverture de coffre en cours
            if p.opening is not None:
                if p.open_phase == "anim" and p.open_t <= 0:
                    p.open_phase = "wait"
                    p.loot_wait = 1.6
                    if self.is_arbiter():
                        self.grant_chest(p.opening, self.link.iid, p.name)
                    else:
                        self.link.emit(type="claim", to="arb", chest=p.opening, pet=p.name)
                elif p.open_phase == "wait" and p.loot_wait <= 0:
                    p.opening, p.open_phase = None, None
                    p.say(random.choice(HUNT["empty"]), 1.6)
                    p.set_expr("pout", 1.5)
                elif p.open_phase is None and self.role is None:
                    self.seek_chest(p, dt, radius=99999)
            # salut aux voisins pacifiques
            if self.role is None and self.remote and self.greet_cd <= 0 and p.state in ("idle", "walk"):
                for r in self.remote:
                    if r.active() and dist2(p.cx(), p.feet(), r.cx(), r.feet()) < 130:
                        p.face(r)
                        p.say(random.choice(["Salut !", "Yo !", "Encore vous ?"]), 1.6)
                        p.set_expr("happy", 1.5)
                        p.arm_up = True
                        QTimer.singleShot(1200, lambda p=p: setattr(p, "arm_up", False))
                        self.greet_cd = 20
                        break
        for entry in list(self.respawn_q):
            entry[1] -= dt
            if entry[1] <= 0:
                self.respawn_q.remove(entry)
                seg = self.terrain.segs[0]
                entry[0].respawn(self.terrain.random_x(seg), seg)
                entry[0].role = self.role
                entry[0].busy = self.role is not None
        if self.quit_t is not None:
            self.quit_t -= dt
            if self.quit_t <= 0:
                self.quit_t = None
                self.dead = True
                if not self.headless:
                    self.app.quit()

    # ---------- liaison entre instances ----------
    def link_tick(self, dt):
        self.link_acc += dt
        if self.link_acc < 1.0 / LINK_HZ:
            return
        self.link_acc = 0.0
        arrived, gone = self.link.poll()
        self.update_roles(arrived, gone)
        self.rebuild_remote()
        self.process_inbox()
        self.link.publish(self.state_dict())

    def state_dict(self):
        d = dict(pets=[p.snapshot() for p in self.pets], role=self.role,
                 hunt=self.hunt_enabled, arb=self.arbiter)
        if self.is_arbiter():
            d["chests"] = [dict(id=c["id"], x=round(c["x"]), y=round(c["y"]), taken=c["taken"])
                           for c in self.chests.values()]
            d["drops"] = [dict(id=k, x=round(v["x"]), y=round(v["y"]), kind=v["kind"])
                          for k, v in self.drops.items()]
        return d

    def rebuild_remote(self):
        self.remote = []
        for iid, pr in self.link.peers.items():
            role = self.peer_roles.get(iid)
            for pd in pr["state"].get("pets", []):
                self.remote.append(RemotePet(iid, role, pd, pr["seen"]))

    def update_roles(self, arrived, gone):
        live = [(self.link.born, self.link.iid)]
        for iid, pr in self.link.peers.items():
            live.append((pr["state"].get("born", 0), iid))
        live.sort()
        self.arbiter = live[0][1]
        if self.is_arbiter() and not self.family.active:
            self.family.activate()
        elif not self.is_arbiter() and self.family.active:
            self.family.deactivate()
        if self.is_arbiter():
            hunt_on = self.hunt_enabled
        else:
            hunt_on = bool(self.link.peers[self.arbiter]["state"].get("hunt", True))
        game = len(live) > 1 and hunt_on
        for iid in self.link.peers:
            self.peer_roles[iid] = ("hunter" if iid == self.arbiter else "prey") if game else None
        new_role = None
        if game:
            new_role = "hunter" if self.is_arbiter() else "prey"
        if new_role != self.role:
            self.set_role(new_role)
        elif new_role == "hunter" and arrived:
            for p in self.pets:
                if p.active():
                    p.say(random.choice(HUNT["alert"]), 2)
                    p.set_expr("surprised", 1.0)
                    p.hop(300)
            self.hunt["last_seen"] = None

    def set_role(self, role):
        old = self.role
        self.role = role
        self.cancel_duo()
        if self.family.scene is not None:
            self.family.end_scene()
        self.fanmeet.end(quiet=True)
        for p in self.pets:
            p.role = role
            p.ai = {}
            p.busy = role is not None
            p.camo = False
            p.opening, p.open_phase = None, None
            if p.state == "sleep":
                p.wake("Hm ?!")
            if p.state == "ride":
                p.dismount(True)
        for k in self.kids:
            k.camo = role == "prey"
            if k.state == "ride":
                k.dismount(True)
            if role == "prey":
                k.say("Chut...", 1.5)
            elif role == "hunter":
                k.say(random.choice(["Allez !", "Attrapez-les !", "Go go go !"]), 1.8)
                k.hop(200)
        if role == "hunter":
            self.hunt = dict(phase="ally", t=0.0, last_seen=None, kills=0, t0=self.now)
            a, b = self.pets
            a.say(random.choice(HUNT["alert"]), 2)
            b.say(random.choice(HUNT["ally"]), 2)
            for p in self.pets:
                p.mood = "hunt"
                p.set_expr("surprised", 0.8)
                p.hop(320)
            self.chest_timer = min(self.chest_timer, rnd(5, 15))
        elif role == "prey":
            self.hunt = dict(phase="flee", t=0.0, last_seen=None, kills=0)
            for i, p in enumerate(self.pets):
                p.mood = "scared"
                p.say(HUNT["prey_alert"][i % 2] if i < 2 else random.choice(HUNT["prey_alert"]), 2)
                p.set_expr("surprised", 1.2)
                p.hop(360)
        else:
            for p in self.pets:
                p.mood = None
                p.busy = False
                if p.state == "idle":
                    p.timer = rnd(1, 3)
            if old == "hunter" and self.hunt.get("kills", 0) > 0:
                for p in self.pets:
                    if p.active():
                        p.say(random.choice(HUNT["win"]), 2.6)
                        p.set_expr("happy", 3)
                        p.emit("heart", 5, y=GROUND - 80)
                        p.hop(400)
            elif old == "prey":
                for p in self.pets:
                    if p.active():
                        p.say(random.choice(["Ouf... ils sont partis.", "On a survécu !", "Libres !"]), 2.4)
                        p.set_expr("happy", 2)
            self.hunt = dict(phase=None, t=0.0, last_seen=None, kills=0)

    def process_inbox(self):
        for iid, ev in self.link.inbox:
            t = ev.get("type")
            if t == "hit":
                p = self.pet_by_name(ev.get("pet"))
                if p and p.active() and p.state not in ("drag", "tunnel"):
                    self.damage(p, ev.get("dmg", 10), ev.get("dirn", 1), remote=True, by=ev.get("by"))
            elif t == "claim" and self.is_arbiter():
                self.grant_chest(ev.get("chest"), iid, ev.get("pet"))
            elif t == "loot":
                p = self.pet_by_name(ev.get("pet"))
                if p and p.active():
                    p.give_item(ev.get("item"))
                    self.after_loot(p)
            elif t == "drop" and self.is_arbiter():
                self.add_drop(ev.get("kind", "banane"), ev.get("x", 0), ev.get("y", 0), (iid, ev.get("pet")))
            elif t == "slip":
                p = self.pet_by_name(ev.get("pet"))
                if p and p.active():
                    p.slip()
            elif t == "spawn" and self.is_arbiter():
                self.spawn_chest(ev.get("x"), ev.get("y"))
            elif t == "hunt" and self.is_arbiter():
                self.hunt_enabled = bool(ev.get("on", True))
                if hasattr(self, "hunt_act"):
                    self.hunt_act.blockSignals(True)
                    self.hunt_act.setChecked(self.hunt_enabled)
                    self.hunt_act.blockSignals(False)
            elif t == "killed" and self.role == "hunter":
                self.hunt["kills"] = self.hunt.get("kills", 0) + 1
                for p in self.pets:
                    if p.active():
                        p.say(random.choice(HUNT["caught"]), 2)
                        p.set_expr("happy", 2)
                        p.spark = 0.5
        self.link.inbox = []

    # ---------- coffres, pièges, objets ----------
    def chest_list(self):
        if self.is_arbiter():
            return [c for c in self.chests.values() if not c["taken"]]
        pr = self.link.peers.get(self.arbiter)
        if not pr:
            return []
        return [c for c in pr["state"].get("chests", []) if not c.get("taken")]

    def spawn_chest(self, x=None, y=None):
        T = self.terrain
        if x is None:
            seg = T.random_seg()
            x = T.random_x(seg)
        else:
            seg = T.ground_at(x, y if y is not None else T.min_top) or T.seg_near(x, y or 0)
            x = T.clamp_x(x, seg)
        cid = self.new_id()
        self.chests[cid] = dict(id=cid, x=x, y=seg.yb, item=roll_item(), taken=False, t=0.0)
        if self.visible and not self.paused:
            self.props[cid] = Prop("chest", x, seg.yb)
        return cid

    def sow(self, n=1, at_cursor=False):
        """Semer des coffres (menu)."""
        for _ in range(n):
            x = y = None
            if at_cursor:
                c = QCursor.pos()
                x, y = c.x() + rnd(-20, 20), c.y()
            if self.is_arbiter():
                self.spawn_chest(x, y)
            else:
                self.link.emit(type="spawn", to="arb", x=x, y=y)

    def grant_chest(self, cid, iid, pet_name):
        c = self.chests.get(cid)
        if c is None or c["taken"]:
            return
        c["taken"], c["t"] = True, 0.0
        self.opened += 1
        pr = self.props.get(cid)
        if pr is not None:
            pr.opened = True
        if self.visible and not self.paused:
            self.props[self.new_id()] = Prop("loot", c["x"], c["y"], item=c["item"])
        if iid == self.link.iid:
            p = self.pet_by_name(pet_name)
            if p:
                p.give_item(c["item"])
                self.after_loot(p)
        else:
            self.link.emit(type="loot", to=iid, chest=cid, pet=pet_name, item=c["item"])

    def after_loot(self, p):
        p.fun = min(100.0, p.fun + 15)
        o = p.partner
        if o is not None and self.role is None and p.item and ITEMS[p.item]["kind"] == "potion" and o.active() \
                and o.state in ("idle", "walk") and random.random() < 0.6 and not self.duo:
            self.start_duo("share", giver=p)

    def drop_trap(self, kind, x, y, pet):
        if self.is_arbiter():
            self.add_drop(kind, x, y, (self.link.iid, pet.name))
        else:
            self.link.emit(type="drop", to="arb", kind=kind, x=x, y=y, pet=pet.name)

    def add_drop(self, kind, x, y, by):
        T = self.terrain
        seg = T.ground_at(x, y + 2) or T.seg_near(x, y)
        did = self.new_id()
        self.drops[did] = dict(id=did, x=T.clamp_x(x, seg), y=seg.yb, kind=kind, by=tuple(by), t=0.0)
        if self.visible and not self.paused:
            self.props[did] = Prop(kind, self.drops[did]["x"], seg.yb)

    def ensure_props(self):
        """(Re)crée les fenêtres des coffres et pièges après une pause ou un masquage."""
        if not self.visible or self.paused:
            return
        for cid, c in self.chests.items():
            if cid not in self.props and not c["taken"]:
                self.props[cid] = Prop("chest", c["x"], c["y"])
        for did, d in self.drops.items():
            if did not in self.props:
                self.props[did] = Prop(d["kind"], d["x"], d["y"])
        for pr in self.props.values():
            pr.setVisible(True)
        self.family.set_visible(True)
        self.fanmeet.set_visible(True)

    def props_tick(self, dt):
        if self.is_arbiter():
            self.chest_timer -= dt
            if self.chest_timer <= 0:
                if len([c for c in self.chests.values() if not c["taken"]]) < 4:
                    self.spawn_chest()
                hunting = any(r.role == "prey" for r in self.remote)
                self.chest_timer = rnd(20, 45) if hunting else rnd(120, 240)
            for cid, c in list(self.chests.items()):
                c["t"] += dt
                if (c["taken"] and c["t"] > 2.5) or (not c["taken"] and c["t"] > 240):
                    pr = self.props.pop(cid, None)
                    if pr:
                        pr.kill()
                    del self.chests[cid]
            for did, d in list(self.drops.items()):
                d["t"] += dt
                victim = None
                if d["t"] > 0.8:
                    for p in self.pets:
                        if p.active() and p.grounded() and p.moving() and abs(p.cx() - d["x"]) < 26 \
                                and abs(p.feet() - d["y"]) < 8 \
                                and not (d["by"] == (self.link.iid, p.name) and d["t"] < 3):
                            victim = p
                            break
                    if victim is None:
                        for r in self.remote:
                            if r.active() and r.moving() and abs(r.cx() - d["x"]) < 26 \
                                    and abs(r.feet() - d["y"]) < 8 \
                                    and not (d["by"] == (r.iid, r.name) and d["t"] < 3):
                                victim = r
                                break
                if victim is not None or d["t"] > 90:
                    pr = self.props.pop(did, None)
                    if pr:
                        pr.kill()
                    del self.drops[did]
                    if isinstance(victim, Pet):
                        victim.slip()
                    elif victim is not None:
                        self.link.emit(type="slip", to=victim.iid, pet=victim.name)
        elif self.props or self.chests or self.drops:
            for pr in self.props.values():
                pr.kill()
            self.props, self.chests, self.drops = {}, {}, {}
        for pid, pr in list(self.props.items()):
            pr.step(dt)
            if pr.kind == "loot" and pr.age > 1.4:
                pr.kill()
                del self.props[pid]

    def seek_chest(self, p, dt, radius=600, safe_from=(), safe_d=0):
        """Aller ouvrir un coffre. Renvoie True si le pet est occupé par un coffre."""
        a = p.ai
        a["walk_cd"] = max(0.0, a.get("walk_cd", 0) - dt)
        chests = self.chest_list()
        T = self.terrain
        if p.opening is not None:
            if p.open_phase is not None:
                return True                                   # animation / attente du loot
            c = next((c for c in chests if c["id"] == p.opening), None)
            if c is None:
                p.opening = None
                return False
            if abs(p.cx() - c["x"]) < 34 and abs(p.feet() - c["y"]) < 8 and p.grounded():
                p.facing = 1 if c["x"] >= p.cx() else -1
                p.go_idle(1.3)
                p.open_phase, p.open_t = "anim", 0.8
                return True
            if a["walk_cd"] <= 0 and p.state in ("idle", "walk"):
                a["walk_cd"] = 0.5
                seg = T.ground_at(c["x"], c["y"] + 2) or T.seg_near(c["x"], c["y"])
                if not p.go_to(c["x"], seg, RUN_SPEED if self.role else 90) and p.state == "idle":
                    p.opening = None                          # inaccessible pour l'instant
                    return False
            return True
        best, bd = None, None
        for c in chests:
            d = dist2(p.cx(), p.feet(), c["x"], c["y"])
            if d > radius:
                continue
            if any(dist2(c["x"], c["y"], r.cx(), r.feet()) < safe_d for r in safe_from):
                continue
            if p.partner is not None and p.partner.opening == c["id"]:
                continue
            if bd is None or d < bd:
                best, bd = c, d
        if best is None:
            return False
        p.opening, p.open_phase = best["id"], None
        if random.random() < 0.5:
            p.say(random.choice(HUNT["loot"]), 1.5)
        return True

    # ---------- chasse : la Garde contre les intrus ----------
    def hunt_tick(self, dt):
        if self.role is None:
            return
        hs = self.hunt
        hs["t"] = hs.get("t", 0.0) + dt
        if self.role == "hunter":
            if hs.get("phase") == "ally":
                if hs["t"] > 1.8:
                    hs["phase"] = "hunt"
                    for p in self.pets:
                        p.spark = 0.5
                        p.emit("sparkle", 5, y=GROUND - 90)
                return
            for p in self.pets:
                if p.active():
                    self.hunter_ai(p, dt)
        else:
            for p in self.pets:
                if p.active():
                    self.prey_ai(p, dt)

    def can_see(self, p, r):
        if not r.active():
            return False
        d = dist2(p.cx(), p.feet(), r.cx(), r.feet())
        if r.hid:
            return d < 130
        return d < 760 or (r.moving() and d < 1200)

    def ai_timers(self, p, dt):
        a = p.ai
        for k in ("cd", "walk_cd", "say_cd", "patrol_cd", "item_cd", "jump_cd", "goal_cd"):
            a[k] = max(0.0, a.get(k, 0.0) - dt)
        return a

    def hunter_ai(self, p, dt):
        a = self.ai_timers(p, dt)
        hs = self.hunt
        T = self.terrain
        if p.state not in ("idle", "walk"):
            return
        p.mood = "hunt"
        preys = [r for r in self.remote if r.role == "prey" and r.active()]
        visible = [r for r in preys if self.can_see(p, r)]
        if visible:
            tgt = min(visible, key=lambda r: dist2(p.cx(), p.feet(), r.cx(), r.feet()))
            hs["last_seen"] = (tgt.cx(), tgt.feet(), self.now)
            if a.get("target") != tgt.key:
                a["target"] = tgt.key
                if a["say_cd"] <= 0:
                    p.say(random.choice(HUNT["found"]), 1.5)
                    a["say_cd"] = 6
            d = dist2(p.cx(), p.feet(), tgt.cx(), tgt.feet())
            dx = tgt.cx() - p.cx()
            side = 1 if dx > 0 else -1
            elev = p.feet() - tgt.feet()                     # > 0 : la cible est en l'air
            mate = p.partner
            leader = (not mate.active() or mate.role != "hunter"
                      or d <= dist2(mate.cx(), mate.feet(), tgt.cx(), tgt.feet()))
            # objets : vol pour rattraper un fuyard en l'air ou trop loin
            if p.item in FLIGHT_ITEMS and not p.flying() and a["item_cd"] <= 0 \
                    and (elev > 80 or d > 700 or tgt.fly):
                p.use_item()
                a["item_cd"] = 4
                return
            if p.flying():
                p.fly_alt = tgt.feet() - 20
                goal = tgt.cx() - side * 40
            elif elev > 80:
                goal = tgt.cx() - side * (20 if leader else -60)
                if a["say_cd"] <= 0 and random.random() < 0.02:
                    p.say(random.choice(HUNT["fly_taunt"]), 1.6)
                    a["say_cd"] = 7
            else:
                goal = tgt.cx() - side * 30 if leader else tgt.cx() + side * 170
            if a["walk_cd"] <= 0:
                a["walk_cd"] = 0.3
                p.go_to(goal, T.seg_near(tgt.cx(), tgt.feet()), RUN_SPEED)
            if a["cd"] <= 0:
                p.facing = side
                if self.attack(p, tgt, abs(dx), elev):
                    a["cd"] = rnd(1.2, 1.9)
            return
        a["target"] = None
        if self.seek_chest(p, dt, radius=450):
            return
        ls = hs.get("last_seen")
        if ls and self.now - ls[2] < 25 and a.get("checked") != ls[2]:
            if abs(p.cx() - ls[0]) < 70 and abs(p.feet() - ls[1]) < 60:
                a["checked"] = ls[2]
                p.go_idle(1.2)
                if a["say_cd"] <= 0:
                    p.say(random.choice(HUNT["search"]), 1.6)
                    a["say_cd"] = 6
                return
            if a["walk_cd"] <= 0:
                a["walk_cd"] = 0.5
                dest = ls[0] + (0 if p is self.pets[0] else rnd(-260, 260))
                p.go_to(dest, T.seg_near(ls[0], ls[1]), RUN_SPEED * 0.9)
            return
        if p.state == "idle" and a["patrol_cd"] <= 0:                 # patrouille
            a["patrol_cd"] = rnd(2, 5)
            if a["say_cd"] <= 0 and random.random() < 0.4:
                p.say(random.choice(HUNT["search"]), 1.6)
                a["say_cd"] = 8
            lost = self.now - (ls[2] if ls else hs.get("t0", self.now))
            if preys and lost > 30 and random.random() < 0.5:      # flair : vague indice
                r = random.choice(preys)
                p.go_to(r.cx() + rnd(-320, 320), T.seg_near(r.cx(), r.feet()), 120)
                if a["say_cd"] <= 0:
                    p.say("Je sens un intrus...", 1.6)
                    a["say_cd"] = 8
                return
            seg = T.random_seg(exclude=p.seg) if (random.random() < 0.45 and len(T.segs) > 1) else p.seg
            p.go_to(T.random_x(seg), seg, 120)

    # ---- intrus ----
    def prey_ai(self, p, dt):
        a = self.ai_timers(p, dt)
        T = self.terrain
        if p.state not in ("idle", "walk"):
            return
        if p.hp < 45 and p.item == "potion_sang":
            p.use_item()
        if p.hp < 30 and not a.get("second_wind"):             # sursaut d'adrénaline
            a["second_wind"] = True
            p.speed_t = max(p.speed_t, 7.0)
            p.stamina = 100.0
            p.say(random.choice(["Pas aujourd'hui !", "Jamais !", "Tu m'auras pas !"]), 1.6)
        hunters = [r for r in self.remote if r.role == "hunter" and r.active()]
        threats = [r for r in hunters if dist2(p.cx(), p.feet(), r.cx(), r.feet()) < 850]
        weapon = p.item in WEAPONS and p.ammo > 0
        if threats:
            p.camo = False
            near = min(threats, key=lambda r: dist2(p.cx(), p.feet(), r.cx(), r.feet()))
            dn = dist2(p.cx(), p.feet(), near.cx(), near.feet())
            if p.flying():
                return self.prey_fly(p, hunters, near, dn, a, dt)
            # s'envoler si on peut
            if p.item in FLIGHT_ITEMS and a["item_cd"] <= 0 and dn < 480:
                if p.use_item():
                    a["item_cd"] = 4
                    return
            brave = (weapon and p.hp > 35 and (p.shield > 0 or p.hp > 55 or dn > 240)
                     and not (len(threats) >= 2 and p.hp < 60 and p.shield == 0))
            if brave:
                return self.prey_fight(p, near, dn, a, dt)
            a["brave_said"] = False
            p.mood = "scared"
            if a["say_cd"] <= 0 and random.random() < 0.3:
                p.say(random.choice(HUNT["prey_flee"]), 1.5)
                a["say_cd"] = 5
            if a["item_cd"] <= 0:                              # objets défensifs
                if p.item == "fumigene" and dn < 320:
                    p.use_item()
                    a["item_cd"] = 8
                elif p.item == "banane" and dn < 280:
                    p.use_item()
                    a["item_cd"] = 6
                elif p.item == "potion_invisible" and dn < 380:
                    p.use_item()
                    a["item_cd"] = 15
            return self.prey_flee(p, hunters, near, dn, a, dt)
        # personne à moins de 850 px
        a["brave_said"] = False
        p.mood = "scared" if hunters else None
        if p.flying():
            if p.state == "idle" and a["walk_cd"] <= 0:       # continuer à s'éloigner en vol
                a["walk_cd"] = 1.0
                far = T.farthest_point([(r.cx(), r.feet()) for r in hunters]) if hunters else None
                p.walk_to(far[0] if far else T.random_x(), p.fly_speed)
            return
        if self.seek_chest(p, dt, radius=800, safe_from=hunters, safe_d=650):
            return
        if not hunters:
            return
        self.prey_hide(p, hunters, weapon, a, dt)

    def prey_fight(self, p, near, dn, a, dt):
        """Armé : on tient tête (blaster à distance, marteau au contact)."""
        T = self.terrain
        side = 1 if near.cx() > p.cx() else -1
        p.mood = "war"
        if not a.get("brave_said"):
            a["brave_said"] = True
            p.say(random.choice(HUNT["brave"]), 1.6)
            p.set_expr("wink", 1.2)
        if a.get("retreat", 0) > 0:
            a["retreat"] -= dt
            if a["walk_cd"] <= 0:
                a["walk_cd"] = 0.3
                p.walk_to(p.cx() - side * 220, PREY_SPEED)
            return
        if p.item == "blaster":
            if dn < 190:
                if T.room(p.seg, p.cx(), -side) > 120:
                    if a["walk_cd"] <= 0:
                        a["walk_cd"] = 0.3
                        p.walk_to(p.cx() - side * 240, PREY_SPEED)
                elif a["jump_cd"] <= 0:
                    p.hop(620)
                    p.walk_to(p.cx() + side * 520, PREY_SPEED)
                    a["jump_cd"] = 2.5
            elif dn > 480:
                if a["walk_cd"] <= 0:
                    a["walk_cd"] = 0.4
                    p.walk_to(near.cx() - side * 330, PREY_SPEED * 0.8)
            elif p.state == "walk":
                p.go_idle(0.5)
            if a["cd"] <= 0 and dn < 560:
                p.facing = side
                self.shoot(p, near, kind="dart", speed=760, dmg=14)
                p.consume_use()
                a["cd"] = 1.1
        else:                                                  # marteau
            if dn > 85:
                if a["walk_cd"] <= 0:
                    a["walk_cd"] = 0.3
                    p.walk_to(near.cx() - side * 40, PREY_SPEED)
                if 120 < dn < 260 and a["jump_cd"] <= 0:
                    p.hop(420)
                    a["jump_cd"] = 1.5
            elif a["cd"] <= 0:
                p.facing = side
                self.hit(near, rnd(20, 26), side, "bonk", p)
                p.attack_t = 0.3
                p.consume_use()
                a["cd"] = 1.2
                a["retreat"] = 0.9

    def prey_flee(self, p, hunters, near, dn, a, dt):
        """Pas armé : filer vers le point le plus sûr, percer si coincé."""
        T = self.terrain
        side = 1 if near.cx() > p.cx() else -1
        away = -side
        pts = [(r.cx(), r.feet()) for r in hunters]
        far = T.farthest_point(pts)
        toward = far is not None and (far[0] - p.cx()) * side > 0
        room = T.room(p.seg, p.cx(), away)
        if far and far[1] is not p.seg and not T.reachable(p.seg, far[1]) and p.tunnel_cd <= 0 \
                and (toward or room < 220 or dn < 320):
            p.tunnel_to(far[0], far[1])
            return
        cornered = room < 200 or toward
        if cornered:
            if p.tunnel_cd <= 0 and len(T.segs) > 1 and dn < 420:   # creuser pour disparaître
                seg = T.hunter_free_seg(pts, exclude=p.seg) or (far[1] if far else None)
                if seg is not None and seg is not p.seg:
                    p.tunnel_to(T.random_x(seg), seg)
                    p.tunnel_cd = 9.0
                    return
            if p.veh_t > 0 and a["jump_cd"] <= 0 and far:      # percée en trottinette
                p.hop(500)
                p.go_to(far[0], far[1], PREY_SPEED)
                a["jump_cd"] = 2.5
                if random.random() < 0.6:
                    p.say(random.choice(HUNT["dash"]), 1.2)
                return
            if dn < 260 and a["jump_cd"] <= 0:                 # saut par-dessus
                p.hop(620)
                p.walk_to(p.cx() + side * 560, PREY_SPEED)
                a["jump_cd"] = 2.5
                if random.random() < 0.5:
                    p.say("Hop !", 1.0)
                return
            # percée : on fonce vers le point sûr tant qu'il reste de la place
            others = [r for r in hunters if r is not near and (r.cx() - p.cx()) * side > 0]
            if a["walk_cd"] <= 0:
                a["walk_cd"] = 0.35
                if far and dn > 320 and not others:
                    p.go_to(far[0], far[1], PREY_SPEED)
                else:
                    p.walk_to(p.cx() + away * 300, PREY_SPEED)
            if dn < 500 and a["jump_cd"] <= 0 and random.random() < dt * 1.5:
                p.hop(400)
                a["jump_cd"] = 1.0
            return
        if a["walk_cd"] <= 0:
            a["walk_cd"] = 0.4
            if far and far[1] is not p.seg:
                p.go_to(far[0], far[1], PREY_SPEED)
            else:
                p.walk_to(p.cx() + away * 450, PREY_SPEED)
        if dn < 450 and a["jump_cd"] <= 0 and random.random() < dt * 1.2:   # zigzag
            p.hop(380)
            a["jump_cd"] = 1.0

    def prey_fly(self, p, hunters, near, dn, a, dt):
        """En vol : rester hors de portée et bombarder."""
        T = self.terrain
        pts = [(r.cx(), r.feet()) for r in hunters]
        far = T.farthest_point(pts)
        flyers = [r for r in hunters if r.fly]
        if a["walk_cd"] <= 0:
            a["walk_cd"] = 0.6
            if flyers and dn < 300:
                p.walk_to(p.cx() + (1 if p.cx() > near.cx() else -1) * 600, p.fly_speed)
            elif dn < 380 or p.state == "idle":
                p.walk_to(far[0] if far else T.random_x(), p.fly_speed)
        if p.fly_kind != "ballon" and dn < 520 and a["cd"] <= 0 and random.random() < 0.7:
            p.facing = 1 if near.cx() > p.cx() else -1
            if p.item == "blaster" and p.ammo > 0:
                self.shoot(p, near, kind="dart", speed=760, dmg=14)
                p.consume_use()
            else:
                self.shoot(p, near, arc=True, T=0.7)
            a["cd"] = 1.3
            if a["say_cd"] <= 0 and random.random() < 0.4:
                p.say(random.choice(HUNT["bomb"]), 1.4)
                a["say_cd"] = 6

    def prey_hide(self, p, hunters, weapon, a, dt):
        """Hors de vue : embuscade si armé, sinon changer de planque et se camoufler."""
        T = self.terrain
        pts = [(r.cx(), r.feet()) for r in hunters]
        near = min(hunters, key=lambda r: dist2(p.cx(), p.feet(), r.cx(), r.feet()))
        dn = dist2(p.cx(), p.feet(), near.cx(), near.feet())
        same_screen = any(T.seg_near(r.cx(), r.feet()) is p.seg for r in hunters)
        a["relocate"] = a.get("relocate", rnd(30, 55)) - dt
        if weapon:                                             # embuscade
            if p.state == "idle" and p.still_t > 1.0 and not p.camo:
                p.camo = True
                if a["say_cd"] <= 0 and random.random() < 0.5:
                    p.say("Embuscade...", 1.4)
                    a["say_cd"] = 10
            return
        must_move = (same_screen and dn < 1300) or a["relocate"] <= 0
        if must_move and p.state == "idle" and a["goal_cd"] <= 0:
            a["goal_cd"] = 3.0
            a["relocate"] = rnd(30, 55)
            seg = T.hunter_free_seg(pts, exclude=p.seg if same_screen else None)
            if seg is not None:
                p.go_to(T.random_x(seg), seg, PREY_SPEED * 0.85)
            else:
                far = T.farthest_point(pts, prefer=p.seg)
                if far and dist2(far[0], far[1].yb, p.cx(), p.feet()) > 150:
                    p.go_to(far[0] + rnd(-120, 120), far[1], PREY_SPEED * 0.85)
            return
        if p.state == "idle" and p.still_t > 1.2 and not p.camo:
            p.camo = True
            if a["say_cd"] <= 0 and random.random() < 0.5:
                p.say(random.choice(HUNT["prey_hide"]), 1.4)
                a["say_cd"] = 10

    # ---------- combat ----------
    def attack(self, p, tgt, d, elev=0.0):
        if p.item == "blaster" and d < 560:
            self.shoot(p, tgt, kind="dart", speed=760, dmg=14)
            p.consume_use()
            if random.random() < 0.3:
                p.say("Pan !", 1.0)
            return True
        if p.item == "marteau" and d < 80 and abs(elev) < 60:
            self.hit(tgt, rnd(22, 28), p.facing, "bonk", p)
            p.attack_t = 0.3
            p.consume_use()
            return True
        if d < 60 and abs(elev) < 60:
            self.hit(tgt, rnd(10, 14), p.facing, "tackle", p)
            p.attack_t = 0.3
            p.hop(240)
            return True
        if d < 440 and random.random() < 0.45:
            self.shoot(p, tgt, arc=(d > 260 or abs(elev) > 60), T=max(0.6, d / 420),
                       spread=70 if abs(elev) > 60 else 15)
            return True
        return False

    def hit(self, target, dmg, dirn, kind, attacker):
        if isinstance(target, Pet):
            self.damage(target, dmg, dirn, by=attacker.name)
        else:
            self.link.emit(type="hit", to=target.iid, pet=target.name, dmg=round(dmg, 1),
                           dirn=dirn, kind=kind, by=attacker.name)
            attacker.emit("sparkle", 3, x=W / 2 + 40 * attacker.facing, y=GROUND - 40)

    def shoot(self, f, o, arc=False, T=0.8, kind=None, speed=520.0, dmg=None, spread=15):
        f.attack_t = 0.3
        sx = f.cx() + f.facing * 38
        sy = f.feet() - 36
        tx, ty = o.cx() + rnd(-spread, spread), o.feet() - 38
        if arc:
            g = 900.0
            vx = (tx - sx) / T
            vy = (ty - sy - 0.5 * g * T * T) / T
            dmg = dmg if dmg is not None else rnd(6, 9)
        elif kind == "dart":                                   # visée directe
            dx, dy = tx - sx, ty - sy
            dd = math.hypot(dx, dy) or 1.0
            g, vx, vy = 0.0, speed * dx / dd, speed * dy / dd
            dmg = dmg if dmg is not None else 14
        else:
            g, vx, vy = 0.0, f.facing * speed, 0.0
            dmg = dmg if dmg is not None else rnd(9, 13)
        self.shots.append(Shot(f, o, sx, sy, vx, vy, g, dmg, kind))

    def run_shots(self, dt):
        T = self.terrain
        for s in list(self.shots):
            s.step(dt)
            o = s.target
            gx, gy = o.cx(), o.feet() - 38
            local = isinstance(o, Pet)
            if local and s.dodge and o.grounded() and o.state != "ko" and abs(s.x - gx) < 130:
                o.hop(440)
                s.dodge = False
            hit = (o.active() and o.state not in ("ko", "drag", "tunnel") and o.cloud_t <= 0
                   and abs(s.x - gx) < 26 and abs(s.y - gy) < 34)
            if hit and not local and not getattr(s, "rolled", False):
                s.rolled = True                                # esquive des cibles distantes
                miss = 0.55 if o.fly else 0.4 if o.moving() else 0.15
                if random.random() < miss:
                    s.missed = True
            if getattr(s, "missed", False):
                hit = False
            gone = (s.t > 4 or s.y > T.max_yb + 10 or s.x < T.x0 - 50 or s.x > T.x1 + 50)
            if hit:
                dirn = 1 if s.vx > 0 else -1
                if s.dmg <= 0:                                 # boule de neige d'enfant : surprise
                    if local:
                        o.emit("snow", 6, x=s.x - o.x, y=s.y - o.y, spread=6)
                        o.floaters.append(["POF !", 0.0])
                        o.set_expr("surprised", 1.2)
                        if o.grounded():
                            o.launch(dirn * 60, -140)
                        if random.random() < 0.5:
                            o.say(random.choice(["Hé !", "Petit garnement !", "Brrr !", "Toi, viens ici !"]), 1.4)
                elif local:
                    o.emit("feather" if s.kind == "pillow" else "snow", 6,
                           x=s.x - o.x, y=s.y - o.y, spread=6)
                    self.damage(o, s.dmg, dirn, by=s.owner.name)
                else:
                    self.link.emit(type="hit", to=o.iid, pet=o.name, dmg=round(s.dmg, 1),
                                   dirn=dirn, kind=s.kind, by=s.owner.name)
            if hit or gone:
                s.kill()
                self.shots.remove(s)

    def damage(self, o, dmg, dirn, by=None, remote=False):
        if o.shield > 0:
            o.shield -= 1
            o.floaters.append(["BLOQUÉ !", 0.0])
            o.emit("sparkle", 4, y=GROUND - 60)
            o.hp_show = 2
            o.launch(dirn * 60, -120)
            return
        crit = random.random() < 0.12
        dmg = dmg * (1.6 if crit else 1)
        o.hp = max(0.0, o.hp - dmg)
        o.hurt = 0.35
        o.floaters.append(["SUPER BONK !" if crit else random.choice(HIT_WORDS), 0.0])
        o.emit("sparkle", 3, y=GROUND - 70)
        if o.hp <= 0:
            self.freeze = 0.3
            if remote:
                self.on_death(o, by)
            else:
                o.pending_ko = True
                o.launch(dirn * 300, -440)
                o.say("Pouf...", 1.4)
        elif o.fly_t > 0:                                      # touché en vol
            self.freeze = 0.12
            if o.fly_kind == "ballon":
                o.end_flight(popped=True)
            else:
                o.x += dirn * 40
                o.fly_alt += rnd(-40, 40)
        else:
            self.freeze = 0.2 if crit else 0.12
            o.launch(dirn * (230 if crit else 120), -300 if crit else -200)
            if random.random() < 0.25:
                o.say(random.choice(["Aïe !", "Ouille !", "Hé !"]), 1.2)

    def on_death(self, o, by=None):
        o.die()
        self.cancel_duo()
        if self.role == "prey":
            self.link.emit(type="killed", to="*", pet=o.name, by=by)
            mate = o.partner
            if mate.active():
                mate.say(random.choice(HUNT["prey_panic"]), 2.2)
                mate.set_expr("surprised", 1.5)
                mate.speed_t = max(mate.speed_t, 6.0)               # adrénaline
            if not any(p.active() for p in self.pets):
                self.quit_t = 4.0
        else:
            o.say("Je reviendrai...", 2.2)
            self.respawn_q.append([o, 20.0 if self.role == "hunter" else 8.0])

    # ---------- cerveau du duo (temps de paix) ----------
    def decide(self, p):
        if p.is_idol:
            p.go_idle(2)
            return
        if p.opening is not None:
            p.timer = 0.5
            return
        if p.is_kid:
            return self.family.decide_person(p)
        cfg = self.cfg
        other = p.partner
        T = self.terrain
        if p.energy < 20 and random.random() < 0.6:
            p.say("*bâille*", 1.5)
            p.sleep(rnd(25, 45))
            return
        if self.family.founder_hook(p):
            return
        if (self.family.active and self.family.founders_can_lay() and self.bond >= BIRTH_BOND
                and p.energy > 50 and other.energy > 50 and other.active() and other.state in ("idle", "walk")
                and random.random() < 0.08 and self.start_duo("birth")):
            return
        duo_p = cfg["duo"] * (1.3 if p.fun < 40 else 1.0)
        if random.random() < duo_p and other.grounded() and other.state in ("idle", "walk") \
                and not other.busy and other.dizzy <= 0 and other.opening is None:
            kinds = {"highfive": 2, "chase": 2, "photo": 1, "race": 2, "hide_seek": 1,
                     "dance": 2 if p.fun < 50 else 1,
                     "bump": 1 if self.bond > 50 else 3,
                     "piggy": 2 if self.bond > 65 else 0.5}
            if self.bubble_ok():
                kinds["chat"] = 2
                kinds["debate"] = 1
            if cfg["war"] is not None and self.now - self.last_war > cfg["war"] \
                    and self.cursor_still > 45:
                kinds["war"] = 3 if self.bond < 40 else 1.5
            kind = random.choices(list(kinds), weights=list(kinds.values()))[0]
            if self.start_duo(kind):
                return
        if random.random() < 0.5 and self.seek_chest(p, 0.0, radius=900):
            return
        if p.item in FLIGHT_ITEMS and p.grounded() and random.random() < 0.5:
            if p.use_item():
                p.walk_to(T.random_x(), p.fly_speed)
                return
        r = random.random()
        if len(T.segs) > 1 and r < 0.12:
            seg = T.random_seg(exclude=p.seg)
            p.go_to(T.random_x(seg), seg)
            if p.state == "tunnel" or random.random() < 0.3:
                p.say(random.choice(["Je vais voir à côté.", "Autre écran !", "Exploration !"]), 1.6)
        elif r < 0.55:
            near_kids = [k for k in self.kids if k.leaving is None and k.active()]
            if near_kids and random.random() < 0.7:            # rester près des petits
                kid = random.choice(near_kids)
                p.go_to(kid.cx() + rnd(-320, 320), kid.seg)
            else:
                p.walk_to(T.random_x(p.seg))
        elif r < 0.66 and self.bubble_ok():
            p.say(random.choice(SOLO_LINES[p.name]), 3.2)
            self.last_bubble = self.now
            p.go_idle(3.5)
        elif r < 0.74 or (self.cursor_still > 120 and r < 0.86):
            p.sleep()
        elif r < 0.86:
            p.hop(300)
            p.go_idle(2)
        else:
            p.go_idle(rnd(2, 4))

    def start_duo(self, kind=None, **data):
        a, b = self.pets
        if self.duo or self.role is not None or self.family.scene is not None or self.fanmeet.active \
                or not all(p.grounded() and p.active() for p in self.pets):
            return False
        for p in self.pets:
            if p.state == "sleep":
                p.wake("Hm ? J'arrive.")
            p.busy = True
        kind = kind or random.choice(["chat", "highfive", "chase", "bump"])
        if kind == "war":
            self.last_war = self.now
        T = self.terrain
        if kind == "chase":
            chaser, runner = random.sample(self.pets, 2)
            seg = runner.seg or T.seg_near(runner.cx(), runner.feet())
            d = 1 if runner.cx() >= chaser.cx() else -1
            tx = seg.x1 - 70 if d > 0 else seg.x0 + 70
            runner.walk_to(tx, RUN_SPEED)
            chaser.go_to(tx - d * 75, seg, RUN_SPEED * 0.9)
            chaser.say("Attends-moi !", 2)
            runner.set_expr("wink", 2)
            runner.say("Attrape-moi !", 2)
            self.duo = dict(kind=kind, phase="act", t=0.0, step=0, a=chaser, b=runner)
            return True
        if kind == "race":
            seg = a.seg or T.seg_near(a.cx(), a.feet())
            d = 1 if (seg.x1 - max(a.cx(), b.cx())) > (min(a.cx(), b.cx()) - seg.x0) else -1
            self.duo = dict(kind=kind, phase="act", t=0.0, step=0, a=a, b=b, d=d, seg=seg)
            return True
        if kind == "hide_seek":
            seeker, hider = random.sample(self.pets, 2)
            self.duo = dict(kind=kind, phase="act", t=0.0, step=0, a=seeker, b=hider)
            return True
        # duos qui commencent face à face
        left, right = sorted(self.pets, key=lambda p: p.cx())
        seg = left.seg or T.seg_near(left.cx(), left.feet())
        gap = 170 if kind == "war" else 36
        if right.seg is not seg and not T.reachable(right.seg, seg):
            seg = right.seg or seg
            mid = right.cx()
        else:
            mid = (left.cx() + right.cx()) / 2
        mid = max(seg.x0 + gap + 50, min(seg.x1 - gap - 50, mid))
        left.go_to(mid - gap, seg, 95)
        right.go_to(mid + gap, seg, 95)
        self.duo = dict(kind=kind, phase="approach", t=0.0, step=0, a=left, b=right, **data)
        return True

    def run_duo(self, dt):
        d = self.duo
        if not d:
            return
        a, b = d["a"], d["b"]
        d["t"] += dt
        if d["phase"] == "approach":
            if a.state == "idle" and b.state == "idle" and a.grounded() and b.grounded():
                a.face(b)
                b.face(a)
                d.update(phase="act", t=0.0, step=0)
            elif d["t"] > 18:
                self.end_duo()
            return
        fn = getattr(self, "duo_" + d["kind"], None)
        if fn is None:
            self.end_duo()
        else:
            fn(d, dt)

    @staticmethod
    def nxt(d, step):
        d.update(step=step, t=0.0)

    def reward(self, fun=0, bond=0):
        for p in self.pets:
            p.fun = min(100.0, p.fun + fun)
        self.bond = max(0.0, min(100.0, self.bond + bond))

    def duo_chat(self, d, dt):
        a, b, t, s = d["a"], d["b"], d["t"], d["step"]
        l1, l2 = d.setdefault("lines", random.choice(DUO_CHATS))
        if s == 0:
            a.say(l1, 2.6)
            self.last_bubble = self.now
            d["step"] = 1
        elif s == 1 and t > 2.6:
            b.say(l2, 2.8)
            d["step"] = 2
        elif s == 2 and t > 5.6:
            a.set_expr("happy", 1.2)
            self.reward(fun=5, bond=3)
            self.end_duo()

    def duo_debate(self, d, dt):
        a, b, t, s = d["a"], d["b"], d["t"], d["step"]
        lines = d.setdefault("lines", random.choice(DEBATES))
        if s < len(lines):
            if s == 0 or t > 2.3:
                spk, other = (a, b) if s % 2 == 0 else (b, a)
                spk.say(lines[s], 2.6)
                other.set_expr(random.choice(["pout", "surprised", "wink"]), 1.5)
                self.last_bubble = self.now
                self.nxt(d, s + 1)
        elif t > 2.6:
            loser = a if len(lines) % 2 == 0 else b
            loser.set_expr("pout", 2)
            loser.partner.set_expr("happy", 2)
            loser.partner.emit("note", 2, y=GROUND - 85)
            self.reward(fun=8, bond=2)
            self.end_duo()

    def duo_highfive(self, d, dt):
        a, b, t, s = d["a"], d["b"], d["t"], d["step"]
        if s == 0 and t > 0.25:
            a.arm_up = b.arm_up = True
            a.hop(380)
            b.hop(380)
            d["step"] = 1
        elif s == 1 and t > 0.45:
            a.spark = b.spark = 0.5
            for p in (a, b):
                p.set_expr("happy", 1.6)
                p.emit("sparkle", 5, x=W / 2 + 34 * p.facing, y=GROUND - 90)
            a.say("Yay !", 1.4)
            b.say("Yay !", 1.4)
            d["step"] = 2
        elif s == 2 and t > 1.8:
            self.reward(fun=6, bond=4)
            self.end_duo()

    def duo_bump(self, d, dt):
        a, b, t, s = d["a"], d["b"], d["t"], d["step"]
        if s == 0:
            pusher, target = random.choice([(a, b), (b, a)])
            d.update(p=pusher, q=target, step=1)
            pusher.set_expr("wink", 1.5)
            pusher.say("Bouh !", 1.2)
            pusher.hop(200)
        elif s == 1 and t > 0.35:
            pusher, target = d["p"], d["q"]
            dirn = 1 if target.cx() > pusher.cx() else -1
            target.launch(dirn * 240, -380)
            target.set_expr("surprised", 1.0)
            target.say("Iiih !", 1.4)
            target.land_msg = "Pas drôle !"
            d["step"] = 2
        elif s == 2 and t > 1.4:
            d["q"].set_expr("pout", 2)
            d["p"].say("Hihi.", 1.5)
            d["step"] = 3
        elif s == 3 and t > 3.4:
            self.reward(fun=4, bond=-4)
            self.end_duo()

    def duo_chase(self, d, dt):
        a, b, t = d["a"], d["b"], d["t"]
        if (a.state == "idle" and b.state == "idle") or t > 10:
            a.face(b)
            b.face(a)
            a.say("Pff... trop rapide.", 2)
            b.set_expr("happy", 1.5)
            b.say("Hihi !", 2)
            self.reward(fun=8, bond=2)
            self.end_duo()

    def duo_birth(self, d, dt):
        a, b, t, s = d["a"], d["b"], d["t"], d["step"]
        if s == 0:
            a.say(KID_LINES["birth"][0], 1.8)
            a.set_expr("happy", 4)
            self.nxt(d, 1)
        elif s == 1 and t > 1.7:
            b.say(KID_LINES["birth"][1], 1.8)
            b.set_expr("surprised", 1.2)
            b.hop(320)
            self.nxt(d, 2)
        elif s == 2 and t > 1.6:
            for p in (a, b):
                p.hugging = True
                p.set_expr("happy", 3)
                p.emit("heart", 5, x=W / 2 + 30 * p.facing, y=GROUND - 70)
            a.say(KID_LINES["birth"][2], 2)
            self.nxt(d, 3)
        elif s == 3 and t > 2.2:
            a.hugging = b.hugging = False
            seg = a.seg or self.terrain.segs[0]
            x = (a.cx() + b.cx()) / 2
            if not self.family.lay_egg(x, seg, self.pets, hatch=12 if d.get("quick") else None):
                return self.end_duo()
            for p in (a, b):
                p.walk_to(x + (-75 if p is a else 75), 80)
            self.nxt(d, 4)
        elif s == 4 and t > 2.5:
            b.say(KID_LINES["birth"][3], 2)
            e = self.family.egg
            for p in (a, b):
                p.facing = 1 if e and e["x"] > p.cx() else -1
            self.reward(fun=10, bond=5)
            self.end_duo()

    def kids_react(self, what):
        for k in self.kids:
            if k.leaving is not None or k.state not in ("idle", "walk"):
                continue
            if what == "flash":
                k.emit("flash", 1)
                k.set_expr("happy", 2)
            elif what == "beat":
                k.hop(220)
                k.set_expr("happy", 0.6)
                if random.random() < 0.5:
                    k.emit("note", 1, y=GROUND - 70)

    def duo_photo(self, d, dt):
        a, b, t, s = d["a"], d["b"], d["t"], d["step"]
        if s == 0:
            a.say("Photo souvenir !" if not self.kids else "Photo de famille !", 1.6)
            for p in (a, b):
                p.arm_up = True
                p.set_expr("happy", 3.5)
            for k in self.kids:
                if k.state in ("idle", "walk") and k.leaving is None:
                    k.go_to((a.cx() + b.cx()) / 2 + rnd(-90, 90), a.seg, k.run_speed())
            self.nxt(d, 1)
        elif s == 1 and t > 1.4:
            b.say("Cheese !", 1.4)
            self.nxt(d, 2)
        elif s == 2 and t > 0.8:
            for p in (a, b):
                p.emit("flash", 1)
                p.emit("sparkle", 6, y=GROUND - 90)
            self.kids_react("flash")
            self.nxt(d, 3)
        elif s == 3 and t > 1.6:
            a.arm_up = b.arm_up = False
            self.reward(fun=7, bond=4)
            self.end_duo()

    def duo_dance(self, d, dt):
        a, b, t, s = d["a"], d["b"], d["t"], d["step"]
        if s == 0:
            a.say("♪ On danse ? ♪", 1.8)
            b.say("♫ Toujours ! ♫", 1.8)
            self.nxt(d, 1)
        elif s == 1:
            beat = int(t * 2.2)
            if beat != d.get("beat"):
                d["beat"] = beat
                (a if beat % 2 == 0 else b).hop(300)
                if beat % 2 == 0:
                    self.kids_react("beat")
                for p in (a, b):
                    p.set_expr("happy", 0.6)
                    if random.random() < 0.6:
                        p.emit("note", 1, y=GROUND - 90)
            if t > 7:
                self.reward(fun=12, bond=3)
                self.end_duo()

    def duo_race(self, d, dt):
        a, b, t, s = d["a"], d["b"], d["t"], d["step"]
        seg, dirn = d["seg"], d["d"]
        if s == 0:
            for p in (a, b):
                p.facing = dirn
            a.say("Course jusqu'au bord !", 1.6)
            self.nxt(d, 1)
        elif s == 1 and t > 1.5:
            b.say("3, 2, 1... GO !", 1.4)
            edge = seg.x1 - 60 if dirn > 0 else seg.x0 + 60
            for p in (a, b):
                p.go_to(edge, seg, RUN_SPEED * rnd(0.92, 1.08))
            self.nxt(d, 2)
        elif s == 2:
            arrived = [p for p in (a, b) if p.state == "idle"]
            if arrived or t > 14:
                w = arrived[0] if arrived else random.choice((a, b))
                w.say("Gagné !", 1.8)
                w.set_expr("happy", 2)
                w.hop(380)
                w.partner.set_expr("pout", 2)
                w.partner.say("Pff.", 1.4)
                self.nxt(d, 3)
        elif s == 3 and t > 2.4:
            self.reward(fun=10, bond=1)
            self.end_duo()

    def duo_hide_seek(self, d, dt):
        seeker, hider, t, s = d["a"], d["b"], d["t"], d["step"]
        T = self.terrain
        if s == 0:
            seeker.say("Cache-cache ! Je compte.", 1.8)
            seeker.set_expr("closed", 6.5)
            hider.say("Hihi !", 1.2)
            far = T.farthest_point([(seeker.cx(), seeker.feet())])
            if far:
                hider.go_to(far[0] + rnd(-120, 120), far[1], RUN_SPEED)
            self.nxt(d, 1)
        elif s == 1:
            n = int(t / 1.6)
            if n != d.get("n") and n < 3:
                d["n"] = n
                seeker.say("%d..." % (n + 1), 1.2)
            if hider.state == "idle" and hider.still_t > 0.8:
                hider.camo = True
            if t > 6.2:
                seeker.set_expr(None, 0)
                seeker.say("J'arrive !", 1.4)
                hider.camo = True
                self.nxt(d, 2)
        elif s == 2:
            if hider.state == "idle":
                hider.camo = True
            dist = dist2(seeker.cx(), seeker.feet(), hider.cx(), hider.feet())
            if dist < 140 and seeker.state in ("idle", "walk"):
                seeker.say("Trouvé !", 1.8)
                seeker.set_expr("happy", 2)
                hider.camo = False
                hider.set_expr("surprised", 1.5)
                hider.say("Zut !", 1.4)
                hider.hop(260)
                self.nxt(d, 3)
                return
            if t > 30:
                hider.camo = False
                hider.say("Tu m'as pas trouvé !", 2)
                hider.set_expr("happy", 2)
                seeker.set_expr("pout", 2)
                self.nxt(d, 3)
                return
            d["scan"] = d.get("scan", 0) - dt
            if seeker.state == "idle" and d["scan"] <= 0:
                d["scan"] = rnd(1.5, 3)
                if random.random() < 0.6:
                    seg = hider.seg or T.seg_near(hider.cx(), hider.feet())
                    x = hider.cx() + rnd(-350, 350)
                else:
                    seg = T.random_seg()
                    x = T.random_x(seg)
                if random.random() < 0.3:
                    seeker.say(random.choice(["Où est-il ?", "Je te vois... non.", "Hmm..."]), 1.4)
                seeker.go_to(x, seg, 110)
        elif s == 3 and t > 2.4:
            self.reward(fun=14, bond=4)
            self.end_duo()

    def duo_piggy(self, d, dt):
        a, b, t, s = d["a"], d["b"], d["t"], d["step"]
        T = self.terrain
        if s == 0:
            b.say("Porte-moi !", 1.5)
            b.set_expr("happy", 2)
            self.nxt(d, 1)
        elif s == 1 and t > 1.2:
            a.say("Grimpe !", 1.2)
            if not b.mount(a):
                return self.end_duo()
            d["dur"] = rnd(9, 14)
            self.nxt(d, 2)
        elif s == 2:
            if b.state != "ride":
                return self.end_duo()
            if a.state == "idle":
                a.walk_to(T.random_x(a.seg), 80)
            if t > d["dur"]:
                b.dismount(True)
                a.say("Ouf, t'es lourd.", 1.6)
                b.say("Encore !", 1.4)
                for p in (a, b):
                    p.emit("heart", 3, y=GROUND - 80)
                self.nxt(d, 3)
        elif s == 3 and t > 2.2:
            self.reward(fun=10, bond=6)
            self.end_duo()

    def duo_share(self, d, dt):
        giver = d.get("giver") or d["a"]
        other = giver.partner
        t, s = d["t"], d["step"]
        if s == 0:
            if not giver.item:
                return self.end_duo()
            giver.say("Tiens, pour toi !", 1.8)
            giver.attack_t = 0.6
            self.nxt(d, 1)
        elif s == 1 and t > 1.2:
            if giver.item:
                other.give_item(giver.item)
                giver.item, giver.ammo = None, 0
            other.say("Merci !", 1.5)
            for p in (giver, other):
                p.set_expr("happy", 2)
                p.emit("heart", 3, y=GROUND - 80)
            self.nxt(d, 2)
        elif s == 2 and t > 2:
            self.reward(fun=4, bond=6)
            self.end_duo()

    # ---------- bataille de polochons (le duo entre eux) ----------
    def duo_war(self, d, dt):
        a, b, t, s = d["a"], d["b"], d["t"], d["step"]
        if s == 0:
            for p in self.pets:
                p.mood, p.hp, p.hp_show = "war", 100.0, 0.0
            a.set_expr("wink", 1.3)
            a.say("C'est la guerre !", 1.8)
            d["cd"] = {a.name: 1.3, b.name: 1.9}
            self.nxt(d, 1)
        elif s == 1 and t > 1.4:
            b.set_expr("wink", 1.3)
            b.say("Même pas peur !", 1.8)
            self.nxt(d, 2)
        elif s == 2 and t > 1.3:
            self.nxt(d, 3)
        elif s == 3:
            if d.get("cloud"):
                return self.run_cloud(d, dt)
            for p in self.pets:
                if p.state == "ko":
                    w = p.partner
                    self.score[w.name] += 1
                    w.mood, w.hp_show = None, 4
                    w.set_expr("happy", 3)
                    w.say(WIN_LINES[w.name], 2.6)
                    if self.tray:
                        self.tray.setToolTip("H13ris — Hybris %d · %d Iblis"
                                             % (self.score["Hybris"], self.score["Iblis"]))
                    self.clear_shots()
                    d.update(w=w, l=p)
                    return self.nxt(d, 4)
            if t > 60:
                a.say("Match nul !", 2)
                b.say("...Égalité.", 2)
                self.clear_shots()
                d.update(w=a, l=b)
                return self.nxt(d, 5)
            self.resolve_charge(d)
            for f in (a, b):
                o = f.partner
                if f.state == "idle":
                    f.face(o)
                d["cd"][f.name] -= dt
                if d["cd"][f.name] <= 0 and f.state == "idle" and f.grounded() \
                        and o.state != "ko" and d.get("charger") is None and not d.get("cloud"):
                    self.war_action(f, o, d)
        elif s == 4:
            w, l = d["w"], d["l"]
            if t > 0.3 and not d.get("h1"):
                d["h1"] = True
                w.hop(420)
            if t > 1.0 and not d.get("h2"):
                d["h2"] = True
                w.hop(420)
                w.spark = 0.5
                w.emit("sparkle", 7, y=GROUND - 90)
            if t > 2.6:
                l.go_idle(30)
                l.hp, l.mood, l.hp_show = 100.0, None, 2.5
                l.hop(220)
                l.set_expr("pout", 3.5)
                l.say("Hmpf...", 2.2)
                self.nxt(d, 5)
        elif s == 5 and t > 1.4:
            w, l = d["w"], d["l"]
            for p in self.pets:
                p.mood = None
            if w.state == "idle" and l.grounded():
                dirn = 1 if l.cx() > w.cx() else -1
                w.go_to(l.cx() - dirn * 34, l.seg)
                self.nxt(d, 6)
            elif t > 6:
                self.end_duo()
        elif s == 6 and ((d["w"].state == "idle" and t > 0.2) or t > 9):
            w, l = d["w"], d["l"]
            w.face(l)
            l.face(w)
            w.say("Désolé... câlin ?", 2)
            self.nxt(d, 7)
        elif s == 7 and t > 1.8:
            w, l = d["w"], d["l"]
            l.say("...Ok. Câlin.", 2)
            for p in (w, l):
                p.hugging = True
                p.set_expr("happy", 3.2)
                p.emit("heart", 4, x=W / 2 + 30 * p.facing, y=GROUND - 70)
            self.nxt(d, 8)
        elif s == 8:
            if dt > 0 and int(t * 3) != int((t - dt) * 3):
                for p in self.pets:
                    p.emit("heart", 1, x=W / 2 + 30 * p.facing, y=GROUND - 75)
            if t > 3.2:
                self.reward(fun=10, bond=-6)
                self.end_duo()

    def war_action(self, f, o, d):
        dist = o.cx() - f.cx()
        dirn = 1 if dist > 0 else -1
        f.facing = dirn
        d["cd"][f.name] = rnd(0.9, 1.9)
        names = ATTACKS[f.name]
        r = random.random()
        if abs(dist) < 150 and r < 0.5:
            f.walk_to(f.cx() - dirn * 170, 160)
            d["cd"][f.name] = 0.5
        elif r < 0.50:
            self.shoot(f, o, arc=False)
            if random.random() < 0.3:
                f.say(names[0], 1.2)
        elif r < 0.75:
            for T in (0.75, 0.95, 1.15):
                self.shoot(f, o, arc=True, T=T)
            f.say(names[1], 1.3)
            d["cd"][f.name] += 0.6
        elif r < 0.90 and abs(dist) > 160:
            f.walk_to(o.cx() - dirn * 45, 330)
            f.say(names[2], 1.3)
            d["charger"] = f
        else:
            f.set_expr("wink", 1.2)
            f.say(random.choice(WAR_TAUNTS[f.name]), 2)
            d["cd"][f.name] += 0.8

    def resolve_charge(self, d):
        c = d.get("charger")
        if c is None:
            return
        o = c.partner
        if c.state != "walk":
            d["charger"] = None
            return
        if abs(c.cx() - o.cx()) < 62 and abs(c.y - o.y) < 30 and o.state in ("idle", "walk"):
            c.go_idle(30)
            o.go_idle(30)
            c.hide()
            dur = rnd(1.6, 2.6)
            o.cloud_t = dur
            d["cloud"] = dict(t=0.0, dur=dur, c=c, o=o)
            d["charger"] = None

    def run_cloud(self, d, dt):
        cl = d["cloud"]
        cl["t"] += dt
        c, o = cl["c"], cl["o"]
        if random.random() < dt * 8:
            o.emit("dust", 1, y=GROUND - 10, spread=40)
        if cl["t"] < cl["dur"]:
            return
        o.cloud_t = 0.0
        side = random.choice((-1, 1))
        c.x = self.terrain.clamp_x(o.cx() + side * 55, o.seg) - W / 2
        c.y = o.y
        c.seg = o.seg
        c.move(int(c.x), int(c.y))
        c.setVisible(self.visible and not self.paused)
        loser = o if random.random() < 0.6 else c
        winner = loser.partner
        dirn = 1 if loser.cx() >= winner.cx() else -1
        winner.launch(-dirn * 120, -260)
        self.damage(loser, rnd(15, 20), dirn)
        d["cloud"] = None

    def clear_shots(self):
        for q in self.shots:
            q.kill()
        self.shots = []

    def end_duo(self):
        self.clear_shots()
        self.duo = None
        for p in self.pets:
            p.cloud_t = 0.0
            if not self.paused and not p.gone:
                p.setVisible(self.visible)
            p.mood = "hunt" if self.role == "hunter" else "scared" if self.role == "prey" else None
            p.pending_ko, p.hugging, p.camo = False, False, False
            if p.expr == "closed":
                p.set_expr(None, 0)
            if p.ride_on is not None:
                p.dismount(True)
            if p.hp < 100 or p.state == "ko":
                p.hp = 100.0
            if p.state == "ko":
                p.go_idle(2)
            p.busy, p.arm_up = self.role is not None, False
            if p.state == "idle":
                p.timer = rnd(2, 5)

    def cancel_duo(self):
        if self.duo:
            self.end_duo()

    # ---------- menu / tray ----------
    def build_menu(self):
        m = QMenu()
        m.setToolTipsVisible(True)

        def add(menu, text, fn, tip=None):
            act = menu.addAction(text)
            act.triggered.connect(fn)
            if tip:
                act.setToolTip(tip)
            return act

        def check(menu, text, on, fn, tip=None):
            act = menu.addAction(text)
            act.setCheckable(True)
            act.setChecked(bool(on))
            act.toggled.connect(fn)
            if tip:
                act.setToolTip(tip)
            return act

        def radio(menu, choices, current, fn):
            grp = QActionGroup(menu)
            for key, label in choices:
                act = menu.addAction(label)
                act.setCheckable(True)
                act.setChecked(key == current)
                grp.addAction(act)
                act.triggered.connect(lambda _=False, k=key: fn(k))

        # en-tête vivant (mis à jour à chaque ouverture)
        self.title_act = m.addAction("H13ris — Hybris && Iblis")
        self.title_act.setEnabled(False)
        self.status_act = m.addAction("")
        self.status_act.setEnabled(False)
        m.addSeparator()

        # interactions du duo
        inter = m.addMenu("🎭 Interactions")
        for label, kind in (("💬 Discussion", "chat"), ("🙌 Check !", "highfive"),
                            ("🏃 Course-poursuite", "chase"), ("🙈 Cache-cache", "hide_seek"),
                            ("🐣 Portage", "piggy"), ("🏁 Course", "race"), ("📸 Photo souvenir", "photo"),
                            ("💃 Danse", "dance"), ("💢 Bousculade", "bump")):
            add(inter, label, lambda _=False, k=kind: self.force_duo(k))
        inter.addSeparator()
        add(inter, "⚔ Bataille de polochons", lambda: self.force_duo("war"))
        self.peace_act = add(inter, "🕊 Armistice (câlin)", self.armistice)

        # coffres et objets
        loot = m.addMenu("📦 Coffres && objets")
        loot.setToolTipsVisible(True)
        add(loot, "📦 Semer un coffre ici", lambda: self.sow(1, at_cursor=True), "Un coffre apparaît sous le curseur.")
        add(loot, "📦 Semer 3 coffres", lambda: self.sow(3), "Trois coffres au hasard sur les écrans.")
        give = loot.addMenu("🎁 Donner un objet")
        for key in ("jetpack", "ballon", "fusee", "potion_vol", "trottinette", "blaster",
                    "marteau", "bouclier", "potion_sang", "fumigene", "banane"):
            give.addAction(ITEMS[key]["label"]).triggered.connect(lambda _=False, k=key: self.give(k))
        loot.addSeparator()
        self.explore_act = add(loot, "🖥 Explorer un autre écran", self.explore)

        # famille et village (contenu vivant)
        self.family_menu = m.addMenu("👨‍👩‍👧 Famille && village")
        self.family_menu.setToolTipsVisible(True)
        self.family_menu.aboutToShow.connect(lambda: self.family.fill_menu(self.family_menu))
        self.fan_menu = m.addMenu("🎤 Fan meeting")
        self.fan_menu.aboutToShow.connect(lambda: self.fanmeet.fill_menu(self.fan_menu))
        m.addSeparator()

        # actions rapides
        self.demo_act = check(m, "🎬 Mode démo", False, self.family.toggle_demo,
                              "Une vie entière du village en huit minutes : naissance, école, bêtises, mariage, "
                              "petits-enfants, vieillesse. La vraie famille revient ensuite, intacte.")
        self.sleep_act = add(m, "😴 Tout le monde au dodo", self.all_sleep)
        self.wake_act = add(m, "☀ Réveil !", self.wake_all)
        self.hide_act = add(m, "👁 Masquer", self.toggle)
        m.addSeparator()

        # état et réglages
        self.state_menu = m.addMenu("📊 État")
        self.state_menu.aboutToShow.connect(self.fill_state_menu)
        cfg = m.addMenu("⚙ Réglages")
        cfg.setToolTipsVisible(True)
        mood = cfg.addMenu("🙂 Humeur du duo")
        radio(mood, [(k, c["label"]) for k, c in MODES.items()], self.mode, self.set_mode)
        rhythm = cfg.addMenu("⏳ Rythme de vie du village")
        radio(rhythm, (("court", "Court — une vie ≈ 3 jours de bureau"), ("normal", "Normal — une vie ≈ 1 semaine"),
                       ("long", "Long — une vie ≈ 1 mois")),
              self.settings.value("life_scale", "normal"), self.family.set_scale)
        cfg.addSeparator()
        self.hunt_act = check(cfg, "🎯 Mode chasse entre instances", self.hunt_enabled, self.toggle_hunt,
                              "Lance le script une deuxième fois : la première instance devient la Garde, "
                              "les suivantes des intrus traqués.")
        self.decor_act = check(cfg, "🏡 Décor du village (maison, école, bureau)", self.family.decor_on,
                               self.family.toggle_decor)
        self.moon_act = check(cfg, "☾ Départs vers la lune (vieillesse)", self.family.death_mode == "lune",
                              self.family.set_death_mode, "Décoché : les aînés restent pour toujours.")
        self.idol_act = check(cfg, "🎤 Visites surprises d'idoles", self.fanmeet.surprise, self.fanmeet.set_surprise,
                              "De temps en temps, un groupe passe au village.")
        self.toast_act = check(cfg, "🔔 Notifications du village", self.family.toasts_on, self.family.set_toasts,
                               "Naissances, mariages, départs… trois notifications par jour au maximum.")
        if sys.platform == "win32":
            self.auto_act = check(cfg, "🚀 Lancer au démarrage de Windows", autostart_get(), self.toggle_autostart)
        m.addSeparator()
        add(m, "✖ Quitter", self.app.quit)
        m.aboutToShow.connect(self.refresh_menu)
        return m

    def status_text(self):
        f = self.family
        n = len(self.link.peers) + 1
        role = {"hunter": "la Garde", "prey": "intrus", None: "en paix"}[self.role]
        bits = [role if n == 1 else "%s · %d instances" % (role, n)]
        if self.fanmeet.active:
            bits.append("%s en visite !" % self.fanmeet.group["name"])
        if f.demo:
            bits.append("démo en cours")
        elif f.active:
            bits.append("%d habitant%s" % (f.population(), "s" if f.population() > 1 else ""))
        segs = len(self.terrain.segs)
        bits.append("%d écran%s" % (segs, "s" if segs > 1 else ""))
        if self.duo and self.duo["kind"] == "war":
            bits.append("bataille !")
        return " · ".join(bits)

    def refresh_menu(self):
        f = self.family

        def sync(act, on):
            act.blockSignals(True)
            act.setChecked(bool(on))
            act.blockSignals(False)

        self.status_act.setText(self.status_text())
        self.peace_act.setEnabled(bool(self.duo and self.duo["kind"] == "war"))
        self.explore_act.setEnabled(len(self.terrain.segs) > 1)
        alive = [p for p in self.everyone() if p.active()]
        self.sleep_act.setEnabled(any(p.state != "sleep" for p in alive))
        self.wake_act.setEnabled(any(p.state == "sleep" for p in alive))
        self.hide_act.setText("👁 Masquer" if self.visible else "👁 Afficher")
        self.demo_act.setEnabled(f.demo or (f.active and self.role is None))
        sync(self.demo_act, f.demo)
        sync(self.hunt_act, self.hunt_enabled)
        sync(self.decor_act, f.decor_on)
        sync(self.moon_act, f.death_mode == "lune")
        sync(self.toast_act, f.toasts_on)
        sync(self.idol_act, self.fanmeet.surprise)
        self.update_tray_tip()

    def update_tray_tip(self):
        if self.tray is not None:
            self.tray.setToolTip("H13ris — " + self.status_text())

    def fill_state_menu(self):
        sm = self.state_menu
        sm.clear()

        def line(text):
            sm.addAction(text).setEnabled(False)

        for p in self.pets:
            it = ITEMS[p.item]["label"] if p.item else "rien en main"
            what = {"sleep": "dort", "walk": "se balade", "ride": "porté", "ghost": "fantôme", "gone": "éliminé",
                    "tunnel": "creuse", "drag": "dans ta main", "ko": "K.-O."}.get(p.state, "flâne")
            if p.fly_t > 0:
                what = "vole"
            elif p.duty:
                what = {"school": "à l'école", "study": "devoirs", "work": "au travail", "meal": "à table",
                        "sleep": "au lit", "help": "aide aux devoirs"}.get(p.duty, what)
            line("%s — énergie %d · fun %d · faim %d · %s · %s" % (p.name, p.energy, p.fun, p.hunger, it, what))
        line("Complicité : %d / 100" % self.bond)
        sm.addSeparator()
        n = len(self.link.peers) + 1
        role = {"hunter": "la Garde", "prey": "intrus", None: "en paix"}[self.role]
        line("Instances : %d — %s%s" % (n, role, " (arbitre)" if self.is_arbiter() and n > 1 else ""))
        line("Écrans : %d · coffres : %d · ouverts : %d" % (len(self.terrain.segs), len(self.chest_list()), self.opened))
        line("Humeur : %s" % self.cfg["label"])
        f = self.family
        if f.active:
            sm.addSeparator()
            line("Village : %d habitant%s · %.1f h de vie · %d parti%s vers la lune"
                 % (f.population(), "s" if f.population() > 1 else "", f.hours,
                    len(f.memorial), "s" if len(f.memorial) > 1 else ""))
            c = f.slot
            when = ("%s %02d:%02d" % ("semaine" if c.get("weekday") else "week-end", int(c["h"]), int((c["h"] % 1) * 60))
                    if c else "")
            line("Journée : %s%s" % (f.slot_label(), " (%s)" % when if when else ""))

    def set_mode(self, k):
        self.mode = k
        self.settings.setValue("mode", k)

    def toggle_hunt(self, on):
        self.hunt_enabled = on
        self.settings.setValue("hunt", on)
        if not self.is_arbiter():
            self.link.emit(type="hunt", to="arb", on=on)

    def toggle_autostart(self, on):
        ok = autostart_set(on)
        if not ok:
            self.auto_act.blockSignals(True)
            self.auto_act.setChecked(autostart_get())
            self.auto_act.blockSignals(False)
        p = random.choice(self.pets)
        p.say(("À demain matin !" if on else "Ok, je reste sage.") if ok else "Oups, registre refusé.", 2.4)
        if ok and on:
            p.set_expr("happy", 1.5)

    def on_tray(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.toggle()

    def force_duo(self, kind):
        self.cancel_duo()
        for p in self.pets:
            if p.state == "walk":
                p.go_idle()
            p.dizzy = 0.0
        if not self.start_duo(kind):
            random.choice(self.pets).say("Pas maintenant !", 1.5)

    def give(self, kind):
        pool = [p for p in self.pets if p.active() and p.state in ("idle", "walk", "sleep")]
        if not pool:
            return
        p = random.choice(pool)
        p.wake("Oh ?")
        p.give_item(kind)
        if self.role is not None and p.item in FLIGHT_ITEMS:
            p.use_item()

    def explore(self):
        T = self.terrain
        if len(T.segs) < 2:
            random.choice(self.pets).say("Il n'y a qu'un écran !", 1.8)
            return
        self.cancel_duo()
        for p in self.pets:
            if p.state in ("idle", "walk", "sleep"):
                p.wake("On bouge !")
                seg = T.random_seg(exclude=p.seg)
                p.go_to(T.random_x(seg), seg)

    def armistice(self):
        if self.duo and self.duo["kind"] == "war":
            self.end_duo()
            for p in self.pets:
                p.say("Paix !", 2)
                p.set_expr("happy", 2)
                p.emit("heart", 4, y=GROUND - 80)

    def all_sleep(self):
        self.cancel_duo()
        self.fanmeet.end()
        for p in self.everyone():
            if p.grounded():
                p.sleep(rnd(60, 120))

    def wake_all(self):
        for p in self.everyone():
            p.wake("Debout !")

    def toggle(self):
        self.visible = not self.visible
        if not self.visible:
            self.cancel_duo()
        for p in self.everyone():
            p.setVisible(self.visible and not self.paused and not p.gone)
        if self.visible:
            self.ensure_props()
        else:
            for pr in self.props.values():
                pr.hide()
            self.family.set_visible(False)
            self.fanmeet.set_visible(False)

    @staticmethod
    def make_icon(pet):
        pm = QPixmap(W, H)
        pm.fill(Qt.GlobalColor.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        state, seg = pet.state, pet.seg
        pet.state, pet.seg = "idle", Seg(0, 0, pet.feet() + 1000, 0)     # pas d'ombre
        pet.paint_all(p, bubble=False)
        pet.state, pet.seg = state, seg
        p.end()
        return QIcon(pm.copy(int(W / 2 - 46), GROUND - 92, 92, 92))


def main():
    if "--autostart" in sys.argv:
        i = sys.argv.index("--autostart")
        on = (sys.argv[i + 1:i + 2] or ["on"])[0].lower() != "off"
        ok = autostart_set(on)
        try:                                                   # pas de console dans l'exe
            print(("Démarrage auto " + ("activé" if on else "désactivé")) if ok
                  else "Impossible (Windows uniquement).")
        except Exception:
            pass
        QSettings("H13ris", "DesktopPets").setValue("autostart_init", True)
        return
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    world = World(app)  # noqa: F841 (garder la référence)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
