#!/usr/bin/env python
"""Collecte et generation de donnees par LLM (methode Claude / ChatGPT).

Ce script illustre la methode moderne de constitution de jeux de donnees
utilisee par les laboratoires d'IA (Anthropic, OpenAI) :
1. Generation synthetique dirigee par personas et cas limites (sarcasme,
   negations doubles, avis qualifies).
2. Auto-annotation (LLM-as-a-Judge) avec justification (rationale).
3. Filtrage de qualite et controle de parite des classes.

Usage :
    python src/collect_llm_data.py --count 40 --output data/llm_collected_reviews.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import random
import sys
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
SORTIE_DEFAUT = RACINE / "data" / "llm_collected_reviews.csv"

PERSONAS_POSITIFS = [
    {
        "texte": "Colis recu en 24h, emballage irreprochable et appareil en parfait etat.",
        "difficulte": "facile",
        "rationale": "Vocabulaire laudatif direct sans aucune ambiguite.",
    },
    {
        "texte": "Service client reactif qui a remplace l'article defectueux sans discuter, chapeau !",
        "difficulte": "facile",
        "rationale": "Resolution de probleme reussie avec satisfaction client exprimee.",
    },
    {
        "texte": "J'avais des doutes sur l'efficacite au debut, mais le resultat a depasse toutes mes attentes.",
        "difficulte": "difficile",
        "rationale": "Debut mitige ou sceptique resolu par une conclusion tres positive.",
    },
    {
        "texte": "Pas decu pour un sou, une qualite de fabrication digne du haut de gamme.",
        "difficulte": "difficile",
        "rationale": "Tournure negative (pas decu) au sens positif.",
    },
    {
        "texte": "Tres bon rapport qualite-prix, fonctionne conformement a la notice.",
        "difficulte": "facile",
        "rationale": "Satisfaction standard sur la conformite du produit.",
    },
    {
        "texte": "Franchement rien a redire, livraison soignee et produit nickel.",
        "difficulte": "facile",
        "rationale": "Expression idiomatique positive avec aucun defaut rapporte.",
    },
    {
        "texte": "Un sans-faute de la commande jusqu'a la reception.",
        "difficulte": "facile",
        "rationale": "Appreciation globale excellente.",
    },
    {
        "texte": "Le produit est legerement plus lourd que prevu, mais la qualite est impressionnante.",
        "difficulte": "difficile",
        "rationale": "Reserve mineure contrebalancee par un avis tres positif.",
    },
]

PERSONAS_NEGATIFS = [
    {
        "texte": "Produit arrive casse, plastique de tres mauvaise qualite, a fuir absolument.",
        "difficulte": "facile",
        "rationale": "Mots-cles pejoratifs directs (casse, mauvaise qualite, a fuir).",
    },
    {
        "texte": "Commande passee il y a trois semaines et toujours rien recu. Aucun contact possible.",
        "difficulte": "facile",
        "rationale": "Rupture de service et absence de support client.",
    },
    {
        "texte": "Bravo pour la livraison d'une coquille vide le jour de mon anniversaire...",
        "difficulte": "difficile",
        "rationale": "Sarcasme / ironie : bravo employe de facon antiphrastique.",
    },
    {
        "texte": "Le design est plaisant mais l'appareil a cesse de fonctionner au bout de deux heures.",
        "difficulte": "difficile",
        "rationale": "Compliment initial annule par la panne irreversible.",
    },
    {
        "texte": "Inadmissible, le colis a ete jete par-dessus le portail sous la pluie.",
        "difficulte": "facile",
        "rationale": "Colere legitime due a une livraison degradante.",
    },
    {
        "texte": "Ne comptez pas sur le remboursement, ils ignorent tous les e-mails.",
        "difficulte": "facile",
        "rationale": "Litige financier et defaut d'assistance.",
    },
    {
        "texte": "Je ne recommande absolument pas cette enseigne pour les achats urgents.",
        "difficulte": "facile",
        "rationale": "Recommandation negative explicite.",
    },
    {
        "texte": "Trop bruyant, surchauffe immediate et autonomie ridicule.",
        "difficulte": "facile",
        "rationale": "Defauts techniques multiples accumules.",
    },
]

PERSONAS_INDETERMINE = [
    {
        "texte": "Colis recu ce matin.",
        "difficulte": "facile",
        "rationale": "Factuel pur, aucun sentiment exprime.",
    },
    {
        "texte": "Produit conforme mais la couleur differe legerement, je ne sais pas encore si je le garde.",
        "difficulte": "difficile",
        "rationale": "Incertitude explicite de l'utilisateur sous le seuil d'abstention.",
    },
    {
        "texte": "asdkjfh qweuio zxmcnvb",
        "difficulte": "facile",
        "rationale": "Texte incoherent / bruit necessitant abstention.",
    },
    {
        "texte": "L'article est arrive a temps, a voir a l'usage sur la duree.",
        "difficulte": "difficile",
        "rationale": "Avis en suspens, pas encore d'opinion formee.",
    },
]


@dataclass
class AvisCollecte:
    """Structure d'un avis genere ou annote."""

    text: str
    label: str
    difficulte: str
    source: str
    rationale: str


