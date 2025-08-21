def merge_dict(original_dict: dict, new_dict: dict):
    # 동일한 key가 있는 경우, original_dict의 내부 dict을 유지하면서 새로운 dict을 병합.
    for key, value in new_dict.items():
        if (
            key in original_dict
            and isinstance(value, dict)
            and isinstance(original_dict[key], dict)
        ):
            merge_dict(original_dict[key], value)
        else:
            original_dict[key] = value


def get_nested_value(d: dict, keys: list):
    """
    중첩된 딕셔너리에서 키를 순서대로 조회하여 값을 반환하는 함수.
    키가 존재하지 않으면 None을 반환.

    Args:
        d (dict): 딕셔너리
        keys (list): 키의 리스트

    Returns:
        중첩된 값 또는 None
    """
    for key in keys:
        if isinstance(d, dict) and key in d:
            d = d[key]
        else:
            return None
    return d
