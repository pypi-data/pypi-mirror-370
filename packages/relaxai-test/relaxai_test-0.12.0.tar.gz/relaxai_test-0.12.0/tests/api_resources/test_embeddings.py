# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from relaxai import Relaxai, AsyncRelaxai
from tests.utils import assert_matches_type
from relaxai.types import EmbeddingResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEmbeddings:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_embedding(self, client: Relaxai) -> None:
        embedding = client.embeddings.create_embedding(
            input={},
            model="model",
        )
        assert_matches_type(EmbeddingResponse, embedding, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_embedding_with_all_params(self, client: Relaxai) -> None:
        embedding = client.embeddings.create_embedding(
            input={},
            model="model",
            dimensions=0,
            encoding_format="encoding_format",
            user="user",
        )
        assert_matches_type(EmbeddingResponse, embedding, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_embedding(self, client: Relaxai) -> None:
        response = client.embeddings.with_raw_response.create_embedding(
            input={},
            model="model",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        embedding = response.parse()
        assert_matches_type(EmbeddingResponse, embedding, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_embedding(self, client: Relaxai) -> None:
        with client.embeddings.with_streaming_response.create_embedding(
            input={},
            model="model",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            embedding = response.parse()
            assert_matches_type(EmbeddingResponse, embedding, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncEmbeddings:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_embedding(self, async_client: AsyncRelaxai) -> None:
        embedding = await async_client.embeddings.create_embedding(
            input={},
            model="model",
        )
        assert_matches_type(EmbeddingResponse, embedding, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_embedding_with_all_params(self, async_client: AsyncRelaxai) -> None:
        embedding = await async_client.embeddings.create_embedding(
            input={},
            model="model",
            dimensions=0,
            encoding_format="encoding_format",
            user="user",
        )
        assert_matches_type(EmbeddingResponse, embedding, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_embedding(self, async_client: AsyncRelaxai) -> None:
        response = await async_client.embeddings.with_raw_response.create_embedding(
            input={},
            model="model",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        embedding = await response.parse()
        assert_matches_type(EmbeddingResponse, embedding, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_embedding(self, async_client: AsyncRelaxai) -> None:
        async with async_client.embeddings.with_streaming_response.create_embedding(
            input={},
            model="model",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            embedding = await response.parse()
            assert_matches_type(EmbeddingResponse, embedding, path=["response"])

        assert cast(Any, response.is_closed) is True
