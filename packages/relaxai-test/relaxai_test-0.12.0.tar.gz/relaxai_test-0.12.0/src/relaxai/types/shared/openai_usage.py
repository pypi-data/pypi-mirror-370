# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ..._models import BaseModel
from .openai_prompt_tokens_details import OpenAIPromptTokensDetails
from .openai_completion_tokens_details import OpenAICompletionTokensDetails

__all__ = ["OpenAIUsage"]


class OpenAIUsage(BaseModel):
    completion_tokens: int

    completion_tokens_details: OpenAICompletionTokensDetails

    prompt_tokens: int

    prompt_tokens_details: OpenAIPromptTokensDetails

    total_tokens: int
