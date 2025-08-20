# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable, Optional

import httpx

from ..types import batch_create_params, batch_retrieve_status_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, strip_not_given, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.batch_create_response import BatchCreateResponse
from ..types.batch_retrieve_status_response import BatchRetrieveStatusResponse

__all__ = ["BatchResource", "AsyncBatchResource"]


class BatchResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> BatchResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/spatiali-se/spatialise-python#accessing-raw-response-data-eg-headers
        """
        return BatchResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BatchResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/spatiali-se/spatialise-python#with_streaming_response
        """
        return BatchResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        jobs: Iterable[batch_create_params.Job],
        metadata: Optional[Dict[str, object]] | NotGiven = NOT_GIVEN,
        webhook_url: Optional[str] | NotGiven = NOT_GIVEN,
        webhook_secret: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> BatchCreateResponse:
        """Submit a batch of soil organic carbon prediction requests.

        This endpoint:

        1.

        Validates the batch request containing multiple prediction jobs
        2. Creates a batch for processing soil organic carbon density predictions
        3. Initiates processing for each geographic area and year combination
        4. Returns batch information for tracking progress

        Each job in the batch will generate a cloud-optimized GeoTIFF containing soil
        organic carbon density predictions for the specified polygon and year.

        **Idempotency:** Provide an `Idempotency-Key` header to ensure requests are
        processed only once. If the same key is received within 24 hours, the original
        response is returned without reprocessing.

        **Rate Limits:**

        - Maximum 5000 hectares per day per API key
        - Maximum 1000 jobs per day per API key

        Args: request: The FastAPI request object client_batch_request: The batch
        creation request containing prediction jobs idempotency_key: Optional key for
        idempotent requests webhook_secret: Optional secret for webhook authentication
        token: The validated authentication token

        Returns: BatchResponse: The created batch information including batch ID and
        status

        Raises: HTTPException: If batch creation fails 409: If idempotency key is reused
        with different request body 429: If daily rate limits are exceeded

        Args:
          jobs: List of prediction jobs

          metadata: Optional metadata for the batch

          webhook_url: Optional webhook URL for batch completion

          webhook_secret: Secret token for authenticating webhook callbacks. Required if webhook_url is
              provided.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        extra_headers = {**strip_not_given({"Webhook-Secret": webhook_secret}), **(extra_headers or {})}
        return self._post(
            "/v1/batch/",
            body=maybe_transform(
                {
                    "jobs": jobs,
                    "metadata": metadata,
                    "webhook_url": webhook_url,
                },
                batch_create_params.BatchCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=BatchCreateResponse,
        )

    def retrieve_status(
        self,
        batch_id: str,
        *,
        cursor: Optional[str] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BatchRetrieveStatusResponse:
        """
        Retrieve the current status of a soil organic carbon prediction batch.

        Returns detailed information about the batch processing progress, including the
        status of individual prediction jobs. Once jobs are completed, result URLs
        provide access to cloud-optimized GeoTIFF files.

        **Pagination:** Job results are paginated with a default limit of 100 jobs per
        page. Use the `cursor` parameter with the `next_cursor` value from the previous
        response to fetch subsequent pages.

        The client identity is determined from the Authorization token.

        Args: request: The FastAPI request object batch_id: The batch ID to query limit:
        Maximum number of jobs to return (default: 100, max: 100) cursor: Pagination
        cursor from previous response (Phase 1: ignored) token: The validated
        authentication token

        Returns: BatchStatusResponse: The batch status and paginated job details

        Raises: HTTPException: If batch not found or query fails

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not batch_id:
            raise ValueError(f"Expected a non-empty value for `batch_id` but received {batch_id!r}")
        return self._get(
            f"/v1/batch/{batch_id}/status",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "cursor": cursor,
                        "limit": limit,
                    },
                    batch_retrieve_status_params.BatchRetrieveStatusParams,
                ),
            ),
            cast_to=BatchRetrieveStatusResponse,
        )


class AsyncBatchResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncBatchResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/spatiali-se/spatialise-python#accessing-raw-response-data-eg-headers
        """
        return AsyncBatchResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBatchResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/spatiali-se/spatialise-python#with_streaming_response
        """
        return AsyncBatchResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        jobs: Iterable[batch_create_params.Job],
        metadata: Optional[Dict[str, object]] | NotGiven = NOT_GIVEN,
        webhook_url: Optional[str] | NotGiven = NOT_GIVEN,
        webhook_secret: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> BatchCreateResponse:
        """Submit a batch of soil organic carbon prediction requests.

        This endpoint:

        1.

        Validates the batch request containing multiple prediction jobs
        2. Creates a batch for processing soil organic carbon density predictions
        3. Initiates processing for each geographic area and year combination
        4. Returns batch information for tracking progress

        Each job in the batch will generate a cloud-optimized GeoTIFF containing soil
        organic carbon density predictions for the specified polygon and year.

        **Idempotency:** Provide an `Idempotency-Key` header to ensure requests are
        processed only once. If the same key is received within 24 hours, the original
        response is returned without reprocessing.

        **Rate Limits:**

        - Maximum 5000 hectares per day per API key
        - Maximum 1000 jobs per day per API key

        Args: request: The FastAPI request object client_batch_request: The batch
        creation request containing prediction jobs idempotency_key: Optional key for
        idempotent requests webhook_secret: Optional secret for webhook authentication
        token: The validated authentication token

        Returns: BatchResponse: The created batch information including batch ID and
        status

        Raises: HTTPException: If batch creation fails 409: If idempotency key is reused
        with different request body 429: If daily rate limits are exceeded

        Args:
          jobs: List of prediction jobs

          metadata: Optional metadata for the batch

          webhook_url: Optional webhook URL for batch completion

          webhook_secret: Secret token for authenticating webhook callbacks. Required if webhook_url is
              provided.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        extra_headers = {**strip_not_given({"Webhook-Secret": webhook_secret}), **(extra_headers or {})}
        return await self._post(
            "/v1/batch/",
            body=await async_maybe_transform(
                {
                    "jobs": jobs,
                    "metadata": metadata,
                    "webhook_url": webhook_url,
                },
                batch_create_params.BatchCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=BatchCreateResponse,
        )

    async def retrieve_status(
        self,
        batch_id: str,
        *,
        cursor: Optional[str] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BatchRetrieveStatusResponse:
        """
        Retrieve the current status of a soil organic carbon prediction batch.

        Returns detailed information about the batch processing progress, including the
        status of individual prediction jobs. Once jobs are completed, result URLs
        provide access to cloud-optimized GeoTIFF files.

        **Pagination:** Job results are paginated with a default limit of 100 jobs per
        page. Use the `cursor` parameter with the `next_cursor` value from the previous
        response to fetch subsequent pages.

        The client identity is determined from the Authorization token.

        Args: request: The FastAPI request object batch_id: The batch ID to query limit:
        Maximum number of jobs to return (default: 100, max: 100) cursor: Pagination
        cursor from previous response (Phase 1: ignored) token: The validated
        authentication token

        Returns: BatchStatusResponse: The batch status and paginated job details

        Raises: HTTPException: If batch not found or query fails

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not batch_id:
            raise ValueError(f"Expected a non-empty value for `batch_id` but received {batch_id!r}")
        return await self._get(
            f"/v1/batch/{batch_id}/status",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "cursor": cursor,
                        "limit": limit,
                    },
                    batch_retrieve_status_params.BatchRetrieveStatusParams,
                ),
            ),
            cast_to=BatchRetrieveStatusResponse,
        )


class BatchResourceWithRawResponse:
    def __init__(self, batch: BatchResource) -> None:
        self._batch = batch

        self.create = to_raw_response_wrapper(
            batch.create,
        )
        self.retrieve_status = to_raw_response_wrapper(
            batch.retrieve_status,
        )


class AsyncBatchResourceWithRawResponse:
    def __init__(self, batch: AsyncBatchResource) -> None:
        self._batch = batch

        self.create = async_to_raw_response_wrapper(
            batch.create,
        )
        self.retrieve_status = async_to_raw_response_wrapper(
            batch.retrieve_status,
        )


class BatchResourceWithStreamingResponse:
    def __init__(self, batch: BatchResource) -> None:
        self._batch = batch

        self.create = to_streamed_response_wrapper(
            batch.create,
        )
        self.retrieve_status = to_streamed_response_wrapper(
            batch.retrieve_status,
        )


class AsyncBatchResourceWithStreamingResponse:
    def __init__(self, batch: AsyncBatchResource) -> None:
        self._batch = batch

        self.create = async_to_streamed_response_wrapper(
            batch.create,
        )
        self.retrieve_status = async_to_streamed_response_wrapper(
            batch.retrieve_status,
        )
