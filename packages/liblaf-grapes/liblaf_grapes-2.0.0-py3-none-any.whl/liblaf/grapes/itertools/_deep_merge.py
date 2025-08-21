from collections.abc import Mapping, Sequence


def deep_merge[KT, VT](
    *mappings: Mapping[KT, VT], append_arrays: bool = False
) -> dict[KT, VT]:
    result: dict[KT, VT] = {}
    for mapping in mappings:
        for key, value in mapping.items():
            if key in result:
                if isinstance(result[key], Mapping):
                    result[key] = deep_merge(  # pyright: ignore[reportArgumentType]
                        result[key],  # pyright: ignore[reportArgumentType]
                        value,  # pyright: ignore[reportArgumentType]
                        append_arrays=append_arrays,
                    )
                    continue
                if append_arrays and isinstance(result[key], Sequence):
                    result[key] = [*result[key], *value]  # pyright: ignore[reportArgumentType, reportGeneralTypeIssues]
                    continue
            result[key] = value
    return result
