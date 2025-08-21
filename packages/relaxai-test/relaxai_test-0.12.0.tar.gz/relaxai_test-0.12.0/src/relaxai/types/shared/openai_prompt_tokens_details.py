# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ..._models import BaseModel

__all__ = ["OpenAIPromptTokensDetails"]


class OpenAIPromptTokensDetails(BaseModel):
    audio_tokens: int

    cached_tokens: int
