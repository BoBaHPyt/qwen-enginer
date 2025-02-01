from dataclasses import dataclass
from typing import Dict, Any
from pathlib import Path
import tomlkit
import platform
import os


@dataclass(frozen=True)
class Config:
    connection: Dict[str, str]
    prompt: Dict[str, str]
    
    @classmethod
    def load(cls, workhome):
        if platform.system() == "Windows":
            filename = Path(os.path.join(os.getenv('APPDATA'), 'qwen-enginer/config.toml'))
        elif platform.system() == "Darwin":
            filename = Path("~/Library/Application Support/qwen-enginer/config.toml")
            filename = filename.expanduser()
        else:
            filename = Path("~/.config/qwen-enginer/config.toml")
            filename = filename.expanduser()
        if not filename.exists():
            filename.parent.mkdir(parents=True, exist_ok=True)
            config = tomlkit.document()

            connection = tomlkit.table()
            connection.add("BASE_URL", "https://chat.qwenlm.ai/api")
            connection.add("MODEL", "qwen2.5-coder-32b-instruct")
            connection.add("TOKEN", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY1MjdhNTJhLWY2NTgtNDk1MC04ZDk4LThkNmM2ZTIzZjA3MCIsImV4cCI6MTczOTIwMTQ5MX0.cxDNbLUTgioZqngAbXOPzKjn1RxHneLBF6a1PfnR1vw")
            connection.add("INCREMENT", False)

            environment = tomlkit.table()
            environment.add("MODULES", ["code", "shell"])
            environment.add("code-write", True)
            environment.add("code-replace", False)
            environment.add("code-rename", True)
            environment.add("code-delete", True)
            environment.add("shell-commands", ["python", "python3", "pip", "pip3", "source", "cd", "mv"])
            environment["shell-commands"].comment("\"*\" to all")
            environment.add("shell-sudo", False)

            prompt = tomlkit.table()
            prompt.add("boocks", [])

            config.add("connection", connection)
            config.add("prompt", prompt)
            
            with open(filename, "w") as file:
                file.write(tomlkit.dumps(config))
        with open(filename) as file:
            return cls(**tomlkit.parse(file.read()))
