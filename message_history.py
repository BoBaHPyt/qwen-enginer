import json
from pathlib import Path
try:
    from .message import Message
except:
    from message import Message


class MessageHistory(list):
    one_system: bool
    
    def __init__(self, *args, one_system=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.one_system = one_system
    
    def __iter__(self, json_friendly=True):
        systems = 0
        if json_friendly:
            for message in super().__iter__():
                md = message.to_dict(keys=["role", "content"])
                if self.one_system and message.role == "system" and systems > 0:
                    md["role"] = "user"
                    md["content"] = f"SYSTEM: {md['content']}"
                yield md
                if message.role == "system":
                    systems += 1
        else:
            for message in super().__iter__():
                yield message
        
    @classmethod
    def from_json(cls, filename, one_system=False):
        filename = Path(filename)
        if filename.exists():
            with open(filename, "r") as file:
                messages_data = json.load(file)
            return cls([Message(**message_data) for message_data in messages_data], one_system=one_system)
        return cls(one_system=one_system)

    def to_json(self, filename):
        filename = Path(filename)
        filename.parent.mkdir(parents=True, exist_ok=True)
        with open(filename, "w") as file:
            json.dump(self, file)
