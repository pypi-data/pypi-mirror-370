from typing import List
from dataclasses import dataclass

from ..flexi_trie import FlexiTrieNode
from .correction_detail import CorrectionDetail


@dataclass
class SearchState:
    position: int
    path: str
    node: FlexiTrieNode
    corrections: List[CorrectionDetail]
