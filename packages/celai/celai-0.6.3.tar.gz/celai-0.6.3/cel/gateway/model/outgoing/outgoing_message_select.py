from cel.gateway.model.attachment import FileAttachment
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.outgoing.outgoing_message import OutgoingMessage, OutgoingMessageType


class OutgoingSelectMessage(OutgoingMessage):
    """This class represents a specific outgoing message object with select options"""
    
    def __init__(self, 
                 lead: ConversationLead, 
                 content: str = None,
                 button: str = None,
                 list_title: str = None,
                 options: list[str] = None,
                 **kwargs
                ):
        super().__init__(OutgoingMessageType.SELECT, 
                         lead, **kwargs)
        
        self.content = content
        self.options = options
        self.button = button
        self.list_title = list_title    

        assert isinstance(self.content, str), "body must be a string"
        assert isinstance(self.options, list), "options must be a list"
        for option in self.options:
            assert isinstance(option, str), "each option must be a string"
            
    def __str__(self):
        """Returns the content of the message plus the options"""
        return f"{self.content}\n\n" + "\n".join([f"{i + 1}. {option}" for i, option in enumerate(self.options)])
            
    @staticmethod
    def from_dict(data: dict) -> 'OutgoingSelectMessage':
        """Creates an OutgoingSelectMessage instance from a dictionary"""
        assert isinstance(data, dict),\
            "data must be a dictionary"
        assert "content" in data,\
            "data must have a 'content' key"
        assert "options" in data,\
            "data must have a 'options' key"
        assert isinstance(data["options"], list),\
            "options must be a list"
        assert "lead" in data,\
            "data must have a 'lead' key"
        assert isinstance(data["lead"], ConversationLead),\
            "lead must be an instance of ConversationLead"
        
        return OutgoingSelectMessage(
            content=data["content"],
            options=data["options"],
            list_title=data.get("list_title"),
            button=data.get("button"),
            lead=data["lead"],
            metadata=data.get("metadata"),
            attachments=[FileAttachment.from_dict(attachment) for attachment in data.get("attachments", [])],
            is_partial=data.get("is_partial", True)
        )
        
        
    @staticmethod
    def description() -> str:
        return """When the message asks the user to make select between options, use the following structure:
    Maximum of 10 options. Ideal for dropdown like questions.
{
    "type": "select",
    "list_title": "A title for the list",
    "options": [],
    "content": "A body text",
    "button": View Options"
}

The options must be a list of strings. Options should be short and clear in title case. 
The prompt is keeped in the content field, and the options are the possible choices.
"""