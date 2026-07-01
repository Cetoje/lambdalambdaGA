# Racunarska Inteligencija

Implementacija genetskog algoritma i (1 + λ) genetskog algoritma za problem trgovačkog putnika (TSP).

## 1. Kloniranje repozitorijuma

```bash
git clone https://github.com/Cetoje/lambdalambdaGA.git
cd RacunarskaInteligencija
```

## 2. Virtuelno okruženje i zavisnosti

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 3. Pokretanje algoritama

```bash
python Kodovi/geneticki.py ..Rezultati/st70.tsp
python Kodovi/lambdageneticki.py ../Rezultati/st70.tsp
```

Ovo outputuje:

- Rezultati/rezultati_GA_.json
- Rezultati/rezultati_lambda_.json

## 4. Vizualizacija rezultata

**poređenje GA i (1 + λ) za istu instancu**

```bash
python Kodovi/plot.py ..Rezultati/rezultati_GA_st70.json ..Rezultati/rezultati_lambda_st70.json
```
