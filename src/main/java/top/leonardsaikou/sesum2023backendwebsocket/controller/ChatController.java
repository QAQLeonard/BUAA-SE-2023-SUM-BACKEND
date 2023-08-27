package top.leonardsaikou.sesum2023backendwebsocket.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.*;
import org.springframework.stereotype.Component;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.socket.CloseStatus;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;
import top.leonardsaikou.sesum2023backendwebsocket.dto.MessageDto;
import org.json.JSONObject;

import java.io.DataOutputStream;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Map;
import java.util.concurrent.CopyOnWriteArrayList;

@RestController // 标记为 Spring 的 Controller 组件
@Component
public class ChatController extends TextWebSocketHandler {

    // 存储所有在线的 WebSocketSession
    private static final CopyOnWriteArrayList<WebSocketSession> sessions = new CopyOnWriteArrayList<>();

    // 连接建立
    @Override
    public void afterConnectionEstablished(WebSocketSession session) {
        sessions.add(session);
        // 可以添加一些开启连接时的逻辑
    }


    private static final String DJANGO_API_URL = "http://23.94.102.135:8000/api/save_message";

    @Autowired
    private RestTemplate restTemplate;

    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception {
        // 广播消息
        for (WebSocketSession webSocketSession : sessions) {
            try {
                webSocketSession.sendMessage(message);
            } catch (IOException e) {
                // 使用日志库记录异常，这里为简化仅用 println
                System.out.println("Error while sending message: " + e);
            }
        }

        try {
            // 将接收到的消息从 JSON 转为 JSONObject
            JSONObject jsonMessage = new JSONObject(message.getPayload());

            URL url = new URL(DJANGO_API_URL);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("POST");
            conn.setRequestProperty("Content-Type", "application/json; utf-8");
            conn.setRequestProperty("Accept", "application/json");
            conn.setDoOutput(true);

            // 写入输出流
            try (DataOutputStream os = new DataOutputStream(conn.getOutputStream())) {
                os.writeBytes(jsonMessage.toString());
                os.flush();
            }

            int responseCode = conn.getResponseCode();

            // 检查响应，例如，HTTP状态码
            if (responseCode != HttpURLConnection.HTTP_OK) {
                System.out.println("Failed to save message, status code: " + responseCode);
            }

        } catch (Exception e) {
            // 使用日志库记录异常，这里为简化仅用 println
            System.out.println("Error while handling message: " + e);
        }
    }

    // 连接关闭
    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) {
        sessions.remove(session);
        // 可以添加一些关闭连接时的逻辑
    }
}
