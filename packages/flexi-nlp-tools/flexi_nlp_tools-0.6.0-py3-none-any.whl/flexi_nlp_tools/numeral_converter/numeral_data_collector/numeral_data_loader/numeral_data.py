from dataclasses import dataclass
from typing import Dict

from .numeral_entry import NumeralEntry


@dataclass
class NumeralData(Dict[int, NumeralEntry]):
    """Class to represent numeral data that behaves like a dictionary."""

    is_available_case: bool = False
    is_available_gender: bool = False
    is_available_number: bool = False
    is_available_num_class: bool = False

    def __setitem__(self, idx: int, numeral_entry: NumeralEntry):

        super().__setitem__(idx, numeral_entry)
        if numeral_entry.number is not None:
            self.is_available_number = True
        if numeral_entry.gender is not None:
            self.is_available_gender = True
        if numeral_entry.num_class is not None:
            self.is_available_num_class = True
        if numeral_entry.case is not None:
            self.is_available_case = True
