from datetime import datetime
from uuid import UUID

from data_aggregator_sdk.integration_message import IntegrationV0MessageMeta
from pydantic import BaseModel, field_validator
from ul_api_utils.api_resource.api_response import JsonApiResponsePayload


class ApiDeviceDataHistoryBody(BaseModel):
    period_from: datetime
    period_to: datetime
    mac: int
    protocol_type: str | None = None
    packet_type: str | None = None

    @field_validator("period_from", mode="before")
    @classmethod
    def validate_period_from(cls, value: str | datetime) -> datetime:
        if isinstance(value, str):
            return datetime.combine(datetime.fromisoformat(value), datetime.min.time())
        return value

    @field_validator("period_to", mode="before")
    @classmethod
    def validate_period_to(cls, value: str | datetime) -> datetime:
        if isinstance(value, str):
            return datetime.combine(datetime.fromisoformat(value), datetime.max.time())
        return value


class ApiDeviceDataHistoryResponse(JsonApiResponsePayload):
    mac: int
    bs_serial_number: int | None = None
    date_created: datetime
    id: UUID | None = None
    raw_dt: datetime
    raw_payload: str
    raw_message: str
    meta: IntegrationV0MessageMeta
