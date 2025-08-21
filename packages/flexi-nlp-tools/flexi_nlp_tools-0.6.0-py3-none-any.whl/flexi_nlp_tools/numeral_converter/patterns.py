import re

WORD_PATTERN = re.compile("[a-zA-Zа-яА-ЯїЇґҐєЄёЁіІ'’]+")
ENGLISH_RULES = re.compile(r"(\sand\s|-and-|\-)")
MULTIPLE_SPACES = re.compile(r"\s+")
