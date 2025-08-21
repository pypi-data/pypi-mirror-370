import bisect
from typing import Optional

from flexi_nlp_tools.flexi_dict.search_engine.fuzzy_search_result import FuzzySearchResult

from .search_index import SearchIndex
from .config import DEFAULT_QUERY_TRANSFORMATION_PRICE
from ..flexi_dict.exceptions import InvalidScoresError
from .exceptions import EmptyQueryError


def fuzzy_search(
        query: str,
        search_index: SearchIndex,
        topn: Optional[int] = None,
        query_transformation_price: float = DEFAULT_QUERY_TRANSFORMATION_PRICE
):
    fuzzy_search_result = fuzzy_search_internal(
        query=query,
        search_index=search_index,
        topn=topn,
        query_transformation_price=query_transformation_price)

    return [item.value for item in fuzzy_search_result]


def fuzzy_search_internal(
        query: str,
        search_index: SearchIndex,
        topn: Optional[int] = None,
        query_transformation_price: float = DEFAULT_QUERY_TRANSFORMATION_PRICE
):
    if not 0 <= query_transformation_price <= 1:
        raise InvalidScoresError([query_transformation_price, ])

    if not query:
        raise EmptyQueryError()

    search_result = list()
    added = set()

    for rate in sorted(search_index):
        n = 0
        rate_search_result = search_index[rate].search_internal(query=query)

        for item in rate_search_result:

            if item.value in added:
                continue

            added.add(item.value)
            if rate:
                # print(item.path, item.total_corrections_price)
                total_correction_price = __update_total_corrections_price(
                    item=item, rate=rate, query=query, query_transformation_price=query_transformation_price)
                item.set_total_correction_price(total_correction_price)

            pos = bisect.bisect_left(
                search_result, item.total_corrections_price, lo=0, hi=len(search_result),
                key=lambda x: x.total_corrections_price)
            search_result.insert(pos, item)
            n += 1
            if topn and n > topn:
                break

    if search_result:
        return search_result[:topn]

    return search_result


def __update_total_corrections_price(
        item: FuzzySearchResult, query: str, rate: int, query_transformation_price: float
):
    total_corrections_price = item.total_corrections_price
    if rate:
        total_corrections_price += query_transformation_price
        total_corrections_price += 1e-5 * __get_path_key_dist(item.path, item.key, query)

    return total_corrections_price


def __get_path_key_dist(path: str, key: str, query: str) -> float:
    """
    Посчитать цену разницы между длинами запроса и найденного пути для ранжирования результата поиска.

    Чем больше разница в длине - тем ниже опускаем в результате поиска.
    Ключ - это запрос с исправлениями, по которому нашли значение
    Путь - это путь в дереве до листка дереве, в котором лежит найденное значение

    Например, ключем может быть "ман" а путем - "мандарин" или "манка"

    :param str path: путь в дереве, по которому был найдено значение
    :param str key: ключ, по которому был найдено значение

    :return float: нормализированная цена разницы между длинами

    """
    # абсолютная разница между длиной пути и длиной ключа
    # если длина пути меньше длины запроса, то удваиваем путь;
    # например, если искали "ябл", а нашли "я" и "яблок", то "я" нужно опустиь ниже по рангу
    len_path, len_key, len_query = len(path), len(key), len(query)
    dist = len_path - len_key if len_path >= len_query else (len_query - len_path) ** 3

    # абсолютная разница между длиной последнего токена
    start = key.rfind(' ') + 1 if ' ' in key else 0
    len_path_last_token = (path[start:] + ' ').find(' ')
    len_key_last_token = len(key) - start
    len_token_dist = abs(len_path_last_token - len_key_last_token)

    # комбинируем расстояния
    if len_path >= len_query and not len_token_dist:
        dist = 0

    return dist
