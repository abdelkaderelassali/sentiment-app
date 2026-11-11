"""Tests de l'API /v1 (TP 2) : versionnement, authentification, autorisation, format d'erreur, CORS."""
from pathlib import Path

import pytest

MODELE = Path(__file__).resolve().parents[1] / "models" / "sentiment.joblib"
pytestmark = pytest.mark.skipif(not MODELE.exists(), reason="modèle non produit : python src/train.py")

CLE_CLIENT = "cle-client-de-test-0001"
CLE_ADMIN = "cle-admin-de-test-00001"
AVIS = {"text": "Livraison rapide, produit conforme, très satisfait"}


@pytest.fixture
def client(monkeypatch):
    from fastapi.testclient import TestClient

    from api.main import app

    monkeypatch.setenv("API_KEYS", f"{CLE_CLIENT}:client,{CLE_ADMIN}:admin")
    with TestClient(app) as c:
        yield c


def entetes(cle: str) -> dict[str, str]:
    return {"X-API-Key": cle}


# --- versionnement --------------------------------------------------------
def test_v1_health_est_public(client):
    r = client.get("/v1/health")
    assert r.status_code == 200 and r.json()["status"] == "OK"


def test_v1_predict_meme_contrat_que_la_premiere_version(client):
    r = client.post("/v1/predict", json=AVIS, headers=entetes(CLE_CLIENT))
    assert r.status_code == 200
    assert r.json() == client.post("/predict", json=AVIS).json()


def test_ancienne_route_annonce_son_remplacement(client):
    r = client.post("/predict", json=AVIS)
    assert r.status_code == 200
    assert r.headers["Deprecation"] == "true"
    assert "/v1/predict" in r.headers["Link"]


def test_documentation_marque_l_ancienne_route_depreciee(client):
    schema = client.get("/openapi.json").json()
    assert schema["paths"]["/predict"]["post"]["deprecated"] is True
    assert "X-API-Key" in str(schema["components"]["securitySchemes"])


# --- authentification : 401 ---------------------------------------------
def test_sans_cle_401(client):
    r = client.post("/v1/predict", json=AVIS)
    assert r.status_code == 401
    assert r.json()["erreur"]["code"] == "NON_AUTHENTIFIE"
    assert r.headers["WWW-Authenticate"] == "APIKey"


def test_cle_inconnue_401(client):
    r = client.post("/v1/predict", json=AVIS, headers=entetes("cle-inventee-par-un-curieux"))
    assert r.status_code == 401
    assert r.json()["erreur"]["message"] == "Clé d'API invalide"


def test_sans_cle_on_n_apprend_rien_du_contrat(client):
    """L'authentification passe avant la validation : un inconnu reçoit 401, pas le détail du schéma."""
    r = client.post("/v1/predict", json={"mauvais": "corps"})
    assert r.status_code == 401


def test_aucune_cle_configuree_tout_est_ferme(monkeypatch):
    from fastapi.testclient import TestClient

    from api.main import app

    monkeypatch.setenv("API_KEYS", "")
    with TestClient(app) as c:
        assert c.post("/v1/predict", json=AVIS, headers=entetes(CLE_CLIENT)).status_code == 401


# --- autorisation : 403 --------------------------------------------------
def test_client_n_accede_pas_au_modele(client):
    r = client.get("/v1/modele", headers=entetes(CLE_CLIENT))
    assert r.status_code == 403
    assert r.json()["erreur"]["code"] == "ACCES_REFUSE"


def test_admin_accede_au_modele(client):
    r = client.get("/v1/modele", headers=entetes(CLE_ADMIN))
    assert r.status_code == 200
    corps = r.json()
    assert corps["seuil_abstention"] == 0.60
    assert corps["metriques"]["f1_macro"] >= 0.85


def test_admin_peut_aussi_predire(client):
    assert client.post("/v1/predict", json=AVIS, headers=entetes(CLE_ADMIN)).status_code == 200


# --- format d'erreur unique ----------------------------------------------
@pytest.mark.parametrize("corps", [{"text": ""}, {"text": "   "}, {}, {"text": 42}, {"text": "x" * 2001}],
                         ids=["vide", "blancs", "absent", "nombre", "trop-long"])
def test_entree_invalide_422_format_v1(client, corps):
    r = client.post("/v1/predict", json=corps, headers=entetes(CLE_CLIENT))
    assert r.status_code == 422
    erreur = r.json()["erreur"]
    assert erreur["code"] == "ENTREE_INVALIDE"
    assert erreur["champs"] and erreur["champs"][0]["champ"].startswith("body")


def test_modele_absent_503_format_v1(client, monkeypatch):
    from api.main import app

    monkeypatch.setattr(app.state, "classifier", None)
    r = client.post("/v1/predict", json=AVIS, headers=entetes(CLE_CLIENT))
    assert r.status_code == 503
    assert r.json()["erreur"]["code"] == "MODELE_INDISPONIBLE"


def test_panne_500_sans_fuite(client, monkeypatch):
    from api.main import app

    class EnPanne:
        model_name = "panne"

        def predict(self, text):
            raise RuntimeError("secret interne")

    monkeypatch.setattr(app.state, "classifier", EnPanne())
    r = client.post("/v1/predict", json=AVIS, headers=entetes(CLE_CLIENT))
    assert r.status_code == 500
    assert r.json()["erreur"]["code"] == "ERREUR_INTERNE"
    assert "secret interne" not in r.text


def test_route_inconnue_404_format_v1(client):
    assert client.get("/v1/inexistante").json()["erreur"]["code"] == "INTROUVABLE"


def test_hors_v1_le_format_d_origine_est_garde(client):
    assert "detail" in client.post("/predict", json={"text": ""}).json()


# --- CORS ------------------------------------------------------------------
def test_cors_origine_autorisee(client):
    r = client.options("/v1/predict", headers={"Origin": "http://localhost:5500",
                                               "Access-Control-Request-Method": "POST",
                                               "Access-Control-Request-Headers": "content-type,x-api-key"})
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] == "http://localhost:5500"


def test_cors_origine_inconnue_refusee(client):
    r = client.options("/v1/predict", headers={"Origin": "https://site-pirate.example",
                                               "Access-Control-Request-Method": "POST"})
    assert "access-control-allow-origin" not in r.headers


# --- configuration des clés ------------------------------------------------
def test_charger_cles():
    from api.securite import charger_cles

    assert charger_cles(f"{CLE_CLIENT}:client, {CLE_ADMIN}:admin") == {CLE_CLIENT: "client",
                                                                       CLE_ADMIN: "admin"}
    assert charger_cles("") == {}


@pytest.mark.parametrize("brut", ["courte:client", f"{CLE_CLIENT}:root", CLE_CLIENT])
def test_configuration_invalide_refusee(brut):
    from api.securite import charger_cles

    with pytest.raises(ValueError):
        charger_cles(brut)


def test_message_d_erreur_ne_recopie_pas_la_cle():
    from api.securite import charger_cles

    with pytest.raises(ValueError) as erreur:
        charger_cles("secret12:client")
    assert "secret12" not in str(erreur.value)


def test_cles_mal_formees_l_api_refuse_de_demarrer(monkeypatch):
    from fastapi.testclient import TestClient

    from api.main import app

    monkeypatch.setenv("API_KEYS", "courte:client")
    with pytest.raises(ValueError, match="trop courte"):
        with TestClient(app):
            pass
