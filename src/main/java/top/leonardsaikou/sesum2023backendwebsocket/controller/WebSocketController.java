// WebSocketController.java
package top.leonardsaikou.sesum2023backendwebsocket.controller;

import org.springframework.messaging.handler.annotation.DestinationVariable;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import top.leonardsaikou.sesum2023backendwebsocket.model.Message;
import top.leonardsaikou.sesum2023backendwebsocket.service.DjangoApiService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.handler.annotation.SendTo;
import org.springframework.messaging.simp.SimpMessageHeaderAccessor;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class WebSocketController {

    @Autowired
    private SimpMessagingTemplate simpMessagingTemplate;

    @Autowired
    private DjangoApiService djangoApiService;

    @MessageMapping("/send/{groupId}")
    public void sendMessageToGroup(@DestinationVariable String groupId, Message message) {
        // 把groupId存储到WebSocket会话中，如果需要
        // SimpMessageHeaderAccessor headerAccessor
        // headerAccessor.getSessionAttributes().put("groupID", groupId);

        // 保存消息到数据库
        djangoApiService.saveMessage(message);

        // 动态地设置目的地并发送消息
        simpMessagingTemplate.convertAndSend("/topic/messages/" + groupId, message);
    }
}
