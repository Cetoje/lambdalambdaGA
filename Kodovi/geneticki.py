import sys
import random
import statistics

import tsp_util as tsp

VELICINA_POPULACIJE = 100
VEROVATNOCA_UKRSTANJA = 0.9      # pc
VEROVATNOCA_MUTACIJE = 0.2       # pm (po detetu)
VELICINA_TURNIRA = 3             # k za turnirsku selekciju
BROJ_ELITA = 1                   # koliko najboljih ide direktno u sledecu generaciju
BUDZET_EVALUACIJA = 100000       # ukupan broj racunanja funkcije cilja
BROJ_POKRETANJA = 10             # nezavisnih pokretanja (zbog statistike)
SNAPSHOT_NA = 500                # na svakih koliko evaluacija pamtimo najbolju duzinu
OSNOVNI_SEED = 1234              # baza za seed-ove (reproduktivnost)


def turnirska_selekcija(populacija, duzine, k):
    najbolji = random.randrange(len(populacija))
    for _ in range(k - 1):
        kandidat = random.randrange(len(populacija))
        if duzine[kandidat] < duzine[najbolji]:
            najbolji = kandidat
    return populacija[najbolji][:]  # vracamo kopiju


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


def pokreni_ga(matrica, n, seed):
    random.seed(seed)

    populacija = [tsp.nasumicna_tura(n) for _ in range(VELICINA_POPULACIJE)]
    duzine = [tsp.duzina_ture(j, matrica) for j in populacija]
    evaluacije = VELICINA_POPULACIJE

    najbolji = min(range(len(duzine)), key=lambda i: duzine[i])
    najbolja_duzina = duzine[najbolji]
    najbolja_tura = populacija[najbolji][:]

    istorija = [[evaluacije, najbolja_duzina]]
    sledeci_snapshot = evaluacije + SNAPSHOT_NA

    while evaluacije < BUDZET_EVALUACIJA:
        poredak = sorted(range(len(populacija)), key=lambda i: duzine[i])
        nova_populacija = [populacija[poredak[i]][:] for i in range(BROJ_ELITA)]
        nove_duzine = [duzine[poredak[i]] for i in range(BROJ_ELITA)]

        while len(nova_populacija) < VELICINA_POPULACIJE and evaluacije < BUDZET_EVALUACIJA:
            roditelj1 = turnirska_selekcija(populacija, duzine, VELICINA_TURNIRA)
            roditelj2 = turnirska_selekcija(populacija, duzine, VELICINA_TURNIRA)

            if random.random() < VEROVATNOCA_UKRSTANJA:
                dete = ukrstanje_ox(roditelj1, roditelj2)
            else:
                dete = roditelj1[:]

            if random.random() < VEROVATNOCA_MUTACIJE:
                dete = tsp.mutacija_inverzija(dete)

            d = tsp.duzina_ture(dete, matrica)
            evaluacije += 1

            nova_populacija.append(dete)
            nove_duzine.append(d)

            if d < najbolja_duzina:
                najbolja_duzina = d
                najbolja_tura = dete[:]

            if evaluacije >= sledeci_snapshot:
                istorija.append([evaluacije, najbolja_duzina])
                sledeci_snapshot += SNAPSHOT_NA

        populacija = nova_populacija
        duzine = nove_duzine

    istorija.append([evaluacije, najbolja_duzina])

    return {
        "seed": seed,
        "najbolja_duzina": najbolja_duzina,
        "najbolja_tura": najbolja_tura,
        "evaluacije": evaluacije,
        "istorija": istorija,
    }


def main():
    putanja = sys.argv[1]

    instanca = tsp.ucitaj_tsplib(putanja)
    n = instanca["dimenzija"]
    matrica = tsp.napravi_matricu_rastojanja(instanca["koordinate"])
    print("Instanca:", instanca["naziv"], "| broj gradova:", n)
    print("Budzet evaluacija po pokretanju:", BUDZET_EVALUACIJA)

    pokretanja = []
    for r in range(BROJ_POKRETANJA):
        seed = OSNOVNI_SEED + r
        rez = pokreni_ga(matrica, n, seed)
        gap = tsp.odstupanje_od_optimuma(instanca["naziv"], rez["najbolja_duzina"])
        if gap is not None:
            rez["odstupanje_od_optimuma_%"] = round(gap, 2)
        pokretanja.append(rez)
        print("  pokretanje %d/%d -> najbolja duzina: %d %s"
              % (r + 1, BROJ_POKRETANJA, rez["najbolja_duzina"],
                 ("(gap %.2f%%)" % gap) if gap is not None else ""))

    najbolje_duzine = [p["najbolja_duzina"] for p in pokretanja]
    statistika = {
        "najbolje": min(najbolje_duzine),
        "najgore": max(najbolje_duzine),
        "prosek": round(statistics.mean(najbolje_duzine), 2),
        "std": round(statistics.stdev(najbolje_duzine), 2) if len(najbolje_duzine) > 1 else 0.0,
    }

    rezultat = {
        "algoritam": "obicni_GA",
        "instanca": instanca["naziv"],
        "dimenzija": n,
        "budzet_evaluacija": BUDZET_EVALUACIJA,
        "parametri": {
            "velicina_populacije": VELICINA_POPULACIJE,
            "verovatnoca_ukrstanja": VEROVATNOCA_UKRSTANJA,
            "verovatnoca_mutacije": VEROVATNOCA_MUTACIJE,
            "velicina_turnira": VELICINA_TURNIRA,
            "broj_elita": BROJ_ELITA,
        },
        "broj_pokretanja": BROJ_POKRETANJA,
        "statistika": statistika,
        "pokretanja": pokretanja,
    }

    izlaz = "rezultati_GA_" + (instanca["naziv"] if instanca["naziv"] else "instanca") + ".json"
    tsp.sacuvaj_json(rezultat, izlaz)
    print("Statistika (preko svih pokretanja):", statistika)


if __name__ == "__main__":
    main()
