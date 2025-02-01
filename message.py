import json
import textwrap
from typing import Literal, Generator, Tuple, Dict, Any
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from lxml import etree, html
import re


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

    @property
    def codeblocks(self) -> Generator[Dict[str, Any], None, None]:
        tags = ["message", "workspace", "code", "shell", "new", "code-replace", "original"]
        xml = self.to_xml()
        xml = xml.replace("<", "šŠ").replace(">", "Šš").replace("&", "ŝ")
        for tag in tags:
            pattern = rf"šŠ(/?{tag}[^Š\n\r]*?)Šš"
            xml = re.sub(pattern, lambda x: f"<{x.group(1)}>", xml)
        parser = etree.XMLParser(remove_blank_text=True, recover=True)
        tree = html.fromstring(xml, parser=parser)
        blocks = tree.xpath("//workspace/*")
        for block in blocks:
            for element in list(block.iterdescendants()) + [block]:
                if element.text:
                    element.text = element.text.replace("šŠ", "<").replace("Šš", ">").replace("ŝ", "&")
                if element.tail:
                    element.tail = element.tail.replace("šŠ", "<").replace("Šš", ">").replace("ŝ", "&")
            codeblock = {"block": block, "blockname": block.tag}
            codeblock.update(block.attrib)
            yield codeblock


if __name__ == "__main__":
    msg = Message("system", "Hello\n<code filename=\"f.txt\">this is text</code>\n<shell>sudo apt install python3</shell>")
    for code in msg.codeblocks:
        print(code)
    
