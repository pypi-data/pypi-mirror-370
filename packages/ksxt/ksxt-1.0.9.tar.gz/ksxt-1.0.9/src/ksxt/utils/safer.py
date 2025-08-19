import ast


@staticmethod
def key_exists(dictionary, key):
    if hasattr(dictionary, "__getitem__") and not isinstance(dictionary, str):
        if isinstance(dictionary, list) and type(key) is not int:
            return False
        try:
            value = dictionary[key]
            return value is not None and value != ""
        except LookupError:
            return False
    return False


@staticmethod
def safe_value(dictionary, key, default_value=None):
    return dictionary[key] if key_exists(dictionary, key) else default_value


@staticmethod
def safe_string(dictionary, key, default_value=""):
    return str(dictionary[key]) if key_exists(dictionary, key) else default_value


@staticmethod
def safe_number(dictionary, key, default_value=0):
    value = safe_string(dictionary, key)
    if value == "":
        return default_value

    try:
        return float(value)
    except Exception:
        return default_value


@staticmethod
def safe_boolean(dictionary, key, default_value=False):
    value = safe_string(dictionary, key)
    if value == "":
        return default_value

    try:
        return bool(ast.literal_eval(value.capitalize()))
    except (ValueError, SyntaxError):
        return default_value
