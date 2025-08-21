from liblaf.grapes import deps

with deps.optional_imports(extra="duration"):
    import about_time


def human_count(count: int, unit: str = "", prec: int | None = None) -> str:
    """Convert a numerical count into a human-readable string.

    Args:
        count: The numerical count to be converted.
        unit: The unit of measurement to be appended to the count.
        prec: The precision for the human-readable format. If None, default precision is used.

    Returns:
        The human-readable string representation of the count.
    """
    # TODO: remove dependency on `about-time`
    hc = about_time.HumanCount(count, unit)
    return hc.as_human(prec)
