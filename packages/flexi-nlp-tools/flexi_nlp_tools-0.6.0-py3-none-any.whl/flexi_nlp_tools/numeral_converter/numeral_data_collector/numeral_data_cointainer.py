from typing import Dict, Set, Optional
from dataclasses import dataclass

from flexi_nlp_tools.flexi_dict import FlexiDict

from .numeral_data_loader.numeral_data import NumeralData


@dataclass
class NumeralDataContainer:
    numeral_data: NumeralData
    flexi_index: FlexiDict
    value_index: Dict[int, Set[int]]
    max_order: int
    max_numeral_word_number: Optional[int] = None

    def __post_init__(self):
        self.max_numeral_word_number = (self.max_order // 3 + 1) * 4
