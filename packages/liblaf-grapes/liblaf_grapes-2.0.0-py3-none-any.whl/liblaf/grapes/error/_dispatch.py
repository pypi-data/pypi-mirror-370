from collections.abc import Callable, Mapping, Sequence

import attrs

from liblaf.grapes import pretty


@attrs.define
class DispatchLookupError(LookupError):
    func: Callable = attrs.field()
    call_args: Sequence = attrs.field(factory=tuple)
    call_kwargs: Mapping = attrs.field(factory=dict)

    def __str__(self) -> str:
        pretty_call: str = pretty.pretty_call(
            self.func, self.call_args, self.call_kwargs
        )
        return f"`{pretty_call}` could not be resolved."
