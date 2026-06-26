import sys
import random
import statistics

import tsp_util as tsp


LAMBDA_VREDNOSTI = [1, 5, 10, 20, 50]  
BUDZET_EVALUACIJA = 100000              
BROJ_POKRETANJA = 30
SNAPSHOT_NA = 500
OSNOVNI_SEED = 1234


def pokreni_lambda(matrica, n, lam, seed):
    random.seed(seed)

    # pocetni roditelj = nasumicna tura
    roditelj = tsp.nasumicna_tura(n)
    duzina_roditelja = tsp.duzina_ture(roditelj, matrica)
    evaluacije = 1

    # najbolje resenje do sada (globalno)
    najbolja_duzina = duzina_roditelja
    najbolja_tura = roditelj[:]

    istorija = [[evaluacije, najbolja_duzina]]
    sledeci_snapshot = evaluacije + SNAPSHOT_NA

    while evaluacije < BUDZET_EVALUACIJA:
        mutacijski_pobednik = None
        duzina_mut_pobednika = None

        for _ in range(lam):
            if evaluacije >= BUDZET_EVALUACIJA:
                break

            dete = tsp.mutacija_inverzija(roditelj)
            d = tsp.duzina_ture(dete, matrica)
            evaluacije += 1

            if duzina_mut_pobednika is None or d < duzina_mut_pobednika:
                duzina_mut_pobednika = d
                mutacijski_pobednik = dete

            if d < najbolja_duzina:
                najbolja_duzina = d
                najbolja_tura = dete[:]

            if evaluacije >= sledeci_snapshot:
                istorija.append([evaluacije, najbolja_duzina])
                sledeci_snapshot += SNAPSHOT_NA
                
        najbolje_ukrsteno = None
        duzina_najboljeg_ukrstenog = None

        if mutacijski_pobednik is not None:
            for _ in range(lam):
                if evaluacije >= BUDZET_EVALUACIJA:
                    break

                dete = tsp.ukrstanje_ox(roditelj, mutacijski_pobednik)
                d = tsp.duzina_ture(dete, matrica)
                evaluacije += 1

                if duzina_najboljeg_ukrstenog is None or d < duzina_najboljeg_ukrstenog:
                    duzina_najboljeg_ukrstenog = d
                    najbolje_ukrsteno = dete

                if d < najbolja_duzina:
                    najbolja_duzina = d
                    najbolja_tura = dete[:]

                if evaluacije >= sledeci_snapshot:
                    istorija.append([evaluacije, najbolja_duzina])
                    sledeci_snapshot += SNAPSHOT_NA


        if najbolje_ukrsteno is not None and duzina_najboljeg_ukrstenog <= duzina_roditelja:
            roditelj = najbolje_ukrsteno
            duzina_roditelja = duzina_najboljeg_ukrstenog

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

    rezultati_po_lambda = []
    for lam in LAMBDA_VREDNOSTI:
        print("--- lambda =", lam, "---")
        pokretanja = []
        for r in range(BROJ_POKRETANJA):
            seed = OSNOVNI_SEED + r
            rez = pokreni_lambda(matrica, n, lam, seed)
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
        rezultati_po_lambda.append({
            "lambda": lam,
            "statistika": statistika,
            "pokretanja": pokretanja,
        })
        print("  statistika:", statistika)

    rezultat = {
        "algoritam": "1+(lambda,lambda)_GA",
        "instanca": instanca["naziv"],
        "dimenzija": n,
        "budzet_evaluacija": BUDZET_EVALUACIJA,
        "broj_pokretanja": BROJ_POKRETANJA,
        "lambda_vrednosti": LAMBDA_VREDNOSTI,
        "rezultati_po_lambda": rezultati_po_lambda,
    }

    izlaz = "rezultati_lambda_" + (instanca["naziv"] if instanca["naziv"] else "instanca") + ".json"
    tsp.sacuvaj_json(rezultat, izlaz)


if __name__ == "__main__":
    main()
