def calculate_score(requirements: list[dict]) -> int | None:
    """Calculate coverage: required=2, preferred=1; partial earns half credit."""
    if not requirements:
        return None

    earned = 0
    possible = 0
    credit = {"supported": 1, "partial": 0.5, "missing": 0, "unclear": 0}
    for requirement in requirements:
        weight = 2 if requirement["importance"] == "required" else 1
        earned += weight * credit[requirement["status"]]
        possible += weight
    return round(100 * earned / possible)
