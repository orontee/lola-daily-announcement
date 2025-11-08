#!/usr/bin/env python3

"""Perpetuation of Lola's daily announcement for the holy object.

A desktop notification is sent unless ``notify-send`` program is not
found or called with ``--stdout`` argument.

"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import argparse
import base64
import datetime
import logging
import subprocess

logging.basicConfig()
LOGGER = logging.getLogger()


ANNOUNCE_TEMPLATE = """\
Chalut ! Aujourd'hui, {day_name} {day}, c'est la {hallow_prefix}-{hallow}.
Bonne fête à {hallow_all} les {hallow_plural} 🎆\
"""

DAY_NAMES = ("Lourdi", "Pardi", "Morquidi", "Jourdi", "Dendrevi", "Sordi", "Mitanche")

LOLA_PNG_PATH = "/tmp/lola.png"

class Genre(Enum):
    MALE = (0,)
    FEMALE = 1
    NEUTRAL = 2


@dataclass
class DayData:
    singular: str
    plural: str
    genre: Genre


# See https://github.com/tobozo/SaintObjetBot for data credits
DATA_MAP: dict[tuple[int, int], DayData] = {
    (1, 1): DayData("veisalgie", "veisalgies", Genre.FEMALE),
    (1, 2): DayData("ankylostome", "ankylostomes", Genre.MALE),
    (1, 3): DayData("apex", "apexes", Genre.MALE),
    (1, 4): DayData("arlequin", "arlequins", Genre.MALE),
    (1, 5): DayData("bengali", "bengalis", Genre.MALE),
    (1, 6): DayData("bouquetin", "bouquetins", Genre.MALE),
    (1, 7): DayData("cancrelat", "cancrelats", Genre.MALE),
    (1, 8): DayData("cerf-volant", "cerfs-volants", Genre.MALE),
    (1, 9): DayData("colibri", "colibris", Genre.MALE),
    (1, 10): DayData("dromadaire", "dromadaires", Genre.MALE),
    (1, 11): DayData("embrouillamini", "embrouillaminis", Genre.MALE),
    (1, 12): DayData("fauconneau", "fauconeaux", Genre.MALE),
    (1, 13): DayData("gambette", "gambettes", Genre.FEMALE),
    (1, 14): DayData("hérisson", " hérissons", Genre.MALE),
    (1, 15): DayData("javelot", "javelots", Genre.MALE),
    (1, 16): DayData("kangourou", "kangourous", Genre.MALE),
    (1, 17): DayData("lampion", "lampions", Genre.MALE),
    (1, 18): DayData("manuscrit", "manuscrits", Genre.MALE),
    (1, 19): DayData("quignon", "quignons", Genre.MALE),
    (1, 20): DayData("tablier", "tabliers", Genre.MALE),
    (1, 21): DayData("zorglub", "zorglubs", Genre.MALE),
    (1, 22): DayData("pataquès", "pataquès", Genre.MALE),
    (1, 23): DayData("bobèche", "bobèches", Genre.FEMALE),
    (1, 24): DayData("zézaiement", "zézaiements", Genre.MALE),
    (1, 25): DayData("flibustier", "flibustiers", Genre.MALE),
    (1, 26): DayData("mirliton", "mirlitons", Genre.MALE),
    (1, 27): DayData("craspouille", "craspouilles", Genre.FEMALE),
    (1, 28): DayData("zigouigoui", "zigouigouis", Genre.MALE),
    (1, 29): DayData("faribole", "fariboles", Genre.FEMALE),
    (1, 30): DayData("pantouflette", "pantouflettes", Genre.FEMALE),
    (1, 31): DayData("zinzin", "zinzins", Genre.MALE),
    (2, 1): DayData("bibelot", "bibelots", Genre.MALE),
    (2, 2): DayData("ukulélé", "ukulélés", Genre.MALE),
    (2, 3): DayData("grigris", "grigris", Genre.MALE),
    (2, 4): DayData("crinoline", "crinolines", Genre.FEMALE),
    (2, 5): DayData("turlutaine", "turlutaines", Genre.FEMALE),
    (2, 6): DayData("boudeuse", "boudeuses", Genre.FEMALE),
    (2, 7): DayData("tralala", "tralalas", Genre.MALE),
    (2, 8): DayData("carambolage", "carambolages", Genre.MALE),
    (2, 9): DayData("frimousse", "frimousses", Genre.FEMALE),
    (2, 10): DayData("catafalque", "catafalques", Genre.MALE),
    (2, 11): DayData("chicane", "chicanes", Genre.FEMALE),
    (2, 12): DayData("barbichette", "barbichettes", Genre.FEMALE),
    (2, 13): DayData("croquignole", "croquignoles", Genre.MALE),
    (2, 14): DayData("rouleau de sopalin", "rouleaux de sopalin", Genre.MALE),
    (2, 15): DayData("clavicule", "clavicules", Genre.FEMALE),
    (2, 16): DayData("bambinette", "bambinettes", Genre.FEMALE),
    (2, 17): DayData("sporange", "sporanges", Genre.MALE),
    (2, 18): DayData("fléole", "fléoles", Genre.FEMALE),
    (2, 19): DayData("goubelin", "goubelins", Genre.MALE),
    (2, 20): DayData("bélin", "bélins", Genre.MALE),
    (2, 21): DayData("grébiche", "grébiches", Genre.FEMALE),
    (2, 22): DayData("pipistrelle", "pipistrelles", Genre.FEMALE),
    (2, 23): DayData("badine", "badines", Genre.FEMALE),
    (2, 24): DayData("guttule", "guttules", Genre.FEMALE),
    (2, 25): DayData("sautoir", "sautoirs", Genre.MALE),
    (2, 26): DayData("tourniquet", "tourniquets", Genre.MALE),
    (2, 27): DayData("grenouillère", "grenouillères", Genre.FEMALE),
    (2, 28): DayData("torsade", "torsades", Genre.FEMALE),
    (2, 29): DayData("calicot", "calicots", Genre.MALE),
    (3, 1): DayData("gousset", "goussets", Genre.MALE),
    (3, 2): DayData("tournebille", "tournebilles", Genre.FEMALE),
    (3, 3): DayData("gibelotte", "gibelottes", Genre.FEMALE),
    (3, 4): DayData("cabestan", "cabestans", Genre.MALE),
    (3, 5): DayData("mélopée", "mélodées", Genre.FEMALE),
    (3, 6): DayData("galurin", "galurins", Genre.MALE),
    (3, 7): DayData("joug", "jougs", Genre.MALE),
    (3, 8): DayData("cabriole", "cabrioles", Genre.FEMALE),
    (3, 9): DayData("attache parisienne", "attaches parisiennes", Genre.FEMALE),
    (3, 10): DayData("bac à charbon", "bacs à charbon", Genre.MALE),
    (3, 11): DayData("béquille", "béquilles", Genre.FEMALE),
    (3, 12): DayData("boussole", "boussoles", Genre.FEMALE),
    (3, 13): DayData("caméra argentique", "caméras argentiques", Genre.FEMALE),
    (3, 14): DayData("canne", "cannes", Genre.FEMALE),
    (3, 15): DayData("cloche", "cloches", Genre.FEMALE),
    (3, 16): DayData("clou", "clous", Genre.MALE),
    (3, 17): DayData("coton-tige", "cotons-tiges", Genre.MALE),
    (3, 18): DayData("disque vinyle", "disques vinyles", Genre.MALE),
    (3, 19): DayData("encrier", "encriers", Genre.MALE),
    (3, 20): DayData("fer à repasser", "fers à repasser", Genre.MALE),
    (3, 21): DayData("fusil à pompe", "fusils à pompe", Genre.MALE),
    (3, 22): DayData("gourde", "gourdes", Genre.FEMALE),
    (3, 23): DayData(
        "imprimante à marguerite", "imprimantes à marguerite", Genre.FEMALE
    ),
    (3, 24): DayData("tendu-de-majeur", "doigts d'honneur", Genre.MALE),
    (3, 25): DayData("machine à écrire", "machines à écrire", Genre.FEMALE),
    (3, 26): DayData("poignée de porte", "poignées de porte", Genre.FEMALE),
    (3, 27): DayData("savon de marseille", "savons de marseille", Genre.MALE),
    (3, 28): DayData("stylo à plume", "stylos à plume", Genre.MALE),
    (3, 29): DayData("téléviseur cathodique", "téléviseurs cathodiques", Genre.MALE),
    (3, 30): DayData("urne funéraire", "urnes funéraires", Genre.FEMALE),
    (3, 31): DayData("balai", "balais", Genre.MALE),
    (4, 1): DayData("microplastique", "microplastiques", Genre.MALE),
    (4, 2): DayData("bougie", "bougies", Genre.FEMALE),
    (4, 3): DayData("cabine téléphonique", "cabines téléphoniques", Genre.FEMALE),
    (4, 4): DayData("canapé", "canapés", Genre.MALE),
    (4, 5): DayData("carte postale", "cartes postales", Genre.FEMALE),
    (4, 6): DayData("ceinture", "ceintures", Genre.FEMALE),
    (4, 7): DayData("engrenage", "engrenages", Genre.MALE),
    (4, 8): DayData("escalier", "escaliers", Genre.MALE),
    (4, 9): DayData("monogramme", "monogrammes", Genre.MALE),
    (4, 10): DayData("acanthe", "acanthes", Genre.FEMALE),
    (4, 11): DayData("humus", "humus", Genre.MALE),
    (4, 12): DayData("entroque", "entroque", Genre.FEMALE),
    (4, 13): DayData("fourneau", "fourneaux", Genre.MALE),
    (4, 14): DayData(
        "ampoule multiprise et rallonge",
        "ampoules multiprises et rallonges",
        Genre.FEMALE,
    ),
    (4, 15): DayData("alésoir à cliquet", "Alésoirs à cliquets", Genre.MALE),
    (4, 16): DayData("clapier", "clapiers", Genre.MALE),
    (4, 17): DayData("taloche", "taloches", Genre.FEMALE),
    (4, 18): DayData("occiput", "occiputs", Genre.MALE),
    (4, 19): DayData("diodon", "diodons", Genre.MALE),
    (4, 20): DayData("tricorne", "tricornes", Genre.MALE),
    (4, 21): DayData("spume", "spumes", Genre.FEMALE),
    (4, 22): DayData("manchon", "manchons", Genre.MALE),
    (4, 23): DayData("limaçon", "limaçons", Genre.MALE),
    (4, 24): DayData("levraut", "levrauts", Genre.MALE),
    (4, 25): DayData("gymkhana", "gymkhanas", Genre.MALE),
    (4, 26): DayData("dosimètre", "dosimètres", Genre.MALE),
    (4, 27): DayData("queue-de-pie", "queues-de-pie", Genre.FEMALE),
    (4, 28): DayData("clé à pipe débouchée", "Clés à pipe débouchées", Genre.FEMALE),
    (4, 29): DayData("perruque", "perruques", Genre.FEMALE),
    (4, 30): DayData("traille", "trailles", Genre.FEMALE),
    (5, 1): DayData("tripalium", "tripaliums", Genre.MALE),
    (5, 2): DayData("pastille", "pastilles", Genre.FEMALE),
    (5, 3): DayData("francisque", "francisques", Genre.FEMALE),
    (5, 4): DayData("pirouette", "pirouettes", Genre.FEMALE),
    (5, 5): DayData("marmouset", "marmousets", Genre.MALE),
    (5, 6): DayData("pédicelle", "pédicelles", Genre.MALE),
    (5, 7): DayData("hypsomètre", "hypsomètres", Genre.MALE),
    (5, 8): DayData("lambrequin", "lambrequins", Genre.MALE),
    (5, 9): DayData("cribellum", "cribellums", Genre.MALE),
    (5, 10): DayData("hélicoïde", "hélicoïdes", Genre.FEMALE),
    (5, 11): DayData("quenouille", "quenouilles", Genre.FEMALE),
    (5, 12): DayData("zythum", "zytha", Genre.MALE),
    (5, 13): DayData("sarbacane", "sarbacanes", Genre.FEMALE),
    (5, 14): DayData("turion", "turions", Genre.MALE),
    (5, 15): DayData("blaireau", "blaireaux", Genre.MALE),
    (5, 16): DayData("sémaphore", "sémaphores", Genre.FEMALE),
    (5, 17): DayData("crispatule", "crispatules", Genre.FEMALE),
    (5, 18): DayData("zist", "zists", Genre.MALE),
    (5, 19): DayData("chiquenaude", "chiquenaudes", Genre.FEMALE),
    (5, 20): DayData("sagouin", "sagouins", Genre.MALE),
    (5, 21): DayData("borborygme", "borborygmes", Genre.MALE),
    (5, 22): DayData("zéphyr", "zéphyrs", Genre.MALE),
    (5, 23): DayData("schnock", "schnocks", Genre.MALE),
    (5, 24): DayData("pendeloque", "pendeloques", Genre.FEMALE),
    (5, 25): DayData("falbala", "falbalas", Genre.MALE),
    (5, 26): DayData("nycthémère", "nycthémères", Genre.MALE),
    (5, 27): DayData("houppier", "houppiers", Genre.MALE),
    (5, 28): DayData("suaire", "suaires", Genre.MALE),
    (5, 29): DayData("jable", "jables", Genre.MALE),
    (5, 30): DayData("goulot", "goulots", Genre.MALE),
    (5, 31): DayData("bourdalou", "bourdalous", Genre.MALE),
    (6, 1): DayData("zibeline", "zibelines", Genre.FEMALE),
    (6, 2): DayData("turpitude", "turpitudes", Genre.FEMALE),
    (6, 3): DayData("carafon", "carafons", Genre.MALE),
    (6, 4): DayData("roubignole", "roubignoles", Genre.FEMALE),
    (6, 5): DayData("cantharide", "cantharides", Genre.FEMALE),
    (6, 6): DayData("pédoncule", "pédoncules", Genre.MALE),
    (6, 7): DayData("élytre", "élytres", Genre.MALE),
    (6, 8): DayData("cressonnière", "cressonnières", Genre.FEMALE),
    (6, 9): DayData("araignée", "araignées", Genre.FEMALE),
    (6, 10): DayData("sarment", "sarments", Genre.MALE),
    (6, 11): DayData("argousin", "argousins", Genre.MALE),
    (6, 12): DayData("poudingue", "poudingues", Genre.MALE),
    (6, 13): DayData("pandiculation", "pandiculations", Genre.FEMALE),
    (6, 14): DayData("gaudriole", "gaudrioles", Genre.FEMALE),
    (6, 15): DayData("chenapan", "chenapans", Genre.MALE),
    (6, 16): DayData("carabistouille", "carabistouilles", Genre.FEMALE),
    (6, 17): DayData("baliverne", "balivernes", Genre.FEMALE),
    (6, 18): DayData("histrion", "histrions", Genre.MALE),
    (6, 19): DayData("babiole", "babioles", Genre.FEMALE),
    (6, 20): DayData("pétouille", "pétouilles", Genre.FEMALE),
    (6, 21): DayData("baragouin", "baragouins", Genre.MALE),
    (6, 22): DayData("patatras", "patatras", Genre.MALE),
    (6, 23): DayData("alambic", "alambics", Genre.MALE),
    (6, 24): DayData("billevesée", "billevesées", Genre.FEMALE),
    (6, 25): DayData("rigolboche", "rigolboches", Genre.FEMALE),
    (6, 26): DayData("turlupin", "turlupins", Genre.MALE),
    (6, 27): DayData("turlurette", "turlurettes", Genre.FEMALE),
    (6, 28): DayData("guignol", "guignols", Genre.MALE),
    (6, 29): DayData("bille-molle", "billes-molles", Genre.FEMALE),
    (6, 30): DayData("brimborion", "brimborions", Genre.MALE),
    (7, 1): DayData("mirliflore", "mirliflores", Genre.FEMALE),
    (7, 2): DayData("clapiotte", "clapiottes", Genre.FEMALE),
    (7, 3): DayData("gaffophone", "gaffophones", Genre.MALE),
    (7, 4): DayData("légumineur", "légumineurs", Genre.MALE),
    (7, 5): DayData("micro-onduleur", "micro-onduleurs", Genre.MALE),
    (7, 6): DayData("frite-magique", "frites-magiques", Genre.FEMALE),
    (7, 7): DayData(
        "extracteur du potentiel de point zéro",
        "extracteurs du potentiel de point zéro",
        Genre.MALE,
    ),
    (7, 8): DayData("réveil-tartine", "réveils-tartines", Genre.MALE),
    (7, 9): DayData("horloge-moussante", "horloges-moussantes", Genre.FEMALE),
    (7, 10): DayData("canapélicoptère", "canapélicoptères", Genre.MALE),
    (7, 11): DayData("éponge-lumineuse", "éponges-lumineuses", Genre.FEMALE),
    (7, 12): DayData("spatulon", "spatulons", Genre.MALE),
    (7, 13): DayData("vaissellier-volant", "vaisselliers-volants", Genre.MALE),
    (7, 14): DayData("boîte-à-bêtises", "boîtes-à-bêtises", Genre.FEMALE),
    (7, 15): DayData("télé-poubelle", "télé-poubelles", Genre.FEMALE),
    (7, 16): DayData("baignoire-parlante", "baignoires-parlantes", Genre.FEMALE),
    (7, 17): DayData("armoire-à-glissade", "armoires-à-glissade", Genre.FEMALE),
    (7, 18): DayData("pierre manale", "pierres manales", Genre.FEMALE),
    (7, 19): DayData(
        "grille-pain de l'espace", "grilles-pains de l'espace", Genre.MALE
    ),
    (7, 20): DayData("robot-raccommodeur", "robots-raccommodeurs", Genre.MALE),
    (7, 21): DayData("fourchette-à-comptine", "fourchettes-à-comptines", Genre.FEMALE),
    (7, 22): DayData("pantoufle-réactive", "pantoufles-réactives", Genre.FEMALE),
    (7, 23): DayData("coussin-péteur", "coussins-péteurs", Genre.MALE),
    (7, 24): DayData("télé-orbitale", "télés-orbitales", Genre.FEMALE),
    (7, 25): DayData("brosse-à-dent sonique", "brosses-à-dent soniques", Genre.FEMALE),
    (7, 26): DayData("couette-intelligente", "couettes-intelligentes", Genre.FEMALE),
    (7, 27): DayData("pyjama-à-histoires", "pyjamas-à-histoires", Genre.MALE),
    (7, 28): DayData("bol-à-mystère", "bols-à-mystère", Genre.MALE),
    (7, 29): DayData("tabouret-téléphone", "tabourets-téléphone", Genre.MALE),
    (7, 30): DayData("miroir-savant", "miroirs-savants", Genre.MALE),
    (7, 31): DayData(
        "tapis-volant d'intérieur", "tapis-volants d'intérieur", Genre.MALE
    ),
    (8, 1): DayData("oreiller-à-musique", "oreillers-à-musique", Genre.MALE),
    (8, 2): DayData(
        "papier-peint interactif", "papiers-peints interactifs", Genre.MALE
    ),
    (8, 3): DayData("xylophone", "xylophones", Genre.MALE),
    (8, 4): DayData("guilloché", "guillochés", Genre.MALE),
    (8, 5): DayData("djembé", "djembés", Genre.MALE),
    (8, 6): DayData("caipirinha", "caipirinhas", Genre.FEMALE),
    (8, 7): DayData("tzatziki", "tzatzikis", Genre.NEUTRAL),
    (8, 8): DayData("karaoke", "karaokes", Genre.MALE),
    (8, 9): DayData("kantele", "kanteles", Genre.FEMALE),
    (8, 10): DayData("haiku", "haikus", Genre.MALE),
    (8, 11): DayData("colchique", "colchiques", Genre.FEMALE),
    (8, 12): DayData("molinillo", "molinillos", Genre.MALE),
    (8, 13): DayData("quokka", "quokkas", Genre.FEMALE),
    (8, 14): DayData("duduk", "duduks", Genre.MALE),
    (8, 15): DayData("balalaïka", "balalaïkas", Genre.FEMALE),
    (8, 16): DayData("fajitas", "fajitas", Genre.FEMALE),
    (8, 17): DayData("bobineau", "bobineaux", Genre.MALE),
    (8, 18): DayData("fjord", "fjords", Genre.MALE),
    (8, 19): DayData("tsampa", "tsampas", Genre.FEMALE),
    (8, 20): DayData("qipao", "qipaos", Genre.FEMALE),
    (8, 21): DayData("boomerang", "boomerangs", Genre.MALE),
    (8, 22): DayData("cachou", "cachous", Genre.MALE),
    (8, 23): DayData("sac à dos", "sacs à dos", Genre.MALE),
    (8, 24): DayData("brosse à dents", "brosses à dents", Genre.FEMALE),
    (8, 25): DayData("lampe de bureau", "lampes de bureau", Genre.FEMALE),
    (8, 26): DayData("tapis de souris", "tapis de souris", Genre.MALE),
    (8, 27): DayData("pot de fleurs", "pots de fleurs", Genre.MALE),
    (8, 28): DayData("brosse à cheveux", "brosses à cheveux", Genre.FEMALE),
    (8, 29): DayData("boucle d'oreille", "boucles d'oreilles", Genre.FEMALE),
    (8, 30): DayData("manette de jeu", "manettes de jeu", Genre.FEMALE),
    (8, 31): DayData("tapis de yoga", "tapis de yoga", Genre.MALE),
    (9, 1): DayData("corde à sauter", "cordes à sauter", Genre.FEMALE),
    (9, 2): DayData("haltère", "haltères", Genre.MALE),
    (9, 3): DayData("trottinette", "trottinettes", Genre.FEMALE),
    (9, 4): DayData("sac de couchage", "sacs de couchage", Genre.MALE),
    (9, 5): DayData("réchaud de camping", "réchauds de camping", Genre.MALE),
    (9, 6): DayData("chaussure de randonnée", "chaussures de randonnée", Genre.FEMALE),
    (9, 7): DayData("taille-crayon", "taille-crayons", Genre.MALE),
    (9, 8): DayData("agrafeuse", "agrafeuses", Genre.FEMALE),
    (9, 9): DayData("aspirateur", "aspirateurs", Genre.MALE),
    (9, 10): DayData("lave-linge", "lave-linges", Genre.MALE),
    (9, 11): DayData("sèche-linge", "sèche-linges", Genre.MALE),
    (9, 12): DayData("machine à coudre", "machines à coudre", Genre.FEMALE),
    (9, 13): DayData("serpillère", "serpillères", Genre.FEMALE),
    (9, 14): DayData("tronçonneuse", "tronçonneuses", Genre.FEMALE),
    (9, 15): DayData("débroussailleuse", "débroussailleuses", Genre.FEMALE),
    (9, 16): DayData("motoculteur", "motoculteurs", Genre.MALE),
    (9, 17): DayData("râteau", "râteaux", Genre.MALE),
    (9, 18): DayData("clé à molette", "clés à molette", Genre.FEMALE),
    (9, 19): DayData("scie circulaire", "scies circulaires", Genre.FEMALE),
    (9, 20): DayData("détecteur de fumée", "détecteurs de fumée", Genre.MALE),
    (9, 21): DayData("caméra de surveillance", "caméras de surveillance", Genre.FEMALE),
    (9, 22): DayData("moustiquaire", "moustiquaires", Genre.FEMALE),
    (9, 23): DayData("brise-vent", "brise-vent", Genre.MALE),
    (9, 24): DayData("balcon", "balcons", Genre.MALE),
    (9, 25): DayData("jardinière", "jardinières", Genre.FEMALE),
    (9, 26): DayData("buisson", "buissons", Genre.MALE),
    (9, 27): DayData("haie", "haies", Genre.FEMALE),
    (9, 28): DayData("système d'irrigation", "systèmes d'irrigation", Genre.MALE),
    (9, 29): DayData("thermomètre", "thermomètres", Genre.MALE),
    (9, 30): DayData("hygromètre", "hygromètres", Genre.MALE),
    (10, 1): DayData("luxmètre", "luxmètres", Genre.MALE),
    (10, 2): DayData("anémomètre", "anémomètres", Genre.MALE),
    (10, 3): DayData("pluviomètre", "pluviomètres", Genre.MALE),
    (10, 4): DayData("baromètre", "baromètres", Genre.MALE),
    (10, 5): DayData("chronomètre", "chronomètres", Genre.MALE),
    (10, 6): DayData("microscope", "microscopes", Genre.MALE),
    (10, 7): DayData("télescope", "télescopes", Genre.MALE),
    (10, 8): DayData("spectroscope", "spectroscopes", Genre.MALE),
    (10, 9): DayData("sac à bière", "sacs à bière", Genre.MALE),
    (10, 10): DayData("ohmmètre", "ohmmètres", Genre.MALE),
    (10, 11): DayData("ampermètre", "ampermètres", Genre.MALE),
    (10, 12): DayData("voltmètre", "voltmètres", Genre.MALE),
    (10, 13): DayData("oscilloscope", "oscilloscopes", Genre.MALE),
    (10, 14): DayData("fréquencemètre", "fréquencemètres", Genre.MALE),
    (10, 15): DayData("analyseur de spectre", "analyseurs de spectre", Genre.MALE),
    (10, 16): DayData("circuit imprimé", "circuits imprimés", Genre.MALE),
    (10, 17): DayData("disjoncteur", "disjoncteurs", Genre.MALE),
    (10, 18): DayData(
        "machine-à-faire-des-trous-dans-les-spaghetti",
        "machines-à-faire-des-trous-dans-les-spaghetti",
        Genre.FEMALE,
    ),
    (10, 19): DayData("morceau de bois", "morceaux de bois", Genre.MALE),
    (10, 20): DayData("pot de colle", "pots de colle", Genre.MALE),
    (10, 21): DayData("paquet cadeau", "paquets cadeaux", Genre.MALE),
    (10, 22): DayData("cacatoès", "cacatoès", Genre.FEMALE),
    (10, 23): DayData("harmonica", "harmonicas", Genre.MALE),
    (10, 24): DayData("bigoudi", "bigoudis", Genre.MALE),
    (10, 25): DayData("dent de lait", "dents de lait", Genre.FEMALE),
    (10, 26): DayData("bonhomme de neige", "bonhommes de neige", Genre.MALE),
    (10, 27): DayData("marteau picoreur", "marteaux picoreurs", Genre.MALE),
    (10, 28): DayData("bande magnétique", "bandes magnétiques", Genre.FEMALE),
    (10, 29): DayData("punaise de lit", "punaises de lit", Genre.FEMALE),
    (10, 30): DayData("carte de voeux", "cartes de voeux", Genre.FEMALE),
    (10, 31): DayData("moins que rien", "moins que rien", Genre.MALE),
    (11, 1): DayData("tour eiffel", "tours eiffel", Genre.FEMALE),
    (11, 2): DayData("symptôme", "symptômes", Genre.MALE),
    (11, 3): DayData("mamanite", "amanites", Genre.FEMALE),
    (11, 4): DayData("cornichon", "cornichons", Genre.MALE),
    (11, 5): DayData("zinzolin", "zinzolins", Genre.MALE),
    (11, 6): DayData("jouet à bascule", "jouets à bascule", Genre.MALE),
    (11, 7): DayData("bloc-notes", "blocs-notes", Genre.MALE),
    (11, 8): DayData("routoir", "routoirs", Genre.MALE),
    (11, 9): DayData("guenille", "guenilles", Genre.FEMALE),
    (11, 10): DayData("lunette de soleil", "lunettes de soleil", Genre.FEMALE),
    (11, 11): DayData("octavin", "octavins", Genre.MALE),
    (11, 12): DayData("toque à trois cornes", "toques à trois cornes", Genre.FEMALE),
    (11, 13): DayData("navire-hôpital", "navires-hôpitaux", Genre.MALE),
    (11, 14): DayData("sesquiplan", "sesquiplans", Genre.MALE),
    (11, 15): DayData("baldaquin", "baldaquins", Genre.MALE),
    (11, 16): DayData("anémoscope", "anémoscopes", Genre.MALE),
    (11, 17): DayData("clavicythérium", "clavicythériums", Genre.MALE),
    (11, 18): DayData(
        "certificat de conformité", "certificats de conformité", Genre.MALE
    ),
    (11, 19): DayData("bonnet de nuit", " bonnets de nuit", Genre.MALE),
    (11, 20): DayData("atmomètre", "atmomètres", Genre.MALE),
    (11, 21): DayData("pnéomètre", "pnéomètres", Genre.MALE),
    (11, 22): DayData("marie-salope", "marie-salopes", Genre.FEMALE),
    (11, 23): DayData("lettre de crédit", "lettres de crédit", Genre.FEMALE),
    (11, 24): DayData("cithare", "cithares", Genre.FEMALE),
    (11, 25): DayData("tramezzino", "tramezzinos", Genre.MALE),
    (11, 26): DayData("ichcahuipilli", "ichcahuipillis", Genre.FEMALE),
    (11, 27): DayData("journal intime", "journaux intimes", Genre.MALE),
    (11, 28): DayData("harpe celtique", "harpes celtiques", Genre.FEMALE),
    (11, 29): DayData("nœud d’agui", "nœuds d’agui", Genre.MALE),
    (11, 30): DayData("cabotière", "cabotières", Genre.FEMALE),
    (12, 1): DayData("pique-œuf", "pique-œufs", Genre.MALE),
    (12, 2): DayData("revue de contrat", "revues de contrats", Genre.FEMALE),
    (12, 3): DayData("grande surface", "grandes surfaces", Genre.FEMALE),
    (12, 4): DayData("manteau de cheminée", "manteaux de cheminées", Genre.MALE),
    (12, 5): DayData("charentaise", "charentaises", Genre.FEMALE),
    (12, 6): DayData("chasse-goupille", "chasse-goupilles", Genre.MALE),
    (12, 7): DayData("chaussure à orteils", "chaussures à orteils", Genre.FEMALE),
    (12, 8): DayData(
        "giroflée à cinq pétales", "giroflées a cinq pétales", Genre.FEMALE
    ),
    (12, 9): DayData("salade de phalanges", "salades de phalanges", Genre.FEMALE),
    (12, 10): DayData("rogntudju", "rogntudju", Genre.MALE),
    (12, 11): DayData("lixiviateuse", "lixiviateuses", Genre.FEMALE),
    (12, 12): DayData("chaise berçante", "chaises berçantes", Genre.FEMALE),
    (12, 13): DayData("chebec", "chebec", Genre.MALE),
    (12, 14): DayData("boulevard circulaire", "boulevards circulaires", Genre.MALE),
    (12, 15): DayData("bande cyclable", "bandes cyclables", Genre.FEMALE),
    (12, 16): DayData("coupe-boulons", "coupe-boulons", Genre.MALE),
    (12, 17): DayData("clé à pipe", "clés à pipes", Genre.FEMALE),
    (12, 18): DayData("ensacheuse", "ensacheuses", Genre.FEMALE),
    (12, 19): DayData("fulguromètre", "fulguromètre", Genre.MALE),
    (12, 20): DayData("diptyque", "diptyques", Genre.MALE),
    (12, 21): DayData("cucurbitacée", "cucurbitacées", Genre.MALE),
    (12, 22): DayData("glassophone", "glassophones", Genre.MALE),
    (12, 23): DayData("métaphore", "métaphores", Genre.FEMALE),
    (12, 24): DayData("pentécontère", "pentécontères", Genre.MALE),
    (12, 25): DayData("prépuce", "prépuces", Genre.MALE),
    (12, 26): DayData("cumulus bourgeonnant", "cumulus bourgeonnants", Genre.MALE),
    (12, 27): DayData("pyréolophore", "pyréolophores", Genre.MALE),
    (12, 28): DayData("soubassophone", "soubassophones", Genre.MALE),
    (12, 29): DayData("béret basque", "bérets basques", Genre.MALE),
    (12, 30): DayData("vocifération sportive", "vociférations sportives", Genre.MALE),
    (12, 31): DayData("armoire à glace", "armoires à glace", Genre.FEMALE),
}


# Output of: cat lola.png | base64
LOLA_PNG_DATA = """\
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\
"""


def get_announce() -> str:
    now = datetime.datetime.now()
    day = now.day
    month = now.month

    try:
        day_name = DAY_NAMES[now.weekday()]
    except KeyError:
        LOGGER.error("Unexpected day of week!")
        exit(1)

    try:
        data = DATA_MAP[(month, day)]
    except KeyError:
        LOGGER.error("Daily data not found!")
        exit(1)

    hallow = data.singular.capitalize()
    hallow_plural = data.plural.capitalize()

    if data.genre == Genre.FEMALE:
        hallow_prefix = "Sainte"
        hallow_all = "toutes"
    else:
        hallow_prefix = "Saint"
        hallow_all = "tous"

    return ANNOUNCE_TEMPLATE.format(
        day=day,
        day_name=day_name,
        hallow_prefix=hallow_prefix,
        hallow=hallow,
        hallow_all=hallow_all,
        hallow_plural=hallow_plural,
    )


def ensure_png_exists() -> None:
    if not Path(LOLA_PNG_PATH).exists():
        png_bytes = base64.b64decode(LOLA_PNG_DATA)
        with open(LOLA_PNG_PATH, "wb") as image_file:
            image_file.write(png_bytes)


def send_notification(announce: str) -> bool:
    """Send desktop notification for the given announce.

    The notification is sent using the command ``notify-send``.

    Return True iff the subprocess call succeeded.
    """
    ensure_png_exists()

    text, summary = announce.splitlines()
    command = [
        "notify-send",
        "--app-name=Annonce de Lola",
        "--urgency=normal",
        f"--icon={LOLA_PNG_PATH}",
        summary,
        text
    ]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            check=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
    except (OSError, FileNotFoundError):
        LOGGER.debug("Is notify-send available?")
        return False
    except subprocess.CalledProcessError as ex:
        LOGGER.debug(f"Subprocess exited with {ex.returncode} status")
        LOGGER.debug(f"Standard output: {ex.stdout}")
        LOGGER.debug(f"Standard error: {ex.stderr}")
        return False
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stdout", help="use standard output", action="store_true")
    args = parser.parse_args()

    announce = get_announce()

    if args.stdout is True:
        print(announce)
    else:
        sent = send_notification(announce)
        exit(0 if sent else 1)
