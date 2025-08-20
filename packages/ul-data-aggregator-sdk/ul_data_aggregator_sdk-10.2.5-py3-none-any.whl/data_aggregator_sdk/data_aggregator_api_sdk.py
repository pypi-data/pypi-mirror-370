import base64
import json
from decimal import Decimal
from datetime import date, datetime
from typing import Dict, Any, List, Tuple, Optional, Union
from uuid import UUID

from ul_api_utils.api_resource.api_response import JsonApiResponsePayload
from ul_api_utils.api_resource.api_response_payload_alias import ApiBaseUserModelPayloadResponse, ApiBaseModelPayloadResponse
from ul_api_utils.internal_api.internal_api import InternalApi
from ul_api_utils.internal_api.internal_api_response import InternalApiResponse, InternalApiResponseCheckLevel
from ul_api_utils.validators.custom_fields import WhiteSpaceStrippedStrAnnotation, PgTypeInt32Annotation, CronScheduleAnnotation, UTCOffsetSecondsAnnotation
from ul_api_utils.utils.json_encoder import CustomJSONEncoder
from pydantic import BaseModel, UUID4, Field

from data_aggregator_sdk.constants.enums import IntervalSelectValue, EncryptionType, ResourceKind, NetworkTypeEnum, \
    NetworkSysTypeEnum, DeviceHack, DataAggregatorApiUserType, DownlinkTaskType, ScheduleType, ReglamentType, \
    SignalModulation, DownlinkTaskStatus, IntegrationV0MessageEvent, JournalDataType, SensorType, UnbpGetDataPacket, \
    UnbpSetSchedulePacket, UnbpSetScheduleAction, DeviceDownlinkTaskStatus, BinaryDataFileType
from data_aggregator_sdk.data_aggregator_api_sdk_config import DataAggregatorApiSdkConfig
from data_aggregator_sdk.integration_message import ProfileKind, ProfileGranulation
from data_aggregator_sdk.types.device import ApiImportDeviceResponse, ApiDataGatewayNetworkDevicePayloadResponse, \
    ApiDeviceMeterPayloadResponse, ApiDeviceChannelPayloadResponse
from data_aggregator_sdk.types.get_data_gateway_network_device_list import ApiDataGatewaysNetworkResponse, \
    ApiDeviceModificationTypeResponse, ApiProtocolResponse
from data_aggregator_sdk.utils.internal_api_error_handler import internal_api_error_handler
from data_aggregator_sdk.utils.internal_api_error_handler_old import internal_api_error_handler_old


class ApiDeviceProfileGranularityResponse(JsonApiResponsePayload):
    device_id: UUID4 = Field(
        ...,
        title="Device ID",
        description="Each device has got unique identifier which is UUID (ex.'f273cbef-0182-4f10-a2b9-17bf54223925')",
    )
    start_date: datetime = Field(
        ...,
        title="Start date of device profile",
        description="Each device profile has start date of collecting data by time granularity",
    )
    end_date: datetime = Field(
        ...,
        title="End date of device profile",
        description="Each device profile has end date of collecting data by time granularity",
    )
    profile_kind: ProfileKind = Field(
        ...,
        title="Type of profile",
        description="Profile type is like side view of collecting data for device (ex. 'VOLTAGE_ABC', 'ENERGY_A_N')",
    )
    granularity_s: ProfileGranulation = Field(
        ...,
        title="Device profile granulation by minutes or seconds",
        description="Granulation is detailing of collecting data, resolution of graph by device (ex. 1 hour (MINUTE_60), 1 second (SECONDS_01))",
    )


class ApiDeviceProfileResponse(JsonApiResponsePayload):
    date_start: datetime = Field(
        ...,
        title="Start date of device profile",
        description="Each device profile has start date of collecting data by time granularity",
    )
    date_end: datetime = Field(
        ...,
        title="End date of device profile",
        description="Each device profile has end date of collecting data by time granularity",
    )
    values_count: int = Field(
        ...,
        title="Amount of collected values",
        description="Number of collected values in sequence of collected values for device by profile type",
    )
    values: List[Optional[float]] = Field(
        ...,
        title="Sequence of collected values",
        description="Collected values for device by profile type looks like sequence of numbers with floating point which depends on profile type",
    )
    profile_kind: ProfileKind = Field(
        ...,
        title="Type of profile",
        description="Profile type is like side view of collecting data for device (ex. 'VOLTAGE_ABC', 'ENERGY_A_N')",
    )
    granularity_s: ProfileGranulation = Field(
        ...,
        title="Device profile granulation by minutes or seconds",
        description="Granulation is detailing of collecting data, resolution of graph by device (ex. 1 hour (MINUTE_60), 1 second (SECONDS_01))",
    )


class DeviceValueDescriptionModelBase(BaseModel):
    registration_date: Optional[datetime] = Field(None, title='Registration Date', description='registration date')
    kind: ResourceKind = Field(ResourceKind.COMMON_CONSUMED, title='Kind', description=f'value kind ({", ".join(kind.name for kind in ResourceKind)})')
    tariff_number: int = Field(-1, title='Tariff Number', description='tariff number')


class DeviceValueDescriptionModel(DeviceValueDescriptionModelBase):
    device_id: Optional[UUID] = Field(None, title='Device Id', description='device identifier')


class DeviceChannelValueDescriptionModel(DeviceValueDescriptionModelBase):
    device_channel_id: Optional[UUID] = Field(None, title='Device Channel Id', description='device channel identifier')


class DeviceMeterValueDescriptionModel(DeviceValueDescriptionModelBase):
    device_meter_id: Optional[UUID] = Field(None, title='Device Meter Id', description='device meter identifier')


class ApiDeviceLastValueDateResponse(JsonApiResponsePayload):
    last_value_date: Dict[str, datetime] = Field(title='Last Value Date', description='last value date: key - device identifier, value - datetime')    # str - UUID (Device.id)


class ApiDeviceChannelLastValueDateResponse(JsonApiResponsePayload):
    last_value_date: Dict[str, datetime] = Field(title='Last Value Date', description='last value date: key - device meter identifier, value - datetime')    # str - UUID (DeviceMeter.id)


class ApiDeviceMeterLastValueDateResponse(JsonApiResponsePayload):
    last_value_date: Dict[UUID, datetime] = Field(title='Last Value Date', description='last value date: key - device meter identifier, value - datetime')   # str - UUID (DeviceMeter.id)


class GeneralApiDeviceMeter(BaseModel):
    value_multiplier: float = Field(title='Value Multiplier', description='value multiplier')
    unit_multiplier: float = Field(title='Unit Multiplier', description='unit multiplier')
    kind: ResourceKind = Field(title='Kind', description=f'meter kind ({", ".join(kind.name for kind in ResourceKind)})')


class GeneralApiDeviceChannel(BaseModel):
    serial_number: int = Field(title='Serial Number', description='Serial Number')
    inactivity_limit: Optional[int] = Field(None, title='Inactivity Limit', description='Inactivity Limit')
    device_meter: List[GeneralApiDeviceMeter] = Field(title='GeneralApiDeviceMeters', description='array of GeneralApiDeviceMeter')


class ApiDeviceManufacturerResponse(JsonApiResponsePayload):
    id: UUID4 = Field(title='Id', description='manufacturer identifier')
    date_created: datetime = Field(title='Date Created', description='date created')
    date_modified: datetime = Field(title='Date Modified', description='date modified')
    name: str = Field(title='Name', description='manufacturer name')


class ApiDeviceModificationResponse(JsonApiResponsePayload):
    id: UUID4 = Field(title='Id', description='modification identifier')
    date_created: datetime = Field(title='Date Created', description='date created')
    date_modified: datetime = Field(title='Date Modified', description='date modified')
    name: Optional[str] = Field(None, title='Name', description='modification name')
    device_modification_type_id: Optional[UUID4] = Field(None, title='Device Modification Type Id', description='device modification type identifier')
    device_modification_type: ApiDeviceModificationTypeResponse = Field(title='ApiDeviceModificationTypeResponse', description='device modification type')


class ApiDataGatewayNetworkDeviceResponse(ApiBaseUserModelPayloadResponse):
    manufacturer_serial_number: str = Field(title='Manufacturer Serial Number', description='manufacturer serial number')
    firmware_version: Optional[str] = Field(None, title='Firmware Version', description='firmware version')
    hardware_version: Optional[str] = Field(None, title='Hardware Version', description='hardware version')
    date_produced: Optional[datetime] = Field(None, title='Date Produced', description='date produced')
    device_manufacturer: ApiDeviceManufacturerResponse = Field(title='ApiDeviceManufacturerResponse', description='device manufacturer')
    device_modification: ApiDeviceModificationResponse = Field(title='ApiDeviceModificationResponse', description='device modification')
    device_channel: List[ApiDeviceChannelPayloadResponse] = Field(title='ApiDeviceChannelPayloadResponse', description='device channel')


class ApiDataGatewayNetworkDeviceByMacAndNetworkPayloadResponse(JsonApiResponsePayload):
    id: UUID4 = Field(title='Id', description='ID')
    date_created: datetime = Field(title='Date Created', description='date created')
    date_modified: datetime = Field(title='Date Modified', description='date modified')
    uplink_protocol_id: UUID4 = Field(title='Uplink Protocol Id', description='uplink protocol identifier')
    downlink_protocol_id: UUID4 = Field(title='Downlink Protocol Id', description='downlink protocol identifier')
    data_gateway_network_id: UUID4 = Field(title='Data Gateway Network Id', description='data gateway network identifier')
    mac: int = Field(title='Mac', description='MAC')
    key_id: Optional[UUID4] = Field(None, title='Key Id', description='key id')
    device_id: UUID4 = Field(title='Device Id', description='device id')
    device: ApiDataGatewayNetworkDeviceResponse = Field(title='ApiDataGatewayNetworkDeviceResponse', description='device')
    uplink_encryption_key: Optional[str] = Field(None, title='Uplink Encryption Key', description='uplink encryption key')
    downlink_encryption_key: Optional[str] = Field(None, title='Downlink Encryption Key', description='downlink encryption key')
    encryption_key: Optional[str] = Field(None, title='Encryption Key', description='encryption key')
    protocol: ApiProtocolResponse = Field(title='ApiProtocolResponse', description='protocol')
    network: Optional[ApiDataGatewaysNetworkResponse] = Field(None, title='ApiDataGatewaysNetworkResponse', description='data gateway network')


