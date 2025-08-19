from pydash.strings import snake_case


def dict_keys_to_snake_case(d):
    if isinstance(d, list):
        return [
            dict_keys_to_snake_case(i) if isinstance(i, (dict, list)) else i for i in d
        ]
    return {
        snake_case(a): dict_keys_to_snake_case(b) if isinstance(b, (dict, list)) else b
        for a, b in d.items()
    }
