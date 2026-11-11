package ma.cours.avis;

import org.springframework.boot.web.client.RestClientCustomizer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.JdkClientHttpRequestFactory;

import java.net.http.HttpClient;
import java.time.Duration;

/**
 * Le transport HTTP du RestClient : java.net.http.HttpClient (JDK 11 et plus).
 *
 * Piège : sans cette ligne, Spring Boot 3.3 utilise HttpURLConnection. Sur une réponse 401
 * accompagnée de l'en-tête WWW-Authenticate (ce que renvoie notre API), HttpURLConnection tente
 * une réauthentification, échoue (HttpRetryException) et l'erreur 401 devient une erreur 500
 * illisible. Les tests avec un faux serveur ne le voient pas : ils ne passent pas par le réseau.
 *
 * Second piège : HttpClient tente par défaut de passer en HTTP/2 (en-tête « Upgrade: h2c »).
 * Uvicorn ne le gère pas et lit une requête corrompue : on fixe HTTP/1.1.
 */
@Configuration
public class ClientHttpConfig {

    @Bean
    RestClientCustomizer transportJdk() {
        HttpClient http = HttpClient.newBuilder()
                .version(HttpClient.Version.HTTP_1_1)
                .connectTimeout(Duration.ofSeconds(3))
                .build();
        JdkClientHttpRequestFactory transport = new JdkClientHttpRequestFactory(http);
        transport.setReadTimeout(Duration.ofSeconds(10));  // un modèle bloqué ne bloque pas Java
        return builder -> builder.requestFactory(transport);
    }
}
