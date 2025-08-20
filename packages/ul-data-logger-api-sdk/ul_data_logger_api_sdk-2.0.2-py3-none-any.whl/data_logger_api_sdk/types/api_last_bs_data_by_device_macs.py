from datetime import datetime, timedelta, timezone
from typing import List, Set

from pydantic import UUID4, BaseModel, Field
from ul_api_utils.api_resource.api_response import JsonApiResponsePayload
from ul_api_utils.api_resource.api_response_payload_alias import ApiBaseModelPayloadResponse

BASE_STATION__INACTIVITY_LIMIT = timedelta(minutes=10)


class ApiDeviceMacsListBodyModel(BaseModel):
    macs: Set[int] = Field(title="Macs", description="list of device macs", min_length=1)


class SdrConfigDataResponse(JsonApiResponsePayload):
    baud_rate: int


class BsResponse(ApiBaseModelPayloadResponse):
    api_user_modified_id: UUID4 | None = None
    note: str

    type: str
    serial_number: int

    latest_log_datetime: datetime | None = None
    latest_geo_latitude: float | None = None
    latest_geo_longitude: float | None = None
    latest_soft_version: str | None = None
    latest_geo_is_actual: bool | None = None

    sdr_config_data_list: List[SdrConfigDataResponse] | None = None


    @property
    def status_ok(self) -> bool:
        if self.latest_log_datetime is None:
            return False
        if self.latest_log_datetime.tzinfo is None:
            self.latest_log_datetime = self.latest_log_datetime.replace(tzinfo=timezone.utc)
        return (datetime.now(tz=timezone.utc) - self.latest_log_datetime) < BASE_STATION__INACTIVITY_LIMIT


class ApiDeviceLastBsDataResponse(JsonApiResponsePayload):
    mac: int
    latest_signal_rssi: int | None = None
    latest_signal_snr: int | None = None
    bs: BsResponse | None = None
