import json
import textwrap
from typing import Literal, Generator, Tuple, Dict, Any
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from lxml import etree

etree.XMLParser()
@dataclass(eq=False, frozen=True)
class Message:
    role: Literal["system", "user", "assistant"]
    content: str
    pinned: bool = False
    hide: bool = False
    quiet: bool = False
    timestamp: datetime = field(default_factory=datetime.now)
    files: list[Path] = field(default_factory=list)

    def __repr__(self):
        content = textwrap.shorten(self.content, 20, placeholder="...")
        return f"<Message role={self.role} content={content}>"

    def __eq__(self, other):
        # FIXME: really include timestamp?
        if not isinstance(other, Message):
            return False
        return (
            self.role == other.role
            and self.content == other.content
            and self.timestamp == other.timestamp
        )

    def to_dict(self, keys=None) -> dict:
        """Return a dict representation of the message, serializable to JSON."""

        d: dict = {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
        }
        if self.files:
            d["files"] = [str(f) for f in self.files]
        if self.pinned:
            d["pinned"] = True
        if self.hide:
            d["hide"] = True
        if keys:
            return {k: d[k] for k in keys if k in d}
        return d

    def to_xml(self) -> str:
        """Converts a message to an XML string."""
        attrs = f"role='{self.role}'"
        content = self.content
        return f"<message {attrs}>\n{content}\n</message>"

    def cdata(self, element, recursive=["code", "new", "code-replace", "original", "shell"]):
        code_replace_elements = []
        # Собираем текст, исключая содержимое <code-replace>
        cdata_text = []
        # Проходим по всем дочерним элементам внутри <code> 
        for child in element:
            if child.tag in recursive:
                code_replace_elements.append(self.cdata(child))
            else:
                cdata_text.append(etree.tostring(child).decode())
        
            if child.tail.strip():
                cdata_text.append(child.tail.strip())
                child.tail = ""
    
        if element.text:
            cdata_text.insert(0, element.text.strip())
    
        cdata_text = '\n'.join(cdata_text)
        element.clear()

        if cdata_text:
            cdata = etree.CDATA(cdata_text)
            element.text = cdata
        
        for child in code_replace_elements:
            element.append(child)

        return element

    @property
    def codeblocks(self) -> Generator[Dict[str, Any], None, None]:
        xml = self.to_xml()
        parser = etree.XMLParser(remove_blank_text=True, recover=True)
        tree = etree.fromstring(xml, parser)
        blocks = tree.xpath("//workspace/*")
        for block in blocks:
            codeblock = {}
            codeblock.update(block.attrib)
            block = self.cdata(block)
            codeblock.update({"block": block, "blockname": block.tag})
            yield codeblock


if __name__ == "__main__":
    msg = Message("system", "Hello\n<code filename=\"f.txt\">this is text</code>\n<shell>sudo apt install python3</shell>")
    for code in msg.codeblocks:
        print(code)
    
