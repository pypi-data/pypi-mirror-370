from liblaf.grapes import deps

with deps.optional_imports(extra="duration"):
    import about_time


def human_throughput(value: float, unit: str = "", prec: int | None = None) -> str:
    throughput: about_time.HumanThroughput = about_time.HumanThroughput(value, unit)
    return throughput.as_human(prec)
