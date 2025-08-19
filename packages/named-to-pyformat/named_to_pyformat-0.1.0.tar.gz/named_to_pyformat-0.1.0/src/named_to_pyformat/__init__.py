import re


def s(named_sql: str) -> str:
    """
    Convert SQL string with named parameters (e.g., :name) to Python format parameters (e.g., %(name)s).

    Args:
        named_sql (str): SQL string containing named parameters prefixed with ':'.

    Returns:
        str: SQL string with parameters converted to Python's pyformat style.
    """
    return re.sub(r":(\w+)", r"%(\1)s", named_sql)
