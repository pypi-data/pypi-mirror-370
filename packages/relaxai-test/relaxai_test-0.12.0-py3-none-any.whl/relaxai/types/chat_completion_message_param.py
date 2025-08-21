# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .function_call_param import FunctionCallParam

__all__ = ["ChatCompletionMessageParam", "MultiContent", "MultiContentImageURL", "ToolCall"]


class MultiContentImageURL(TypedDict, total=False):
    detail: str

    url: str


class MultiContent(TypedDict, total=False):
    image_url: MultiContentImageURL

    text: str

    type: str


class ToolCall(TypedDict, total=False):
    function: Required[FunctionCallParam]

    type: Required[str]

    id: str

    index: int


class ChatCompletionMessageParam(TypedDict, total=False):
    content: Required[str]

    role: Required[str]

    function_call: FunctionCallParam

    multi_content: Annotated[Iterable[MultiContent], PropertyInfo(alias="MultiContent")]

    name: str

    reasoning_content: str

    refusal: str

    tool_call_id: str

    tool_calls: Iterable[ToolCall]
