from typing import Optional
from dataclasses import dataclass
from enum import Enum


class NumClass(str, Enum):
    """Enumeration for different types of numerals.

    Attributes:
        CARDINAL: Represents cardinal numbers (e.g., one, two, three).
        COLLECTIVE: Represents collective numerals (e.g., pair, dozen, двое).
        ORDINAL: Represents ordinal numbers (e.g., first, second, third).
    """
    CARDINAL = 'cardinal'      # en: one, two, three etc.
    COLLECTIVE = 'collective'  # en: pair, dozen; uk: двое, троє, сотня
    ORDINAL = 'ordinal'        # en: first, second, third, etc.


class Case(str, Enum):
    """Enumeration for grammatical cases in languages with declension.

    Attributes:
        ACCUSATIVE: Accusative case.
        DATIVE: Dative case.
        GENETIVE: Genitive case.
        INSTRUMENTAL: Instrumental case.
        NOMINATIVE: Nominative case.
        PREPOSITIONAL: Prepositional case.
    """
    ACCUSATIVE = 'accusative'
    DATIVE = 'dative'
    GENETIVE = 'genetive'
    INSTRUMENTAL = 'instrumental'
    NOMINATIVE = 'nominative'
    PREPOSITIONAL = 'prepositional'


class Gender(str, Enum):
    """Enumeration for grammatical genders.

    Attributes:
        FEMININE: Feminine gender.
        MASCULINE: Masculine gender.
        NEUTER: Neuter gender.
    """
    FEMININE = 'feminine'
    MASCULINE = 'masculine'
    NEUTER = 'neuter'


class Number(str, Enum):
    """Enumeration for singular and plural number forms.

    Attributes:
        PLURAL: Plural form.
        SINGULAR: Singular form.
    """
    PLURAL = 'plural'
    SINGULAR = 'singular'


@dataclass
class MorphForm:
    """Base class for all enumerations, ensuring they are logically related."""
    pass


@dataclass
class NumeralEntry:
    """Represents a numeral with its string representation, value, and grammatical attributes.

    Attributes:
        string (str): The string representation of the numeral (e.g., "one", "two").
        value (int): The numeric value of the numeral (e.g., 1, 2, 3).
        order (int): The order of the numeral in a sequence (e.g., 1 for first, 2 for second).
        num_class (NumClass): The class of the numeral (e.g., cardinal, ordinal).
        scale (bool): Whether the numeral is a scaled number (e.g., million, billion).
        case (Optional[Case]): The grammatical case of the numeral (optional).
        gender (Optional[Gender]): The grammatical gender of the numeral (optional).
        number (Optional[Number]): The number form (singular or plural) of the numeral (optional).
    """
    string: str
    value: int
    order: int
    scale: bool

    num_class: NumClass
    case: Optional[Case] = None
    gender: Optional[Gender] = None
    number: Optional[Number] = None
