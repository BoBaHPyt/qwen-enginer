import requests
import json
from modules import BaseModule
from pathlib import Path
from typing import Optional, List
from config import Config
from prompt import Prompt
from message import Message
from message_history import MessageHistory


class Chat:
    workhome: Path
    __chat_id: int
    __config: Config
    __session: requests.Session
    __base_url: str
    __model: str
    __token: str
    __increment: str
    __lastpos: int
    __prompt: Prompt
    __message_history: MessageHistory
    __message_history_path: Path
    __modules: List[BaseModule]
    
    def __init__(self, chat_id, workhome, config):
        self.workhome = Path(workhome)
        self.__chat_id = chat_id
        self.__config = config
        self.__prompt = Prompt(workhome, config)
        self.__message_history_path = self.workhome / f".qwen-enginer/{chat_id}.json"
        self.set_api(config.connection["BASE_URL"], config.connection["MODEL"],
                     config.connection["TOKEN"], config.connection["INCREMENT"])
        self.__message_history = MessageHistory.from_json(self.__message_history_path, one_system=True)

        if len(self.__message_history) == 0:
            self.__message_history.append(Message(role="system", content=self.__prompt.content, pinned=True))
        self.__init_modules()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __init_modules(self):
        self.__modules = []
        for module in BaseModule.__subclasses__():
            self.__modules.append(module(self.workhome))

    def __init_session(self, token):
        self.__session = requests.Session()
        self.__session.headers.update({"Authorization": f"Bearer {token}", "referer": "https://openrouter.ai/chat"})
        self.__lastpos = 0

    def set_api(self, base_url, model, token, increment):
        self.__base_url = base_url
        self.__model = model
        self.__token = token
        self.__increment = increment
        self.__init_session(token)

    def close(self):
        self.__message_history.to_json(self.__message_history_path)
        for module in self.__modules:
            module.close()

    def _process_block(self, block):
        for module in self.__modules:
            if module.validate(**block):
                return module.process(**block)

    def process(self, content: str):
        user_message = Message(role="user", content=content)
        self.__message_history.append(user_message)
        data = {"model": self.__model, "stream": True, "messages": self.__message_history}
        full_content = ""
        try:
            with self.__session.post(f"{self.__base_url}/chat/completions", json=data, stream=True) as resp:
                for chunk in resp.iter_lines():
                    chunk = chunk.decode()
                    if chunk.startswith("data: "):
                        chunk = chunk[6:]
                    if chunk.startswith("{\""):
                        chunk = json.loads(chunk)
                        content = chunk["choices"][0]
                        if "delta" in content:
                            content = content["delta"]["content"]
                        else:
                            content = content["message"]["content"]
                        if content:
                            if not self.__increment:
                                content, self.__lastpos = content[self.__lastpos:], len(content)
                            yield content
                            full_content += content
        finally:
            self.__lastpos = 0
            message = Message(role="assistant", content=full_content)
            self.__message_history.append(message)

            try:
                for block in message.codeblocks:
                    resp = self._process_block(block)
                    if resp:
                        self.__message_history.append(Message(role="system", content=resp))
            except Exception as ex:
                print(ex)
                self.__message_history.append(Message(role="system", content=f"ERROR: {ex}"))


def serialize(obj):
    if isinstance(obj, Message):
        return obj.as_dict()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


if __name__ == '__main__':
    config = Config.load("./")
    with Chat(123, "./saas", config) as chat:
        while True:
            for s in chat.process(input(">>>")):
                print(s, sep="", end="")
            print()
