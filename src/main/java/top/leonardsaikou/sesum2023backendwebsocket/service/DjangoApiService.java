package top.leonardsaikou.sesum2023backendwebsocket.service;

// DjangoApiService.java

import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import top.leonardsaikou.sesum2023backendwebsocket.model.Message;

import java.util.*;

import java.util.Map;

@Service
public class DjangoApiService
{
    String djangoBaseUrl = "http://23.94.102.135:8000/api/v1/tm/";

    public void saveMessage(Message message)
    {
        RestTemplate restTemplate = new RestTemplate();

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<Message> request = new HttpEntity<>(message, headers);
        restTemplate.postForEntity(djangoBaseUrl + "save_message", request, String.class);
    }

    public List<Map<String, Object>> getUserGroups(String username)
    {
        RestTemplate restTemplate = new RestTemplate();

        ResponseEntity<Map> response = restTemplate.getForEntity(djangoBaseUrl + "get_groups?username=" + username, Map.class);

        if (response.getStatusCode() == HttpStatus.OK)
        {
            Map<String, Object> body = response.getBody();
            if ("success".equals(body.get("status")))
            {
                return (List<Map<String, Object>>) body.get("data");
            }
        }

        return Collections.emptyList();
    }

    public List<Map<String, Object>> getGroupMembers(String groupId)
    {
        RestTemplate restTemplate = new RestTemplate();

        ResponseEntity<Map> response = restTemplate.getForEntity(djangoBaseUrl + "get_group_members?group_id=" + groupId, Map.class);

        if (response.getStatusCode() == HttpStatus.OK)
        {
            Map<String, Object> body = response.getBody();
            if ("success".equals(body.get("status")))
            {
                return (List<Map<String, Object>>) body.get("data");
            }
        }

        return Collections.emptyList();
    }
}








