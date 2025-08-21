# Standard Libaries
import os
from pathlib import Path
from typing import Tuple, TypeVar, TypeAlias, Sequence

PathLike: TypeAlias = str | os.PathLike | Path

_T = TypeVar("_T")
# (class_name, [(field_name, val), (field_name, val), ...])
DataClassConstructor: TypeAlias = Tuple[str, Sequence[Tuple[str, _T]]]
