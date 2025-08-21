# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ..._models import BaseModel

__all__ = ["OpenAICompletionTokensDetails"]


class OpenAICompletionTokensDetails(BaseModel):
    accepted_prediction_tokens: int

    audio_tokens: int

    reasoning_tokens: int

    rejected_prediction_tokens: int
