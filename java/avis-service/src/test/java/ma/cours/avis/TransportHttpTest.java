package ma.cours.avis;

import com.sun.net.httpserver.HttpServer;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.client.JdkClientHttpRequestFactory;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.web.client.RestClient;

import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;

import static org.assertj.core.api.Assertions.assertThatThrownBy;

/** Un vrai serveur HTTP local qui répond comme l'API /v1 sans clé : 401 et WWW-Authenticate. */
class TransportHttpTest {

    private HttpServer serveur;
    private String url;

    @BeforeEach
    void demarrer() throws Exception {
        serveur = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        serveur.createContext("/v1/predict", echange -> {
            byte[] corps = "{\"erreur\":{\"code\":\"NON_AUTHENTIFIE\",\"message\":\"Clé d'API invalide\",\"champs\":[]}}"
                    .getBytes(StandardCharsets.UTF_8);
            echange.getRequestBody().readAllBytes();
            echange.getResponseHeaders().add("WWW-Authenticate", "APIKey");
            echange.getResponseHeaders().add("Content-Type", "application/json");
            echange.sendResponseHeaders(401, corps.length);
            echange.getResponseBody().write(corps);
            echange.close();
        });
        serveur.start();
        url = "http://127.0.0.1:" + serveur.getAddress().getPort();
    }

    @AfterEach
    void arreter() {
        serveur.stop(0);
    }

    @Test
    void avecLeTransportJdkUn401ResteUn401() {
        RestClient.Builder builder = RestClient.builder();
        new ClientHttpConfig().transportJdk().customize(builder);
        SentimentClient client = new SentimentClient(builder, url, "mauvaise-cle-de-service");
        assertThatThrownBy(() -> client.analyser("Très bien"))
                .isInstanceOfSatisfying(SentimentApiException.class, e -> {
                    org.assertj.core.api.Assertions.assertThat(e.statut()).isEqualTo(401);
                    org.assertj.core.api.Assertions.assertThat(e.code()).isEqualTo("NON_AUTHENTIFIE");
                });
    }

    @Test
    void lePiegeEstReelAvecHttpUrlConnection() {
        RestClient.Builder builder = RestClient.builder().requestFactory(new SimpleClientHttpRequestFactory());
        SentimentClient client = new SentimentClient(builder, url, "mauvaise-cle-de-service");
        // l'erreur n'est pas une SentimentApiException : le code NON_AUTHENTIFIE est perdu
        assertThatThrownBy(() -> client.analyser("Très bien"))
                .isNotInstanceOf(SentimentApiException.class);
    }
}
