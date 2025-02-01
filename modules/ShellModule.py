from . import BaseModule
from pathlib import Path
import re
import container
import io
import select


class ShellModule(BaseModule):
    name = "shell"
    __exec_start = re.compile(br"^\x01\x00\x00\x00\x00\x00\x00.*?\x1b[\?2004h.*?<\x1b\]0;[\w\-]+@[\w\-]+: [\~/\w]*\x07[\w\-]+@[\w\-]+:[~\w/]*[#\$] ")
    __exec_done = re.compile(br"\x01\x00\x00[^\[\r\n]*?[\s\S]*?\x1b\].*;[\w\-]+@[\w\-]+: [\~/\w]*\x07[\w\-]+@[\w\-]+:[~\w/]*[#\$] ")
    __exec_start_replace = re.compile(br"^\x01\x00\x00\x00\x00\x00\x00.*?\x1b[\?2004h.*?<\x1b\]0;[\w\-]+@[\w\-]+: [\~/\w]*\x07")
    __exec_done_replace = re.compile(br"\x01\x00\x00[^\[^\r^\n]*?\[[^\x1b]*?\x1b\].*;[\w\-]+@[\w\-]+: [\~/\w]*\x07")
    __r_replace = re.compile(br"\x01\x00.{6}")
    __container_manager: container.ContainerManager
    runtime_sock = None
    mainshell_sock = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__container_manager = container.ContainerManager()
        self.runtime_sock = self.__container_manager.exec(self.workhome.name, "bash")
        self.mainshell_sock = self.__container_manager.exec(self.workhome.name, "bash")

        self.readall(self.runtime_sock)
        self.readall(self.mainshell_sock)
        self.exec(self.runtime_sock, "\x03")
        self.exec(self.mainshell_sock, "\x03")
        self.exec(self.mainshell_sock, "git config --global --add safe.directory /project")
        self.exec(self.mainshell_sock, "git config --global user.email \"qwen-enginer@mstat.kz\"")
        self.exec(self.mainshell_sock, "git config --global user.name \"QwenEnginer\"")

        self.exec(self.runtime_sock, "source /venv/bin/activate && export WORKHOME=/project\n")
        self.exec(self.mainshell_sock, "source /venv/bin/activate && export WORKHOME=/project\n")

    def exec(self, sock, cmd):
        if not cmd.endswith("\n"):
            cmd += "\n"
        cmd = cmd.encode()
        sock.send(cmd)
        return self.readall(sock)

    def readall(self, sock):
        data = b""
        while (not self.__exec_done.match(data) and not self.__exec_start.match(data)) and select.select([sock], [], [], 10)[0]:
            data += sock.recv(1024)
        data = self.__r_replace.sub(b"", data)
        if self.__exec_start.match(data):
            data = self.__exec_start_replace.sub(b"", data, 1)
        elif self.__exec_done.match(data):
            data = self.__exec_done_replace.sub(b"", data, 1)
        data = data.decode(errors="")
        lines = data.split("\n")
        for i in range(len(lines)):
            line = lines[i]
            for chunk in line.split("\r"):
                if chunk:
                    lines[i] = chunk
        return "\n".join(lines)

    def validate(self, blockname, block, filename=None, **kwargs):
        if blockname == "shell":
            return True
        return False
    
    def process(self, blockname, block, id, **kwargs):
        if id == "runtime":
            self.exec(self.runtime_sock, "\x03")
            return self.exec(self.runtime_sock, block.text.replace("\x06", "<").replace("\x07", ">").replace("\x08", "&").strip())
        else:
            self.exec(self.mainshell_sock, "\x03")
            return self.exec(self.mainshell_sock, block.text.replace("\x06", "<").replace("\x07", ">").replace("\x08", "&").strip())
