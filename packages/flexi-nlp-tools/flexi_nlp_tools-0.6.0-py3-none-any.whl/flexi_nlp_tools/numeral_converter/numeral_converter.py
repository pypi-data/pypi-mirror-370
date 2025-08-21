import logging
from typing import Optional, Dict, Any
import math

from .numeral_data_collector.numeral_data_loader.numeral_entry import Case, Gender, Number, NumClass
from .numeral_converter_helpers import (
    _numeral2number_items,
    _int2number_items,
    _number_items2int,
    _number_items2numeral
)
from .numeral_converter_loader import _get_language_data, get_max_numeral_word_number, get_max_order
from .config import MAX_NUMERAL_LENGTH
from .utils import transform_to_morph_form


logger = logging.getLogger(__name__)


def numeral2int(numeral: str, lang: str, multi_threaded: bool = True) -> Optional[int]:
    """
    Converts the input numeral (in the form of a string) into an integer value for the given language.

    Args:
        numeral (str): The input numeral string (e.g., "forty two").
        lang (str): The language code (e.g., 'en', 'uk').

    Returns:
        Optional[int]: The corresponding integer value, or None if conversion fails.

    Example:
        >>> numeral2int("сорок два", lang="uk")
        42
    """
    language_data = _get_language_data(lang)

    length = len(numeral)
    if length > MAX_NUMERAL_LENGTH:
        raise ValueError(
            f'too long numeral; '
            f'expected numeral with less than {MAX_NUMERAL_LENGTH} symbols; got {length}.')

    words_number = len(numeral.split())
    max_order = get_max_order(lang)
    max_words_number = get_max_numeral_word_number(lang)
    if words_number > max_words_number:
        raise ValueError(
            f'For language "{lang}", only numbers of order less than or equal to "{max_order}" are supported; '
            f'expected numeral with less than {max_words_number} words.')

    logger.info(f"Converting numeral '{numeral}' to integer in language '{lang}'")

    number_items = _numeral2number_items(
        numeral=numeral, lang=lang,
        numeral_data=language_data.numeral_data,
        flexi_index=language_data.flexi_index,
        multi_threaded=multi_threaded
    )

    value = _number_items2int(number_items=number_items)
    return value


def int2numeral(
        value: int,
        lang: str,
        case: Optional[Case] = None,
        num_class: Optional[NumClass] = None,
        gender: Optional[Gender] = None,
        number: Optional[Number] = None) -> str:
    """
    Converts an integer to its corresponding numeral string in the given language and morphological form.

    Args:
        value (int): The input integer value (e.g., 42).
        lang (str): The language code (e.g., 'en', 'uk').
        case (Optional[Case]): The grammatical case to apply.
        num_class (Optional[NumClass]): The numerical class (e.g., ordinal, cardinal).
        gender (Optional[Gender]): The grammatical gender (e.g., masculine, feminine).
        number (Optional[Number]): The number form (singular or plural).

    Returns:
        str: The corresponding numeral string in the given morphological form.

    Example:
        >>> int2numeral(42, lang='uk', case="nominative", num_class="cardinal")
        'сорок два'
    """
    numeral = __int2numerals(value, lang, case, num_class, gender, number)
    return numeral['numeral']


def int2numerals(
        value: int,
        lang: str,
        case: Optional[Case] = None,
        num_class: Optional[NumClass] = None,
        gender: Optional[Gender] = None,
        number: Optional[Number] = None) -> str:
    """
    Converts an integer to its corresponding numeral string in the given language and morphological form.

    Args:
        value (int): The input integer value (e.g., 42).
        lang (str): The language code (e.g., 'en', 'uk').
        case (Optional[Case]): The grammatical case to apply.
        num_class (Optional[NumClass]): The numerical class (e.g., ordinal, cardinal).
        gender (Optional[Gender]): The grammatical gender (e.g., masculine, feminine).
        number (Optional[Number]): The number form (singular or plural).

    Returns:
        str: The corresponding numeral string in the given morphological form.

    Example:
        >>> int2numeral(42, lang='uk', case="nominative", num_class="cardinal")
        'сорок два'
    """
    numeral = __int2numerals(value, lang, case, num_class, gender, number)
    return numeral['numeral_forms']


def __int2numerals(
        value: int,
        lang: str,
        case: Optional[Case] = None,
        num_class: Optional[NumClass] = None,
        gender: Optional[Gender] = None,
        number: Optional[Number] = None) -> Dict[str, any]:

    language_data = _get_language_data(lang)

    if value != 0:
        order = int(round(math.log(value, 10)))
        max_order = get_max_order(lang)

        if order > max_order:
            raise ValueError(
                f'Numbers of order {order} are not supported. '
                f'For language "{lang}", only numbers of order less than or equal to {max_order} are supported.')

    number_items = _int2number_items(value, lang)

    numeral = _number_items2numeral(
        number_items,
        lang=lang,
        numeral_data=language_data.numeral_data,
        value_index=language_data.value_index,
        case=transform_to_morph_form(case, Case),
        num_class=transform_to_morph_form(num_class, NumClass),
        gender=transform_to_morph_form(gender, Gender),
        number=transform_to_morph_form(number, Number)
    )

    return numeral
