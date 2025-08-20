from enum import Enum


class EmailBodyType(str, Enum):
    HTML = "html"
    PLAIN = "plain"
