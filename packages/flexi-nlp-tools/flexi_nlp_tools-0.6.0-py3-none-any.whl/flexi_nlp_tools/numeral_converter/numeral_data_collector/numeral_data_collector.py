from typing import Dict
from collections import defaultdict

from .numeral_data_cointainer import NumeralDataContainer
from .numeral_data_loader import NumeralDataLoader
from .numeral_data_loader.numeral_entry import NumeralEntry
from .flexi_index_builder import FlexiIndexBuilder


class NumeralDataCollector:

    def __init__(self):
        self.__numeral_data_loader = NumeralDataLoader()
        self.__flexi_index_builder = FlexiIndexBuilder()

    def collect(self, lang: str) -> NumeralDataContainer:
        numeral_data = self.__numeral_data_loader.load_language_data(lang)
        flexi_index = self.__flexi_index_builder.build(numeral_data)
        value_index = self.__collect_value_index(numeral_data)
        max_number_order = max([x.order for x in numeral_data.values() if x])
        max_order = max_number_order + (max_number_order - 1)
        return NumeralDataContainer(
            numeral_data=numeral_data,
            flexi_index=flexi_index,
            value_index=value_index,
            max_order=max_order
        )

    @staticmethod
    def __collect_value_index(numeral_data: Dict[int, NumeralEntry]):
        value_index = defaultdict(set)
        for idx, numeral_entry in numeral_data.items():
            value_index[numeral_entry.value].add(idx)
        return value_index
