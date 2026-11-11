// Client web de l'API /v1 (TP 2). Aucune dépendance : JavaScript standard, exécuté par le navigateur.
// La logique (appel, traduction des réponses) est séparée de l'affichage : on la teste sans navigateur.

export const VERDICTS = {
  POSITIVE: { titre: "Avis positif", classe: "positif" },
  NEGATIVE: { titre: "Avis négatif", classe: "negatif" },
  INDETERMINE: { titre: "Je ne sais pas : à faire vérifier par un humain", classe: "indetermine" },
};

// Un message par code d'erreur stable du contrat /v1 : le client teste le code, jamais le texte
export const MESSAGES = {
  NON_AUTHENTIFIE: "Clé d'API absente ou invalide.",
  ACCES_REFUSE: "Votre clé ne donne pas accès à cette opération.",
  ENTREE_INVALIDE: "Texte refusé : vide, fait d'espaces, ou de plus de 2000 caractères.",
  MODELE_INDISPONIBLE: "Le modèle n'est pas chargé côté serveur. Réessayez plus tard.",
  ERREUR_INTERNE: "Erreur du serveur. L'incident est journalisé.",
};
export const INJOIGNABLE = "API injoignable : vérifiez l'adresse et que l'API est lancée (uvicorn api.main:app).";

/** Traduit une réponse de l'API en ce que la page affiche : { ok, titre, classe, score, message }. */
export function interpreter(statut, corps) {
  if (statut === 200 && corps && corps.label in VERDICTS) {
    return { ok: true, ...VERDICTS[corps.label], score: corps.score };
  }
  const code = corps && corps.erreur ? corps.erreur.code : null;
  return { ok: false, message: MESSAGES[code] ?? `Réponse inattendue de l'API (HTTP ${statut}).` };
}

/** Appelle POST /v1/predict. fetchFn est remplaçable : les tests passent une fausse fonction. */
export async function analyser(urlApi, cle, texte, fetchFn = fetch) {
  let reponse;
  try {
    reponse = await fetchFn(`${urlApi.replace(/\/+$/, "")}/v1/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-API-Key": cle },
      body: JSON.stringify({ text: texte }),
    });
  } catch {
    // réseau coupé, API arrêtée, ou requête bloquée par CORS : le navigateur ne dit pas lequel
    return { ok: false, message: INJOIGNABLE };
  }
  let corps = null;
  try { corps = await reponse.json(); } catch { /* corps vide ou non JSON */ }
  return interpreter(reponse.status, corps);
}
