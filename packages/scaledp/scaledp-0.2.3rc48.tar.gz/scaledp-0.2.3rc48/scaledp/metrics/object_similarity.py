from typing import Any, Dict, List

from Levenshtein import distance
from pydantic import BaseModel


def calculate_similarity(obj1: BaseModel, obj2: BaseModel) -> float:
    """
    Calculates the similarity between two instances of a Pydantic model.

    Args:
      obj1: The first Pydantic model instance.
      obj2: The second Pydantic model instance.

    Returns:
      A float value representing the similarity between the two objects.
      Higher values indicate greater similarity.

    """

    # 1. Get dictionaries of model attributes
    obj1_dict = obj1.dict()
    obj2_dict = obj2.dict()

    # 2. Find common attributes
    common_attributes = set(obj1_dict.keys()).intersection(set(obj2_dict.keys()))

    # 3. Calculate similarity based on common attributes
    similarity_score = 0
    for attr in common_attributes:
        value1 = obj1_dict[attr]
        value2 = obj2_dict[attr]

        similarity_score += _calculate_value_similarity(value1, value2)

    # 4. Normalize similarity score
    similarity_score /= len(common_attributes)

    return similarity_score


def _calculate_value_similarity(value1: Any, value2: Any) -> float:
    """
    Calculates the similarity between two values.

    Handles different data types, including nested objects within lists and dictionaries.
    """
    if isinstance(value1, BaseModel):
        return calculate_similarity(value1, value2)
    if isinstance(value1, list):
        return _calculate_list_similarity(value1, value2)
    if isinstance(value1, dict):
        return _calculate_dict_similarity(value1, value2)
    if isinstance(value1, (int, float)):
        return 1 - abs(value1 - value2) / max(abs(value1), abs(value2), 1)
    if isinstance(value1, str):
        if value1 == "" and value2 == "":
            return 1.0
        return 1 - distance(value1, value2) / max(len(value1), len(value2))
    # Handle other data types (e.g., booleans, dates) as needed
    return int(value1 == value2)


def _calculate_list_similarity(list1: List[Any], list2: List[Any]) -> float:
    """
    Calculates the similarity between two lists.

    Handles nested objects within lists.
    """
    if not list1 and not list2:
        return 1.0  # Both lists are empty
    if not list1 or not list2:
        return 0.0  # One list is empty

    min_len = min(len(list1), len(list2))
    max_len = max(len(list1), len(list2))

    total_similarity = 0
    for i in range(min_len):
        total_similarity += _calculate_value_similarity(list1[i], list2[i])

    # Handle cases where lists have different lengths
    total_similarity /= max_len

    return total_similarity


def _calculate_dict_similarity(dict1: Dict[Any, Any], dict2: Dict[Any, Any]) -> float:
    """
    Calculates the similarity between two dictionaries.

    Handles nested objects within dictionaries.
    """
    common_keys = set(dict1.keys()).intersection(set(dict2.keys()))
    if not common_keys:
        return 0

    total_similarity = 0
    for key in common_keys:
        total_similarity += _calculate_value_similarity(dict1[key], dict2[key])

    return total_similarity / len(common_keys)
