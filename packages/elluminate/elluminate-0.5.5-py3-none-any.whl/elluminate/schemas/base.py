from typing import Generic, Sequence, TypeVar

from pydantic import BaseModel

# Generic type variable for the result type
TResult = TypeVar("TResult", bound=BaseModel | Sequence[BaseModel])


class BatchCreateStatus(BaseModel, Generic[TResult]):
    # DEPRECATED: Remove `result`, `percent` and `progress_msg` with 0.5.3 minimum version
    status: str
    result: list[TResult] | None = None
    percent: int | None = None
    progress_msg: str | None = None
    error_msg: str | None = None
