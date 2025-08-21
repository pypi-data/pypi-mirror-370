from typing import Dict
import logging
from collections import defaultdict

from .numeral_data_collector import NumeralDataContainer, NumeralDataCollector
from .numeral_data_collector.numeral_data_collector import NumeralDataLoader


logger = logging.getLogger(__name__)

_NUMERAL_LANGUAGE_DATA: Dict[str, NumeralDataContainer] = defaultdict(lambda: None)
_numeral_data_collector = NumeralDataCollector()
_numeral_data_loader = NumeralDataLoader()


def _get_language_data(lang: str):
    """
    Check if the language is already loaded, and if not, load the necessary language data.

    Args:
        lang (str): The language code (e.g., 'en', 'uk', 'ru').
    """
    if _NUMERAL_LANGUAGE_DATA[lang] is None:
        logger.debug(f"Loading language data for: {lang}")
        _NUMERAL_LANGUAGE_DATA[lang] = _numeral_data_collector.collect(lang)
    return _NUMERAL_LANGUAGE_DATA[lang]


def get_available_languages():
    available_languages = _numeral_data_loader.get_available_languages()
    return available_languages


def get_max_order(lang):
    language_data = _get_language_data(lang)
    return language_data.max_order


def get_max_numeral_word_number(lang):
    language_data = _get_language_data(lang)
    return language_data.max_numeral_word_number
