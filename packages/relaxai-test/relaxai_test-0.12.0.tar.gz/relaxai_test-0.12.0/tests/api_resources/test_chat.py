# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from relaxai import Relaxai, AsyncRelaxai
from tests.utils import assert_matches_type
from relaxai.types import ChatCompletionResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestChat:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_completion(self, client: Relaxai) -> None:
        chat = client.chat.create_completion(
            messages=[
                {
                    "content": "content",
                    "role": "role",
                }
            ],
            model="model",
        )
        assert_matches_type(ChatCompletionResponse, chat, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_completion_with_all_params(self, client: Relaxai) -> None:
        chat = client.chat.create_completion(
            messages=[
                {
                    "content": "content",
                    "role": "role",
                    "function_call": {
                        "arguments": "arguments",
                        "name": "name",
                    },
                    "multi_content": [
                        {
                            "image_url": {
                                "detail": "detail",
                                "url": "url",
                            },
                            "text": "text",
                            "type": "type",
                        }
                    ],
                    "name": "name",
                    "reasoning_content": "reasoning_content",
                    "refusal": "refusal",
                    "tool_call_id": "tool_call_id",
                    "tool_calls": [
                        {
                            "function": {
                                "arguments": "arguments",
                                "name": "name",
                            },
                            "type": "type",
                            "id": "id",
                            "index": 0,
                        }
                    ],
                }
            ],
            model="model",
            chat_template_kwargs={},
            frequency_penalty=0,
            function_call={},
            functions=[
                {
                    "name": "name",
                    "parameters": {},
                    "description": "description",
                    "strict": True,
                }
            ],
            logit_bias={"foo": 0},
            logprobs=True,
            max_completion_tokens=0,
            max_tokens=0,
            metadata={"foo": "string"},
            n=0,
            parallel_tool_calls={},
            prediction={
                "content": "content",
                "type": "type",
            },
            presence_penalty=0,
            reasoning_effort="reasoning_effort",
            response_format={
                "json_schema": {
                    "name": "name",
                    "strict": True,
                    "description": "description",
                },
                "type": "type",
            },
            seed=0,
            stop=["string"],
            store=True,
            stream=True,
            stream_options={"include_usage": True},
            temperature=0,
            tool_choice={},
            tools=[
                {
                    "type": "type",
                    "function": {
                        "name": "name",
                        "parameters": {},
                        "description": "description",
                        "strict": True,
                    },
                }
            ],
            top_logprobs=0,
            top_p=0,
            user="user",
        )
        assert_matches_type(ChatCompletionResponse, chat, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_completion(self, client: Relaxai) -> None:
        response = client.chat.with_raw_response.create_completion(
            messages=[
                {
                    "content": "content",
                    "role": "role",
                }
            ],
            model="model",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        chat = response.parse()
        assert_matches_type(ChatCompletionResponse, chat, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_completion(self, client: Relaxai) -> None:
        with client.chat.with_streaming_response.create_completion(
            messages=[
                {
                    "content": "content",
                    "role": "role",
                }
            ],
            model="model",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            chat = response.parse()
            assert_matches_type(ChatCompletionResponse, chat, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncChat:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_completion(self, async_client: AsyncRelaxai) -> None:
        chat = await async_client.chat.create_completion(
            messages=[
                {
                    "content": "content",
                    "role": "role",
                }
            ],
            model="model",
        )
        assert_matches_type(ChatCompletionResponse, chat, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_completion_with_all_params(self, async_client: AsyncRelaxai) -> None:
        chat = await async_client.chat.create_completion(
            messages=[
                {
                    "content": "content",
                    "role": "role",
                    "function_call": {
                        "arguments": "arguments",
                        "name": "name",
                    },
                    "multi_content": [
                        {
                            "image_url": {
                                "detail": "detail",
                                "url": "url",
                            },
                            "text": "text",
                            "type": "type",
                        }
                    ],
                    "name": "name",
                    "reasoning_content": "reasoning_content",
                    "refusal": "refusal",
                    "tool_call_id": "tool_call_id",
                    "tool_calls": [
                        {
                            "function": {
                                "arguments": "arguments",
                                "name": "name",
                            },
                            "type": "type",
                            "id": "id",
                            "index": 0,
                        }
                    ],
                }
            ],
            model="model",
            chat_template_kwargs={},
            frequency_penalty=0,
            function_call={},
            functions=[
                {
                    "name": "name",
                    "parameters": {},
                    "description": "description",
                    "strict": True,
                }
            ],
            logit_bias={"foo": 0},
            logprobs=True,
            max_completion_tokens=0,
            max_tokens=0,
            metadata={"foo": "string"},
            n=0,
            parallel_tool_calls={},
            prediction={
                "content": "content",
                "type": "type",
            },
            presence_penalty=0,
            reasoning_effort="reasoning_effort",
            response_format={
                "json_schema": {
                    "name": "name",
                    "strict": True,
                    "description": "description",
                },
                "type": "type",
            },
            seed=0,
            stop=["string"],
            store=True,
            stream=True,
            stream_options={"include_usage": True},
            temperature=0,
            tool_choice={},
            tools=[
                {
                    "type": "type",
                    "function": {
                        "name": "name",
                        "parameters": {},
                        "description": "description",
                        "strict": True,
                    },
                }
            ],
            top_logprobs=0,
            top_p=0,
            user="user",
        )
        assert_matches_type(ChatCompletionResponse, chat, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_completion(self, async_client: AsyncRelaxai) -> None:
        response = await async_client.chat.with_raw_response.create_completion(
            messages=[
                {
                    "content": "content",
                    "role": "role",
                }
            ],
            model="model",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        chat = await response.parse()
        assert_matches_type(ChatCompletionResponse, chat, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_completion(self, async_client: AsyncRelaxai) -> None:
        async with async_client.chat.with_streaming_response.create_completion(
            messages=[
                {
                    "content": "content",
                    "role": "role",
                }
            ],
            model="model",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            chat = await response.parse()
            assert_matches_type(ChatCompletionResponse, chat, path=["response"])

        assert cast(Any, response.is_closed) is True
