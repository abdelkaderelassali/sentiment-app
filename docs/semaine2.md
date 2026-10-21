# Semaine 2 : Entraînement et évaluation du modèle de sentiment

## Résultats de l'évaluation

Le modèle de classification de sentiment (TF-IDF + Régression Logistique) a été entraîné sur le jeu de données de démonstration de 290 avis.
- **F1 macro sur le jeu de test** : 0.879 (supérieur au seuil exigé de 0.85).
- **Matrice de confusion** : 27 vrais négatifs, 24 vrais positifs, 2 faux positifs et 5 faux négatifs.
- **Total des erreurs** : 7 erreurs sur 58 avis du jeu de test.

## Analyse des erreurs

Toutes les erreurs observées se concentrent sur des avis mitigés et complexes (contenant à la fois des termes positifs et négatifs articulés par des connecteurs comme *sauf que ensuite* ou *au début*).
1. **Pourquoi ces erreurs surviennent** : L'approche par sac de mots (Bag of Words / TF-IDF) compte la présence et la fréquence des mots de manière indépendante. Elle ne prend pas en compte l'ordre des mots dans la phrase, la syntaxe, ni le retournement d'opinion introduit par les conjonctions d'opposition.
2. **Comment les corriger** :
   - À court terme : Ajuster les seuils de décision et introduire une zone d'abstention (statut INDÉTERMINÉ) pour les prédictions où la certitude est faible (prévu au TP4).
   - À moyen terme : Utiliser des modèles de langage contextuels pré-entraînés pour le français (ex. CamemBERT) capables d'appréhender la sémantique globale et les retournements de situation.
