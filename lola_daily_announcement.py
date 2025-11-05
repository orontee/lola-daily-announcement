#!/usr/bin/env python3

"""Perpetuation of Lola's daily announcement for the holy object.

A desktop notification is sent unless ``notify-send`` program is not
found or called with ``--stdout`` argument.

"""

from dataclasses import dataclass
from enum import Enum
import argparse
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


def send_notification(announce: str) -> bool:
    """Send desktop notification for the given announce.

    The notification is sent using the command ``notify-send``.

    Return True iff the subprocess call succeeded.
    """
    text, summary = announce.splitlines()
    command = [
        "notify-send",
        "--app-name=Annonce de Lola",
        "--urgency=normal",
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
