from typing import Literal, TypeVar

from sqlalchemy.ext.declarative import DeclarativeMeta

LitInt = Literal["int"]
LitFloat = Literal["float"]
LitStr = Literal["str"]
LitBool = Literal["bool"]

OptInt = int | None
OptFloat = float | None
OptStr = str | None
OptBool = bool | None

TableType = TypeVar("TableType", bound=DeclarativeMeta)
