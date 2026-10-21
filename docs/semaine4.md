# Semaine 4 : tests approfondis et qualité, notes du binôme

## 1. Couverture

- **Avant (étape A)** : 91 % sur le package pi/ (69 instructions, 6 manquantes dans pi/main.py : lignes 49, 77-79, 85-87).
- **Pour chacune, le comportement qu'aucun test ne vérifiait** :
  - Ligne 49 : Le cas où le modèle n'est pas chargé dans pp.state (réponse 503).
  - Lignes 77-79 : La gestion d'une exception imprévue du classifieur dans predict (réponse 500 interne).
  - Lignes 85-87 : Le bloc de démarrage direct if __name__ == '__main__': uvicorn.run(...).
- **Après (étape D)** : 100 % de couverture sur l'ensemble des modules d'API (pi/main.py, pi/model.py, pi/schemas.py). Lignes exclues de la mesure et pourquoi : les 2 lignes du bloc if __name__ == '__main__': ont été annotées avec # pragma: no cover, car ce bloc n'est destiné qu'à un lancement manuel de développement et n'a pas vocation à être appelé lors de la suite de tests automatisés pilotée par TestClient.

## 2. Défauts trouvés

| Symptôme | Test qui l'a révélé | Correction |
| --- | --- | --- |
| Corps fait d'espaces seuls ({'text': '   '}) ou espaces typographiques renvoyant un 422 avec corps non standard (texte brut) | 	ests/test_limites.py (	est_frontieres_du_contrat et propriété Hypothesis) | Ajout d'un ield_validator Pydantic v2 sur le champ 	ext appliquant la règle str.strip() identique au modèle. |
| Panne interne du modèle (ValueError('bug interne')) renvoyant un statut HTTP 422 avec fuite du message technique au client | 	ests/test_integration.py (	est_modele_en_panne_repond_500) | Suppression de l'interception de ValueError dans pi/main.py ; toute panne lève une HTTPException(500, 'Erreur interne du serveur') from None avec log serveur. |
| Modèle réentraîné sur des classes imprévues cassant silencieusement le contrat de sortie | 	ests/test_integration.py (	est_classes_inconnues_l_api_refuse_de_demarrer) | Vérification stricte des classes du modèle lors de l'initialisation de SentimentClassifier par rapport à CORRESPONDANCE. |
| Texte sans mot connu recevant arbitrairement NEGATIVE avec confiance faible (0.5162) | Essai T24 / ilan_jeu_or.py | Introduction de la règle d'abstention : étiquette INDETERMINE dès que la confiance est inférieure à SEUIL_ABSTENTION = 0.60. |

## 3. Seuil d'abstention

- **Points de la courbe (python src/courbe_seuil.py)** :
  - Seuil 0.50 : 58 avis répondus (100 %), exactitude 0.879, 7 erreurs, 0 renvoyé vers un humain.
  - Seuil 0.60 : 42 avis répondus (72 %), exactitude 0.952, 2 erreurs, 16 renvoyés vers un humain.
  - Seuil 0.70 : 37 avis répondus (64 %), exactitude 1.000, 0 erreur, 21 renvoyés vers un humain.
- **Seuil retenu** : 0.60. Part des avis envoyés à un humain : 28 % (16 avis sur 58). Justification : Ce seuil élimine plus de 70 % des erreurs initiales (les erreurs passent de 7 à 2) tout en automatisant le traitement pour près de trois quarts des requêtes (72 %). Le passage à 0.70 éliminerait certes les 2 erreurs restantes mais augmenterait de 31 % le volume de révision humaine.

## 4. Jeu d'or

- **Bilan (python src/bilan_jeu_or.py)** : 15 justes, 3 abstentions (INDETERMINE), 2 erreurs franches déclarées en xfail(strict=True).
- **Ce que ces chiffres disent du modèle** : Le modèle est performant sur les avis formulés de manière directe. En revanche, il est structurellement limité par son architecture par sac de mots : il est aveugle à la négation (« Je ne recommande pas » classé positif à cause du mot « recommande ») et n'a pas le vocabulaire pour traiter les avis hors domaine (critique de film). L'abstention joue efficacement son rôle de garde-fou sur les avis ambigus.

## 5. Outils statiques

- **Remarques au départ** : ruff a signalé 11 remarques (variables l ambiguës E741 dans les tests TP1, imports non triés I001, imports inutilisés F401, appels zip sans strict=True B905, chaînage d'exceptions B904). mypy indiquait Success dès le départ.
- **Parmi les défauts de la partie 2, combien ruff et mypy avaient-ils signalés ?** Aucun des 4 défauts réels n'a été détecté par ces outils au départ. mypy ne voyait rien car predict() renvoyait un simple dictionnaire non typé (dict), et ruff ne fait que de l'analyse lexicale/syntaxique. Ce n'est qu'après avoir annoté avec des TypedDict et Literal que mypy a pu garantir le respect du contrat.
- **Conclusion** : L'analyse statique est une hygiène de code essentielle mais insuffisante à elle seule ; elle vient épauler la conception des tests sans jamais pouvoir se substituer aux tests fonctionnels, aux tests aux limites et aux tests d'intégration.
