"""aiohttp docs."""

from ._decorator import docs
from ._types import DocParams
from ._spec import OpenapiSpec

__all__ = (
    'DocParams',
    'OpenapiSpec',
    'docs',
)