class DeviceDescriptionModel(BaseModel):
    device_id: Union[UUID4, UUID] = Field(title='Device Id', description='device id')
    serial_number: int = Field(title='Serial Number', description='serial number')
    registration_date: Optional[datetime] = Field(None, title='Registration Date', description='registration date')
    kind: ResourceKind = Field(ResourceKind.COMMON_CONSUMED, title='Kind', description=f'meter kind ({", ".join(kind.name for kind in ResourceKind)})')
    tariff_number: int = Field(-1, title='Tariff Number', description='tariff number')


class GeneralDeviceValueDescriptionModel(BaseModel):
    device_id: Union[UUID4, UUID] = Field(title='Device Id', description='device id')
    serial_number: int = Field(title='Serial Number', description='serial number')
    registration_date: Optional[datetime] = Field(None, title='Registration Date', description='registration date')
    kind: ResourceKind = Field(ResourceKind.COMMON_CONSUMED, title='Kind', description=f'meter kind ({", ".join(kind.name for kind in ResourceKind)})')
    tariff_number: int = Field(-1, title='Tariff Number', description='tariff number')


class GeneralDeviceMeterValueDescriptionModel(BaseModel):
    meter_id: UUID = Field(title='Meter Id', description='device meter identifier')
    registration_date: Optional[datetime] = Field(None, title='Registration Date', description='registration date')
    kind: ResourceKind = Field(ResourceKind.COMMON_CONSUMED, title='Kind', description=f'meter kind ({", ".join(kind.name for kind in ResourceKind)})')
    tariff_number: int = Field(-1, title='Tariff Number', description='tariff number')
    journal_data_type: JournalDataType = Field(
        JournalDataType.CURRENT,
        title="Journal data type",
        description=f"Journal data type ({', '.join(i.name for i in JournalDataType)})",
    )


class DeviceBatteryLvlDescriptionModel(BaseModel):
    device_id: Union[UUID4, UUID] = Field(title='Device Id', description='device id')
    registration_date: Optional[datetime] = Field(None, title='Registration Date', description='registration date')


class GeneralDeviceValueModel(BaseModel):
    devices: List[GeneralDeviceValueDescriptionModel] = Field(title='GeneralDeviceValueDescriptionModels', description='array of GeneralDeviceValueDescriptionModel')


class ShortDeviceMeterValuesModel(BaseModel):
    device_meter_ids: List[UUID] = Field(title='Device Meter ID list', description='array of device meter ids')

class ShortDeviceChannelValuesModel(BaseModel):
    device_channel_ids: List[UUID] = Field(title='Device Channel ID list', description='array of device channel ids')

class GeneralDeviceMeterValueModel(BaseModel):
    devices_meter: List[GeneralDeviceMeterValueDescriptionModel] = Field(title='GeneralDeviceValueDescriptionModels', description='array of GeneralDeviceValueDescriptionModel')


class GeneralDeviceModificationModel(BaseModel):
    devices: List[DeviceDescriptionModel] = Field(title='DeviceDescriptionModel', description='array of DeviceDescriptionModel')


class DeviceValueBatteryLvlModel(BaseModel):
    devices: List[DeviceBatteryLvlDescriptionModel] = Field(title='DeviceBatteryLvlDescriptionModels', description='array of DeviceBatteryLvlDescriptionModel')


class GeneralApiDeviceResponse(BaseModel):
    date: datetime = Field(title='Date', description='Date')
    device_id: UUID = Field(title='Device Id', description='device identifier')
    serial_number: int = Field(title='Serial Number', description='serial number')
    value: float = Field(title='Value', description='Value')
    kind: ResourceKind = Field(title='Kind', description=f'Kind ({", ".join(kind.name for kind in ResourceKind)})')
    tariff_number: int = Field(title='Tariff Number', description='tariff number')
    journal_data_type: Optional[JournalDataType] = Field(
        None,
        title="Journal data type",
        description=f"Journal data type ({', '.join(i.name for i in JournalDataType)})",
    )


class GeneralApiDeviceMeterResponse(BaseModel):
    meter_id: UUID = Field(title='Meter Id', description='meter identifier')
    value: float = Field(title='Value', description='Value')
    value_date: datetime = Field(title='Value Date', description='Value Date')
    kind: ResourceKind = Field(title='Kind', description=f'Kind ({", ".join(kind.name for kind in ResourceKind)})')
    tariff_number: int = Field(title='Tariff Number', description='tariff number')
    journal_data_type: Optional[JournalDataType] = Field(
        None,
        title="Journal data type",
        description=f"Journal data type ({', '.join(i.name for i in JournalDataType)})",
    )


class GeneralApiDeviceValueResponse(BaseModel):
    device_id: UUID = Field(title='Device Id', description='device identifier')
    serial_number: int = Field(title='Serial Number', description='serial number')
    kind: ResourceKind = Field(title='Kind', description=f'Kind ({", ".join(kind.name for kind in ResourceKind)})')
    tariff_number: int = Field(title='Tariff Number', description='tariff number')
    value: float = Field(title='Value', description='Value')
    value_date: datetime = Field(title='Value Date', description='Value Date')
    last_value: Optional[float] = Field(None, title='Last Value', description='last value')
    last_value_date: Optional[datetime] = Field(None, title='Last Value Date', description='last value date')
    journal_data_type: Optional[JournalDataType] = Field(
        None,
        title="Journal data type",
        description=f"Journal data type ({', '.join(i.name for i in JournalDataType)})",
    )


class ShortDeviceMeterValuesResponse(JsonApiResponsePayload):
    device_channel_ids: List[UUID] = Field(title='Device Channel ID list', description='array of device channel ids')


class ShortDeviceChannelLastValuesResponse(BaseModel):
    device_channel_id: UUID = Field(title='Device Channel ID list', description='array of device channel ids')
    last_value: Optional[float] = Field(None, title='Last Value', description='last value')
    last_value_date: Optional[datetime] = Field(None, title='Last Value Date', description='last value date')

class ShortDeviceChannelLastValuesListResponse(JsonApiResponsePayload):
    device_channels: List[ShortDeviceChannelLastValuesResponse]

class GeneralApiDeviceMeterValueResponse(JsonApiResponsePayload):
    meter_id: UUID = Field(title='Meter Id', description='meter identifier')
    kind: ResourceKind = Field(title='Kind', description=f'Kind ({", ".join(kind.name for kind in ResourceKind)})')
    tariff_number: int = Field(title='Tariff Number', description='tariff number')
    value: float = Field(title='Value', description='Value')
    value_date: datetime = Field(title='Value Date', description='Value Date')
    last_value: Optional[float] = Field(None, title='Last Value', description='last value')
    last_value_date: Optional[datetime] = Field(None, title='Last Value Date', description='last value date')
    journal_data_type: JournalDataType = Field(
        title="Journal data type",
        description=f"Journal data type ({', '.join(i.name for i in JournalDataType)})",
    )


class ApiDeviceMeterDailyValueResponse(JsonApiResponsePayload):
    device_meter_id: UUID = Field(title='Meter Id', description='meter identifier')
    value_date: datetime = Field(title='Value Date', description='Value Date')
    value: float = Field(title='Value', description='Value')


class ApiDeviceLowBatteryResponse(JsonApiResponsePayload):
    value_date: datetime = Field(title='Value Date', description='Value Date')
    device_id: UUID = Field(title='Device Id', description='device identifier')
    value: float = Field(title='Value', description='Value')
    last_value: Optional[float] = Field(None, title='Last Value', description='last value')
    last_value_date: Optional[datetime] = Field(None, title='Last Value Date', description='last value date')


class ApiDeviceBatteriesResponse(JsonApiResponsePayload):
    device_id: UUID4 = Field(title='Device Identifier', description='device unique identifier')
    manufacturer_serial_number: str = Field(title='Manufacturer Serial Number', description='device manufacturer serial number')
    device_modification_name: Optional[str] = Field(None, title='Device Modification Name', description='name of device modification')
    device_modification_type_name: Optional[str] = Field(None, title='Device Modification Type Name', description='name of device type modification')
    date: datetime = Field(title='Date', description='date of the battery value')
    battery_id: int = Field(title='Battery Identifier', description='device battery identifier')
    battery_value: float = Field(title='Battery value', description='battery value (volts')


class ApiDeviceResponse(ApiBaseUserModelPayloadResponse):
    manufacturer_serial_number: str = Field(title='Manufacturer Serial Number', description='manufacturer serial number')
    firmware_version: Optional[str] = Field(None, title='Firmware Version', description='firmware version')
    hardware_version: Optional[str] = Field(None, title='Hardware Version', description='hardware version')
    date_produced: Optional[datetime] = Field(None, title='Date Produced', description='date produced')
    device_manufacturer: ApiDeviceManufacturerResponse = Field(title='Device Manufacturer', description='device manufacturer')
    device_modification: ApiDeviceModificationResponse = Field(title='Device Modification', description='device modification')
    device_channel: List[ApiDeviceChannelPayloadResponse] = Field(title='ApiDeviceChannelPayloadResponse', description='array of ApiDeviceChannelPayloadResponse')
    data_gateway_network_device: Optional[ApiDataGatewayNetworkDevicePayloadResponse] = Field(None, title='ApiDataGatewayNetworkDevicePayloadResponses', description='array of ApiDataGatewayNetworkDevicePayloadResponse')


class ApiDeviceChannelResponse(BaseModel):
    response: Dict[str, Any] = Field(title='Response', description='response')


