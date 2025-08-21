from typing import Any

import pydantic

from liblaf.grapes.typed import PathLike

from ._serde import load, save


def load_pydantic[C: pydantic.BaseModel](
    path: PathLike, cls: type[C], *, ext: str | None = None, **kwargs
) -> C:
    data: Any = load(path, ext=ext, **kwargs)
    return cls.model_validate(data)


def save_pydantic(
    path: PathLike,
    data: pydantic.BaseModel,
    *,
    ext: str | None = None,
    # pydantic.BaseModel.model_dump(**kwargs)
    context: Any | None = None,
    by_alias: bool = False,
    exclude_unset: bool = False,
    exclude_defaults: bool = False,
    exclude_none: bool = False,
    round_trip: bool = False,
    serialize_as_any: bool = False,
) -> None:
    save(
        path,
        data.model_dump(
            context=context,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            serialize_as_any=serialize_as_any,
        ),
        ext=ext,
    )
