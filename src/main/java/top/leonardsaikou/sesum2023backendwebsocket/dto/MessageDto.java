package top.leonardsaikou.sesum2023backendwebsocket.dto;

public class MessageDto
{
    String content;
    String sender_uname;
    String group_id;

    public MessageDto(String content, String sender_uname, String group_id)
    {
        this.content = content;
        this.sender_uname = sender_uname;
        this.group_id = group_id;
    }

}
