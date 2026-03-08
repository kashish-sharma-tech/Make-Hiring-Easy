import json


def compare_keywords(jd_keywords, original_text, optimized_data):
    """Compare JD keywords against original and optimized resume.

    Returns dict with 'added', 'already_present', and 'not_added' lists.
    """
    original_lower = original_text.lower()

    # Flatten optimized data into a single searchable string
    optimized_text = _flatten_to_text(optimized_data).lower()

    already_present = []
    added = []
    not_added = []

    for keyword in jd_keywords:
        kw_lower = keyword.lower()
        in_original = kw_lower in original_lower
        in_optimized = kw_lower in optimized_text

        if in_original and in_optimized:
            already_present.append(keyword)
        elif not in_original and in_optimized:
            added.append(keyword)
        else:
            not_added.append(keyword)

    return {
        "already_present": already_present,
        "added": added,
        "not_added": not_added,
    }


def _flatten_to_text(data):
    """Recursively flatten a dict/list structure into a single string."""
    if isinstance(data, str):
        return data
    if isinstance(data, list):
        return " ".join(_flatten_to_text(item) for item in data)
    if isinstance(data, dict):
        return " ".join(_flatten_to_text(v) for v in data.values())
    return str(data)
