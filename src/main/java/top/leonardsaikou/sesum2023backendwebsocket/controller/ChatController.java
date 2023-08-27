package top.leonardsaikou.sesum2023backendwebsocket.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.http.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.socket.CloseStatus;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;
import top.leonardsaikou.sesum2023backendwebsocket.dto.MessageDto;
import org.springframework.web.client.RestTemplate;

import java.io.IOException;
import java.util.concurrent.CopyOnWriteArrayList;

public class ChatController extends TextWebSocketHandler
{

    // 存储所有在线的 WebSocketSession
    private static final CopyOnWriteArrayList<WebSocketSession> sessions = new CopyOnWriteArrayList<>();

    // 连接建立
    @Override
    public void afterConnectionEstablished(WebSocketSession session)
    {
        sessions.add(session);
        // 可以添加一些开启连接时的逻辑
    }

    private RestTemplate restTemplate = new RestTemplate();
    private ObjectMapper objectMapper = new ObjectMapper();
    private static final String DJANGO_API_URL = "http://127.0.0.1:8000/api/save_message/";  // 或从配置文件读取

    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception
    {
        // 广播消息
        for (WebSocketSession webSocketSession : sessions)
        {
            try
            {
                webSocketSession.sendMessage(message);
            }
            catch (IOException e)
            {
                // 使用日志库记录异常
                System.out.println("Error while sending message" + e);
            }
        }

        try
        {
            MessageDto messageDto = objectMapper.readValue(message.getPayload(), MessageDto.class);
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<MessageDto> entity = new HttpEntity<>(messageDto, headers);

            // 将消息存储到数据库
            ResponseEntity<String> response = restTemplate.exchange(DJANGO_API_URL, HttpMethod.POST, entity, String.class);
            // 检查响应，例如，HTTP状态码
            if (response.getStatusCode() != HttpStatus.OK)
            {
                System.out.println("Failed to save message, status code: " + response.getStatusCode());
            }
        }
        catch (Exception e)
        {
            // 使用日志库记录异常
            System.out.println("Error while handling message" + e);
        }
    }


    // 连接关闭
    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status)
    {
        sessions.remove(session);
        // 可以添加一些关闭连接时的逻辑
    }
}


