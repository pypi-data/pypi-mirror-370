import json
import time
from datetime import datetime
from functools import lru_cache
from typing import Any, List, Type
from uuid import UUID

from ul_api_utils.internal_api.internal_api import InternalApi
from ul_api_utils.internal_api.internal_api_response import TPyloadType
from ul_api_utils.utils.api_method import ApiMethod

from data_logger_api_sdk.data_logger_sdk_config import DataLoggerApiSdkConfig
from data_logger_api_sdk.types.api_bs_traffic_stats import ApiBsTrafficStatsResponse
from data_logger_api_sdk.types.api_device_data_history import ApiDeviceDataHistoryBody, ApiDeviceDataHistoryResponse
from data_logger_api_sdk.types.api_last_bs_data_by_device_macs import ApiDeviceLastBsDataResponse, ApiDeviceMacsListBodyModel
from data_logger_api_sdk.types.api_packet_types import ApiPacketTypesListResponse
from data_logger_api_sdk.types.api_protocol_types import ApiProtocolTypesListResponse


class DataLoggerApiSdk:

    def __init__(self, config: DataLoggerApiSdkConfig) -> None:
        self._config = config
        self._api = InternalApi(entry_point=self._config.api_url, default_auth_token=self._config.api_token)

    @lru_cache(maxsize=None)  # there should not be leaks memory leaks. flake8 just scared inmemory cache ;)
    def request_payload(
        self,
        _: int,
        method: ApiMethod,
        endpoint: str,
        typed_as: Type[TPyloadType],
        body: str | None,
        query: dict[str, Any] | None = None,
    ) -> TPyloadType:
        return (
            self._api.request(
                method=method,
                path=endpoint,
                json=json.loads(body) if body is not None else None,
                q=query,
            )
            .typed(typed_as)
            .check()
            .payload
        )

    def _get_cache_post_payload(
        self,
        method: ApiMethod,
        path: str,
        typed: Type[TPyloadType],
        body: str | None = None,
        query: dict[str, Any] | None = None,
    ) -> TPyloadType:
        ttl_status = round(time.time() / self._config.cache_ttl_s)
        return self.request_payload(ttl_status, method, path, typed, body, query)  # type: ignore  # Type[TPyloadType] is hashable

    def get_protocol_types_list(self, mac: int) -> List[str]:
        return self._get_cache_post_payload(
            ApiMethod.GET,
            f"/devices/mac/{mac}/logs/protocol-types",
            ApiProtocolTypesListResponse,
        ).protocol_types

    def get_packet_types_list(self, mac: int) -> List[str]:
        return self._get_cache_post_payload(
            ApiMethod.GET,
            f"/devices/mac/{mac}/logs/packet-types",
            ApiPacketTypesListResponse,
        ).packet_types

    def get_device_data_history(
        self,
        period_from: datetime,
        period_to: datetime,
        mac: int,
        protocol_type: str | None = None,
        packet_type: str | None = None,
    ) -> List[ApiDeviceDataHistoryResponse]:
        api_device_history_body = ApiDeviceDataHistoryBody(
            period_from=period_from,
            period_to=period_to,
            mac=mac,
            protocol_type=protocol_type,
            packet_type=packet_type,
        ).model_dump_json()
        return self._get_cache_post_payload(
            ApiMethod.POST,
            "/device-data-history",
            List[ApiDeviceDataHistoryResponse],  # type: ignore
            api_device_history_body,
        )

    def get_last_bs_data_by_device_macs(
        self,
        macs: set[int],
    ) -> List[ApiDeviceLastBsDataResponse]:
        return self._get_cache_post_payload(
            ApiMethod.POST,
            "/devices/last-bs-data",
            List[ApiDeviceLastBsDataResponse],  # type: ignore
            ApiDeviceMacsListBodyModel(macs=macs).model_dump_json(),
        )

    def get_bs_traffic_stats(
        self,
        base_station_id: UUID,
        start_at: datetime,
        end_at: datetime,
    ) -> List[ApiBsTrafficStatsResponse]:
        return self._get_cache_post_payload(
            ApiMethod.POST,
            f"/base-stations/{base_station_id}/traffic-stats",
            List[ApiBsTrafficStatsResponse],  # type: ignore
            None,
            {"start_at": start_at, "end_at": end_at},
        )

