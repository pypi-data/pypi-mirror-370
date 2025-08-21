from typing import Dict

from ....flexi_dict import FlexiDict
from ....flexi_dict.search_engine import (
    SearchEngine, SymbolInsertion, SymbolsDeletion, SymbolSubstitution, SymbolsTransposition
)
from ..numeral_data_loader.numeral_entry import NumeralEntry


class FlexiIndexBuilder:
    """Class responsible for building a FlexiDict index from numeral data.

    The index is built by extracting strings from the NumeralEntry data and mapping them
    to the corresponding numeral entry IDs. This index is then used for efficient search
    and retrieval of numeral data.
    """
    def __init__(self):
        """
        Initialize the IndexBuilder with a search engine and optional symbol weights.
        """
        corrections = [
            SymbolInsertion(),
            SymbolsTransposition(),
            SymbolsDeletion(),
            SymbolSubstitution()
        ]
        self.__search_engine = SearchEngine(corrections=corrections, symbol_insertion=SymbolInsertion())

    def build(self, numeral_data: Dict[int, NumeralEntry]) -> FlexiDict:
        """Build a FlexiDict index from the provided numeral data.

        Args:
            numeral_data (Dict[int, NumeralEntry]): A dictionary of NumeralEntry objects with unique IDs.

        Returns:
            FlexiDict: A FlexiDict index containing numeral data, where the key is the numeral string
                       and the value is the associated ID of the NumeralEntry.
        """
        numeral_flexi_dict = FlexiDict(self.__search_engine)

        for idx, numeral_entry in numeral_data.items():
            numeral_flexi_dict[numeral_entry.string] = idx

        return numeral_flexi_dict
