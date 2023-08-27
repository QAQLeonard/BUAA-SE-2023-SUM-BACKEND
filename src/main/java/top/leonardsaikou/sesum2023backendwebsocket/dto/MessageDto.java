package top.leonardsaikou.sesum2023backendwebsocket.dto;
import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;
public class MessageDto
{
    String content;
    String sender_uname;
    String group_id;

    public MessageDto( @JsonProperty("content")  String content,
                       @JsonProperty("sender_uname") String sender_uname,
                       @JsonProperty("group_id") String group_id)
    {
        this.content = content;
        this.sender_uname = sender_uname;
        this.group_id = group_id;
    }


}
