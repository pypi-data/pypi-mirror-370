from uuid import UUID
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import UUID4, BaseModel
from ul_api_utils.api_resource.api_response_payload_alias import ApiBaseUserModelPayloadResponse, JsonApiResponsePayload

from data_aggregator_sdk.constants.enums import DeviceModificationTypeEnum, NetworkSysTypeEnum, NetworkTypeEnum, ProtocolEnum
from data_aggregator_sdk.types.device import ApiDeviceMeterPayloadResponse


# REQUEST BODY


class ApiDataGatewayNetworkDevicesInfo(BaseModel):
    mac: int
    network_id: UUID


class ApiDataGatewayNetworkDevicesBody(BaseModel):
    devices: List[ApiDataGatewayNetworkDevicesInfo]


# RESPONSE BODY


class ApiDeviceManufacturerResponse(JsonApiResponsePayload):
    id: UUID4
    date_created: datetime
    date_modified: datetime
    name: str


class ApiDataGatewayResponse(ApiBaseUserModelPayloadResponse):
    name: str


class ApiProtocolResponse(JsonApiResponsePayload):
    id: UUID4
    date_created: datetime
    date_modified: datetime
    name: str
    type: ProtocolEnum


class ApiDeviceMeteringTypeResponse(JsonApiResponsePayload):
    id: UUID4
    date_created: datetime
    date_modified: datetime

    sys_name: str
    name_ru: str
    name_en: str


class ApiDeviceModificationTypeResponse(JsonApiResponsePayload):
    id: UUID4
    date_created: datetime
    date_modified: datetime

    sys_name: str
    name_ru: str
    name_en: str
    type: DeviceModificationTypeEnum
    metering_type_id: Optional[UUID4] = None
    device_metering_type: Optional[ApiDeviceMeteringTypeResponse] = None


class ApiDeviceModificationResponse(JsonApiResponsePayload):
    id: UUID4
    date_created: datetime
    date_modified: datetime
    name: Optional[str] = None
    device_modification_type_id: Optional[UUID4] = None
    device_modification_type: ApiDeviceModificationTypeResponse


class ApiDeviceChannelPayloadResponse(ApiBaseUserModelPayloadResponse):
    device_id: UUID4
    serial_number: int
    inactivity_limit: Optional[int] = None
    device_meter: List[ApiDeviceMeterPayloadResponse]


class ApiDataGatewayNetworkDeviceResponse(ApiBaseUserModelPayloadResponse):
    manufacturer_serial_number: str
    firmware_version: Optional[str] = None
    hardware_version: Optional[str] = None
    date_produced: Optional[datetime] = None
    device_manufacturer: ApiDeviceManufacturerResponse
    device_modification: ApiDeviceModificationResponse
    device_channel: List[ApiDeviceChannelPayloadResponse]


class ApiDataGatewaysNetworkResponse(ApiBaseUserModelPayloadResponse):
    name: str
    type_network: NetworkTypeEnum
    data_gateway_id: UUID4
    data_gateway: ApiDataGatewayResponse
    sys_type: NetworkSysTypeEnum
    specifier: Optional[str] = None
    params: Optional[Dict[str, Any]] = None


class ApiDataGatewayNetworkDeviceInfoResponse(JsonApiResponsePayload):
    id: UUID4
    date_created: datetime
    date_modified: datetime
    uplink_protocol_id: UUID4
    downlink_protocol_id: UUID4
    data_gateway_network_id: UUID4
    mac: int
    key_id: Optional[UUID4] = None
    device_id: UUID4
    device: ApiDataGatewayNetworkDeviceResponse
    uplink_encryption_key: Optional[str] = None
    uplink_decrypted_encryption_key: Optional[str] = None
    downlink_encryption_key: Optional[str] = None
    downlink_decrypted_encryption_key: Optional[str] = None
    encryption_key: Optional[str] = None
    protocol: ApiProtocolResponse
    network: Optional[ApiDataGatewaysNetworkResponse] = None
