"""Prédiction unitaire : le moteur partagé par l'API et la commande CLI."""

import os
from functools import lru_cache
from pathlib import Path
from typing import TypedDict

import joblib

MODELE = Path(__file__).resolve().parents[1] / "models" / "sentiment.joblib"
SEUIL_ABSTENTION = 0.60


class Resultat(TypedDict):
    """Résultat d'une prédiction."""

    label: str
    score: float


@lru_cache(maxsize=1)
def charger_modele():
    """Charge le modèle une seule fois, depuis SENTIMENT_MODELE ou le dépôt."""
    chemin = Path(os.environ.get("SENTIMENT_MODELE", str(MODELE)))
    if not chemin.exists():
        raise FileNotFoundError(
            f"Modèle introuvable : {chemin}. Définissez SENTIMENT_MODELE vers sentiment.joblib."
        )
    return joblib.load(chemin)


def predict(texte: str) -> Resultat:
    """Renvoie l'étiquette positive/négative et la confiance maximale."""
    if not isinstance(texte, str) or not texte.strip():
        raise ValueError("texte vide")
    pipeline = charger_modele()
    etiquette = pipeline.predict([texte])[0]
    score = float(pipeline.predict_proba([texte]).max())
    return {"label": str(etiquette), "score": round(score, 4)}


def main() -> int:
    """Point d'entrée de compatibilité pour `python -m sentiment_app.predict`."""
    import sys

    if len(sys.argv) < 2:
        print('Usage : python -m sentiment_app.predict "votre avis"')
        return 2
    resultat = predict(" ".join(sys.argv[1:]))
    print(f"{resultat['label']} (confiance {resultat['score']:.0%})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

