from typing import Dict, List, Optional, Tuple
from collections import Counter

import math


def calculate_symbols_weights(corpus: List[str]) -> Dict[str, float]:
    """
    Calculate the probability of each symbolacter in the corpus.

    The probability of a symbolacter increases with its frequency in the corpus.
    This probability can be used for error cost estimation in queries.

    Args:
        corpus (List[str]): A list of strings representing the text corpus.
            For query analysis, it's optimal to use a list of recent queries.

    Returns:
        Dict[str, float]: A dictionary where keys are symbolacters and values are their weights.

    Raises:
        ValueError: If the corpus is empty or contains no symbolacters.
    """
    # Count the frequency of each symbolacter
    symbol_frequency = Counter(''.join(corpus))
    total_frequency = sum(symbol_frequency.values())

    if not total_frequency:
        raise ValueError("Invalid corpus: no symbolacters in the corpus.")

    # Calculate weights
    symbol_weights = {symbol: freq / total_frequency for symbol, freq in symbol_frequency.items()}

    # Normalize weights using L2 norm
    norm = math.sqrt(sum(prob ** 2 for prob in symbol_weights.values()))
    normalized_weights = {symbol: prob / norm for symbol, prob in symbol_weights.items()}

    return normalized_weights


def calculate_symbols_distances(symbol_keyboards: List[str], similar_symbols: Optional[List[str]] = None, ) -> Dict[Tuple[str, str], float]:
    """
    Calculate the "distance" between two characters.

    The "distance" between two characters is inversely proportional to the likelihood of confusing the characters when typing.
    For example, the "distance" between 'a' and 'b' will be smaller than between 'a' and 'z' if 'a' and 'b' are closer to each other on the keyboard.

    This distance is used to calculate the cost of an error in a query.

    Args:
        similar_symbols (List[str]): Lists of very similar characters (e.g., Latin 'c' and Cyrillic 'с').
        symbol_keyboards (List[str]): A list of keyboard layouts represented as strings, where each line corresponds to a keyboard row.

    Returns:
        List[Dict[str, float]]: A list of dictionaries where each dictionary contains 'first symbol', 'second symbol', and 'distance'.

    Raises:
        ValueError: If the input data is invalid.
    """
    def _get_symbol_keyboard_coordinates(keyboard: str) -> Dict[str, Tuple[int, int]]:
        """
        Parse a keyboard layout string to extract symbolacter coordinates.

        Args:
            keyboard (str): Keyboard layout as a string.

        Returns:
            Dict[str, Tuple[int, int]]: A dictionary mapping symbolacters to their (row, column) coordinates.
        """
        symbol_keyboard_coordinates = {}
        for i, line in enumerate(keyboard.split('\n')):
            for j, symbol in enumerate(line):
                if symbol != ' ':
                    symbol_keyboard_coordinates[symbol] = (i, j)
        return symbol_keyboard_coordinates

    def _calculate_max_symbol_distance(keyboard: str) -> float:
        """
        Calculate the maximum "distance" between symbolacters on a keyboard.

        Args:
            keyboard (str): Keyboard layout as a string.

        Returns:
            float: The maximum distance between any two symbolacters on the keyboard.
        """

        lines = keyboard.split('\n')
        height = len(lines)
        width = max(len(line) for line in lines)
        return math.sqrt(height ** 2 + width ** 2 + 1)

    def _calculate_symbols_distance(x: str, y: str) -> Optional[float]:
        """
        Calculate the relative distance (from 0 to 1) between two symbolacters.

        Args:
            x (str): The first symbolacter.
            y (str): The second symbolacter.

        Returns:
            Optional[float]: The relative distance (from 0 to 1) between two symbolacters, or None if no coordinates are found.
        """
        if x == y:
            return 0.0

        if is_similar_symbols.get((x, y), False):
            return 0.5 / max_symbols_distance

        distance = float('inf')
        for ik1, k1 in enumerate(symbol_keyboards_coordinates):
            for ik2, k2 in enumerate(symbol_keyboards_coordinates):
                coord_x = k1.get(x)
                coord_y = k2.get(y)
                if coord_x is not None and coord_y is not None:
                    cur_distance = math.sqrt((coord_x[0] - coord_y[0]) ** 2 + (coord_x[1] - coord_y[1]) ** 2 + (int(ik1 != ik2)) ** 2) / max_symbols_distance
                    distance = min(distance, cur_distance)

        return distance if distance != float('inf') else None

    if not similar_symbols:
        similar_symbols = [
            'уеоаіыэeyioaиє', 'єеэёe', 'уюy', 'аяa', 'гґ', 'дт', 'зсc', 'бп', 'вф', 'гхx', 'дт', 'жш', 'цсc', 'рp', 'kк',
        ]

    is_similar_symbols = {(x, y): True for s in similar_symbols for x in s for y in s if x != y}
    symbol_keyboards_coordinates = [_get_symbol_keyboard_coordinates(keyboard) for keyboard in symbol_keyboards]
    max_symbols_distance = max(_calculate_max_symbol_distance(keyboard) for keyboard in symbol_keyboards)

    symbols = list({symbol for keyboard in symbol_keyboards_coordinates for symbol in keyboard})

    symbols_distances = dict()
    for x in symbols:
        for y in symbols:
            distance = _calculate_symbols_distance(x, y)
            if distance is not None:
                symbols_distances[(x, y)] = symbols_distances[(y, x)] = distance

    # Normalize distances using L2 norm
    norm = math.sqrt(sum(d ** 2 for d in symbols_distances.values()))
    for key, dist in symbols_distances.items():
        symbols_distances[key] /= norm

    return symbols_distances
