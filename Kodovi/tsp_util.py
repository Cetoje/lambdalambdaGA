import math
import json
import random

# Poznati optimumi za instance koje koristimo 

POZNATI_OPTIMUMI = {
    "st70": 675,
    "kroA100": 21282,
    "kroB150" : 26130,
    "a280": 2579,
}


def ucitaj_tsplib(putanja):

    naziv = ""
    dimenzija = 0
    koordinate = []
    citaj_koordinate = False

    with open(putanja, "r") as f:
        for linija in f:
            linija = linija.strip()
            if linija == "":
                continue
            gornje = linija.upper()

            if gornje.startswith("NAME"):
                naziv = linija.split(":")[1].strip()
            elif gornje.startswith("DIMENSION"):
                dimenzija = int(linija.split(":")[1].strip())
            elif gornje.startswith("NODE_COORD_SECTION"):
                citaj_koordinate = True
            elif gornje.startswith("EOF"):
                break
            elif citaj_koordinate:
                delovi = linija.split()
                # red izgleda ovako:  indeks  x  y
                if len(delovi) >= 3:
                    x = float(delovi[1])
                    y = float(delovi[2])
                    koordinate.append((x, y))

    return {
        "naziv": naziv,
        "dimenzija": dimenzija if dimenzija > 0 else len(koordinate),
        "koordinate": koordinate,
    }


def napravi_matricu_rastojanja(koordinate):
    
    n = len(koordinate)
    matrica = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            dx = koordinate[i][0] - koordinate[j][0]
            dy = koordinate[i][1] - koordinate[j][1]
            d = int(math.sqrt(dx * dx + dy * dy) + 0.5)
            matrica[i][j] = d
            matrica[j][i] = d
    return matrica


def duzina_ture(tura, matrica):
    
    ukupno = 0
    n = len(tura)
    for i in range(n):
        ukupno += matrica[tura[i]][tura[(i + 1) % n]]
    return ukupno


def nasumicna_tura(n):

    tura = list(range(n))
    random.shuffle(tura)
    return tura


def mutacija_inverzija(tura):
   
    nova = tura[:]  # kopija
    n = len(nova)
    i = random.randint(0, n - 1)
    j = random.randint(0, n - 1)
    if i > j:
        i, j = j, i
    nova[i:j + 1] = reversed(nova[i:j + 1])
    return nova


def ukrstanje_ox(roditelj1, roditelj2):
    
    n = len(roditelj1)
    a = random.randint(0, n - 1)
    b = random.randint(0, n - 1)
    if a > b:
        a, b = b, a

    dete = [None] * n
    for i in range(a, b + 1):
        dete[i] = roditelj1[i]

    vec_uzeti = set(dete[a:b + 1])
    redosled = []
    for k in range(n):
        grad = roditelj2[(b + 1 + k) % n]
        if grad not in vec_uzeti:
            redosled.append(grad)

    indeks = 0
    for k in range(n):
        poz = (b + 1 + k) % n
        if dete[poz] is None:
            dete[poz] = redosled[indeks]
            indeks += 1
    return dete


def odstupanje_od_optimuma(naziv_instance, duzina):
   
    if naziv_instance in POZNATI_OPTIMUMI:
        opt = POZNATI_OPTIMUMI[naziv_instance]
        return 100.0 * (duzina - opt) / opt
    return None


def sacuvaj_json(podaci, putanja):
    """Snima rezultate u JSON fajl u citljivom formatu."""
    with open(putanja, "w") as f:
        json.dump(podaci, f, indent=2, ensure_ascii=False)
    print("Rezultati sacuvani u:", putanja)
