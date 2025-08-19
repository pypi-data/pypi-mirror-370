from urllib.parse import quote_plus


def build_query_params(**params):
    """
    Build a query string from given parameters, excluding any that are None.
    :param params: Dictionary of query parameters
    :return: A query string
    """
    query_parts = []
    for key, value in params.items():
        if value is None:
            continue
        if isinstance(value, list):
            # Handle list values by repeating the key for each item
            query_parts.extend(f"{key}[]={quote_plus(str(item))}" for item in value)
        else:
            query_parts.append(f"{key}={quote_plus(str(value))}")
    return "&".join(query_parts)


def is_valid_id(id: str) -> bool:
    """
    Verify if the given id is a valid ID.
    A valid ID is a string that has a length between 20 and 30 characters.

    Args:
      id (str): The id to verify.

    Returns:
      bool: True if the id is valid, False otherwise.
    """
    return id and isinstance(id, str) and 20 <= len(id) <= 60
