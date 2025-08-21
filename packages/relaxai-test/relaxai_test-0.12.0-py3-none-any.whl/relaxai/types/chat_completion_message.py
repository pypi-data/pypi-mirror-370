# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .function_call import FunctionCall

__all__ = ["ChatCompletionMessage", "MultiContent", "MultiContentImageURL", "ToolCall"]


class MultiContentImageURL(BaseModel):
    detail: Optional[str] = None

    url: Optional[str] = None


class MultiContent(BaseModel):
    image_url: Optional[MultiContentImageURL] = None

    text: Optional[str] = None

    type: Optional[str] = None


class ToolCall(BaseModel):
    function: FunctionCall

    type: str

    id: Optional[str] = None

    index: Optional[int] = None


class ChatCompletionMessage(BaseModel):
    content: str

    role: str

    function_call: Optional[FunctionCall] = None

    multi_content: Optional[List[MultiContent]] = FieldInfo(alias="MultiContent", default=None)

    name: Optional[str] = None

    reasoning_content: Optional[str] = None

    refusal: Optional[str] = None

    tool_call_id: Optional[str] = None

    tool_calls: Optional[List[ToolCall]] = None
