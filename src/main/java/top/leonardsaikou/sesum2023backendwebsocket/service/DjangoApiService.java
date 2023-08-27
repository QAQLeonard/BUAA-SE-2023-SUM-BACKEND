package top.leonardsaikou.sesum2023backendwebsocket.service;

// DjangoApiService.java
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
public class DjangoApiService {

    public void saveMessage(Message message) {
        RestTemplate restTemplate = new RestTemplate();
        String djangoBaseUrl = "http://23.94.102.135:8000/api/v1/tm/";
        restTemplate.postForEntity(djangoBaseUrl + "save_message", message, String.class);
    }

    // 添加获取群组和群组成员的方法...
}

