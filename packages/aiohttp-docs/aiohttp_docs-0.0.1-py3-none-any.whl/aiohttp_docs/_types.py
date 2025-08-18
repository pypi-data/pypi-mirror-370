from typing import TypedDict

from pydantic import BaseModel


class DocParams(TypedDict, total=False):
    tags: list[str]
    summary: str
    description: str
    body_model: type[BaseModel]
    query_model: type[BaseModel]
    response_models: dict[int, type[BaseModel]]
