# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["EmbeddingCreateEmbeddingParams"]


class EmbeddingCreateEmbeddingParams(TypedDict, total=False):
    input: Required[object]

    model: Required[str]

    dimensions: int

    encoding_format: str

    user: str
