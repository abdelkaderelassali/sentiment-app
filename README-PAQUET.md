# sentiment-app

Classe un avis client rédigé en français : `positive` ou `negative`, avec une confiance.

    pip install sentiment_app-1.0.0-py3-none-any.whl
    sentiment "Livraison rapide, très satisfait"

En Python :

    from sentiment_app import predict
    predict("Colis abîmé")   # {'label': 'negative', 'score': ...}

Limites : modèle de démonstration (290 avis), sensible aux avis mitigés ; ne pas l'utiliser sans seuil d'abstention.
