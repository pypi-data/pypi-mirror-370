# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["ContentFilterResults", "Hate", "Jailbreak", "Profanity", "SelfHarm", "Sexual", "Violence"]


class Hate(BaseModel):
    filtered: bool

    severity: Optional[str] = None


class Jailbreak(BaseModel):
    detected: bool

    filtered: bool


class Profanity(BaseModel):
    detected: bool

    filtered: bool


class SelfHarm(BaseModel):
    filtered: bool

    severity: Optional[str] = None


class Sexual(BaseModel):
    filtered: bool

    severity: Optional[str] = None


class Violence(BaseModel):
    filtered: bool

    severity: Optional[str] = None


class ContentFilterResults(BaseModel):
    hate: Optional[Hate] = None

    jailbreak: Optional[Jailbreak] = None

    profanity: Optional[Profanity] = None

    self_harm: Optional[SelfHarm] = None

    sexual: Optional[Sexual] = None

    violence: Optional[Violence] = None
