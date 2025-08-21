from typing import List, Tuple, Callable, Optional, Union
from itertools import chain
import logging

from .utils import tokenize, detokenize
from .config import MIN_START_TOKEN_LENGTH
from .search_index import SearchIndex


logger = logging.getLogger(__name__)


def build_search_index(
        data: List[Tuple[Union[int, str], str]],
        min_start_token_length: int = MIN_START_TOKEN_LENGTH,
        callback: Optional[Callable] = None,
        should_stop: Optional[Callable] = None,
        callback_step: int = 10000
) -> SearchIndex:
    search_index = SearchIndex()
    update_search_index(
        search_index=search_index,
        data=data,
        min_start_token_length=min_start_token_length,
        callback=callback,
        should_stop=should_stop,
        callback_step=callback_step)
    return search_index


def update_search_index(
        search_index: SearchIndex,
        data: List[Tuple[int, str]],
        min_start_token_length: int = MIN_START_TOKEN_LENGTH,
        callback: Optional[Callable] = None,
        should_stop: Optional[Callable] = None,
        callback_step: int = 10000
):

    for i, (idx, key) in enumerate(data):
        if i % callback_step == 0:

            if callback:
                callback(i / len(data))

            if should_stop and should_stop():
                break

        search_index[0][key.lower()] = idx

        tokens, seps = tokenize(key)
        if len(seps) == len(tokens):
            seps[-1] += ' '
        else:
            seps.append(' ')
        for i_token in range(1, len(tokens)):

            if len(tokens[i_token]) < min_start_token_length:
                continue

            alt_tokens = list(chain(tokens[i_token:], tokens[:i_token]))
            alt_seps = list(chain(seps[i_token:], seps[:i_token]))
            alt_key = detokenize(alt_tokens, alt_seps).strip()
            search_index[1][alt_key.lower()] = idx

