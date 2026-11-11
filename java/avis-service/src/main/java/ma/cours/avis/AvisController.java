package ma.cours.avis;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/**
 * L'API métier du service Java : POST /avis/analyse.
 * Elle traduit la réponse de l'API Python dans le vocabulaire de l'application Java.
 */
@RestController
public class AvisController {

    public record AvisRecu(String texte) {}

    public record Analyse(String texte, String verdict, double confiance, boolean aVerifier) {}

    private final SentimentClient sentiment;

    public AvisController(SentimentClient sentiment) {
        this.sentiment = sentiment;
    }

    @PostMapping("/avis/analyse")
    public Analyse analyser(@RequestBody AvisRecu avis) {
        SentimentClient.Prediction p = sentiment.analyser(avis.texte() == null ? "" : avis.texte());
        return new Analyse(avis.texte(), p.label(), p.score(), "INDETERMINE".equals(p.label()));
    }

    /**
     * Les erreurs de l'API Python, vues depuis les clients du service Java :
     *  - entrée refusée : la faute du client, 400 ;
     *  - clé absente ou refusée : une erreur de configuration du service, pas du client, 502 ;
     *  - modèle absent ou API injoignable : 503, réessayer plus tard ;
     *  - le reste : 502, le service en amont a failli.
     */
    @ExceptionHandler(SentimentApiException.class)
    public ResponseEntity<Map<String, String>> erreur(SentimentApiException e) {
        HttpStatus statut = switch (e.code()) {
            case "ENTREE_INVALIDE" -> HttpStatus.BAD_REQUEST;
            case "MODELE_INDISPONIBLE", "API_INJOIGNABLE" -> HttpStatus.SERVICE_UNAVAILABLE;
            default -> HttpStatus.BAD_GATEWAY;
        };
        return ResponseEntity.status(statut).body(Map.of("code", e.code()));
    }
}
