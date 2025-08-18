ES_SORT_QUERY = {
    "newest": {"created_at_epoch": {"order": "desc"}},
    "oldest": {"created_at_epoch": {"order": "asc"}},
    "last_updated": {"updated_at_epoch": {"order": "desc"}},
    "a_z": {"name.keyword": {"order": "asc"}},
    "z_a": {"name.keyword": {"order": "desc"}},
    "lowest_to_highest": {"created_at_epoch": {"order": "asc"}},
    "highest_to_lowest": {"created_at_epoch": {"order": "desc"}},
}

MONGO_DB_SORT_QUERY = {
    "newest": {"created_at_epoch": -1},
    "oldest": {"created_at_epoch": 1},
    "last_updated": {"updated_at_epoch": -1},
    "a_z": {"name": 1},
    "z_a": {"name": -1},
    "lowest_to_highest": {"created_at_epoch": 1},
    "highest_to_lowest": {"created_at_epoch": -1},
}


def sort_query_es(
    sort_by: str,
    alpha_sort_field: str = "name",
    numeric_sort_field: str = "created_at_epoch",
) -> dict:
    """
    Generate a sort query for Elasticsearch based on specified parameters.

    This function creates a sort query dictionary that can be used in Elasticsearch queries
    to sort results by different criteria such as creation date, alphabetical order, or numeric values.

    Args:
        sort_by (str): The sort order to apply. Must be one of:
            - "newest": Sort by creation date (newest first)
            - "oldest": Sort by creation date (oldest first)
            - "last_updated": Sort by last update date
            - "a_z": Sort alphabetically (A to Z)
            - "z_a": Sort alphabetically (Z to A)
            - "lowest_to_highest": Sort numerically (ascending)
            - "highest_to_lowest": Sort numerically (descending)
        alpha_sort_field (str, optional): The field name to use for alphabetical sorting.
            Defaults to "name".
        numeric_sort_field (str, optional): The field name to use for numeric sorting i.e price, position, amount, serial number, etc.
            Defaults to "created_at_epoch".

    Returns:
        dict: A dictionary containing the Elasticsearch sort query configuration.

    Example:
        >>> sort_query_es("newest")
        {'created_at_epoch': {'order': 'desc'}}
        >>> sort_query_es("a_z", alpha_sort_field="title")
        {'title.keyword': {'order': 'asc'}}
        >>> sort_query_es("lowest_to_highest", numeric_sort_field="price")
        {'price': {'order': 'asc'}}
    """
    if sort_by in ["a_z", "z_a"] and alpha_sort_field:
        return {f"{alpha_sort_field}.keyword": ES_SORT_QUERY[sort_by]["name.keyword"]}
    elif sort_by in ["lowest_to_highest", "highest_to_lowest"] and numeric_sort_field:
        return {numeric_sort_field: ES_SORT_QUERY[sort_by]["created_at_epoch"]}
    else:
        return ES_SORT_QUERY[sort_by]


def sort_query_mongo(
    sort_by: str,
    alpha_sort_field: str = "name",
    numeric_sort_field: str = "created_at_epoch",
) -> dict:
    """
    Generate a sort query for MongoDB based on specified parameters.

    This function creates a sort query dictionary that can be used in MongoDB queries
    to sort results by different criteria such as creation date, alphabetical order, or numeric values.

    Args:
        sort_by (str): The sort order to apply. Must be one of:
            - "newest": Sort by creation date (newest first)
            - "oldest": Sort by creation date (oldest first)
            - "last_updated": Sort by last update date
            - "a_z": Sort alphabetically (A to Z)
            - "z_a": Sort alphabetically (Z to A)
            - "lowest_to_highest": Sort numerically (ascending)
            - "highest_to_lowest": Sort numerically (descending)
        alpha_sort_field (str, optional): The field name to use for alphabetical sorting.
            Defaults to "name".
        numeric_sort_field (str, optional): The field name to use for numeric sorting i.e price, position, amount, serial number, etc.
            Defaults to "created_at_epoch".

    Returns:
        dict: A dictionary containing the MongoDB sort query configuration.

    Example:
        >>> sort_query_mongo("newest")
        {'created_at_epoch': -1}
        >>> sort_query_mongo("a_z", alpha_sort_field="title")
        {'title': 1}
        >>> sort_query_mongo("lowest_to_highest", numeric_sort_field="price")
        {'price': 1}
    """
    if sort_by in ["a_z", "z_a"] and alpha_sort_field:
        return {alpha_sort_field: MONGO_DB_SORT_QUERY[sort_by]["name"]}
    elif sort_by in ["lowest_to_highest", "highest_to_lowest"] and numeric_sort_field:
        return {numeric_sort_field: MONGO_DB_SORT_QUERY[sort_by]["created_at_epoch"]}
    else:
        return MONGO_DB_SORT_QUERY[sort_by]


if __name__ == "__main__":
    print(sort_query_es("newest"))
