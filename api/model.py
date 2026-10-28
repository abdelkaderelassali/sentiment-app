"""Raccord entre l'API et le paquet de prédiction."""

from typing import TypedDict

from api.schemas import Label
from sentiment_app.predict import SEUIL_ABSTENTION, charger_modele
from sentiment_app.predict import predict as _predict

CORRESPONDANCE: dict[str, Label] = {"positive": "POSITIVE", "negative": "NEGATIVE"}


class Prediction(TypedDict):
    label: Label
    score: float
    text: str


class SentimentClassifier:
    """Enveloppe du modèle avec l'interface attendue par l'API."""

    model_name = "tfidf-logreg (TP2, models/sentiment.joblib)"

    def __init__(self) -> None:
        modele = charger_modele()
        inconnues = {str(c) for c in modele.classes_} - set(CORRESPONDANCE)
        if inconnues:
            raise ValueError(f"classes inconnues du contrat : {sorted(inconnues)}")

    def predict(self, text: str) -> Prediction:
        """Renvoie une étiquette du contrat, ou INDETERMINE sous le seuil."""
        resultat = _predict(text)
        label: Label = (
            "INDETERMINE"
            if resultat["score"] < SEUIL_ABSTENTION
            else CORRESPONDANCE[resultat["label"]]
        )
        return {"label": label, "score": resultat["score"], "text": text[:100]}


def load_model() -> SentimentClassifier:
    """Construit le classifier ; le chargement du fichier est mis en cache."""
    return SentimentClassifier()


