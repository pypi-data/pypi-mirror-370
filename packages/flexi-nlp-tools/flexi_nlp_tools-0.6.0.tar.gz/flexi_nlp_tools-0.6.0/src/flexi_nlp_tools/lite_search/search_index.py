from typing import Dict
from dataclasses import dataclass

from ..flexi_dict import FlexiDict
from ..flexi_dict.search_engine.correction import SymbolInsertion
from ..flexi_dict.search_engine import SearchEngine


@dataclass
class SearchIndex(Dict[int, 'FlexiDict']):

    def __getitem__(self, key: int) -> 'FlexiDict':
        if key not in self:
            search_engine = SearchEngine(symbol_insertion=SymbolInsertion(price=1e-5))
            self[key] = FlexiDict(search_engine=search_engine)
        return super().__getitem__(key)
