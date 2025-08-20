from typing import Dict, Union

import pydantic_core


def try_convert_str_value_to_json(
    obj: Dict[str, Union[str, int, float, Dict]],
) -> Dict[str, Union[str, int, float, Dict]]:
    """
    Convert string values to JSON format if it contains double quote in-place.

    Args:
        obj (Dict[str, Union[str, int, float, Dict]]): The input dictionary.
    Returns:
        Dict[str, Union[str, int, float, Dict]]: The modified dictionary with string values converted to JSON.

    Raises:
        ValueError: If the input is not a dictionary.
    """
    if not isinstance(obj, dict):
        raise ValueError("Input must be a dictionary.")

    for key, value in obj.items():
        if isinstance(value, str) and (
            value.find('"') >= 0 or value.strip() in ["{}", "[]"]
        ):
            try:
                obj[key] = pydantic_core.from_json(value, allow_partial=True)
            except ValueError:
                obj[key] = value
        else:
            obj[key] = value

    return obj
