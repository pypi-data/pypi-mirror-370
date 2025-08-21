import os
import types

type ClassInfo = type | types.UnionType | tuple[ClassInfo, ...]
type PathLike = str | os.PathLike[str]
