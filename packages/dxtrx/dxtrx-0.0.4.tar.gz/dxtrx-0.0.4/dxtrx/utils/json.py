import orjson

def dumps(obj, **kwargs):
    """Convert a Python object to a JSON string using orjson.

    Args:
        obj: Any Python object that can be serialized to JSON.

    Returns:
        str: A JSON string representation of the input object.
    """
    return orjson.dumps(obj, **kwargs).decode()

def loads(obj, **kwargs):
    """Parse a JSON string into a Python object using orjson.

    Args:
        obj (str): A JSON string to be parsed.

    Returns:
        Any: The Python object represented by the JSON string.
    """
    return orjson.loads(obj, **kwargs)