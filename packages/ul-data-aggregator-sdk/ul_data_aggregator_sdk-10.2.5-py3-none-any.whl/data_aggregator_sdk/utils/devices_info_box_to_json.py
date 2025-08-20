from typing import Dict, Any

from data_aggregator_sdk.constants.annotations import TDevicesInfoBox


def devices_info_box_to_json(devices_info_box: TDevicesInfoBox) -> Dict[str, Any]:
    return {str(key): value for key, value in devices_info_box.items()}
