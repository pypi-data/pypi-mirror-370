from typing import List, Optional, Union

from .config import MAX_CORRECTION_RATE_FOR_SEARCH

from .validators import validate_symbol_weights
from .search_engine import SearchEngine
from .search_engine.fuzzy_search_result import FuzzySearchResult
from .flexi_trie import FlexiTrie


class FlexiDict:

    _trie: FlexiTrie
    _search_engine: SearchEngine

    def __init__(
        self,
        search_engine: Optional[SearchEngine] = None,
    ):

        self._trie = FlexiTrie()
        self._search_engine = search_engine or SearchEngine()

    def __setitem__(self, keyname: str, value_id: Union[int, str]):
        """
        Adds a value to the prefix tree under the specified key.

        Args:
            keyname (str): The key under which to store the value.
            value_id (int): The identifier of the value.

        """
        self._trie.add(keyname, value_id, self._search_engine.symbol_weights)

    def __getitem__(self, query: str) -> Optional[Union[str, int]]:
        """
        Retrieves the first value associated with the specified key.

        Args:
            query (str): The key for which to retrieve the value.

        Returns:
            int: The first value associated with the specified key.

        Raises:
            TypeError: If `query` is not a string.
            KeyError: If the `query` key is not found in the dictionary.
        """
        exact_match_values = self._trie.find(query)
        if exact_match_values:
            return next(iter(exact_match_values))

        fuzzy_match_values = self.get(query)
        if fuzzy_match_values:
            return fuzzy_match_values[0]

        return None

    def get(
            self,
            query: str,
            max_correction_rate: Optional[float] = None,
            max_correction_rate_for_leaves: Optional[float] = None) -> List[Union[str, int]]:

        fuzzy_match_items = self._search_engine.search(
            trie=self.trie,
            query=query,
            max_correction_rate=max_correction_rate,
            max_correction_rate_for_leaves=max_correction_rate_for_leaves)

        return [item.value for item in fuzzy_match_items]

    def search(
            self,
            query: str,
            max_correction_rate: Optional[float] = None,
            max_correction_rate_for_leaves: Optional[float] = None
    ) -> List[Union[str, int]]:

        if max_correction_rate_for_leaves is None:
            max_correction_rate_for_leaves = MAX_CORRECTION_RATE_FOR_SEARCH

        return [
            item.value
            for item in self.search_internal(
                query=query,
                max_correction_rate=max_correction_rate,
                max_correction_rate_for_leaves=max_correction_rate_for_leaves)]

    def search_internal(
            self,
            query: str,
            max_correction_rate: Optional[float] = None,
            max_correction_rate_for_leaves: Optional[float] = None) -> List[FuzzySearchResult]:

        if max_correction_rate_for_leaves is None:
            max_correction_rate_for_leaves = MAX_CORRECTION_RATE_FOR_SEARCH

        fuzzy_match_items = self._search_engine.search(
            trie=self.trie,
            query=query,
            max_correction_rate=max_correction_rate,
            max_correction_rate_for_leaves=max_correction_rate_for_leaves
        )

        return fuzzy_match_items

    @property
    def trie(self):
        return self._trie
