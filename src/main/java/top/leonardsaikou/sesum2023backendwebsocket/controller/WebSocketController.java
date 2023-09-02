// WebSocketController.java
package top.leonardsaikou.sesum2023backendwebsocket.controller;

import org.springframework.messaging.handler.annotation.DestinationVariable;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.web.bind.annotation.RequestBody;
import top.leonardsaikou.sesum2023backendwebsocket.model.Message;
import top.leonardsaikou.sesum2023backendwebsocket.service.DjangoApiService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class WebSocketController
{

    @Autowired
    private SimpMessagingTemplate simpMessagingTemplate;

    @Autowired
    private DjangoApiService djangoApiService;

    @MessageMapping("/send/{group_id}")
    public void sendMessageToGroup(@DestinationVariable String group_id, @RequestBody Message message)
    {
        message.content = message.content.replace("zxd", "qmk").replace("周星达", "秦茂凯");
        if (message.content.contains("原神"))
        {
            Message temp = new Message();
            temp.content = "我超，原批！";
            temp.group_id = group_id;
            temp.sender_uname = "testUsername";
            djangoApiService.saveMessage(temp);
            simpMessagingTemplate.convertAndSend("/topic/messages/" + group_id, temp);
        }
        // 保存消息到数据库
        djangoApiService.saveMessage(message);

        // 动态地设置目的地并发送消息
        simpMessagingTemplate.convertAndSend("/topic/messages/" + group_id, message);
    }

//    @MessageMapping("/sendTest/{testID}")
//    @SendTo("/topic/receiveTest")
//    public String handleTest(@DestinationVariable("testID") String testID, String message) {
//        System.out.println("Received: " + message + " from " + testID);
//        return "Received: " + message;
//    }
}