class ApiDeviceNoData(JsonApiResponsePayload):
    meter_id: UUID4 = Field(title='Meter Id')
    kind: ResourceKind = Field(title='Kind', description=f'Kind ({", ".join(kind.name for kind in ResourceKind)})')
    tariff_number: int = Field(title='Tariff Number')
    last_value: Optional[float] = Field(None, title='Last Value')
    last_value_date: Optional[date] = Field(None, title='Last Value Date')
    count_days: int = Field(title='Count Days', description='count dates')


class ApiDeviceNoDataResponse(JsonApiResponsePayload):
    objects: List[ApiDeviceNoData] = Field(title='ApiDeviceNoDatas', description='array of ApiDeviceNoData')
    procent_no_data: float = Field(title='Procent No Data', description='percent no data')
    count_devices: int = Field(title='Count Devices', description='count devices')
    total_count: int = Field(title='Total Count', description='total count')


class ApiDeviceManufacturer(BaseModel):
    manufacturer_serial_number: str = Field(title='Manufacturer Serial Number', description='manufacturer serial number')


class ApiDeviceFactoryParameters(BaseModel):
    manufacturer_id: Optional[UUID4] = Field(None, title='Manufacturer Id', description='manufacturer id')
    protocol_id: Optional[UUID4] = Field(None, title='Protocol Id', description='protocol id')
    date_produced: Optional[datetime] = Field(None, title='Date Produced', description='date produced')
    device_modification_type_id: Optional[UUID4] = Field(None, title='Device Modification Type Id', description='device modification type id')


class ApiDeviceValues(BaseModel):
    devices: List[List[Any]] = Field(title='Devices', description='devices')


class ApiValueDeviceChannelForEripReports(BaseModel):
    devices: List[Tuple[UUID4, int]] = Field(title='Devices', description='array tuple device identifier, channel number')
    date_to: datetime = Field(title='Date To', description='date to')


class ApiDeviceEvent(BaseModel):
    devices: List[UUID4] = Field(title='Devices', description='array of device identifiers')


class ApiDeviceNoDataList(BaseModel):
    devices: List[GeneralDeviceMeterValueDescriptionModel] = Field(title='GeneralDeviceMeterValueDescriptionModel', description='array of GeneralDeviceMeterValueDescriptionModel')
    period_from: datetime = Field(title='Period From', description='period from (datetime)')
    period_to: Optional[datetime] = Field(None, title='Period To', description='period to (datetime)')


class ApiDataGatewayNetworkDevice(JsonApiResponsePayload):
    id: UUID4 = Field(title='Id', description='identifier')
    date_created: datetime = Field(title='Date Created', description='date created')
    date_modified: datetime = Field(title='Date Modified', description='date modified')
    uplink_protocol_id: UUID4 = Field(title='Uplink Protocol Id', description='uplink protocol identifier')
    downlink_protocol_id: UUID4 = Field(title='Downlink Protocol Id', description='downlink protocol identifier')
    mac: int = Field(title='Mac', description='MAC')
    key_id: Optional[UUID4] = Field(None, title='Key Id', description='key identifier')
    device_id: UUID4 = Field(title='Device Id', description='device id')
    uplink_encryption_key: Optional[str] = Field(None, title='Uplink Encryption Key', description='decryption key')
    downlink_encryption_key: Optional[str] = Field(None, title='Downlink Encryption Key', description='encryption key')
    uplink_encryption_type: EncryptionType = Field(title='Uplink Encryption Type', description=f'uplink encryption type ({", ".join(encryption.name for encryption in EncryptionType)})')
    downlink_encryption_type: EncryptionType = Field(title='Downlink Encryption Type', description=f'downlink encryption type ({", ".join(encryption.name for encryption in EncryptionType)})')
    protocol: ApiProtocolResponse = Field(title='ApiProtocolResponse', description='protocol')
    network: ApiDataGatewaysNetworkResponse = Field(title='ApiDataGatewaysNetworkResponse', description='DataGatewayNetwork')

    @property
    def downlink_encryption_key_bytes(self) -> bytes:
        downlink_encryption_key = self.downlink_encryption_key if self.downlink_encryption_key is not None else ''
        return base64.b64decode(downlink_encryption_key)

    @property
    def uplink_encryption_key_bytes(self) -> bytes:
        uplink_encryption_key = self.uplink_encryption_key if self.uplink_encryption_key is not None else ''
        return base64.b64decode(uplink_encryption_key)


class DeviceData(JsonApiResponsePayload):
    manufacturer_serial_number: str = Field(title='Manufacturer Serial Number', description='device manufacturer serial number')
    firmware_version: Optional[str] = Field(None, title='Firmware Version', description='device firmware version')
    hardware_version: Optional[str] = Field(None, title='Hardware Version', description='device hardware version')
    hacks: List[DeviceHack] = Field(title='Hacks', description=f'array of device processing modifiers ({", ".join(hack.name for hack in DeviceHack)})')
    device_tz: Optional[str] = Field(None, title='Device Tz', description='device time zone')
    date_produced: Optional[datetime] = Field(None, title='Date Produced', description='date produced')
    device_manufacturer: ApiDeviceManufacturerResponse = Field(title='ApiDeviceManufacturerResponse', description='device manufacturer')
    device_modification: ApiDeviceModificationResponse = Field(title='ApiDeviceModificationResponse', description='device modification')
    device_channel: List[ApiDeviceChannelPayloadResponse] = Field(title='ApiDeviceChannelPayloadResponses', description='device channel')
    all_data_gateway_networks: List[ApiDataGatewayNetworkDevice] = Field(title='ApiDataGatewayNetworkDevice', description='all data gateway networks')


class ApiValueDeviceListResponse(JsonApiResponsePayload):
    value_date: datetime = Field(title='Value Date', description='value date')
    device_id: UUID4 = Field(title='Device Id', description='device id')
    serial_number: int = Field(title='Serial Number', description='serial number')
    kind: ResourceKind = Field(title='Kind', description=f'kind ({", ".join(kind.name for kind in ResourceKind)})')
    tariff_number: int = Field(title='Tariff Number', description='tariff number')
    value: float = Field(title='Value', description='VALUE')
    last_value: Optional[float] = Field(None, title='Last Value', description='last value')
    last_value_date: Optional[datetime] = Field(None, title='Last Value Date', description='last value date')


class ApiDeviceFirstValueDateResponse(JsonApiResponsePayload):
    date: datetime = Field(title='Date', description='date')
    device_id: UUID4 = Field(title='Device Id', description='device id')
    serial_number: int = Field(title='Serial Number', description='serial number')
    value: float = Field(title='Value', description='value')
    kind: ResourceKind = Field(title='Kind', description=f'kind ({", ".join(kind.name for kind in ResourceKind)})')
    tariff_number: int = Field(title='Tariff Number', description='tariff number')
    journal_data_type: JournalDataType = Field(
        title="Journal data type",
        description=f"Journal data type ({', '.join(i.name for i in JournalDataType)})",
    )


class ApiMeterFirstValueDateResponse(JsonApiResponsePayload):
    meter_id: UUID = Field(title='Meter Id', description='device meter identifier')
    value: float = Field(title='Value', description='value')
    value_date: datetime = Field(title='Value Date', description='value date')
    kind: ResourceKind = Field(title='Kind', description=f'kind ({", ".join(kind.name for kind in ResourceKind)})')
    tariff_number: int = Field(title='Tariff Number', description='tariff number')
    journal_data_type: JournalDataType = Field(
        title="Journal data type",
        description=f"Journal data type ({', '.join(i.name for i in JournalDataType)})",
    )


class ApiLastValueEripReportsResponse(JsonApiResponsePayload):
    device_id: UUID4 = Field(title='Device Id', description='device id')
    serial_number: int = Field(title='Serial Number', description='serial number')
    date: datetime = Field(title='Date', description='date')
    value: float = Field(title='Value', description='value')
    kind: ResourceKind = Field(title='Kind', description=f'kind ({", ".join(kind.name for kind in ResourceKind)})')
    tariff_number: int = Field(title='Tariff Number', description='tariff number')
    journal_data_type: JournalDataType = Field(
        title="Journal data type",
        description=f"Journal data type ({', '.join(i.name for i in JournalDataType)})",
    )


class DeviceMac(JsonApiResponsePayload):
    mac: int = Field(title='Mac', description='MAC')
    device_id: UUID4 = Field(title='Device Id', description='device identifier')
    address_id: UUID4 = Field(title='Address Id', description='address identifier')


class DeviceImbalanceObject(JsonApiResponsePayload):
    object_procent: float = Field(title='Object Procent', description='object percent')
    different: float = Field(title='Different', description='different')
    flat_sum: float = Field(title='Flat Sum', description='flat sum')
    group_sum: float = Field(title='Group Sum', description='group sum')
    group_devices: List[DeviceMac] = Field(title='Group Devices', description='array of DeviceMac')
    count_not_data_flat: int = Field(title='Count Not Data Flat', description='count not data flat')
    all_flat_count: int = Field(title='All Flat Count', description='all flat count')
    address_id: UUID4 = Field(title='Address Id', description='address id')


class ApiImbalanceValueDeviceListResponse(JsonApiResponsePayload):
    procent: float = Field(title='Procent', description='percent')
    imbalance: float = Field(title='Imbalance', description='imbalance value')
    object: List[DeviceImbalanceObject] = Field(title='Object', description='array of DeviceImbalanceObject')


class SelectValueResultObject(JsonApiResponsePayload):
    number_object: Optional[str] = Field(None, title='Number Object', description='number object')
    count_flat_devices: Optional[int] = Field(None, title='Count Flat Devices', description='count flat devices')
    count_not_data_flat: Optional[int] = Field(None, title='Count Not Data Flat', description='count not data flat')
    device_id: List[UUID4] = Field(title='Device Id', description='device id')
    last_date: date = Field(title='Last Date', description='last date')
    previous_last_value: float = Field(title='Previous Last Value', description='previous last value')
    current_last_value: float = Field(title='Current Last Value', description='current last value')
    address_flat_node_id: Optional[str] = Field(None, title='Address Flat Node Id', description='address flat node id')
    mac: Optional[int] = Field(None, title='Mac', description='MAC')


