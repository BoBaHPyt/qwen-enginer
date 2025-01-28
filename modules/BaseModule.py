from pathlib import Path


class BaseModule:
    workhome: Path
    name: str
    
    def __init__(self, workhome):
        self.workhome = workhome

    def validate(self, block):
        return False

    def process(self, block):
        return False

    def close(self):
        pass
