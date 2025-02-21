def flatten_dict(dict_to_flatten):
    """
    Flatten a dictionary with pattern matching:
    Assume dot notation for nested keys (since that was present in the provided template)
    Assume index notation for lists, ie "key1.0.key2"
    """

    def _flatten_dict(current_key, value):
        match value:
            case dict():
                for key, new_value in value.items():
                    _flatten_dict(f"{current_key}.{key}", new_value)
            case list():
                for index, element in enumerate(value):
                    _flatten_dict(f"{current_key}.{index}", element)
            case _:
                # we don't want initial dot in the key
                current_key = current_key[1:]
                flattened[current_key] = value

    flattened = {}
    _flatten_dict("", dict_to_flatten)
    return flattened