class ApiObjectValuesDeviceListResponse(JsonApiResponsePayload):
    count_object_devices: int = Field(title='Count Object Devices', description='count object devices')
    count_not_data_objects_devices: int = Field(title='Count Not Data Objects Devices', description='count not data objects devices')
    objects: List[SelectValueResultObject] = Field(title='Objects', description='array of SelectValueResultObject')


class DeviceEventsResponse(JsonApiResponsePayload):
    event_id: UUID4 = Field(title='Event Id', description='device event identifier')
    date_created: datetime = Field(title='Date Created', description='date created')
    user_created_id: UUID4 = Field(title='User Created Id', description='user created id')
    value: Optional[float] = Field(None, title='Value', description='device event value')
    device_id: UUID4 = Field(title='Device Id', description='device identifier')
    serial_number: Optional[int] = Field(None, title='Serial Number', description='device channel serial number')
    type: IntegrationV0MessageEvent = Field(title='Type', description='event type')
    date: datetime = Field(title='Date', description='event date')
    data: Optional[Dict[str, Any]] = Field(None, title='Data', description='event extra data')
    is_system_generated: bool = Field(title='Is System Generated', description='is system generated')


class ApiDeviceStateSyncDataResponse(JsonApiResponsePayload):
    device_events: List[DeviceEventsResponse]
    offset_id: Optional[UUID] = None
    has_next: bool


class UpdateSyncOffsetResponse(JsonApiResponsePayload):
    id: UUID4 = Field(title='Id', description='device state sync offset identifier')
    date_created: datetime = Field(title='Date Created', description='device state sync offset date created')
    date_modified: datetime = Field(title='Date Modified', description='device state sync offset date modified')
    user_created_id: UUID4 = Field(title='User Created Id', description='user created identifier')
    user_modified_id: UUID4 = Field(title='User Modified Id', description='user modified identifier')
    api_user_id: UUID4 = Field(title='Api User Id', description='api user identifier')
    type: str = Field(title='Type', description='device state sync offset type')
    offset: datetime = Field(title='Offset', description='device state sync offset')
    is_confirmed: bool = Field(title='Is Confirmed', description='device state sync offset is confirmed')


class DeviceMeterLastValuesResponse(JsonApiResponsePayload):
    device_meter_id: UUID
    last_value_date: datetime
    last_value: Decimal


class ApiDeviceMeterSyncDataResponse(JsonApiResponsePayload):
    device_meters_values: List[DeviceMeterLastValuesResponse]
    offset_id: Optional[UUID] = None
    has_next: bool


class ApiModificationResponse(BaseModel):
    sys_name: str = Field(title='System Name', description='system name')
    name_ru: str = Field(title='Name Ru', description='name in russian language')
    name_en: str = Field(title='Name En', description='name in english language')


class ApiModificationResponseForDevices(JsonApiResponsePayload):
    device_modification: Dict[str, ApiModificationResponse] = Field(title='Device Modification', description='key - device identifier, value - device modification')


class ApiLastValueDateResponseForDevices(JsonApiResponsePayload):
    last_value_date: Dict[str, datetime] = Field(title='Last value date', description='key - device identifier, value - date of last value')


class ApiDeviceImbalanceModel(BaseModel):
    flat_devices: Optional[List[List[Any]]] = Field(None, title='Flat Devices', description='flat devices')
    group_devices: Optional[List[List[Any]]] = Field(None, title='Group Devices', description='group devices')


class ApiBinaryDataMetadata(BaseModel):
    id: UUID4 = Field(title='Id', description='identifier')
    date_created: datetime = Field(title='Date Created', description='date created')
    date_modified: datetime = Field(title='Date Modified', description='date modified')
    user_created_id: UUID4 = Field(title='User Created Id', description='user created identifier')
    user_modified_id: UUID4 = Field(title='User Modified Id', description='user modified identifier')
    type: BinaryDataFileType = Field(title='File Type', description='Uploaded file type')
    description: str = Field(title='Description', description='Uploaded file description')
    name: str = Field(title='File Name', description='Uploaded file name')
    file_id: UUID4 = Field(title='File unique ID', description='uuid4')


class ApiBinaryDataResponse(JsonApiResponsePayload):
    id: UUID4 = Field(title='Id', description='binary data identifier')
    date_created: datetime = Field(title='Date Created', description='date created')
    user_created_id: UUID4 = Field(title='User Created Id', description='user created id')
    hash: str = Field(title='Hash', description='binary data hash')
    content: str = Field(title='Content', description='binary data content')
    binary_data_metadata: Optional[ApiBinaryDataMetadata] = None


class ApiUserResponse(JsonApiResponsePayload):
    id: UUID4 = Field(title='Api User Identifier', description='unique identifier')
    date_created: datetime = Field(title='Date Created', description='date created')
    date_modified: datetime = Field(title='Date Modified', description='date modified')
    is_alive: bool = Field(title='Is Alive', description='indicator of whether the record is alive')
    date_expiration: datetime = Field(title='Date Expiration', description='date of user expiration')
    name: str = Field(title='Name', description='name')
    note: str = Field(title='Note', description='extra user data')
    permissions: List[int] = Field(title='Permissions', description='array of permissions')


class ApiBaseStationTypeResponse(JsonApiResponsePayload):
    id: UUID4 = Field(title='Id', description='identifier')
    date_created: datetime = Field(title='Date Created', description='date created')
    date_modified: datetime = Field(title='Date Modified', description='date modified')
    user_created_id: UUID4 = Field(title='User Created Id', description='user created identifier')
    user_modified_id: UUID4 = Field(title='User Modified Id', description='user modified identifier')
    name: str = Field(title='Name', description='base station type name')
    notes: str = Field(title='Notes', description='base station typ notes')


class ApiBaseStationResponse(ApiBaseUserModelPayloadResponse):
    identifier: str = Field(title='Identifier', description='identifier')
    base_station_api_user_id: UUID = Field(title='Base Station Api User Id', description='base station api user id')
    base_station_type_id: UUID = Field(title='Base Station Type Id', description='base station type id')
    base_station_api_user: ApiUserResponse = Field(title='Base Station Api User', description='base station api user')
    base_station_type: ApiBaseStationTypeResponse = Field(title='Base Station Type', description='base station type')


class ApiDataGatewayNetworkDeviceForBsUplinkSignalResponse(JsonApiResponsePayload):
    id: UUID4
    date_created: datetime
    date_modified: datetime
    uplink_protocol_id: UUID4
    downlink_protocol_id: UUID4
    mac: int
    key_id: Optional[UUID4] = None
    device_id: UUID4
    uplink_encryption_key: Optional[str] = None
    downlink_encryption_key: Optional[str] = None
    uplink_encryption_type: EncryptionType
    downlink_encryption_type: EncryptionType


class ApiDataGatewayNetworkDeviceShortResponse(JsonApiResponsePayload):
    id: UUID4
    mac: int
    downlink_encryption_key: Optional[str] = None
    downlink_encryption_type: EncryptionType


class ApiBSUplinkSignalResponse(JsonApiResponsePayload):
    id: UUID4
    date_created: datetime
    user_created_id: UUID4

    rssi: Optional[int] = None
    snr: Optional[int] = None
    data_gateway_network_device_id: UUID

    data_gateway_network_device: Optional[ApiDataGatewayNetworkDeviceForBsUplinkSignalResponse] = None
    bs_id: UUID


class BaseBSDownLinkStatusLogData(BaseModel):
    effective_date: Optional[datetime] = None
    bs_downlink_task_id: UUID
    status: DownlinkTaskStatus
    status_comment: str


class ApiBSDownLinkStatusLogResponse(BaseBSDownLinkStatusLogData, JsonApiResponsePayload):
    id: UUID4
    is_active: bool
    date_created: datetime
    user_created_id: UUID4


class ApiDeviceDownlinkStatusLogResponse(JsonApiResponsePayload):
    id: UUID4
    is_active: bool
    date_created: datetime
    user_created_id: UUID4
    effective_date: Optional[datetime] = None
    bs_downlink_task_data_gateway_network_device_id: UUID
    status: DeviceDownlinkTaskStatus
    status_comment: str


class BaseApiBSDownlinkTask(JsonApiResponsePayload):
    note: WhiteSpaceStrippedStrAnnotation
    type: DownlinkTaskType
    priority: PgTypeInt32Annotation
    broadcast: bool
    schedule_type: ScheduleType
    schedule_effective_date_from: datetime
    schedule_effective_date_to: datetime
    reglament_type: ReglamentType
    signal_power: int
    signal_freq: int
    signal_baudrate: int
    signal_modulation: SignalModulation
    lbt_enable: bool
    lbt_max_waiting_time_ms: int
    lbt_silent_time_ms: int
    force: bool
    min_tx_delay_after_rx_ms: Optional[int] = None
    tx_duration_ms: Optional[int] = None


class ApiBSDownlinkTaskTimeSyncResponse(BaseModel):
    utc_offset_s: UTCOffsetSecondsAnnotation


class ApiBSDownlinkTaskUnbpMessageResponse(BaseModel):
    payload: str
    note: str
    crc32: Optional[int] = None


class ApiBsDownlinkTaskFirmwareUpdateFileResponse(BaseModel):
    files: List[ApiBinaryDataResponse]
    sort_order: int
    note: str


class ApiBsDownlinkTaskFirmwareUpdateResponse(BaseModel):
    bs_downlink_firmware_update_files: List[ApiBsDownlinkTaskFirmwareUpdateFileResponse]


class ApiBsDownlinkTaskDataGatewayNetworkDeviceResponse(BaseModel):
    data_gateway_network_device: ApiDataGatewayNetworkDeviceShortResponse


class ApiBsDownlinkBaseStationResponse(BaseModel):
    id: UUID4
    base_station_api_user_id: UUID4


class ApiBSDownlinkTaskUnbpMessageSetRelayResponse(BaseModel):
    state: bool
    relay_id: int


class ApiBSDownlinkTaskUnbpMessageSetScheduleResponse(BaseModel):
    packet: UnbpSetSchedulePacket
    action: UnbpSetScheduleAction
    period_ago: int
    week_mask: List[int]
    day_mask: List[int]
    hour_mask: List[int]


