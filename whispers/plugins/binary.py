import re

from pathlib import Path

from whispers.plugins.uri import Uri
from whispers.rules import WhisperRules
from whispers.utils import strip_string, strings

class Bin:
    def __init__(self):
        self.rules = WhisperRules()

    def pairs(self, filepath: Path):
        yield "Binary string", None
        # lines = strings(filepath, 10)
        # for line in lines:
        #     for word in line.split():
        #         if len(word)<10:
        #             continue
        #         if not strip_string(word):
        #             continue
        #         if not re.match("^[A-Za-z]*$", word):
        #             continue
        #         if not re.match("^[0-9]*$", word):
        #             continue
        #         if word.isalnum():
        #             continue
        #         # TODO Measure entropy
        #         yield "Binary string", word
