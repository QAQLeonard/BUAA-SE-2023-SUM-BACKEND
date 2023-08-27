// WebSocketController.java
package top.leonardsaikou.sesum2023backendwebsocket.controller;

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
    private DjangoApiService djangoApiService;

    @MessageMapping("/send")
    @SendTo("/topic/messages")
    public Message send(Message message, SimpMessageHeaderAccessor headerAccessor) {
        headerAccessor.getSessionAttributes().put("groupID", message.getGroupID());
        djangoApiService.saveMessage(message);
        return message;
    }
}