class ApiBSDownlinkTaskUnbpMessageSetClockResponse(BaseModel):
    time: datetime
    timezone_offset_s: int
    timezone_offset_is_negative: bool


class ApiBSDownlinkTaskUnbpMessageGetDataResponse(BaseModel):
    date: date
    request_data_packets: List[UnbpGetDataPacket]


class ApiBSDownlinkTaskResponse(BaseApiBSDownlinkTask):
    id: UUID4
    bs: ApiBsDownlinkBaseStationResponse
    date_created: datetime
    user_created_id: UUID4
    schedule_time: Optional[list[str]] = None
    schedule_cron: Optional[list[CronScheduleAnnotation]] = None
    bs_downlink_task_time_sync: Optional[ApiBSDownlinkTaskTimeSyncResponse] = None
    bs_downlink_task_firmware_update: Optional[ApiBsDownlinkTaskFirmwareUpdateResponse] = None
    bs_downlink_task_unbp_message: Optional[ApiBSDownlinkTaskUnbpMessageResponse] = None
    bs_downlink_task_unbp_message_set_relay: Optional[ApiBSDownlinkTaskUnbpMessageSetRelayResponse] = None
    bs_downlink_task_unbp_message_set_schedule: Optional[ApiBSDownlinkTaskUnbpMessageSetScheduleResponse] = None
    bs_downlink_task_unbp_message_set_clock: Optional[ApiBSDownlinkTaskUnbpMessageSetClockResponse] = None
    bs_downlink_task_unbp_message_get_data: Optional[ApiBSDownlinkTaskUnbpMessageGetDataResponse] = None
    current_status_log: ApiBSDownLinkStatusLogResponse
    bs_downlink_task_dg_network_devices: List[ApiBsDownlinkTaskDataGatewayNetworkDeviceResponse]
    is_active: Optional[bool] = None


class ApiDataGatewayNetworkResponse(ApiBaseUserModelPayloadResponse):
    name: str
    type_network: NetworkTypeEnum
    data_gateway_id: UUID4
    sys_type: NetworkSysTypeEnum
    specifier: Optional[str] = None
    params: Optional[Dict[str, Any]] = None


class DataAggregatorApiUserResponse(ApiBaseModelPayloadResponse):
    date_expiration: datetime = Field(..., title='Date expiration', description='Token date expiration')
    name: str = Field(..., title='Name', description='User name')
    note: str = Field(..., title='Note', description='User notes')
    permissions: List[int] = Field(..., title='Permissions', description='User permsissions')
    type: DataAggregatorApiUserType = Field(..., title='User type', description='User type:')
    data_gateway_network_id: Optional[UUID] = Field(None, title='Data Gateway Network Id', description='Data Gateway Network Identifier')
    data_gateway_network: Optional[ApiDataGatewayNetworkResponse] = Field(None, title='Data Gateway Network', description='Data Gateway Network')


class ApiDeviceUptimeResponse(JsonApiResponsePayload):
    id: UUID4 = Field(title='Identifier', description='uptime unique identifier')
    date_created: datetime = Field(title='Date Created', description='date and time of record creation')
    user_created_id: UUID4 = Field(title='User Created Identifier', description='api user created id')

    device_id: UUID4 = Field(title='Device Identifier', description='device unique identifier')
    channel_id: Optional[UUID4] = Field(None, title='Device Channel Identifier', description='device channel unique identifier')
    date: datetime = Field(title='Date', description='date')
    value: int = Field(title='Uptime value', description='uptime value seconds')


class ApiDeviceSensorResponse(JsonApiResponsePayload):
    id: UUID4 = Field(title='Identifier', description='Device sensor unique identifier')
    date_created: datetime = Field(title='Date Created', description='date and time of record creation')
    user_created_id: UUID4 = Field(title='User Created Identifier', description='api user created id')
    device_id: UUID4 = Field(title='Device Identifier', description='device unique identifier')
    channel_id: Optional[UUID4] = Field(None, title='Device Channel Identifier', description='device channel unique identifier')
    date: datetime = Field(title='Date', description='date')
    sensor_type: SensorType = Field(title="Type of Device Sensor", description=f"One of sensor types ({', '.join(sensor_type.name for sensor_type in SensorType)})")
    sensor_id: int = Field(title="Sensor ID", description="Sensor ID")
    value: Optional[float] = Field(None, title="Value", description="Device Sensor value")


class DataAggregatorApiSdk:

    def __init__(self, config: DataAggregatorApiSdkConfig) -> None:
        self._config = config
        # self._api = InternalApi(entry_point=self._config.api_url, default_auth_token=self._config.api_token)
        self._api_device = InternalApi(entry_point=self._config.api_device_url, default_auth_token=self._config.api_token)

        # self._api_base_station: Optional[InternalApi] = None
        # if self._config.api_base_station_url is not None:
        #     self._api_base_station = InternalApi(entry_point=self._config.api_base_station_url, default_auth_token=self._config.api_token)

#     '''used in services: not used'''
#     @internal_api_error_handler
#     def get_device_dict_by_mac_and_network(self, mac: str, gateway_id: UUID, network_id: UUID) -> Dict[str, Any]:  # TODO: typing
#         return self._api_device.request_get(f'/data-gateways/{gateway_id}/networks/{network_id}/device_mac/{mac}').check().payload_raw    # type: ignore

#     '''used in services: not used'''
#     @internal_api_error_handler
#     def get_device_data(self, gateway_id: UUID, network_id: UUID, mac: int) -> DeviceData:
#         return self._api_device.request_get(f'/data-gateways/{gateway_id}/networks/{network_id}/device_mac/{mac}/data')\
#             .typed(DeviceData).check().payload

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def get_devices_data(self, gateway_id: UUID, network_id: UUID, mac_list: List[int]) -> List[DeviceData]:
        return self._api_device.request_post(f'/data-gateways/{gateway_id}/networks/{network_id}/data', json={"mac_list": mac_list})\
            .typed(List[DeviceData]).check().payload

    '''used in services: Service Data Gateway'''
    @internal_api_error_handler
    def get_device(self, device_id: UUID) -> ApiDeviceResponse:
        return self._api_device.request_get(f'/devices/{device_id}').typed(ApiDeviceResponse).check().payload

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def get_device_channels(self, device_id: UUID) -> List[ApiDeviceChannelPayloadResponse]:
        return self._api_device.request_get(f'/devices/{device_id}/device-channels').typed(List[ApiDeviceChannelPayloadResponse]).check().payload

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def get_device_meters(self, device_channel_id: UUID) -> List[ApiDeviceMeterPayloadResponse]:
        return self._api_device.request_get(f'/device-channels/{device_channel_id}/device-meters').typed(List[ApiDeviceMeterPayloadResponse]).check().payload

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def update_device_meter_unit_multiplier(
        self,
        device_meter_id: UUID,
        device_channel_id: UUID,
        unit_multiplier: float,
        date_application_from: Optional[date],
        date_application_to: Optional[date],
    ) -> ApiDeviceMeterPayloadResponse:
        return self._api_device.request_put(
            f'/device-channels/{device_channel_id}/device-meters/{device_meter_id}/unit-multiplier',
            json={
                "unit_multiplier": unit_multiplier,
                "date_application_from": date_application_from,
                "date_application_to": date_application_to,
            },
        ).typed(ApiDeviceMeterPayloadResponse).check().payload

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def get_or_create_channel(
        self,
        device_id: UUID,
        serial_number: int,
        inactivity_limit: Optional[int],
    ) -> ApiDeviceChannelPayloadResponse:
        return self._api_device.request_post('/device_channel', json={
            "device_id": str(device_id),
            "serial_number": serial_number,
            "inactivity_limit": inactivity_limit,
        }).typed(ApiDeviceChannelPayloadResponse).check().payload

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def get_or_create_meter(
        self,
        device_channel_id: UUID,
        value_multiplier: Optional[float],
        unit_multiplier: Optional[float],
    ) -> ApiDeviceMeterPayloadResponse:
        return self._api_device.request_post('/device-meter', json={
            device_channel_id: str(device_channel_id),
            value_multiplier: value_multiplier,
            unit_multiplier: unit_multiplier,
        }).typed(ApiDeviceMeterPayloadResponse).check().payload

