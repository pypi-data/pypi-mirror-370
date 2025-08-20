import re
from datetime import date, datetime, time
from decimal import Decimal


def normalize_sql_query(query: str) -> str:
    """
    Normalize SQL query to handle newlines and formatting issues.

    - Handles multi-line queries with CTEs, subqueries, etc.
    """
    if not query or not isinstance(query, str):
        return query

    # Remove excessive whitespace while preserving single spaces
    # Replace multiple whitespace characters (including newlines) with single spaces
    normalized = re.sub(r"\s+", " ", query.strip())

    return normalized.strip()


def _convert_to_json_serializable(data):
    """
    Convert Decimal and datetime objects to JSON-serializable types recursively in any nested data structure.
    This fixes the issue where Pydantic converts Decimal to strings and datetime objects can't be JSON serialized.

    Handles lists, tuples, dictionaries, Decimal objects, and datetime objects.
    """
    if isinstance(data, Decimal):
        return float(data)
    elif isinstance(data, datetime):
        return data.isoformat()
    elif isinstance(data, date):
        return data.isoformat()
    elif isinstance(data, time):
        return data.isoformat()
    elif isinstance(data, list):
        for i, item in enumerate(data):
            data[i] = _convert_to_json_serializable(item)
        return data
    elif isinstance(data, tuple):
        # Convert tuple to list, process, then back to tuple
        return tuple(_convert_to_json_serializable(item) for item in data)
    elif isinstance(data, dict):
        for key, value in data.items():
            data[key] = _convert_to_json_serializable(value)
        return data
    else:
        # For all other types (int, float, str, bool, None, etc.), return as-is
        return data
