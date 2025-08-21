import re

from .tokenizer import tokenize, detokenize


CONSONANTS_EN = 'BCDFGHKLMNPQRSTVWXZ'


REGEX_RULES_EN2UK = [
    (rf'([{CONSONANTS_EN}][{CONSONANTS_EN}]+)I([{CONSONANTS_EN}]+)', r'\1І\2'),
    (rf'^([{CONSONANTS_EN}]+)I$', r'\1АЙ'),
    (rf':::U([{CONSONANTS_EN}][{CONSONANTS_EN}]+)', r'А\1'),
    (rf':::([{CONSONANTS_EN}])U([{CONSONANTS_EN}][{CONSONANTS_EN}]+)', r'\1А\2'),
    (r'([CGHMPTF])U', r'\1U'),
    (r':::U', r'Ю'),
    (r'([AE])H:::', r'\1'),
    (rf':::([{CONSONANTS_EN}]+)E:::', r'\1І'),
    ('IE:::', 'АЙ'),
    ('([IE])CIAN', r'\1ШН'),
    ('([IE])CIOU', r'\1Ш'),
    ('([IE])C', r'\1Ч'),
]


STATIC_RULES_EN2UK = {
    r'TIONS:::': 'ШНС',
    r'TION:::': 'ШН',
    r'SIONS:::': 'ЖНС',
    r'SION:::': 'ЖН',
    r'CIANS:::': 'ШНС',
    r'CIAN:::': 'ШН',
    r'OUGH:::': 'У',
    r'IGHTS:::': 'АЙТС',
    r'IGHT:::': 'АЙТ',
    r'CIOUS:::': 'ШС',
    r'NCE:::': 'НС',
    'SES:::': 'СЕС',
    'XES:::': 'КСЕС',
    'IES:::': 'АЙС',
    'ATE:::': 'ЕТ',
    'ATES:::': 'ЕТС',
    'AY:::': 'АЙ',
    'OY:::': 'ОЙ',
    'Y:::': 'І',
    'YS:::': 'ЙС',
    'ES:::': 'С',
    'E:::': '',
    'S:::': 'С',
    'C:::': 'К',
    ':::WH': 'В',
    ':::GH': 'Г',
    ':::SCI': 'САЙ',
    'CE': 'СE',
    'СI': 'СI',
    'СY': 'СY',
    "UE": 'У',
    "UI": 'У',
    'UO': 'У',
    'SHCH': 'Щ',
    'SC': 'Ш',
    'KH': 'Х',
    'TS': 'Ц',
    'THR': 'ТР',
    'TH': 'С',
    'CC': 'КЦ',
    'CH': 'Ч',
    'SH': 'Ш',
    "ZH": "Ж",
    "ZJ": "Ж",
    "IU": "Ю",
    "IA": "Я",
    "IO": "ЙО",
    "IE": "Є",
    "IY": "ІЙ",
    "II": "ІЙ",
    "YA": "Я",
    "YI": "ИЙ",
    "YU": "Ю",
    "YO": "ЙО",
    "YE": "Є",
    "OO": 'У',
    'EE': 'І',
    'PH': 'Ф',
    'GH': 'Ж',
    'CK': 'К',
    'EA': 'ІА',
    "A": "А",
    "B": "Б",
    "V": "В",
    "G": "Г",
    "D": "Д",
    "E": "Е",
    "Z": "З",
    "Y": "У",
    "K": "К",
    "L": "Л",
    "M": "М",
    "N": "Н",
    "O": "О",
    "P": "П",
    "R": "Р",
    "S": "С",
    "T": "Т",
    "U": "У",
    "F": "Ф",
    "Q": "К’Ю",
    "W": "В",
    "I": "І",
    "H": "Х",
    "J": "Ж",
    "X": "КС",
    "C": "К",
    '’': 'Ь',
    '`': 'Ь'
}


STATIC_RULES_UK2RU = {
    'Є': 'Е',
    'Е': 'Е',
    'И': 'Ы',
    'І': 'И',
    'Ґ': 'Г',
    'Ї': 'ЙИ',
    '’': 'Ь',
    '`': 'Ь'
}

REGEX_RULES_EN2UK_PATTERNS = [
    (re.compile(pattern, flags=re.IGNORECASE), replacement)
    for pattern, replacement in REGEX_RULES_EN2UK
]

STATIC_RULES_EN2UK_PATTERNS = {
    re.compile(pattern, flags=re.IGNORECASE): replacement
    for pattern, replacement in STATIC_RULES_EN2UK.items()
}

STATIC_RULES_UK2RU_PATTERNS = {
    re.compile(pattern, flags=re.IGNORECASE): replacement
    for pattern, replacement in STATIC_RULES_UK2RU.items()
}


def en2uk_translit(s: str) -> str:
    tokens, sub = tokenize(s)
    tokens_translit = [_en2uk_translit(token) for token in tokens]
    s_translit = detokenize(tokens_translit, sub)
    return s_translit


def uk2ru_translit(s: str) -> str:
    tokens, sub = tokenize(s)
    tokens_translit = [_uk2ru_translit(token) for token in tokens]
    s_translit = detokenize(tokens_translit, sub)
    return s_translit


def en2ru_translit(s: str) -> str:
    s_translit = en2uk_translit(s)
    return uk2ru_translit(s_translit)


def __preserve_case(word, replacement):

    match word:

        case _ if not word.isalpha():
            result = replacement.lower()
        case _ if word.islower():
            result = replacement.lower()
        case _ if word.isupper():
            result = replacement.upper()
        case _ if word.istitle():
            result = replacement.capitalize()
        case _:
            result = replacement.lower()

    return rf'{result}'


def _en2uk_translit(token: str) -> str:
    s_translit = ':::' + token + ':::'

    for pattern, replacement in REGEX_RULES_EN2UK_PATTERNS:
        s_translit = pattern.sub(
            lambda match: __preserve_case(
                match.group(),
                pattern.sub(replacement, match.group())),
            s_translit)

    for pattern, replacement in STATIC_RULES_EN2UK_PATTERNS.items():
        s_translit = pattern.sub(lambda match: __preserve_case(match.group(), replacement), s_translit)

    return s_translit.replace(':::', '').strip()


def _uk2ru_translit(token: str) -> str:
    def repl_static(match, repl):
        return __preserve_case(match.group(0), repl)

    s_translit = token
    for pattern, replacement in STATIC_RULES_UK2RU_PATTERNS.items():
        s_translit = pattern.sub(lambda x: repl_static(x, replacement), s_translit)

    return s_translit
