"""Contrats d'entrée et de sortie de l'API (Pydantic v2)."""
from typing import Literal

from pydantic import BaseModel, Field, field_validator

# Les trois seules valeurs que l'API peut renvoyer : le contrat, écrit dans un type
Label = Literal["POSITIVE", "NEGATIVE", "INDETERMINE"]


class PredictRequest(BaseModel):
    """Requête de prédiction."""
    text: str = Field(..., min_length=1, max_length=2000, description="Texte à classifier",
                      examples=["Livraison rapide, produit conforme, très satisfait"])

    @field_validator("text")
    @classmethod
    def refuser_texte_blanc(cls, valeur: str) -> str:
        """Même règle que predict() de src/predict.py : un texte vide une fois ses blancs retirés est refusé."""
        if not valeur.strip():
            raise ValueError("texte vide une fois les blancs retirés")
        return valeur


class PredictResponse(BaseModel):
    """Réponse de prédiction."""
    label: Label = Field(..., description="POSITIVE, NEGATIVE, ou INDETERMINE sous le seuil d'abstention")
    score: float = Field(..., ge=0, le=1, description="Confiance de la classe prédite")
    text: str = Field(..., description="Aperçu du texte analysé (100 caractères)")


class HealthResponse(BaseModel):
    """Réponse de l'endpoint de santé."""
    status: str = Field(..., description="OK si le modèle est chargé")
    model: str = Field(..., description="Nom du modèle servi")


class ErrorResponse(BaseModel):
    """Format standard des erreurs FastAPI (routes sans version)."""
    detail: str


class ChampInvalide(BaseModel):
    champ: str = Field(..., description="Chemin du champ refusé, par exemple body.text")
    message: str


class DetailErreur(BaseModel):
    code: str = Field(..., description="Code stable, à tester côté client : ENTREE_INVALIDE, NON_AUTHENTIFIE...")
    message: str = Field(..., description="Message lisible, susceptible de changer")
    champs: list[ChampInvalide] = Field(default_factory=list)


class ErreurV1(BaseModel):
    """Format unique de toutes les erreurs de /v1."""
    erreur: DetailErreur


class ModeleResponse(BaseModel):
    """Réponse de GET /v1/modele (rôle admin)."""
    model: str
    seuil_abstention: float
    metriques: dict = Field(default_factory=dict, description="Contenu de models/metrics.json")