#     '''used in services: not used'''
#     @internal_api_error_handler
#     def get_device_networks(
#         self,
#         device_id: UUID,
#         type_network: NetworkTypeEnum,
#         limit: Optional[int],
#         offset: Optional[int],
#         filters: Optional[List[Dict[str, Any]]],
#         sorts: Optional[List[Tuple[str, str]]],
#     ) -> List[Dict[str, Any]]:  # TODO: typing
#         if type_network not in NetworkTypeEnum:
#             raise ValueError("NetworkType can be only input or output")
#         return self._api_device.request_get(f'/device-network/{device_id}/type/{type_network.value}', q={
#             "filters": filters,
#             "sorts": sorts,
#             "limit": limit,
#             "offset": offset,
#         }).check().payload_raw    # type: ignore

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def get_device_manufacturers(
        self,
        limit: Optional[int],
        offset: Optional[int],
        filters: Optional[List[Dict[str, Any]]],
        sorts: Optional[List[Tuple[str, str]]],
    ) -> List[ApiDeviceManufacturerResponse]:
        return self._api_device.request_get(
            '/manufacturers',
            q={
                "filters": filters,
                "sorts": sorts,
                "limit": limit,
                "offset": offset,
            }).typed(List[ApiDeviceManufacturerResponse]).check().payload

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def get_protocols(
        self,
        limit: Optional[int],
        offset: Optional[int],
        filters: Optional[List[Dict[str, Any]]],
        sorts: Optional[List[Tuple[str, str]]],
    ) -> List[ApiProtocolResponse]:
        return self._api_device.request_get(
            '/protocols',
            q={"filters": filters, "sorts": sorts, "limit": limit, "offset": offset},
        ).typed(List[ApiProtocolResponse]).check().payload

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def get_device_modification_types(
        self,
        limit: Optional[int],
        offset: Optional[int],
        filters: Optional[List[Dict[str, Any]]],
        sorts: Optional[List[Tuple[str, str]]],
    ) -> List[ApiDeviceModificationTypeResponse]:
        return self._api_device.request_get(
            '/device-modification-types',
            q={"filters": filters, "sorts": sorts, "limit": limit, "offset": offset},
        ).typed(List[ApiDeviceModificationTypeResponse]).check().payload

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def get_device_factory_parameters(self, devices_id: Union[UUID, List[UUID]]) -> List[ApiDeviceResponse]:
        devices = [devices_id] if not isinstance(devices_id, list) else devices_id
        return self._api_device.request_post(
            '/devices/factory-parameters',
            json={"devices": [str(device) for device in devices]},
        ).typed(List[ApiDeviceResponse]).check().payload

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler_old
    def get_device_short_factory_parameters(self, device_ids: Union[UUID, List[UUID]]) -> Dict[str, Any]:  # TODO: typing
        devices = [device_ids] if not isinstance(device_ids, list) else device_ids
        return self._api_device.request_post(
            '/devices/short-factory-parameters',
            json={"devices": devices},
        ).check().payload_raw    # type: ignore

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def update_device_manufacturer_by_id(self, device_id: UUID, manufacturer_serial_number: str) -> ApiDeviceResponse:
        return self._api_device.request_patch(
            f'/devices/{device_id}/serial_number',
            json={'manufacturer_serial_number': manufacturer_serial_number},
        ).typed(ApiDeviceResponse).check().payload

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def update_device_factory_parameters(
        self,
        device_id: UUID,
        manufacturer_id: Optional[UUID],
        protocol_id: Optional[UUID],
        date_produced: Optional[datetime],
        device_modification_id: Optional[UUID],
        device_modification_type_id: Optional[UUID],
    ) -> ApiDeviceResponse:
        body_data: Dict[str, Any] = {'date_produced': str(date_produced) if date_produced else None}
        if manufacturer_id is not None:
            body_data.update({'manufacturer_id': str(manufacturer_id)})

        if protocol_id is not None:
            body_data.update({'protocol_id': str(protocol_id)})

        if device_modification_id is not None:
            body_data.update({'device_modification_id': device_modification_id})

        if device_modification_type_id is not None:
            body_data.update({'device_modification_type_id': str(device_modification_type_id)})

        return self._api_device.request_patch(
            f'/devices/{device_id}/factory-parameters',
            json=body_data,
        ).typed(ApiDeviceResponse).check().payload

#   '''used in services: not used'''
#     @internal_api_error_handler
#     def get_device_logger_data(
#         self,
#         device_id: UUID,
#     ) -> Dict[str, Any]:  # TODO: typing
#         return self._api_device.request_get(
#             f'/devices/{device_id}/logger_data').check().payload_raw    # type: ignore

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def get_value_for_device_list(
        self,
        period_from: date | datetime,
        period_to: date | datetime,
        iteration_interval: Optional[IntervalSelectValue],
        devices: GeneralDeviceValueModel,
        locf: Optional[bool],
        journal_data_type: Optional[JournalDataType],
    ) -> List[ApiValueDeviceListResponse]:
        return self._api_device.request_post('/list-device/value-for-device-list', json=devices, q={
            'period_from': period_from,
            'period_to': period_to,
            'locf': locf,
            'iteration_interval': iteration_interval.value if iteration_interval is not None else None,
            'journal_data_type': journal_data_type.value if journal_data_type is not None else None,
        }).typed(List[ApiValueDeviceListResponse]).check().payload

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def get_value_for_device_meter(
        self,
        period_from: date | datetime,
        period_to: date | datetime,
        iteration_interval: Optional[IntervalSelectValue],
        journal_data_type: Optional[JournalDataType],
        devices_meter: GeneralDeviceMeterValueModel,
        is_all_tariffs_flag: bool,
        is_filter_by_period_timezone: bool,
    ) -> List[GeneralApiDeviceMeterValueResponse]:
        return self._api_device.request_post('/list-device/value-for-devices-meter', json=devices_meter, q={
            'period_from': period_from,
            'period_to': period_to,
            'iteration_interval': iteration_interval.value if iteration_interval is not None else None,
            'journal_data_type': journal_data_type.value if journal_data_type is not None else None,
            'is_all_tariffs_flag': is_all_tariffs_flag,
            'is_filter_by_period_timezone': is_filter_by_period_timezone,
        }).typed(List[GeneralApiDeviceMeterValueResponse]).check().payload

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def get_list_device_channel_no_data(
        self,
        period_from: date | datetime,
        period_to: date | datetime,
        devices_channel: ShortDeviceChannelValuesModel,
    ) -> ShortDeviceMeterValuesResponse:
        return self._api_device.request_post('/devices/no-data/period', json=devices_channel, q={
            'period_from': period_from,
            'period_to': period_to,
        }).typed(ShortDeviceMeterValuesResponse).check().payload

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def get_list_device_last_value_by_date(
        self,
        date_selection: date | datetime,
        devices_channel: ShortDeviceChannelValuesModel,
    ) -> ShortDeviceChannelLastValuesListResponse:
        return self._api_device.request_post('/devices/no-data/last-value', json=devices_channel, q={
            'date_selection': date_selection,
        }).typed(ShortDeviceChannelLastValuesListResponse).check().payload

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def get_daily_values_value_for_devices_meter(
        self,
        value_date: date,
        device_meter_ids: List[UUID],
    ) -> List[ApiDeviceMeterDailyValueResponse]:
        return self._api_device.request_post(
            '/list-device/value-for-devices-meter/daily-values',
            json=ShortDeviceMeterValuesModel(device_meter_ids=device_meter_ids),
            q={'value_date': value_date},
        ).typed(List[ApiDeviceMeterDailyValueResponse]).check().payload

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def get_battery_lvl_for_device_list(
        self,
        period_from: date,
        period_to: date,
        iteration_interval: Optional[IntervalSelectValue],
        devices: DeviceValueBatteryLvlModel,
        locf: Optional[bool],
    ) -> List[ApiDeviceLowBatteryResponse]:
        return self._api_device.request_post('/devices/device-sensors/battery-lvl-for-device-list', json=devices, q={
            'period_from': period_from,
            'period_to': period_to,
            'locf': locf,
            'iteration_interval': iteration_interval.value if iteration_interval is not None else None,
        }).typed(List[ApiDeviceLowBatteryResponse]).check().payload

    '''used in services: Data Reporter'''
    @internal_api_error_handler
    def get_device_sensor_battery_list(
        self,
        battery_threshold: Optional[float] = None,
        battery_id: Optional[int] = None,
        device_modifications: Optional[List[UUID]] = None,
        device_metering_types: Optional[List[UUID]] = None,
        macs: Optional[List[int]] = None,
    ) -> List[ApiDeviceBatteriesResponse]:
        return self._api_device.request_post('/devices/device-sensors/batteries-monitoring', json={
            'battery_threshold': battery_threshold,
            'battery_id': battery_id,
            'device_modifications': device_modifications,
            'device_metering_types': device_metering_types,
            'macs': macs,
        }).typed(List[ApiDeviceBatteriesResponse]).check().payload

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def get_first_value_date_for_devices(
        self,
        devices: GeneralDeviceValueModel,
    ) -> List[ApiDeviceFirstValueDateResponse]:
        return self._api_device.request_post(
            '/list-device/search-first-value-date',
            json=devices,
        ).typed(List[ApiDeviceFirstValueDateResponse]).check().payload

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def get_first_value_date_for_meters(
        self,
        meters: GeneralDeviceMeterValueModel,
    ) -> List[ApiMeterFirstValueDateResponse]:
        return self._api_device.request_post(
            '/meters/first-value-date',
            json=meters,
        ).typed(List[ApiMeterFirstValueDateResponse]).check().payload

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def get_last_value_for_erip_reports(
        self,
        devices: List[Tuple[UUID4, int]],
        date_to: datetime,
    ) -> List[ApiLastValueEripReportsResponse]:
        # devices = List[List['device_id: UUID', serial_number: int]]
        return self._api_device.request_post(
            '/erip-reports/last-value',
            json=ApiValueDeviceChannelForEripReports(date_to=date_to, devices=devices),
        ).typed(List[ApiLastValueEripReportsResponse]).check().payload

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def get_object_values_by_device_list(
        self,
        devices: Dict[str, List[List[Any]]],
        reporting_period: date,
    ) -> List[ApiObjectValuesDeviceListResponse]:
        # Dict["name_object": List[List['device_id: UUID', channel: int]],
        # "name_object": List[List['device_id: UUID', channel: int]]]
        return self._api_device.request_post(
            '/list-device/value-object-period',
            q={'reporting_period': reporting_period},
            json={'devices': devices},
        ).typed(List[ApiObjectValuesDeviceListResponse]).check().payload

#   '''used in services: not used'''
# Сделан с соответствием с новой концепцией насчет DataAggregator (get_object_values_by_device_list)
#     @internal_api_error_handler
#     def get_consumption_period_by_device_list(self, devices: List[List[Any]], reporting_period: date) -> List[Dict[str, Any]]:  # TODO: typing
#         # List[List['device_id: UUID', channel: int]]
#         return self._api.request_post('/list-device/consumption-period', q={'reporting_period': reporting_period}, json={'devices': devices}).check().payload_raw

#   '''used in services: not used'''
#     @internal_api_error_handler
#     def get_object_delta(self, devices: Dict[str, List[List[Any]]]) -> List[Dict[str, Any]]:  # TODO: typing
#         # Dict["name_object": List[List['device_id: UUID', channel: int]],
#         # "name_object": List[List['device_id: UUID', channel: int]]]
#         return self._api.request_post('/list-device/value-delta', json={'devices': devices}).check().payload_raw    # type: ignore

