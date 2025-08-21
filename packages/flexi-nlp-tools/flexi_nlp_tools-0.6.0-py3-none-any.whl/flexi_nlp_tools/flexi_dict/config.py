"""
Environment variable validation.

This module validates the required environment variables and ensures they
meet the expected constraints. If any variable has an invalid value, an
`InvalidEnvironmentVariable` exception is raised.

Variables:
    DEFAULT_TOPN_LEAVES (int): Positive integer.
    MIN_CORRECTION_PRICE (float): Float in the range [0, 1].
    MAX_CORRECTION_RATE (float): Float in the range [0, 1].
    MAX_CORRECTION_RATE_FOR_SEARCH (float): Float in the range [0, 1].
    DEFAULT_DELETION_PRICE (float): Float in the range [0, 1].
    DEFAULT_SUBSTITUTION_PRICE (float): Float in the range [0, 1].
    DEFAULT_INSERTION_PRICE (float): Float in the range [0, 1].
    DEFAULT_TRANSPOSITION_PRICE (float): Float in the range [0, 1].
    MAX_QUEUE_SIZE (int): Positive integer.

"""
import os
from ..exceptions import InvalidEnvironmentVariable


def _validate_range(variable_name, value, min_val=0, max_val=1):
    if not (min_val <= value <= max_val):
        raise InvalidEnvironmentVariable(
            variable_name, value, f"float, in range [{min_val}, {max_val}]"
        )


def _validate_positive(variable_name, value):
    if value <= 0:
        raise InvalidEnvironmentVariable(variable_name, value, 'integer, > 0')


DEFAULT_TOPN_LEAVES = int(os.getenv('DEFAULT_TOPN_LEAVES', 10))
_validate_positive('DEFAULT_TOPN_LEAVES', DEFAULT_TOPN_LEAVES)

MIN_CORRECTION_PRICE = float(os.getenv('MIN_CORRECTION_PRICE', 1e-5))
MAX_CORRECTION_RATE = float(os.getenv('MAX_CORRECTION_RATE', 2/3))
MAX_CORRECTION_RATE_FOR_SEARCH = float(os.getenv('MAX_CORRECTION_RATE_FOR_SEARCH', 1.))

DEFAULT_DELETION_PRICE = float(os.getenv('DEFAULT_DELETION_PRICE', .4))
DEFAULT_SUBSTITUTION_PRICE = float(os.getenv('DEFAULT_SUBSTITUTION_PRICE', .2))
DEFAULT_INSERTION_PRICE = float(os.getenv('DEFAULT_INSERTION_PRICE', .05))
DEFAULT_TRANSPOSITION_PRICE = float(os.getenv('DEFAULT_TRANSPOSITION_PRICE', .35))

_validate_range('MIN_CORRECTION_PRICE', MIN_CORRECTION_PRICE)
_validate_range('MAX_CORRECTION_RATE_FOR_SEARCH', MAX_CORRECTION_RATE_FOR_SEARCH)
_validate_range('MAX_CORRECTION_RATE', MAX_CORRECTION_RATE)
_validate_range('DEFAULT_DELETION_PRICE', DEFAULT_DELETION_PRICE)
_validate_range('DEFAULT_SUBSTITUTION_PRICE', DEFAULT_SUBSTITUTION_PRICE)
_validate_range('DEFAULT_INSERTION_PRICE', DEFAULT_INSERTION_PRICE)
_validate_range('DEFAULT_TRANSPOSITION_PRICE', DEFAULT_TRANSPOSITION_PRICE)


MAX_QUEUE_SIZE: int = int(os.getenv('MAX_QUEUE_SIZE', 1024))
_validate_positive('MAX_QUEUE_SIZE', MAX_QUEUE_SIZE)
