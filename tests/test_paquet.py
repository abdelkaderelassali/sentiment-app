"""Tests du paquet INSTALLÉ : lancés hors du dossier source, ils échouent si la roue est incomplète."""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

# Ces tests visent le paquet INSTALLÉ. Dans le dépôt, l'API ajoute src/ au chemin d'import :
# sentiment_app y serait trouvé dans les sources, ce qui ne prouve rien. On les ignore donc,
# sauf quand scripts/verifier_livrable.py les lance (VERIFICATION_LIVRABLE=1) : là, ils doivent passer.
_spec = importlib.util.find_spec("sentiment_app")
if not (_spec and "site-packages" in (_spec.origin or "")) and not os.environ.get("VERIFICATION_LIVRABLE"):
    pytest.skip("paquet non installé : python scripts/verifier_livrable.py", allow_module_level=True)

import sentiment_app  # noqa: E402

# La commande est installée à côté de l'interpréteur qui lance les tests (bin/ sous Linux, Scripts sous Windows).
# On ne compte pas sur le PATH : il dépend de l'activation de l'environnement.
COMMANDE = shutil.which("sentiment", path=str(Path(sys.executable).parent))


def test_importe_depuis_le_paquet_installe():
    assert "site-packages" in sentiment_app.__file__, "le test lit les sources, pas la roue installée"


def test_version_lue_dans_les_metadonnees():
    assert sentiment_app.__version__ == "1.0.0"


def test_modele_embarque_dans_la_roue():
    assert sentiment_app.predict("Livraison rapide, produit conforme, très satisfait")["label"] == "positive"


def test_texte_vide_refuse():
    with pytest.raises(ValueError):
        sentiment_app.predict("   ")


def test_commande_installee():
    assert COMMANDE, "commande sentiment introuvable à côté de l'interpréteur"
    sortie = subprocess.run([COMMANDE, "--json", "Produit cassé et service injoignable, à fuir"],
                            capture_output=True, text=True, check=True).stdout
    assert json.loads(sortie)["label"] == "negative"


def test_commande_code_retour_sur_erreur():
    assert COMMANDE, "commande sentiment introuvable à côté de l'interpréteur"
    assert subprocess.run([COMMANDE, " "], capture_output=True, check=False).returncode == 2
