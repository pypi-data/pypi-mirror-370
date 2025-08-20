from typing import List

from ul_api_utils.api_resource.api_response import JsonApiResponsePayload


class ApiProtocolTypesListResponse(JsonApiResponsePayload):
    protocol_types: List[str]
