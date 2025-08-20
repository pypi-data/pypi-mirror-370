from datetime import datetime
from typing import Dict, List, Optional, Union
from uuid import UUID


TChannelInfoBox = List[Dict[str, Union[List[Dict[str, Optional[datetime]]], int]]]

TDevicesInfoBoxItem = Dict[str, Union[int, TChannelInfoBox]]

TDevicesInfoBox = Dict[UUID, TDevicesInfoBoxItem]
