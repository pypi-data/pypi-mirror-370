from typing import Type, Optional

from .numeral_data_collector.numeral_data_loader.numeral_entry import MorphForm


def transform_to_morph_form(input_string: str, morph_class: Type[MorphForm]) -> Optional[MorphForm]:
    """Converts a string into its corresponding morphological form based on the given enum class.

    Args:
        input_string (str): The string to be converted into the desired morphological form (e.g., "singular").
        morph_class (Type[MorphForm]): The enum class (e.g., `NumClass`, `Case`, `Gender`)
                                       that defines the target morph form.

    Returns:
        Optional[MorphForm]: The input string converted to the morphological form defined by the `morph_class` enum.

    """
    if not input_string:
        return None

    if isinstance(input_string, morph_class):
        return input_string




    try:
        if isinstance(input_string, str):
            input_string = input_string.lower()
        value = morph_class(input_string)
    except KeyError:
        raise ValueError(
            f'Invalid {morph_class.__name__} value "{input_string}"; '
            f'expected one of {[x.value for x in morph_class]}'
        )

    return value
