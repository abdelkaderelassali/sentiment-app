// Tests du client web, sans navigateur ni serveur : node --test web/client.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { analyser, interpreter, INJOIGNABLE, MESSAGES } from "./client.js";

const repondre = (statut, corps) => async () => ({ status: statut, json: async () => corps });

test("200 POSITIVE : verdict et confiance", () => {
  const r = interpreter(200, { label: "POSITIVE", score: 0.91, text: "..." });
  assert.equal(r.ok, true);
  assert.equal(r.classe, "positif");
  assert.equal(r.score, 0.91);
});

test("200 INDETERMINE : renvoi vers un humain", () => {
  assert.match(interpreter(200, { label: "INDETERMINE", score: 0.55 }).titre, /humain/);
});

for (const [statut, code] of [[401, "NON_AUTHENTIFIE"], [403, "ACCES_REFUSE"], [422, "ENTREE_INVALIDE"],
                               [503, "MODELE_INDISPONIBLE"], [500, "ERREUR_INTERNE"]]) {
  test(`${statut} ${code} : message prévu`, () => {
    const r = interpreter(statut, { erreur: { code, message: "texte du serveur", champs: [] } });
    assert.deepEqual(r, { ok: false, message: MESSAGES[code] });
  });
}

test("réponse inattendue : le statut est affiché", () => {
  assert.match(interpreter(502, null).message, /HTTP 502/);
});

test("la requête porte la clé et le texte, vers /v1/predict", async () => {
  let vu;
  const faux = async (url, options) => { vu = { url, options }; return { status: 200, json: async () => ({ label: "NEGATIVE", score: 0.8 }) }; };
  const r = await analyser("http://api.test/", "ma-cle", "Colis abîmé", faux);
  assert.equal(vu.url, "http://api.test/v1/predict");
  assert.equal(vu.options.headers["X-API-Key"], "ma-cle");
  assert.deepEqual(JSON.parse(vu.options.body), { text: "Colis abîmé" });
  assert.equal(r.classe, "negatif");
});

test("réseau coupé ou CORS refusé : API injoignable", async () => {
  const r = await analyser("http://api.test", "k", "x", async () => { throw new TypeError("Failed to fetch"); });
  assert.equal(r.message, INJOIGNABLE);
});

test("corps non JSON : pas de plantage", async () => {
  const r = await analyser("http://api.test", "k", "x", async () => ({ status: 502, json: async () => { throw new SyntaxError(); } }));
  assert.match(r.message, /HTTP 502/);
});

test("un 401 réel passe par fetch puis interpreter", async () => {
  const r = await analyser("http://api.test", "", "x", repondre(401, { erreur: { code: "NON_AUTHENTIFIE" } }));
  assert.equal(r.message, MESSAGES.NON_AUTHENTIFIE);
});
