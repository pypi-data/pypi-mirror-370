from typing import Optional

DETAILS_KEY = "details"
DBNAME_KEYS = ("dbname", "db", "project_id", "project-id")


def get_dbname_from_details(details: dict) -> Optional[str]:
    """
    Extract dbname from details, trying several keys.
    Returns None if all keys failed.
    """
    for key in DBNAME_KEYS:
        if key in details:
            return details.get(key)
    return None
