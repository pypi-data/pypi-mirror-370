# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from spatialise import SpatialiseSoilPrediction, AsyncSpatialiseSoilPrediction
from tests.utils import assert_matches_type
from spatialise.types import (
    BatchCreateResponse,
    BatchRetrieveStatusResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestBatch:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(
        reason="currently no good way to test endpoints defining callbacks, Prism mock server will fail trying to reach the provided callback url"
    )
    @parametrize
    def test_method_create(self, client: SpatialiseSoilPrediction) -> None:
        batch = client.batch.create(
            jobs=[
                {
                    "polygon": {"coordinates": [[[0]]]},
                    "year": 2018,
                }
            ],
        )
        assert_matches_type(BatchCreateResponse, batch, path=["response"])

    @pytest.mark.skip(
        reason="currently no good way to test endpoints defining callbacks, Prism mock server will fail trying to reach the provided callback url"
    )
    @parametrize
    def test_method_create_with_all_params(self, client: SpatialiseSoilPrediction) -> None:
        batch = client.batch.create(
            jobs=[
                {
                    "polygon": {
                        "coordinates": [[[0]]],
                        "type": "Polygon",
                    },
                    "year": 2018,
                }
            ],
            metadata={"foo": "bar"},
            webhook_url="webhook_url",
            webhook_secret="Webhook-Secret",
        )
        assert_matches_type(BatchCreateResponse, batch, path=["response"])

    @pytest.mark.skip(
        reason="currently no good way to test endpoints defining callbacks, Prism mock server will fail trying to reach the provided callback url"
    )
    @parametrize
    def test_raw_response_create(self, client: SpatialiseSoilPrediction) -> None:
        response = client.batch.with_raw_response.create(
            jobs=[
                {
                    "polygon": {"coordinates": [[[0]]]},
                    "year": 2018,
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch = response.parse()
        assert_matches_type(BatchCreateResponse, batch, path=["response"])

    @pytest.mark.skip(
        reason="currently no good way to test endpoints defining callbacks, Prism mock server will fail trying to reach the provided callback url"
    )
    @parametrize
    def test_streaming_response_create(self, client: SpatialiseSoilPrediction) -> None:
        with client.batch.with_streaming_response.create(
            jobs=[
                {
                    "polygon": {"coordinates": [[[0]]]},
                    "year": 2018,
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch = response.parse()
            assert_matches_type(BatchCreateResponse, batch, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_status(self, client: SpatialiseSoilPrediction) -> None:
        batch = client.batch.retrieve_status(
            batch_id="batch_id",
        )
        assert_matches_type(BatchRetrieveStatusResponse, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_status_with_all_params(self, client: SpatialiseSoilPrediction) -> None:
        batch = client.batch.retrieve_status(
            batch_id="batch_id",
            cursor="cursor",
            limit=0,
        )
        assert_matches_type(BatchRetrieveStatusResponse, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve_status(self, client: SpatialiseSoilPrediction) -> None:
        response = client.batch.with_raw_response.retrieve_status(
            batch_id="batch_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch = response.parse()
        assert_matches_type(BatchRetrieveStatusResponse, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve_status(self, client: SpatialiseSoilPrediction) -> None:
        with client.batch.with_streaming_response.retrieve_status(
            batch_id="batch_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch = response.parse()
            assert_matches_type(BatchRetrieveStatusResponse, batch, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve_status(self, client: SpatialiseSoilPrediction) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `batch_id` but received ''"):
            client.batch.with_raw_response.retrieve_status(
                batch_id="",
            )


class TestAsyncBatch:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(
        reason="currently no good way to test endpoints defining callbacks, Prism mock server will fail trying to reach the provided callback url"
    )
    @parametrize
    async def test_method_create(self, async_client: AsyncSpatialiseSoilPrediction) -> None:
        batch = await async_client.batch.create(
            jobs=[
                {
                    "polygon": {"coordinates": [[[0]]]},
                    "year": 2018,
                }
            ],
        )
        assert_matches_type(BatchCreateResponse, batch, path=["response"])

    @pytest.mark.skip(
        reason="currently no good way to test endpoints defining callbacks, Prism mock server will fail trying to reach the provided callback url"
    )
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncSpatialiseSoilPrediction) -> None:
        batch = await async_client.batch.create(
            jobs=[
                {
                    "polygon": {
                        "coordinates": [[[0]]],
                        "type": "Polygon",
                    },
                    "year": 2018,
                }
            ],
            metadata={"foo": "bar"},
            webhook_url="webhook_url",
            webhook_secret="Webhook-Secret",
        )
        assert_matches_type(BatchCreateResponse, batch, path=["response"])

    @pytest.mark.skip(
        reason="currently no good way to test endpoints defining callbacks, Prism mock server will fail trying to reach the provided callback url"
    )
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncSpatialiseSoilPrediction) -> None:
        response = await async_client.batch.with_raw_response.create(
            jobs=[
                {
                    "polygon": {"coordinates": [[[0]]]},
                    "year": 2018,
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch = await response.parse()
        assert_matches_type(BatchCreateResponse, batch, path=["response"])

    @pytest.mark.skip(
        reason="currently no good way to test endpoints defining callbacks, Prism mock server will fail trying to reach the provided callback url"
    )
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncSpatialiseSoilPrediction) -> None:
        async with async_client.batch.with_streaming_response.create(
            jobs=[
                {
                    "polygon": {"coordinates": [[[0]]]},
                    "year": 2018,
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch = await response.parse()
            assert_matches_type(BatchCreateResponse, batch, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_status(self, async_client: AsyncSpatialiseSoilPrediction) -> None:
        batch = await async_client.batch.retrieve_status(
            batch_id="batch_id",
        )
        assert_matches_type(BatchRetrieveStatusResponse, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_status_with_all_params(self, async_client: AsyncSpatialiseSoilPrediction) -> None:
        batch = await async_client.batch.retrieve_status(
            batch_id="batch_id",
            cursor="cursor",
            limit=0,
        )
        assert_matches_type(BatchRetrieveStatusResponse, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve_status(self, async_client: AsyncSpatialiseSoilPrediction) -> None:
        response = await async_client.batch.with_raw_response.retrieve_status(
            batch_id="batch_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch = await response.parse()
        assert_matches_type(BatchRetrieveStatusResponse, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve_status(self, async_client: AsyncSpatialiseSoilPrediction) -> None:
        async with async_client.batch.with_streaming_response.retrieve_status(
            batch_id="batch_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch = await response.parse()
            assert_matches_type(BatchRetrieveStatusResponse, batch, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve_status(self, async_client: AsyncSpatialiseSoilPrediction) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `batch_id` but received ''"):
            await async_client.batch.with_raw_response.retrieve_status(
                batch_id="",
            )
