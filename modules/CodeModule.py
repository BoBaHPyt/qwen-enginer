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
        pattern = original.replace("\n", "\n\s*")
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
                self.__replace(filename, replace_block.xpath("original/text()")[0], replace_block.xpath("new/text()")[0])
        if new_blocks:
            for new_block in new_blocks:
                self.__write(filename, f"\n{new_block.text}", "a+")
        if not replace_blocks and not new_blocks:
            self.__write(filename, block.text)
        return f"{orig_filename} successfully changed"
