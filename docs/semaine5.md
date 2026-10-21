# Semaine 5 : l'interface, notes du binôme

## 1. Pourquoi l'interface n'importe-t-elle jamais predict() ni le fichier .joblib ?

L'interface Streamlit est conçue comme un client HTTP pur, totalement découplé de la couche d'inférence. Si elle importait predict() ou chargeait directement models/sentiment.joblib :
1. **Perte de modularité et de scalabilité** : L'interface serait obligée de tourner sur le même environnement physique ou conteneur que le modèle, empêchant un déploiement distribué ou une montée en charge indépendante du frontend et de l'API.
2. **Cycle de vie Streamlit** : Le framework Streamlit réexécute l'intégralité du script à chaque interaction utilisateur. Charger ou référencer le modèle en direct risquerait de surcharger la mémoire ou de dupliquer les artefacts lourds.
3. **Évolution indépendante** : En passant par le contrat REST (via le module client), le modèle peut être réentraîné, optimisé, ou même remplacé par une autre technologie sans modifier une seule ligne du code de l'interface.

## 2. Que montre l'interface quand le modèle hésite, et pourquoi est-ce mieux qu'un verdict forcé ?

Quand la confiance du modèle se situe sous le seuil d'abstention (0.60), l'API renvoie l'étiquette INDETERMINE. L'interface affiche alors un message informatif explicite : « *Je ne sais pas : confiance insuffisante pour trancher (XX %)* ».

C'est bien supérieur à un verdict forcé pour plusieurs raisons :
- **Fiabilité opérationnelle** : Un modèle TF-IDF sans vocabulaire pertinent (ou face à un texte hors domaine) produit une prédiction par défaut (proche de 0.50). Forcer un verdict conduirait à induire en erreur les conseillers du service client.
- **Routage vers l'humain** : L'abstention permet de transférer automatiquement et en toute transparence les cas litigieux ou ambigus vers un opérateur humain (human-in-the-loop), garantissant une qualité de traitement maximale.

## 3. Que voit l'utilisateur quand l'API tombe ? Et le fichier data/avis_exemple.csv : combien d'avis partent vers un humain ?

- **Quand l'API tombe ou est injoignable** : Grâce à la gestion d'erreurs dans le client de l'interface, l'application n'affiche pas une page de crash technique (stacktrace brute). L'utilisateur voit un bandeau rouge clair : « *API injoignable (http://localhost:8000). Vérifiez qu'elle est lancée : uvicorn api.main:app* ». Si le modèle est manquant sur l'API (erreur 503), l'interface indique spécifiquement « *Modèle non chargé* ».
- **Analyse du fichier data/avis_exemple.csv** : Le fichier contient 6 avis tests. L'analyse par lot produit la répartition : 3 avis positifs, 2 avis négatifs et 1 avis indéterminé (xqzvb wlkptr grombu, confiance 0.5162). Ainsi, exactement **1 avis sur 6** (soit environ 17 %) part vers un humain.
