package top.leonardsaikou.sesum2023backendwebsocket;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.web.client.RestTemplate;

@SpringBootApplication
public class SeSum2023BackendWebsocketApplication
{

    public static void main(String[] args)
    {
        SpringApplication.run(SeSum2023BackendWebsocketApplication.class, args);
    }

    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
}
