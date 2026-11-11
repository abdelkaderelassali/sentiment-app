# TP6 : paquet installable

Le code de prédiction réside dans `sentiment_app.predict`. Le script historique `src/predict.py` reste un pont de compatibilité et l'API importe désormais directement le paquet. Le modèle reste un fichier externe à la roue ; son chemin se configure avec la variable `SENTIMENT_MODELE`.

La commande `sentiment` fournit `--version`, `predict` et `serve`. Le seuil d'abstention est partagé avec l'API : un texte incertain produit `INDETERMINE`. La roue pure Python `sentiment_app-0.6.0-py3-none-any.whl` contient `api`, `sentiment_app` et `ui`, sans inclure les tests, les données ni le modèle.

## Contrôles réalisés

- Installation éditable : `pip install -e .` ; tests : `98 passed, 2 xfailed`.
- Qualité : `ruff check .` et `mypy api` passent.
- CLI locale : `sentiment --version` affiche `sentiment-app 0.6.0` ; le cas positif affiche `POSITIVE 0.777`.
- Compatibilité : `python src/predict.py "Livraison rapide, produit conforme, très satisfait"` affiche `positive (confiance 78%)`.
- Roue : construite et inspectée ; contient `api/`, `sentiment_app/` et `ui/`, sans `tests/`, `data/` ni `models/`.
- Installation hors du dépôt : sans `SENTIMENT_MODELE`, la prédiction échoue avec le code 1 ; avec la variable pointant vers le fichier `.joblib`, elle renvoie `POSITIVE 0.777`.

La publication Git (commit, tag et push) ainsi que la capture d'écran du terminal restent à faire par le binôme.

