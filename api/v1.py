"""Version 1 de l'API (TP 2) : mêmes prédictions, contrat versionné et protégé.

    GET  /v1/health   public           état du service
    POST /v1/predict  client ou admin  classer un avis
    GET  /v1/modele   admin            seuil et métriques du modèle servi

Toute évolution qui casserait un client existant (renommer un champ, changer une étiquette)
ira dans /v2 ; /v1 reste tel quel tant qu'un client l'utilise.
"""
import json
import logging
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from api.model import SEUIL_ABSTENTION, Prediction, SentimentClassifier
from api.schemas import (
    ErreurV1,
    HealthResponse,
    ModeleResponse,
    PredictRequest,
    PredictResponse,
)
from api.securite import exiger

logger = logging.getLogger("sentiment_api")
METRIQUES = Path(__file__).resolve().parents[1] / "models" / "metrics.json"

# Les erreurs possibles, déclarées pour que /docs les montre avec leur format
ERREURS: dict[int | str, dict] = {code: {"model": ErreurV1} for code in (401, 403, 422, 500, 503)}

router = APIRouter(prefix="/v1", tags=["v1"], responses=ERREURS)


def classifier(request: Request) -> SentimentClassifier:
    clf: SentimentClassifier | None = getattr(request.app.state, "classifier", None)
    if clf is None:
        raise HTTPException(503, "Modèle non chargé")
    return clf


# Le classifier, injecté par FastAPI dans chaque route qui le demande
Classifier = Annotated[SentimentClassifier, Depends(classifier)]


@router.get("/health", response_model=HealthResponse, summary="Santé (public)")
def sante(clf: Classifier) -> dict[str, str]:
    return {"status": "OK", "model": clf.model_name}


@router.post("/predict", response_model=PredictResponse, summary="Classer un avis (client, admin)",
             dependencies=[Depends(exiger("client", "admin"))])
def predire(corps: PredictRequest, clf: Classifier) -> Prediction:
    try:
        resultat = clf.predict(corps.text)
    except Exception:
        logger.exception("Erreur lors de la prédiction")
        raise HTTPException(500, "Erreur interne du serveur") from None
    # on journalise le verdict, pas le texte : un avis peut contenir des données personnelles
    logger.info("v1 predict -> %s (%.2f)", resultat["label"], resultat["score"])
    return resultat


@router.get("/modele", response_model=ModeleResponse, summary="Métriques du modèle (admin)",
            dependencies=[Depends(exiger("admin"))])
def modele(clf: Classifier) -> dict:
    metriques = json.loads(METRIQUES.read_text(encoding="utf-8")) if METRIQUES.exists() else {}
    return {"model": clf.model_name, "seuil_abstention": SEUIL_ABSTENTION, "metriques": metriques}
