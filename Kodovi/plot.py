import sys, json, os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REZULTATI_DIR = os.path.join(BASE_DIR, "Rezultati")

OPTIMUMI = {
    "st70": 675,
    "kroA100": 21282,
    "a280": 2579,
    "kroB150": 26130,
}

BOJE = ["#e41a1c", "#ff7f00", "#984ea3", "#377eb8", "#4daf4a", "#f781bf"]


def prosecna_kriva(pokretanja):
    x = [t[0] for t in pokretanja[0]["istorija"]]
    y = np.mean([[t[1] for t in p["istorija"]] for p in pokretanja], axis=0)
    return x, y


def snimi(fig, ime):
    put = os.path.join(REZULTATI_DIR, ime + ".png")
    fig.tight_layout()
    fig.savefig(put, dpi=150, bbox_inches="tight")
    plt.close(fig)


def poredjenje(ga, lam):
    inst = ga["instanca"]
    opt = OPTIMUMI.get(inst)

    fig = plt.figure(figsize=(16, 12))
    fig.suptitle(f"GA vs (1+lambda) - {inst}", fontsize=14, fontweight="bold")
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.3)

    ax = fig.add_subplot(gs[0, :])
    x, y = prosecna_kriva(ga["pokretanja"])
    ax.plot(x, y, color="black", linewidth=2.5, label="GA")
    for i, g in enumerate(lam["rezultati_po_lambda"]):
        x, y = prosecna_kriva(g["pokretanja"])
        ax.plot(x, y, color=BOJE[i % len(BOJE)], linewidth=1.8, label=f"(1+{g['lambda']})")
    if opt:
        ax.axhline(opt, color="green", linestyle="--", label=f"Optimum ({opt})", alpha=0.7)
    ax.set_xlabel("Evaluacije")
    ax.set_ylabel("Duzina ture (prosek)")
    ax.legend(fontsize=8)
    ax.grid(True, linestyle="--", alpha=0.5)

    ax = fig.add_subplot(gs[1, 0])
    lambde = [g["lambda"] for g in lam["rezultati_po_lambda"]]
    proseci = [g["statistika"]["prosek"] for g in lam["rezultati_po_lambda"]]
    stdevi = [g["statistika"]["std"] for g in lam["rezultati_po_lambda"]]
    ax.errorbar(lambde, proseci, yerr=stdevi, fmt="o-", color="steelblue",
                markersize=8, capsize=5, ecolor="#999999")
    if opt:
        ax.axhline(opt, color="green", linestyle="--", label=f"Optimum ({opt})", alpha=0.7)
        ax.legend(fontsize=8)
    ax.set_xlabel("lambda")
    ax.set_ylabel("Prosecna duzina +/- std")
    ax.grid(True, linestyle="--", alpha=0.5)

    ax = fig.add_subplot(gs[1, 1])
    podaci = [[r["najbolja_duzina"] for r in ga["pokretanja"]]]
    labele = ["GA"]
    for g in lam["rezultati_po_lambda"]:
        podaci.append([r["najbolja_duzina"] for r in g["pokretanja"]])
        labele.append(f"(1+{g['lambda']})")
    bp = ax.boxplot(podaci, patch_artist=True, medianprops=dict(color="crimson", linewidth=2))
    boje_box = ["#222222"] + BOJE
    for i, patch in enumerate(bp["boxes"]):
        patch.set_facecolor(boje_box[i % len(boje_box)])
        patch.set_alpha(0.6)
    ax.set_xticklabels(labele, fontsize=8)
    ax.set_ylabel("Duzina ture")
    ax.grid(True, axis="y", linestyle="--", alpha=0.5)

    snimi(fig, f"poredjenje_{inst}")


if len(sys.argv) != 3:
    sys.exit(1)

d1 = json.load(open(sys.argv[1]))
d2 = json.load(open(sys.argv[2]))

if d1.get("algoritam") == "obicni_GA":
    poredjenje(d1, d2)
else:
    poredjenje(d2, d1)