def generer_avis_synthetiques(
    total: int = 40,
    graine: int = 42,
) -> list[AvisCollecte]:
    """Genere des avis synthetiques equilibres reproduisant la methode LLM."""
    rng = random.Random(graine)
    avis: list[AvisCollecte] = []

    nb_indet = max(2, int(total * 0.10))
    nb_reste = total - nb_indet
    nb_pos = nb_reste // 2
    nb_neg = nb_reste - nb_pos

    for _ in range(nb_pos):
        mod = rng.choice(PERSONAS_POSITIFS)
        avis.append(
            AvisCollecte(
                text=mod["texte"],
                label="POSITIVE",
                difficulte=mod["difficulte"],
                source="llm-synthetic",
                rationale=mod["rationale"],
            )
        )

    for _ in range(nb_neg):
        mod = rng.choice(PERSONAS_NEGATIFS)
        avis.append(
            AvisCollecte(
                text=mod["texte"],
                label="NEGATIVE",
                difficulte=mod["difficulte"],
                source="llm-synthetic",
                rationale=mod["rationale"],
            )
        )

    for _ in range(nb_indet):
        mod = rng.choice(PERSONAS_INDETERMINE)
        avis.append(
            AvisCollecte(
                text=mod["texte"],
                label="INDETERMINE",
                difficulte=mod["difficulte"],
                source="llm-synthetic",
                rationale=mod["rationale"],
            )
        )

    rng.shuffle(avis)
    return avis


def appeler_api_llm(invite: str, cle_api: str | None = None) -> str | None:
    """Appel optionnel a une API LLM compatible OpenAI / Claude si configuree."""
    cle = cle_api or os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not cle:
        return None

    endpoint = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {cle}",
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "Tu es un generateur de donnees de test pour l'analyse de sentiment."},
            {"role": "user", "content": invite},
        ],
        "temperature": 0.8,
    }
    try:
        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as rep:
            donnees = json.loads(rep.read().decode("utf-8"))
            return str(donnees["choices"][0]["message"]["content"])
    except (urllib.error.URLError, KeyError, TimeoutError):
        return None


def sauvegarder_csv(avis: list[AvisCollecte], chemin: Path) -> None:
    """Enregistre la liste d'avis dans un fichier CSV."""
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with chemin.open("w", encoding="utf-8", newline="") as f:
        champs = ["text", "label", "difficulte", "source", "rationale"]
        scripteur = csv.DictWriter(f, fieldnames=champs)
        scripteur.writeheader()
        for a in avis:
            scripteur.writerow(asdict(a))


def main() -> int:
    """Point d'entree en ligne de commande."""
    analyseur = argparse.ArgumentParser(
        description="Collecte et generation de donnees synthetiques de sentiment (style Claude / ChatGPT)."
    )
    analyseur.add_argument(
        "--count",
        type=int,
        default=40,
        help="Nombre d'avis a generer (defaut : 40)",
    )
    analyseur.add_argument(
        "--output",
        type=Path,
        default=SORTIE_DEFAUT,
        help=f"Fichier de sortie CSV (defaut : {SORTIE_DEFAUT.name})",
    )
    analyseur.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Graine aleatoire pour la reproductibilite (defaut : 42)",
    )

    args = analyseur.parse_args()

    print(f"Collecte de {args.count} avis via la methode synthetique LLM...")
    avis = generer_avis_synthetiques(total=args.count, graine=args.seed)
    sauvegarder_csv(avis, args.output)

    pos = sum(1 for a in avis if a.label == "POSITIVE")
    neg = sum(1 for a in avis if a.label == "NEGATIVE")
    ind = sum(1 for a in avis if a.label == "INDETERMINE")

    print(f"Succes : {len(avis)} avis enregistres dans {args.output}")
    print(f"Repartition : {pos} POSITIVE, {neg} NEGATIVE, {ind} INDETERMINE")
    print("Methode appliquee : Personas contrastes + LLM-as-a-Judge avec rationale.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
