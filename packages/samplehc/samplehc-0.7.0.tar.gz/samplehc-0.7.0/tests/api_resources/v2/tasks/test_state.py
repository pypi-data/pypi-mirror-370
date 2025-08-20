# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types.v2.tasks import StateGetResponse, StateUpdateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestState:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: SampleHealthcare) -> None:
        state = client.v2.tasks.state.update(
            task_id="taskId",
            key="key",
        )
        assert_matches_type(StateUpdateResponse, state, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: SampleHealthcare) -> None:
        state = client.v2.tasks.state.update(
            task_id="taskId",
            key="key",
            value={},
        )
        assert_matches_type(StateUpdateResponse, state, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: SampleHealthcare) -> None:
        response = client.v2.tasks.state.with_raw_response.update(
            task_id="taskId",
            key="key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        state = response.parse()
        assert_matches_type(StateUpdateResponse, state, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: SampleHealthcare) -> None:
        with client.v2.tasks.state.with_streaming_response.update(
            task_id="taskId",
            key="key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            state = response.parse()
            assert_matches_type(StateUpdateResponse, state, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            client.v2.tasks.state.with_raw_response.update(
                task_id="",
                key="key",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: SampleHealthcare) -> None:
        state = client.v2.tasks.state.get(
            "taskId",
        )
        assert_matches_type(StateGetResponse, state, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: SampleHealthcare) -> None:
        response = client.v2.tasks.state.with_raw_response.get(
            "taskId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        state = response.parse()
        assert_matches_type(StateGetResponse, state, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: SampleHealthcare) -> None:
        with client.v2.tasks.state.with_streaming_response.get(
            "taskId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            state = response.parse()
            assert_matches_type(StateGetResponse, state, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            client.v2.tasks.state.with_raw_response.get(
                "",
            )


class TestAsyncState:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncSampleHealthcare) -> None:
        state = await async_client.v2.tasks.state.update(
            task_id="taskId",
            key="key",
        )
        assert_matches_type(StateUpdateResponse, state, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        state = await async_client.v2.tasks.state.update(
            task_id="taskId",
            key="key",
            value={},
        )
        assert_matches_type(StateUpdateResponse, state, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.tasks.state.with_raw_response.update(
            task_id="taskId",
            key="key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        state = await response.parse()
        assert_matches_type(StateUpdateResponse, state, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.tasks.state.with_streaming_response.update(
            task_id="taskId",
            key="key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            state = await response.parse()
            assert_matches_type(StateUpdateResponse, state, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            await async_client.v2.tasks.state.with_raw_response.update(
                task_id="",
                key="key",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncSampleHealthcare) -> None:
        state = await async_client.v2.tasks.state.get(
            "taskId",
        )
        assert_matches_type(StateGetResponse, state, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.tasks.state.with_raw_response.get(
            "taskId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        state = await response.parse()
        assert_matches_type(StateGetResponse, state, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.tasks.state.with_streaming_response.get(
            "taskId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            state = await response.parse()
            assert_matches_type(StateGetResponse, state, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            await async_client.v2.tasks.state.with_raw_response.get(
                "",
            )
