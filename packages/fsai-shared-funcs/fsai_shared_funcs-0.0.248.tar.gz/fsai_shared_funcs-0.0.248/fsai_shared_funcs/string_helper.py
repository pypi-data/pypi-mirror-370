from beartype import beartype


@beartype
def string_is_true_or_false(input_string: str) -> bool:
    ua = input_string.capitalize()
    if "True".startswith(ua):
        return True
    elif "False".startswith(ua):
        return False
    else:
        return False


@beartype
def string_to_bytes(input_str: str) -> bytes:
    return bytes(str(input_str).encode("utf-8"))


@beartype
def bytes_to_string(_bytes: bytes) -> str:
    return str(_bytes.decode("utf-8"))
