"""Commande en ligne de commande du paquet sentiment-app."""

import argparse

from sentiment_app import __version__
from sentiment_app.predict import SEUIL_ABSTENTION, predict


def main() -> int:
    parser = argparse.ArgumentParser(prog="sentiment", description="Analyse le sentiment d'un avis.")
    parser.add_argument("--version", action="version", version=f"sentiment-app {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)
    prediction = subparsers.add_parser("predict", help="classifier un avis")
    prediction.add_argument("text", nargs="+", help="texte de l'avis")
    subparsers.add_parser("serve", help="lancer l'API FastAPI")
    args = parser.parse_args()

    if args.command == "predict":
        resultat = predict(" ".join(args.text))
        label = "INDETERMINE" if resultat["score"] < SEUIL_ABSTENTION else resultat["label"].upper()
        score = f"{resultat['score']:.4f}".rstrip("0").rstrip(".")
        print(f"{label} {score}")
        return 0

    import uvicorn

    uvicorn.run("api.main:app", host="127.0.0.1", port=8000)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
