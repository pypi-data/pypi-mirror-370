from dataclasses import dataclass, field
from math import ceil
from typing import Union


@dataclass
class MessageSmartEncoding:
    """
    Sms Message Representation
    """

    replacements = {
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "–": "-",
        "—": "-",
        "…": "...",
        "•": "-",
        "€": "EUR",
        "™": "",
        "©": "",
        "®": "",
        "\u0002": "",
        "\u001b": "",
    }
    body: Union[str, list]
    normalized_text: str = field(init=False)
    length: int = field(init=False)
    segments: int = field(init=False)

    def __post_init__(self):
        # Convert body to string if it's a list
        if isinstance(self.body, list):
            body_text = " ".join(str(item) for item in self.body)
        else:
            body_text = self.body

        self.normalized_text = self.normalize(body_text)
        self.length = len(self.normalized_text)
        self.segments = ceil(self.length / 160)

    def normalize(self, text: str) -> str:
        for char, replacement in self.replacements.items():
            text = text.replace(char, replacement)
        return text