#   '''used in services: not used'''
#     @internal_api_error_handler
#     def get_obj_values_deltas_for_group_devices(
#         self,
#         devices_info_box: TDevicesInfoBox,
#         period_from: datetime,
#         period_to: datetime,
#         limit: int,
#         offset: int,
#     ) -> List[Dict[str, Any]]:  # TODO: typing
#         return self._api.request_post('/devices/group/values-deltas', json={"devices_info_box": devices_info_box_to_json(devices_info_box)}, q=get_query_params(
#             period_from=period_from,
#             period_to=period_to,
#             limit=limit,
#             offset=offset,
#         )).check().payload_raw    # type: ignore

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def get_object_imbalance_by_period(
        self,
        devices: Dict[str, ApiDeviceImbalanceModel],
        period_from: date,
        period_to: date,
    ) -> List[ApiImbalanceValueDeviceListResponse]:
        # Dict["object_id": Dict[
        # "flat_devices":List[List['device_id: UUID', channel: int]],
        # "group_devices":List[List['device_id: UUID', channel: int]]]]
        return self._api_device.request_post(
            '/list-device/imbalance',
            q={'period_from': period_from, 'period_to': period_to},
            json={'devices': devices},
        ).typed(List[ApiImbalanceValueDeviceListResponse]).check().payload

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def get_object_actual_imbalance_by_period(
        self,
        devices: Dict[str, ApiDeviceImbalanceModel],
        period_from: date,
        period_to: date,
    ) -> List[ApiImbalanceValueDeviceListResponse]:
        # Dict["object_id": Dict[
        # "flat_devices":List[List['device_id: UUID', channel: int]],
        # "group_devices":List[List['device_id: UUID', channel: int]]]]
        return self._api_device.request_post(
            '/list-device/imbalance/actual',
            q={'period_from': period_from, 'period_to': period_to},
            json={'devices': devices},
        ).typed(List[ApiImbalanceValueDeviceListResponse]).check().payload

#   '''used in services: not used'''
#     @internal_api_error_handler
#     def get_graphics_object_imbalance_by_period(
#         self,
#         devices: Dict[str, List[List[Any]]],
#         period_from: date,
#         period_to: date,
#     ) -> Dict[str, Any]:  # TODO: typing
#         # Dict["name_object": List[List['object_id': UUID]],
#         # "group_devices":List[List['device_id: UUID', channel: int]],
#         # "flat_devices":List[List['device_id: UUID', channel: int]]}
#         return self._api.request_post(
#             '/list-device/imbalance-graphics',
#             q={'period_from': period_from, 'period_to': period_to},
#             json={'devices': devices},
#         ).check().payload_raw    # type: ignore

#     '''used in services: not used'''
#     @internal_api_error_handler
#     def get_events_magnet_devices(
#         self,
#         devices: List[UUID],
#         period_from: date,
#         period_to: date,
#     ) -> Dict[str, Any]:  # TODO: typing
#         return self._api.request_post(
#             '/events-magnet/devices',
#             q={'period_from': period_from, 'period_to': period_to},
#             json=ApiDeviceEvent(devices=devices),
#         ).check().payload_raw    # type: ignore

#     '''used in services: not used'''
#     @internal_api_error_handler
#     def get_events_low_battery_devices(
#         self,
#         devices: List[UUID],
#         period_from: date,
#         period_to: date,
#     ) -> Dict[str, Any]:  # TODO: typing
#         return self._api.request_post(
#             '/events-battery/devices',
#             q={'period_from': period_from, 'period_to': period_to},
#             json=ApiDeviceEvent(devices=devices),
#         ).check().payload_raw    # type: ignore

#     '''used in services: not used'''
#     @internal_api_error_handler
#     def get_events_devices(
#         self,
#         devices: List[UUID],
#         period_from: date,
#         period_to: date,
#     ) -> Dict[str, Any]:  # TODO: typing
#         return self._api.request_post(
#             '/events/devices',
#             q={'period_from': period_from, 'period_to': period_to},
#             json=ApiDeviceEvent(devices=devices),
#         ).check().payload_raw    # type: ignore

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def get_devices_not_data(
        self,
        devices: ApiDeviceNoDataList,
        limit: Optional[int],
        offset: Optional[int],
        filters: Optional[List[Dict[str, Any]]],
        sorts: Optional[List[Tuple[str, str]]],
    ) -> ApiDeviceNoDataResponse:
        query_params: Dict[str, Any] = {
            "filter": filters,
            "sort": sorts,
            "limit": limit,
            "offset": offset,
        }
        return self._api_device.request_post(
            '/devices/no-data',
            q=query_params,
            json=devices,
        ).typed(ApiDeviceNoDataResponse).check().payload

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def upload_device(
        self,
        device_id: Optional[UUID],
        manufacturer_name: str,
        mac: int,
        manufacturer_serial_number: str,
        modification_type_id: str,
        modification_id: Optional[str],
        date_produced: Optional[datetime],
        firmware_version: Optional[str],
        hardware_version: Optional[str],
        uplink_protocol_id: UUID,
        downlink_protocol_id: UUID,
        key_id: Optional[UUID],
        uplink_encryption_key: Optional[str],
        downlink_encryption_key: Optional[str],
        uplink_encryption_type: EncryptionType,
        downlink_encryption_type: EncryptionType,
        data_input_gateway_network_id: UUID,
        data_gateway_id: UUID,
        device_channels: List[GeneralApiDeviceChannel],
        modification_name: Optional[str],  # for script
        modification_type_name: Optional[str],  # for script
    ) -> ApiImportDeviceResponse:
        return self._api_device.request_post('/import/devices', json={
            'device_id': str(device_id) if device_id is not None else None,
            'manufacturer_name': manufacturer_name,
            'mac': mac,
            'manufacturer_serial_number': manufacturer_serial_number,
            'modification_type_id': modification_type_id,
            'modification_id': modification_id,
            'date_produced': str(date_produced) if date_produced is not None else None,
            'firmware_version': firmware_version,
            'hardware_version': hardware_version,
            'uplink_protocol_id': str(uplink_protocol_id) if uplink_protocol_id is not None else None,
            'downlink_protocol_id': str(downlink_protocol_id) if downlink_protocol_id is not None else None,
            'key_id': str(key_id) if key_id is not None else None,
            'uplink_encryption_key': uplink_encryption_key,
            'downlink_encryption_key': downlink_encryption_key,
            'uplink_encryption_type': uplink_encryption_type,
            'downlink_encryption_type': downlink_encryption_type,
            'data_input_gateway_network_id': str(data_input_gateway_network_id),
            'data_gateway_id': str(data_gateway_id),
            'device_channels': device_channels,
            'modification_name': modification_name,
            'modification_type_name': modification_type_name,
        }).typed(ApiImportDeviceResponse).check().payload

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def get_device_event_sync_chunk(self) -> ApiDeviceStateSyncDataResponse:
        return self._api_device.request_post('/device-state-sync-offsets/events').typed(ApiDeviceStateSyncDataResponse).check().payload

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def update_device_state_sync_offset(self, sync_offset_id: UUID, is_confirmed: bool = True) -> UpdateSyncOffsetResponse:
        return self._api_device.request_patch(f'/device-state-sync-offset/{str(sync_offset_id)}', json={'is_confirmed': is_confirmed}).typed(UpdateSyncOffsetResponse).check().payload

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def get_device_meter_sync_values_chunk(self, sync_limit: int) -> ApiDeviceMeterSyncDataResponse:
        return self._api_device.request_post('/device-meter-sync-offsets/values', q={"sync_limit": sync_limit}).typed(ApiDeviceMeterSyncDataResponse).check().payload

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def update_device_meter_sync_offset(self, sync_offset_id: UUID, is_confirmed: bool = True) -> None:
        self._api_device.request_patch(f'/device-meter-sync-offset/{str(sync_offset_id)}', json={'is_confirmed': is_confirmed}).check(level=InternalApiResponseCheckLevel.STATUS_CODE)

    '''used in services: Service Data Gateway'''
    @internal_api_error_handler
    def get_base_station_by_token(self, api_token: str) -> ApiBaseStationResponse:
        assert self._api_device is not None
        return self._api_device.request_get('/base-stations/auth-check', access_token=api_token).typed(ApiBaseStationResponse).check().payload

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def get_modifications_for_list_devices(self, devices: GeneralDeviceValueModel) -> ApiModificationResponseForDevices:
        return self._api_device.request_post(
            '/device-modifications/list-devices',
            json=devices,
        ).typed(ApiModificationResponseForDevices).check().payload

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def get_last_value_date_by_device(
        self,
        device: DeviceValueDescriptionModel,
        period_selection: Optional[date],
        period_to: Optional[datetime],
    ) -> ApiDeviceLastValueDateResponse:
        return self._api_device.request_post(
            '/devices/last-value-date',
            json=device,
            q={"period_selection": period_selection, "period_to": period_to},
        ).typed(ApiDeviceLastValueDateResponse).check().payload

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def get_last_value_date_by_device_channel(
        self,
        device_channel: DeviceChannelValueDescriptionModel,
        period_selection: Optional[date],
        period_to: Optional[datetime],
    ) -> ApiDeviceChannelLastValueDateResponse:
        return self._api_device.request_post(
            '/device-channels/last-value-date',
            json=device_channel,
            q={"period_selection": period_selection, "period_to": period_to},
        ).typed(ApiDeviceChannelLastValueDateResponse).check().payload

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def get_last_value_date_for_list_devices(
        self,
        devices: GeneralDeviceValueModel,
        period_selection: Optional[date],
        period_to: Optional[datetime],
    ) -> ApiLastValueDateResponseForDevices:
        return self._api_device.request_post(
            '/device-channels/last-value-date/list-devices',
            json=devices,
            q={"period_selection": period_selection, "period_to": period_to},
        ).typed(ApiLastValueDateResponseForDevices).check().payload

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def get_last_value_date_by_device_meter_list(
        self,
        device_meters: GeneralDeviceMeterValueModel,
        period_selection: Optional[date],
        period_to: Optional[datetime],
    ) -> ApiDeviceMeterLastValueDateResponse:
        return self._api_device.request_post(
            '/device-meters/last-value-date/list-meters',
            json=device_meters,
            q={"period_selection": period_selection, "period_to": period_to},
        ).typed(ApiDeviceMeterLastValueDateResponse).check().payload

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def get_last_value_date_by_device_meter(
        self,
        device_meter: DeviceMeterValueDescriptionModel,
        period_selection: Optional[date],
        period_to: Optional[datetime],
    ) -> ApiDeviceMeterLastValueDateResponse:
        return self._api_device.request_post(
            '/device-meters/last-value-date',
            json=device_meter,
            q={"period_selection": period_selection, "period_to": period_to},
        ).typed(ApiDeviceMeterLastValueDateResponse).check().payload

    '''used in services: Iot Account Application Backend, Service Data Gateway'''
    @internal_api_error_handler
    def get_data_gateway_networks(
        self,
        data_gateway_id: UUID,
        limit: Optional[int],
        offset: Optional[int],
        filters: Optional[List[Dict[str, Any]]],
        sorts: Optional[List[Tuple[str, str]]],
    ) -> List[ApiDataGatewayNetworkResponse]:
        query_params: Dict[str, Any] = {
            "filter": filters,
            "sort": sorts,
        }
        if limit is not None:
            query_params['limit'] = limit
        if offset is not None:
            query_params['offset'] = offset
        return self._api_device.request_get(
            f'/data-gateways/{data_gateway_id}/networks',
            q=query_params,
        ).typed(List[ApiDataGatewayNetworkResponse]).check().payload

    '''used in services: Iot Account Application Backend'''
    @internal_api_error_handler
    def get_device_modifications(
        self,
        limit: Optional[int],
        offset: Optional[int],
        filters: Optional[List[Dict[str, Any]]],
        sorts: Optional[List[Tuple[str, str]]],
    ) -> List[ApiDeviceModificationResponse]:
        query_params: Dict[str, Any] = {
            "filter": filters,
            "sort": sorts,
        }
        if limit is not None:
            query_params['limit'] = limit
        if offset is not None:
            query_params['offset'] = offset
        return self._api_device.request_get('/device-modifications', q=query_params).typed(List[ApiDeviceModificationResponse]).check().payload

    '''used in services: Iot Account Application Gateway, Service Data Gateway'''
    @internal_api_error_handler
    def get_device_profiles_granularity_list_by_device_id(
        self,
        device_id: UUID,
        date_from: Optional[datetime],
        date_to: Optional[datetime],
        profile_kinds: Optional[str],
    ) -> List[ApiDeviceProfileGranularityResponse]:
        query: Dict[str, Any] = {"date_from": date_from, "date_to": date_to}
        if profile_kinds:
            query.update({"profile_kinds": profile_kinds})
        return self._api_device.request_get(
            f'/devices/{device_id}/device-profiles/granularities',
            q=query,
        ).typed(List[ApiDeviceProfileGranularityResponse]).check().payload

    '''used in services: Iot Account Application Gateway, Service Data Gateway'''
    @internal_api_error_handler
    def get_device_profiles_list(
        self,
        device_id: UUID,
        granularity_s: Optional[str],
        profile_kinds: Optional[str],
        dt_from: datetime,
        dt_to: datetime,
    ) -> List[ApiDeviceProfileResponse]:
        query: Dict[str, Any] = {"dt_from": dt_from, "dt_to": dt_to}
        if profile_kinds:
            query.update({"profile_kinds": profile_kinds})
        if granularity_s:
            query.update({"granularity_s": granularity_s})
        return self._api_device.request_get(
            f'/devices/{device_id}/device-profiles',
            q=query,
        ).typed(List[ApiDeviceProfileResponse]).check().payload

    @internal_api_error_handler
    def get_bs_downlink_tasks(
        self,
        limit: Optional[int],
        offset: Optional[int],
        bs_ids: Optional[List[UUID]] = None,
        only_active: Optional[bool] = None,
        task_current_statuses: Optional[List[DownlinkTaskStatus]] = None,
    ) -> List[ApiBSDownlinkTaskResponse]:
        filters = []
        query: Dict[str, Any] = {}
        assert self._api_device is not None
        if task_current_statuses:
            query['task_current_statuses'] = ', '.join(task_current_statuses)  # type: ignore
        if only_active:
            query['only_active'] = only_active
        if bs_ids:
            filters.append({"name": "bs_id", "op": "in", "val": tuple(bs_ids)})
        if limit is not None:
            query['limit'] = limit
        if offset is not None:
            query['offset'] = offset
        if filters:
            filters = json.dumps(filters, cls=CustomJSONEncoder)  # type: ignore
        return self._api_device.request_get(
            '/bs-downlink-tasks',
            q=query | {'filter': filters},
        ).typed(List[ApiBSDownlinkTaskResponse]).check().payload

    @internal_api_error_handler
    def get_bs_downlink_task_by_id(
        self,
        task_id: UUID,
    ) -> ApiBSDownlinkTaskResponse:
        assert self._api_device is not None
        return self._api_device.request_get(
            f'/bs-downlink-tasks/{task_id}',
        ).typed(ApiBSDownlinkTaskResponse).check().payload

    @internal_api_error_handler
    def get_binary_data_list(
        self,
    ) -> List[ApiBinaryDataResponse]:
        assert self._api_device is not None
        return self._api_device.request_get(
            '/binary-data',
        ).typed(List[ApiBinaryDataResponse]).check().payload

    @internal_api_error_handler
    def get_binary_data_by_id(
        self,
        binary_data_id: UUID,
    ) -> ApiBinaryDataResponse:
        assert self._api_device is not None
        return self._api_device.request_get(
            f'/binary-data/{binary_data_id}',
        ).typed(ApiBinaryDataResponse).check().payload

    @internal_api_error_handler
    def get_bs_downlink_task_status_log(
        self,
        bs_downlink_task_id: UUID,
    ) -> ApiBSDownLinkStatusLogResponse:
        query: Dict[str, Any] = {"bs_downlink_task_id": bs_downlink_task_id}
        assert self._api_device is not None
        return self._api_device.request_get(
            '/bs-downlink-tasks/status-log',
            q=query,
        ).typed(ApiBSDownLinkStatusLogResponse).check().payload

