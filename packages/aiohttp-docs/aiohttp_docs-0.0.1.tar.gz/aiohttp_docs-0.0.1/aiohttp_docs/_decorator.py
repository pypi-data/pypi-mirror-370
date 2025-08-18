from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Unpack

from ._constants import DOCS_ATTR_NAME
from ._types import DocParams

type DecoratedFunc[**P, R] = Callable[P, Awaitable[R]]


def docs[**P, R](**doc_params: Unpack[DocParams]) -> Callable[[DecoratedFunc[P, R]], DecoratedFunc[P, R]]:
    def decorator(func: DecoratedFunc[P, R]) -> DecoratedFunc[P, R]:
        setattr(func, DOCS_ATTR_NAME, doc_params)

        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            return await func(*args, **kwargs)

        return wrapper

    return decorator
