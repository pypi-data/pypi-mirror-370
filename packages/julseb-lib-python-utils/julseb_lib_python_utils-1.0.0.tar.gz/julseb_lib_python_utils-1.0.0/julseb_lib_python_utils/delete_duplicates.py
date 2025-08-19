import json


def delete_duplicates(array: list) -> list:
    """
    Removes duplicates from a list, comparing items by their JSON string representation.
    """
    seen = set()
    result = []
    for item in array:
        item_str = json.dumps(item, sort_keys=True)
        if item_str not in seen:
            seen.add(item_str)
            result.append(item)
    return result
