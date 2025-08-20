from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from ul_api_utils.api_resource.api_response import JsonApiResponsePayload
from ul_api_utils.api_resource.api_response_payload_alias import ApiBaseUserModelPayloadResponse

from data_aggregator_sdk.constants.enums import DeviceModificationTypeEnum, NetworkSysTypeEnum, NetworkTypeEnum, \
    ProtocolEnum, ResourceKind


class ApiDataGatewayResponse(ApiBaseUserModelPayloadResponse):
    name: str


class ApiDataGatewaysNetworkResponse(ApiBaseUserModelPayloadResponse):
    name: str
    type_network: NetworkTypeEnum
    data_gateway_id: UUID
    data_gateway: ApiDataGatewayResponse
    sys_type: NetworkSysTypeEnum
    specifier: Optional[str] = None
    params: Optional[Dict[str, Any]] = None


class ApiProtocolResponse(JsonApiResponsePayload):
    id: UUID
    date_created: datetime
    date_modified: datetime
    name: str
    type: ProtocolEnum


class ApiDataGatewayNetworkDevicePayloadResponse(JsonApiResponsePayload):
    id: UUID
    date_created: datetime
    date_modified: datetime
    uplink_protocol_id: UUID
    downlink_protocol_id: UUID
    data_gateway_network_id: UUID
    mac: int
    key_id: Optional[UUID] = None
    device_id: UUID
    uplink_encryption_key: Optional[str] = None
    downlink_encryption_key: Optional[str] = None
    encryption_key: Optional[str] = None
    protocol: ApiProtocolResponse
    network: Optional[ApiDataGatewaysNetworkResponse] = None


class ApiDeviceMeteringTypeResponse(JsonApiResponsePayload):
    id: UUID
    date_created: datetime
    date_modified: datetime

    sys_name: str
    name_ru: str
    name_en: str


class ApiDeviceModificationTypeResponse(JsonApiResponsePayload):
    id: UUID
    date_created: datetime
    date_modified: datetime

    sys_name: str
    name_ru: str
    name_en: str
    type: DeviceModificationTypeEnum
    metering_type_id: UUID
    device_metering_type: ApiDeviceMeteringTypeResponse


class ApiDeviceModificationResponse(JsonApiResponsePayload):
    id: UUID
    date_created: datetime
    date_modified: datetime
    name: Optional[str] = None
    device_modification_type_id: Optional[UUID] = None
    device_modification_type: ApiDeviceModificationTypeResponse


class ApiDeviceMeterPayloadResponse(ApiBaseUserModelPayloadResponse):
    device_channel_id: UUID
    value_multiplier: Optional[float] = None
    unit_multiplier: Optional[float] = None
    kind: ResourceKind


class ApiDeviceChannelPayloadResponse(ApiBaseUserModelPayloadResponse):
    inactivity_limit: Optional[int] = None
    serial_number: int
    device_meter: List[ApiDeviceMeterPayloadResponse]


class ApiDeviceManufacturerResponse(JsonApiResponsePayload):
    id: UUID
    date_created: datetime
    date_modified: datetime

    name: str


class ApiImportDeviceResponse(ApiBaseUserModelPayloadResponse):
    manufacturer_serial_number: str
    firmware_version: Optional[str] = None
    hardware_version: Optional[str] = None
    date_produced: Optional[datetime] = None
    device_manufacturer: ApiDeviceManufacturerResponse
    device_modification: ApiDeviceModificationResponse
    device_channel: List[ApiDeviceChannelPayloadResponse]
    data_gateway_network_device: Optional[ApiDataGatewayNetworkDevicePayloadResponse] = None
