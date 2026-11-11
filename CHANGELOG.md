# Journal des versions

Ce fichier suit la convention « majeure.mineure.correctif » : un changement incompatible
(fonction renommée, étiquette changée) augmente le premier chiffre.

## [1.0.0] - 2026-11-09

### Ajouté
- Fonction `predict(texte)` : renvoie `{"label": "positive" | "negative", "score": float}`.
- Commande `sentiment "texte"`, options `--json` et `--version` ; code de retour 2 sur un texte vide.
- Modèle de démonstration (TF-IDF et régression logistique, F1 macro 0,879) embarqué dans la roue.

### Limites connues
- Modèle entraîné sur 290 avis : sensible aux avis mitigés ; à utiliser avec un seuil d'abstention.
- Le modèle n'est garanti qu'avec scikit-learn 1.5 (dépendance figée).
