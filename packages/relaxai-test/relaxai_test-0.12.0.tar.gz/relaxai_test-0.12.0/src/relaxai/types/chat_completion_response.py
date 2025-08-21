# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .shared.openai_usage import OpenAIUsage
from .content_filter_results import ContentFilterResults
from .chat_completion_message import ChatCompletionMessage

__all__ = [
    "ChatCompletionResponse",
    "Choice",
    "ChoiceLogprobs",
    "ChoiceLogprobsContent",
    "ChoiceLogprobsContentTopLogprob",
    "PromptFilterResult",
]


class ChoiceLogprobsContentTopLogprob(BaseModel):
    token: str

    logprob: float

    bytes: Optional[str] = None


class ChoiceLogprobsContent(BaseModel):
    token: str

    logprob: float

    top_logprobs: List[ChoiceLogprobsContentTopLogprob]

    bytes: Optional[str] = None


class ChoiceLogprobs(BaseModel):
    content: List[ChoiceLogprobsContent]


class Choice(BaseModel):
    finish_reason: str

    index: int

    message: ChatCompletionMessage

    content_filter_results: Optional[ContentFilterResults] = None

    logprobs: Optional[ChoiceLogprobs] = None


class PromptFilterResult(BaseModel):
    index: int

    content_filter_results: Optional[ContentFilterResults] = None


class ChatCompletionResponse(BaseModel):
    id: str

    choices: List[Choice]

    created: int

    http_header: Dict[str, List[str]] = FieldInfo(alias="httpHeader")

    model: str

    object: str

    system_fingerprint: str

    usage: OpenAIUsage

    prompt_filter_results: Optional[List[PromptFilterResult]] = None
