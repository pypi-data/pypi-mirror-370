from typing import List, Optional
from .numeral_converter_helpers import NumberItem, preprocess_numeral, _number_items2int
from .numeral_converter_loader import _get_language_data
from .patterns import WORD_PATTERN
from .config import MAX_CORRECTION_RATE_FOR_TEXT


def convert_numerical_in_text(
    text: str,
    lang: str,
    max_correction_rate: Optional[int] = None,
    # multi_threaded: bool = True
) -> str:
    """
    Converts numerical string in text into integer values

    :param str text: input text
    :param str lang: input text language
    :param Optional[float] max_correction_rate: default value to calculate
           maximum number of corrections in the query key when searching
           for a matching dictionary key; default = None
           calculated as round(max_corrections_relative * token_length)
    :return str: updated text with converted numerical into integer

    :Example:

    >>> s = "У цій школі працює шість психологів, "
    ...     "і кожен із нас має навантаження понад сто учнів"
    >>> convert_numerical_in_text(s, lang='uk')
    "У цій школі працює 6 психологів, і кожен із нас має навантаження понад 100 учнів"

    >>> s = "У моєму портфелі лежало чотири книги."
    >>> convert_numerical_in_text(s, lang='uk')
    "У моєму портфелі лежало 4 книги."

    """
    # if multi_threaded:
    #     return _convert_numerical_in_text_multi_threaded(text, lang, max_correction_rate)
    if max_correction_rate is None:
        max_correction_rate = MAX_CORRECTION_RATE_FOR_TEXT

    lang_data = _get_language_data(lang)

    updated_text = str()
    i = 0

    number_items: List[NumberItem] = list()
    prev_number_end = None

    for match in WORD_PATTERN.finditer(text):

        number_idxs = lang_data.flexi_index.get(
            preprocess_numeral(match.group(), lang=lang),
            max_correction_rate=max_correction_rate
        )

        if number_idxs:
            idx = number_idxs[0]
            numeral_entry = lang_data.numeral_data[idx]
            number_item = NumberItem(numeral_entry.value, numeral_entry.order, numeral_entry.scale)

            # number starts
            if not len(number_items):
                updated_text += text[i : match.span()[0]]
                number_items.append(number_item)
                prev_number_end = match.span()[1]
                i = match.span()[1]

            # number continues
            elif match.span()[0] - prev_number_end < 2:
                number_items.append(number_item)
                prev_number_end = match.span()[1]
                i = match.span()[1]

            # prev number ends, new number starts
            else:
                updated_text += str(_number_items2int(number_items))
                updated_text += text[i: match.span()[0]]
                number_items = [
                    number_item,
                ]
                prev_number_end = match.span()[1]
                i = match.span()[1]

    if number_items:
        updated_text += str(_number_items2int(number_items))

    updated_text += text[i:]
    return updated_text
