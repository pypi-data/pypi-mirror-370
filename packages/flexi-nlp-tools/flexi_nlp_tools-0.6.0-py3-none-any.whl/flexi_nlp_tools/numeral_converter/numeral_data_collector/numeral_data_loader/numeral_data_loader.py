from typing import List
import pandas as pd
from ...config import NUMERAL_CONVERTER_DATA_PATH
from .numeral_entry import NumeralEntry, Case, Gender, NumClass, Number
from .numeral_data import NumeralData
from ...numeral_preprocessor import preprocess_number_string
from ...utils import transform_to_morph_form


class NumeralDataLoader:
    """Class responsible for loading numeral data for different languages.

    This class handles loading numeral-related data from CSV files, including
    processing values based on their order, and storing the resulting data
    as instances of NumeralEntry.
    """

    # Cache for loaded languages
    __loaded_languages_cache: List[str] = []

    def load_language_data(self, lang: str):
        """Load numerical data for a specific language from a CSV file.

        Args:
            lang (str): The language code (e.g., 'en', 'uk').

        Raises:
            ValueError: If the file for the given language does not exist.

        This method reads the corresponding CSV file for the specified language,
        processes the data, and stores the numerical entries in a dictionary.
        """
        if not self.is_available_language(lang):
            raise ValueError(
                f'The specified language "{lang}" is not supported. '
                f'Please select one of the following: {", ".join(self.get_available_languages())}')

        filename = NUMERAL_CONVERTER_DATA_PATH / f'{lang}.csv'
        df = pd.read_csv(filename, sep=",", dtype={'order': int})
        df = df.apply(lambda col: col.map(lambda x: None if pd.isnull(x) else x))

        numeral_data = NumeralData()
        for i, row in df.iterrows():
            num_class = transform_to_morph_form(row.get('num_class'), NumClass)
            case = transform_to_morph_form(row.get('case'), Case)
            gender = transform_to_morph_form(row.get('gender'), Gender)
            number = transform_to_morph_form(row.get('number'), Number)
            value = int(row['value']) if row['order'] < 6 else 10 ** row['order']

            for string in row["string"].split(' '):
                if not string:
                    continue
                string = preprocess_number_string(string)

                idx = len(numeral_data) + 1
                numeral_data[idx] = NumeralEntry(
                    string=string,
                    order=row['order'],
                    num_class=num_class,
                    scale=row['scale'],
                    case=case,
                    gender=gender,
                    number=number,
                    value=value)

        return numeral_data

    def get_available_languages(self):
        """Return list of available languages by reading the directory.

        This method loads and caches the list of languages from the CSV filenames
        in the NUMERAL_CONVERTER_DATA_PATH folder.

        Returns:
            List[str]: List of language codes (e.g., ['en', 'uk']).

        This method ensures that the list of available languages is only loaded
        once and then cached for future calls.
        """
        if not self.__loaded_languages_cache:
            self.__loaded_languages_cache = [filename.stem for filename in NUMERAL_CONVERTER_DATA_PATH.glob('*.csv')]

        return self.__loaded_languages_cache

    def is_available_language(self, lang: str):
        """Check if a language is available in the data.

        Args:
            lang (str): The language code to check.py.

        Returns:
            bool: True if the language is available, False otherwise.

        This method checks if the language code is available in the list of
        loaded languages.
        """
        return lang in self.get_available_languages()
