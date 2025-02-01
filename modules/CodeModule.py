from . import BaseModule
from pathlib import Path
import re


class CodeModule(BaseModule):
    name = "code"

    def validate(self, blockname, block, filename=None, **kwargs):
        if blockname == self.name:
            assert filename, "<code> The mandatory filename attribute is not set."
            replace_blocks = block.xpath("code-replace")
            if replace_blocks:
                for replace_block in replace_blocks:
                    assert len(replace_block.xpath("original")) == 1, "The <code-replace> block expects one <original> block and one <new> block."
                    assert len(replace_block.xpath("new")) == 1, "The <code-replace> block expects one <original> block and one <new> block."
            return True
        return False

    def __write(self, filename, content:str, mode="w"):
        filename.parent.mkdir(parents=True, exist_ok=True)
        with open(filename, mode) as file:
            file.write(content)

    def __replace(self, filename, original, new):
        content = None
        with open(filename, "r") as file:
            content = file.read()
        if original[-1] == "\n":
            original = original[:-1]

        lines = original.split("\n")
        for i in range(len(lines)):
            while lines[i].startswith(" "):
                lines[i] = lines[i][1:]
            lines[i] = fr"\s*{lines[i]}"
        pattern = "\n".join(lines)
        assert re.findall(pattern, content), f"<original> not in file {filename}"
        content = re.sub(pattern, new, content, 1)
        self.__write(filename, content, "w")
    
    def process(self, blockname, block, filename, **kwargs):
        orig_filename = filename
        filename = self.workhome / Path(filename)
        filename = filename.expanduser()
        replace_blocks = block.xpath("code-replace")
        new_blocks = block.xpath("new")
        if replace_blocks:
            for replace_block in replace_blocks:
                original = replace_block.xpath("original/text()")[0].replace("\x06", "<").replace("\x07", ">").replace("\x08", "&")
                repl = replace_block.xpath("new/text()")[0].replace("\x06", "<").replace("\x07", ">").replace("\x08", "&")
                self.__replace(filename, original, repl)
        if new_blocks:
            for new_block in new_blocks:
                text = new_block.text.replace("\x06", "<").replace("\x07", ">").replace("\x08", "&")
                self.__write(filename, f"\n{text}", "a+")
        if not replace_blocks and not new_blocks:
            text = block.text.replace("\x06", "<").replace("\x07", ">").replace("\x08", "&")
            self.__write(filename, text)
        return f"{orig_filename} successfully changed"
