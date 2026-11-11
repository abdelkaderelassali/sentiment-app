"""Tests unitaires pour la collecte et generation synthetique de donnees LLM."""
import csv
from pathlib import Path

from src.collect_llm_data import (
    AvisCollecte,
    generer_avis_synthetiques,
    sauvegarder_csv,
)


def test_generer_avis_synthetiques_quantite_et_classes() -> None:
    """Verifie que le generateur respecte la quantite et la diversite des classes."""
    total = 30
    avis = generer_avis_synthetiques(total=total, graine=123)
    assert len(avis) == total

    labels = {a.label for a in avis}
    assert "POSITIVE" in labels
    assert "NEGATIVE" in labels
    assert "INDETERMINE" in labels


def test_structure_avis_et_rationale() -> None:
    """Verifie que chaque avis possede une difficulte, une source et une justification."""
    avis = generer_avis_synthetiques(total=10, graine=42)
    for a in avis:
        assert isinstance(a, AvisCollecte)
        assert len(a.text.strip()) > 5
        assert a.difficulte in {"facile", "difficile"}
        assert a.source == "llm-synthetic"
        assert len(a.rationale.strip()) > 5


def test_sauvegarde_csv(tmp_path: Path) -> None:
    """Verifie la generation correcte du fichier CSV."""
    sortie = tmp_path / "test_reviews.csv"
    avis = generer_avis_synthetiques(total=12, graine=99)
    sauvegarder_csv(avis, sortie)

    assert sortie.is_file()
    with sortie.open(encoding="utf-8") as f:
        lecteur = list(csv.DictReader(f))
        assert len(lecteur) == 12
        assert set(lecteur[0].keys()) == {"text", "label", "difficulte", "source", "rationale"}