#     '''used in services: not used'''
#     @internal_api_error_handler
#     def get_data_gateway_netowork_device_list(
#         self,
#         gateway_id: UUID,
#         devices: List[ApiDataGatewayNetworkDevicesInfo],
#         limit: Optional[int],
#         offset: Optional[int],
#         filters: Optional[List[Dict[str, Any]]],
#         sorts: Optional[List[Tuple[str, str]]],
#     ) -> InternalApiResponse[List[ApiDataGatewayNetworkDeviceInfoResponse]]:        # type: ignore
#         query_params: Dict[str, Any] = {
#             "filter": filters,
#             "sort": sorts,
#         }
#         if limit is not None:
#             query_params['limit'] = limit
#         if offset is not None:
#             query_params['offset'] = offset
#         return self._api_device.request_post(
#             f'/data-gateways/{gateway_id}/devices',
#             q=query_params,
#             json=json.dumps(ApiDataGatewayNetworkDevicesBody(devices=devices).model_dump()),
#         ).typed(List[ApiDataGatewayNetworkDeviceInfoResponse]).check()

    '''used in services: Iot Account Application Gateway, Service Data Gateway'''
    @internal_api_error_handler
    def get_data_aggregator_api_user(
        self,
        api_user_id: UUID,
    ) -> DataAggregatorApiUserResponse:
        return self._api_device.request_get(
            f'/api-users/{api_user_id}',
        ).typed(DataAggregatorApiUserResponse).check().payload

    @internal_api_error_handler
    def get_data_aggregator_uptime_by_device_id_and_channel_id(
        self,
        device_id: UUID,
        channel_id: UUID,
        limit: Optional[int],
        offset: Optional[int],
        filters: Optional[List[Dict[str, Any]]],
        sorts: Optional[List[Tuple[str, str]]],
    ) -> InternalApiResponse[List[ApiDeviceUptimeResponse]]:        # type: ignore # broken type checking
        query_params: Dict[str, Any] = {
            "filter": filters,
            "sort": sorts,
        }
        if limit is not None:
            query_params['limit'] = limit
        if offset is not None:
            query_params['offset'] = offset
        return self._api_device.request_get(
            f'/devices/{device_id}/channels/{channel_id}/uptimes',
            q=query_params,
        ).typed(List[ApiDeviceUptimeResponse]).check()

    @internal_api_error_handler
    def get_data_aggregator_uptime_by_device_id(
        self,
        device_id: UUID,
        limit: Optional[int],
        offset: Optional[int],
        filters: Optional[List[Dict[str, Any]]],
        sorts: Optional[List[Tuple[str, str]]],
    ) -> InternalApiResponse[List[ApiDeviceUptimeResponse]]:        # type: ignore # broken type checking
        query_params: Dict[str, Any] = {
            "filter": filters,
            "sort": sorts,
        }
        if limit is not None:
            query_params['limit'] = limit
        if offset is not None:
            query_params['offset'] = offset
        return self._api_device.request_get(
            f'/devices/{device_id}/device-sensors/uptimes',
            q=query_params,
        ).typed(List[ApiDeviceUptimeResponse]).check()

    @internal_api_error_handler
    def get_device_sensors(
        self,
        limit: Optional[int],
        offset: Optional[int],
        device_ids: Optional[List[UUID]] = None,
        sensor_types: Optional[List[SensorType]] = None,
    ) -> List[ApiDeviceSensorResponse]:
        filters = []
        query: Dict[str, Any] = {}
        assert self._api_device is not None
        if sensor_types:
            query['sensor_types'] = ', '.join(sensor_types)  # type: ignore
        if device_ids:
            filters.append({"name": "device_id", "op": "in", "val": tuple(device_ids)})
        if limit is not None:
            query['limit'] = limit
        if offset is not None:
            query['offset'] = offset
        if filters:
            filters = json.dumps(filters, cls=CustomJSONEncoder)  # type: ignore
        return self._api_device.request_get(
            '/devices/device-sensors',
            q=query | {'filter': filters},
        ).typed(List[ApiDeviceSensorResponse]).check().payload
