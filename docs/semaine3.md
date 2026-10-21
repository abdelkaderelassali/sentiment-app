# Semaine 3 : l'API, notes du binôme

## 1. Pourquoi l'API refuse-t-elle de démarrer sans models/sentiment.joblib, plutôt que de démarrer et de répondre 503 ?

L'API applique le principe « fail-fast » (échouer au plus tôt). L'unique finalité de ce service est de fournir des prédictions à partir du modèle de sentiment. Si le fichier sentiment.joblib est absent au démarrage dans le gestionnaire de cycle de vie (lifespan), laisser le serveur démarrer et consommer des requêtes pour simplement renvoyer des erreurs 503 masquerait un problème majeur de déploiement (artefact manquant, oubli d'exécution de 	rain.py, etc.). 

Refuser de démarrer en levant une exception explicite (FileNotFoundError) permet à l'orchestrateur ou à l'administrateur de détecter immédiatement la défaillance avant que le service ne soit enregistré sur le réseau ou exposé aux clients.

## 2. Un texte vide est refusé deux fois : par Pydantic, puis par predict(). Est-ce redondant ?

Cette double vérification n'est pas une redondance superflue, mais une mise en œuvre de la défense en profondeur et du découplage des couches :

1. **Au niveau de l'API (Pydantic)** : La validation du schéma (min_length=1) protège l'entrée HTTP. Elle intercepte les requêtes malformées dès la frontière du service et renvoie une réponse HTTP 422 normalisée et documentée sans gaspiller de ressources de calcul.
2. **Au niveau du modèle (predict)** : La fonction du module src/predict.py constitue la brique métier indépendante. Elle peut être réutilisée dans un script batch, un pipeline de test ou un notebook sans passer par FastAPI. Elle doit donc garantir sa propre intégrité et lever une exception (ValueError) si on lui soumet une entrée invalide.
