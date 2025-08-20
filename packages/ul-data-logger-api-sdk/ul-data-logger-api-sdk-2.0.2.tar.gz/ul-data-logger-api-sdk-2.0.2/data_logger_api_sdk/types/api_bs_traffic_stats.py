from datetime import date

from ul_api_utils.api_resource.api_response import JsonApiResponsePayload


class ApiBsTrafficStatsResponse(JsonApiResponsePayload):
    date: date
    raw_data_size: float
